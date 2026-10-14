import { expect, test, type APIRequestContext, type Page, type Request } from "@playwright/test";
import { DEMO_TITLE, type Task } from "../lib/api";

async function createSelectionTask(request: APIRequestContext, label: string): Promise<Task> {
  const response = await request.post("/api/v1/tasks", { data: {
    title: `F-01 regression ${label} ${crypto.randomUUID()}`,
    origin_device_id: "00000000-0000-4000-8000-000000000010",
  } });
  expect(response.status()).toBe(201);
  return response.json();
}

async function holdRealResponse(page: Page, path: string) {
  let release!: () => void;
  let started!: (request: Request) => void;
  let delivered!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  const observed = new Promise<Request>(resolve => { started = resolve; });
  const completed = new Promise<void>(resolve => { delivered = resolve; });
  await page.route(`**${path}`, async route => {
    const response = await route.fetch(); // Real FastAPI response, held before browser delivery.
    started(route.request());
    await gate;
    // A superseded browser fetch may already have been aborted, which is safe.
    await route.fulfill({ response }).catch(() => undefined);
    delivered();
  });
  return { observed, release, completed };
}

async function settleHeldResponse(page: Page, held: Awaited<ReturnType<typeof holdRealResponse>>) {
  const request = await held.observed;
  held.release();
  await held.completed;
  const response = await request.response();
  if (response) await response.finished();
  // Let response microtasks and React's following paint commit before asserting ownership.
  await page.evaluate(() => new Promise<void>(resolve => {
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
  }));
}

test("real backend continuity survives browser refresh and historical retry", async ({ page, request }) => {
  const browserErrors: string[] = [];
  page.on("pageerror", error => browserErrors.push(error.message));
  await page.goto("/");
  await page.getByRole("button", { name: "New task", exact: true }).click();
  await expect(page.getByLabel("TASK TITLE")).toHaveValue(DEMO_TITLE);
  const creation = page.waitForResponse(response => response.url().endsWith("/api/v1/tasks") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Create task on Desktop" }).click();
  const taskId = (await (await creation).json()).id as string;
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.getByTestId("identity-id")).toBeVisible();
  await expect(page.getByTestId("identity-id")).toHaveText(taskId);
  await expect(page.locator(".device-node.current h3")).toHaveText("Desktop");

  await page.getByRole("link", { name: "Device continuity", exact: true }).click();
  await page.getByRole("button", { name: "Continue on Wearable" }).click();
  await expect(page.locator(".device-node.current h3")).toHaveText("Wearable");
  await expect(page.getByTestId("identity-id")).toHaveText(taskId);
  await page.reload();
  await expect(page.locator(".device-node.current h3")).toHaveText("Wearable");
  await page.screenshot({ path: "test-results/continuity-desktop.png", fullPage: true });

  await page.getByRole("button", { name: "Continue on Mobile" }).click();
  await expect(page.locator(".device-node.current h3")).toHaveText("Mobile");
  await page.reload();
  await expect(page.locator(".device-node.current h3")).toHaveText("Mobile");
  await expect(page.getByTestId("identity-id")).toHaveText(taskId);

  await page.getByRole("link", { name: "Task detail", exact: true }).click();
  await expect(page.getByTestId("task-id")).toHaveText(taskId);
  await expect(page.getByTestId("current-device")).toHaveText("Mobile");
  await expect(page.locator(".event-code")).toHaveText([
    "HANDOFF_WEARABLE_TO_MOBILE", "HANDOFF_DESKTOP_TO_WEARABLE", "TASK_CREATED",
  ]);
  await page.getByRole("button", { name: "Retry Desktop → Wearable", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("No duplicate event or transition");
  await expect(page.getByTestId("current-device")).toHaveText("Mobile");
  const events = await (await request.get(`/api/v1/tasks/${taskId}/events`)).json();
  expect(events).toHaveLength(3);
  expect(events.map((event: { event_type: string }) => event.event_type)).toEqual([
    "TASK_CREATED", "HANDOFF_DESKTOP_TO_WEARABLE", "HANDOFF_WEARABLE_TO_MOBILE",
  ]);
  expect(browserErrors).toEqual([]);
});

test("small screen preserves readable continuity without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/continuity");
  await expect(page.getByTestId("identity-id")).toBeVisible();
  await expect(page.locator(".device-node")).toHaveCount(3);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: "test-results/continuity-mobile.png", fullPage: true });
});

test("backend offline state blocks mutations and supports recovery", async ({ page }) => {
  await page.route("**/api/v1/**", route => route.fulfill({
    status: 503,
    contentType: "application/json",
    body: JSON.stringify({ error: { code: "BACKEND_OFFLINE", message: "Local backend is unreachable." } }),
  }));
  await page.goto("/");
  await expect(page.getByRole("alert", { name: "NOVA error" })).toContainText("Local services are offline");
  await expect(page.getByRole("button", { name: "New task", exact: true })).toBeDisabled();
  await page.unroute("**/api/v1/**");
  await page.getByRole("button", { name: "Retry connection" }).click();
  await expect(page.getByTestId("identity-id")).toBeVisible();
  await expect(page.getByRole("alert", { name: "NOVA error" })).toHaveCount(0);
});

test("missing persisted task displays an actionable error", async ({ page }) => {
  await page.goto("/tasks/00000000-0000-4000-8000-ffffffffffff");
  await expect(page.getByRole("alert", { name: "NOVA error" })).toContainText("Task was not found.");
  await expect(page.getByRole("button", { name: "New task", exact: true })).toBeDisabled();
});

test("F-01 blocks stale handoffs while the requested task is loading", async ({ page, request }) => {
  const taskA = await createSelectionTask(request, "A");
  const taskB = await createSelectionTask(request, "B");
  const handoffs: string[] = [];
  page.on("request", outgoing => {
    if (outgoing.method() === "POST" && outgoing.url().endsWith("/handoff")) handoffs.push(outgoing.url());
  });
  await page.goto(`/continuity?task=${taskA.id}`);
  await expect(page.getByTestId("identity-id")).toHaveText(taskA.id);
  const held = await holdRealResponse(page, `/api/v1/tasks/${taskB.id}`);
  try {
    await page.selectOption("#task-select", taskB.id);
    await held.observed;
    await expect(page).toHaveURL(new RegExp(`task=${taskB.id}$`));
    await expect(page.getByRole("status")).toContainText("Loading selected task");
    await expect(page.getByRole("button", { name: "New task", exact: true })).toBeDisabled();
    await expect(page.getByTestId("identity-id")).toHaveCount(0);
    await expect(page.getByRole("button", { name: /Continue on|Retry original/ })).toHaveCount(0);
    // Even a DOM click attempt cannot find a stale mutation control.
    await page.evaluate(() => {
      document.querySelector<HTMLButtonElement>(".handoff-bar button")?.click();
    });
    expect(handoffs).toEqual([]);

    await settleHeldResponse(page, held);
    await expect(page.getByTestId("identity-id")).toHaveText(taskB.id);
    await expect(page.locator("#task-select")).toHaveValue(taskB.id);
    await expect(page.getByRole("button", { name: "Continue on Wearable" })).toBeEnabled();
    await page.getByRole("button", { name: "Continue on Wearable" }).click();
    await expect(page.locator(".device-node.current h3")).toHaveText("Wearable");
    expect(handoffs).toEqual([new URL(`/api/v1/tasks/${taskB.id}/handoff`, page.url()).href]);
    const persistedA = await (await request.get(`/api/v1/tasks/${taskA.id}`)).json();
    expect(persistedA.current_device_id).toBe(taskA.current_device_id);
    expect(await (await request.get(`/api/v1/tasks/${taskA.id}/events`)).json()).toHaveLength(1);
  } finally { held.release(); }
});

test("late B response cannot replace C after a newer task selection", async ({ page, request }) => {
  const taskA = await createSelectionTask(request, "race A");
  const taskB = await createSelectionTask(request, "race B");
  const taskC = await createSelectionTask(request, "race C");
  await page.goto(`/continuity?task=${taskA.id}`);
  await expect(page.getByTestId("identity-id")).toHaveText(taskA.id);
  const held = await holdRealResponse(page, `/api/v1/tasks/${taskB.id}`);
  try {
    await page.selectOption("#task-select", taskB.id);
    await held.observed;
    await expect(page.getByRole("status")).toContainText("Loading selected task");
    await page.selectOption("#task-select", taskC.id);
    await expect(page.getByTestId("identity-id")).toHaveText(taskC.id);
    await expect(page.locator("#task-select")).toHaveValue(taskC.id);
    await settleHeldResponse(page, held);
    await expect(page).toHaveURL(new RegExp(`task=${taskC.id}$`));
    await expect(page.getByTestId("identity-id")).toHaveText(taskC.id);
    await expect(page.locator("#task-select")).toHaveValue(taskC.id);
    await expect(page.getByRole("button", { name: "Continue on Wearable" })).toBeEnabled();
    await expect(page.getByRole("alert", { name: "NOVA error" })).toHaveCount(0);
  } finally { held.release(); }
});

test("late handoff completion cannot restore a previous task selection", async ({ page, request }) => {
  const taskA = await createSelectionTask(request, "mutation A");
  const taskB = await createSelectionTask(request, "mutation B");
  await page.goto(`/continuity?task=${taskA.id}`);
  await expect(page.getByTestId("identity-id")).toHaveText(taskA.id);
  const held = await holdRealResponse(page, `/api/v1/tasks/${taskA.id}/handoff`);
  try {
    await page.getByRole("button", { name: "Continue on Wearable" }).click();
    await held.observed;
    await page.selectOption("#task-select", taskB.id);
    await expect(page.getByTestId("identity-id")).toHaveText(taskB.id);
    await expect(page.getByRole("button", { name: "Continue on Wearable" })).toBeDisabled();
    await settleHeldResponse(page, held);
    await expect(page).toHaveURL(new RegExp(`task=${taskB.id}$`));
    await expect(page.getByTestId("identity-id")).toHaveText(taskB.id);
    await expect(page.locator(".device-node.current h3")).toHaveText("Desktop");
    await expect(page.getByRole("button", { name: "Continue on Wearable" })).toBeEnabled();
    await expect(page.getByRole("status")).toHaveCount(0);
  } finally { held.release(); }
});
