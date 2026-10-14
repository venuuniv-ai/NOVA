import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import { DEMO_TITLE, type Task } from "../lib/api";
import type { Intelligence } from "../lib/intelligence";

async function createTask(request: APIRequestContext, label?: string): Promise<Task> {
  const response = await request.post("/api/v1/tasks", { data: {
    title: label ? `${DEMO_TITLE} [${label}]` : DEMO_TITLE,
    origin_device_id: "00000000-0000-4000-8000-000000000010",
  } });
  expect(response.status()).toBe(201);
  return response.json();
}

async function intelligence(request: APIRequestContext, taskId: string): Promise<Intelligence> {
  const response = await request.get(`/api/v1/tasks/${taskId}/plan`);
  expect(response.ok()).toBeTruthy();
  return response.json();
}

async function holdResponse(page: Page, path: string) {
  let release!: () => void;
  let markStarted!: () => void;
  let markComplete!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  const started = new Promise<void>(resolve => { markStarted = resolve; });
  const complete = new Promise<void>(resolve => { markComplete = resolve; });
  await page.route(`**${path}`, async route => {
    const response = await route.fetch();
    markStarted();
    await gate;
    await route.fulfill({ response }).catch(() => undefined);
    markComplete();
  }, { times: 1 });
  return { release, started, complete };
}

test("Phase 2 dinner intelligence and its graph survive both device handoffs", async ({ page, request }) => {
  const task = await createTask(request);
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto(`/intelligence?task=${task.id}`);
  await expect(page.getByTestId("identity-id")).toHaveText(task.id);
  await page.getByRole("button", { name: "Run NOVA Intelligence", exact: true }).click();
  await expect(page.locator(".agent-node[data-status='DONE']")).toHaveCount(6);
  await expect(page.locator(".intelligence-disclosure")).toContainText("FIXTURE / DETERMINISTIC");
  await expect(page.locator(".intelligence-disclosure")).toContainText("DEMO CONTEXT");
  await page.getByRole("button", { name: "Inspect Calendar agent", exact: true }).click();
  await expect(page.locator(".agent-inspector")).toContainText("CalendarPlugin.find_events_related_to_task");
  await expect(page.locator(".agent-inspector")).toContainText("5:00 PM");
  await page.locator(".agent-inspector .structured-output summary").click();
  await expect(page.locator(".agent-inspector .structured-output pre")).toContainText("Product Review");
  await expect(page.locator(".agent-inspector .structured-output pre")).toContainText("Downtown");
  await page.getByRole("button", { name: "Inspect Memory agent", exact: true }).click();
  await expect(page.locator(".agent-inspector")).toContainText("Sarah prefers Italian food.");
  await expect(page.locator(".agent-inspector")).toContainText("DEMO_FIXTURE");
  await expect(page.locator(".final-plan")).toContainText("PASS");
  for (const fact of ["5:00 PM", "Downtown", "Italian", "6:00 PM"]) {
    await expect(page.locator(".final-plan")).toContainText(fact);
  }
  const original = await intelligence(request, task.id);
  await page.screenshot({ path: "test-results/intelligence-desktop.png", fullPage: true });
  await page.getByRole("button", { name: "Continue on Wearable", exact: true }).click();
  await expect(page.locator(".device-node.current h3")).toHaveText("Wearable");
  await page.reload();
  await expect(page.getByTestId("identity-id")).toHaveText(task.id);
  await expect(page.locator(".agent-node[data-status='DONE']")).toHaveCount(6);
  expect(await intelligence(request, task.id)).toEqual(original);
  await page.getByRole("button", { name: "Continue on Mobile", exact: true }).click();
  await expect(page.locator(".device-node.current h3")).toHaveText("Mobile");
  await page.reload();
  await expect(page.getByTestId("identity-id")).toHaveText(task.id);
  await expect(page.locator(".final-plan")).toContainText("Sarah prefers Italian food.");
  expect(await intelligence(request, task.id)).toEqual(original);
  await page.getByRole("link", { name: "Task detail", exact: true }).click();
  await expect(page.getByTestId("current-device")).toHaveText("Mobile");
  await expect(page.locator(".final-plan")).toContainText("6:00 PM");
  expect(errors).toEqual([]);
});

test("duplicate clicks and late execution response cannot overwrite rapid task switching", async ({ page, request }) => {
  const taskA = await createTask(request, "switch A");
  const taskB = await createTask(request, "switch B");
  const taskC = await createTask(request, "switch C");
  const posts: string[] = [];
  page.on("request", outgoing => {
    if (outgoing.method() === "POST" && outgoing.url().endsWith("/run-agents")) posts.push(outgoing.url());
  });
  await page.goto(`/intelligence?task=${taskA.id}`);
  await expect(page.getByRole("button", { name: "Run NOVA Intelligence", exact: true })).toBeEnabled();
  const held = await holdResponse(page, `/api/v1/tasks/${taskA.id}/run-agents`);
  try {
    await page.evaluate(() => {
      const button = document.querySelector<HTMLButtonElement>('button[aria-label="Run NOVA Intelligence"]');
      button?.click(); button?.click();
    });
    await held.started;
    await expect(page.getByRole("button", { name: "Run NOVA Intelligence", exact: true })).toBeDisabled();
    expect(posts).toHaveLength(1);
    await page.selectOption("#task-select", taskB.id);
    await expect(page).toHaveURL(new RegExp(`task=${taskB.id}$`));
    await page.selectOption("#task-select", taskC.id);
    await expect(page.getByTestId("identity-id")).toHaveText(taskC.id);
    await expect(page.getByTestId("intelligence")).toHaveAttribute("data-task-id", taskC.id);
    await expect(page.locator(".execution-caption")).toContainText("NO EXECUTION YET");
    held.release();
    await held.complete;
    await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
    await expect(page.getByTestId("identity-id")).toHaveText(taskC.id);
    await expect(page.locator(".execution-caption")).toContainText("NO EXECUTION YET");
    expect((await intelligence(request, taskA.id)).agent_runs).toHaveLength(6);
    expect((await intelligence(request, taskB.id)).agent_runs).toHaveLength(0);
    expect((await intelligence(request, taskC.id)).agent_runs).toHaveLength(0);
    await page.getByRole("button", { name: "Run NOVA Intelligence", exact: true }).click();
    await expect(page.locator(".agent-node[data-status='DONE']")).toHaveCount(6);
    expect(posts).toEqual([
      new URL(`/api/v1/tasks/${taskA.id}/run-agents`, page.url()).href,
      new URL(`/api/v1/tasks/${taskC.id}/run-agents`, page.url()).href,
    ]);
  } finally { held.release(); }
});

test("handoff and refresh during unacknowledged execution preserve the original execution key", async ({ page, request }) => {
  const task = await createTask(request, "refresh in flight");
  await page.goto(`/intelligence?task=${task.id}`);
  await expect(page.getByRole("button", { name: "Run NOVA Intelligence", exact: true })).toBeEnabled();
  const held = await holdResponse(page, `/api/v1/tasks/${task.id}/run-agents`);
  try {
    await page.getByRole("button", { name: "Run NOVA Intelligence", exact: true }).click();
    await held.started;
    const original = await intelligence(request, task.id);
    await page.getByRole("button", { name: "Continue on Wearable", exact: true }).click();
    await expect(page.locator(".device-node.current h3")).toHaveText("Wearable");
    await page.reload();
    await expect(page.getByTestId("identity-id")).toHaveText(task.id);
    await expect(page.locator(".final-plan")).toContainText("Italian");
    held.release();
    await held.complete;
    await expect(page.getByRole("button", { name: "Run NOVA Intelligence", exact: true })).toContainText("Retry original execution");
    await page.getByRole("button", { name: "Run NOVA Intelligence", exact: true }).click();
    await expect(page.locator(".intelligence-workspace .success-notice")).toContainText("no duplicate agents");
    expect(await intelligence(request, task.id)).toEqual(original);
    await page.getByRole("button", { name: "Continue on Mobile", exact: true }).click();
    await expect(page.locator(".device-node.current h3")).toHaveText("Mobile");
    await page.reload();
    await expect(page.locator(".agent-node[data-status='DONE']")).toHaveCount(6);
    expect(await intelligence(request, task.id)).toEqual(original);
  } finally { held.release(); }
});

test("late intelligence read from B never replaces selected C", async ({ page, request }) => {
  const taskA = await createTask(request, "read A");
  const taskB = await createTask(request, "read B");
  const taskC = await createTask(request, "read C");
  await page.goto(`/intelligence?task=${taskA.id}`);
  await expect(page.getByRole("button", { name: "Run NOVA Intelligence", exact: true })).toBeEnabled();
  const held = await holdResponse(page, `/api/v1/tasks/${taskB.id}/plan`);
  try {
    await page.selectOption("#task-select", taskB.id);
    await held.started;
    await page.selectOption("#task-select", taskC.id);
    await expect(page.getByTestId("intelligence")).toHaveAttribute("data-task-id", taskC.id);
    await expect(page.getByRole("button", { name: "Run NOVA Intelligence", exact: true })).toBeEnabled();
    held.release();
    await held.complete;
    await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
    await expect(page.getByTestId("identity-id")).toHaveText(taskC.id);
    await expect(page.getByTestId("intelligence")).toHaveAttribute("data-task-id", taskC.id);
    await expect(page).toHaveURL(new RegExp(`task=${taskC.id}$`));
  } finally { held.release(); }
});

test("intelligence graph remains within a mobile viewport", async ({ page, request }) => {
  const task = await createTask(request, "mobile graph");
  const response = await request.post(`/api/v1/tasks/${task.id}/run-agents`, { data: { idempotency_key: crypto.randomUUID() } });
  expect(response.status()).toBe(201);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/intelligence?task=${task.id}`);
  await expect(page.locator(".agent-node[data-status='DONE']")).toHaveCount(6);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: "test-results/intelligence-mobile.png", fullPage: true });
});
