import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import type { Task } from "../lib/api";
import type { Proposal, ProposalDetail } from "../lib/proactive";

async function createTask(request: APIRequestContext): Promise<Task> {
  const result = await request.post("/api/v1/tasks", { data: { title: `Phase 3 Architecture Review ${crypto.randomUUID().slice(0, 8)}`,
    origin_device_id: "00000000-0000-4000-8000-000000000010" } });
  expect(result.status()).toBe(201); return result.json();
}
async function proposals(request: APIRequestContext, taskId: string): Promise<Proposal[]> {
  const result = await request.get(`/api/v1/tasks/${taskId}/proposals`); expect(result.ok()).toBeTruthy(); return result.json();
}
async function hold(page: Page, path: string) {
  let release!: () => void, started!: () => void, done!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  const begin = new Promise<void>(resolve => { started = resolve; });
  const complete = new Promise<void>(resolve => { done = resolve; });
  await page.route(`**${path}`, async route => {
    const response = await route.fetch(); started(); await gate;
    await route.fulfill({ response }).catch(() => undefined); done();
  }, { times: 1 });
  return { release, begin, complete };
}

test("proactive context prepares a proposal; approval and simulation persist across device handoffs", async ({ page, request }) => {
  const task = await createTask(request);
  await page.goto(`/?task=${task.id}`);
  await expect(page.locator(".risk-summary")).toContainText("29m");
  await expect(page.locator(".risk-summary")).toContainText("35m");
  await expect(page.locator(".risk-summary")).toContainText("+6m");
  await page.getByRole("link", { name: "Review proposal", exact: true }).click();
  await expect(page.locator(".proposal-card")).toContainText("REQUIRES APPROVAL");
  await expect(page.locator(".proposal-card blockquote")).toContainText("2:06 PM");
  await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toHaveCount(0);
  const original = (await proposals(request, task.id))[0];
  for (const device of ["Wearable", "Mobile"]) {
    await page.getByRole("button", { name: `Continue on ${device}`, exact: true }).click();
    await expect(page.locator(".device-node.current h3")).toHaveText(device);
    await page.reload();
    await expect(page.getByTestId("proposal-id")).toHaveText(original.id);
    expect((await proposals(request, task.id))[0].trace_id).toBe(original.trace_id);
  }
  await page.getByRole("button", { name: "Approve", exact: true }).click();
  await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toBeEnabled();
  await page.getByRole("button", { name: "Execute simulation", exact: true }).click();
  await expect(page.locator(".proposal-card .success-notice")).toContainText("NO EXTERNAL MESSAGE WAS SENT");
  await page.reload();
  await expect(page.locator(".proposal-card")).toContainText("SIMULATED DELIVERY COMPLETE");
  const detail: ProposalDetail = await (await request.get(`/api/v1/proposals/${original.id}`)).json();
  expect(detail.approval?.payload_hash).toBe(original.payload_hash);
  expect(detail.execution?.receipt.external_message_sent).toBe(false);
  expect(detail.proposal.task_id).toBe(task.id);
  await page.screenshot({ path: "test-results/phase3-approval-mobile-context.png", fullPage: true });
});

test("reject is persistent and never exposes execution", async ({ page, request }) => {
  const task = await createTask(request); await page.goto(`/approvals?task=${task.id}`);
  await page.getByRole("button", { name: "Reject", exact: true }).click();
  await expect(page.locator(".proposal-card")).toContainText("REJECTED");
  await page.reload(); await expect(page.locator(".proposal-card")).toContainText("REJECTED");
  await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toHaveCount(0);
});

test("editing approved content creates a new unapproved proposal and invalidates old approval", async ({ page, request }) => {
  const task = await createTask(request); await page.goto(`/approvals?task=${task.id}`);
  await page.getByRole("button", { name: "Approve", exact: true }).click();
  await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toBeEnabled();
  const original = (await proposals(request, task.id))[0];
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByRole("textbox", { name: "Edit draft", exact: true }).fill("Running 15 minutes late.");
  await page.getByRole("button", { name: "Save new proposal", exact: true }).click();
  await expect(page.locator(".proposal-card")).toHaveCount(2);
  await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toHaveCount(0);
  const all = await proposals(request, task.id); const edited = all.find(item => item.supersedes_id === original.id)!;
  expect(edited.status).toBe("PENDING_APPROVAL");
  expect(all.find(item => item.id === original.id)?.status).toBe("SUPERSEDED");
  const denied = await request.post(`/api/v1/proposals/${original.id}/execute`, { data: { idempotency_key: crypto.randomUUID() } });
  expect(denied.status()).toBe(409);
  await page.reload(); await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
  await page.getByRole("button", { name: "Approve", exact: true }).click();
  await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toBeEnabled();
});

test("duplicate approval and execution clicks issue one request each", async ({ page, request }) => {
  const task = await createTask(request); await page.goto(`/approvals?task=${task.id}`);
  await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
  const item = (await proposals(request, task.id))[0];
  const posts: string[] = [];
  page.on("request", req => { if (req.method() === "POST" && /\/(approve|execute)$/.test(req.url())) posts.push(req.url()); });
  for (const [operation, label] of [["approve", "Approve"], ["execute", "Execute simulation"]]) {
    const held = await hold(page, `/api/v1/proposals/${item.id}/${operation}`);
    try {
      await page.evaluate(buttonLabel => {
        const button = [...document.querySelectorAll<HTMLButtonElement>("button")].find(item => item.textContent === buttonLabel);
        button?.click(); button?.click();
      }, label);
      await held.begin;
      expect(posts.filter(url => url.endsWith(`/${operation}`))).toHaveLength(1);
      held.release(); await held.complete;
      if (operation === "approve") await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toBeEnabled();
      else await expect(page.locator(".proposal-card")).toContainText("SIMULATED DELIVERY COMPLETE");
    } finally { held.release(); }
  }
});

test("late proposal read from B cannot overwrite selected C", async ({ page, request }) => {
  const a = await createTask(request), b = await createTask(request), c = await createTask(request);
  await page.goto(`/approvals?task=${a.id}`); await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
  const held = await hold(page, `/api/v1/tasks/${b.id}/proposals`);
  try {
    await page.selectOption("#task-select", b.id); await held.begin;
    await page.selectOption("#task-select", c.id);
    await expect(page.getByTestId("approvals")).toHaveAttribute("data-task-id", c.id);
    await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
    held.release(); await held.complete;
    await expect(page.getByTestId("approvals")).toHaveAttribute("data-task-id", c.id);
    const item = (await proposals(request, c.id))[0];
    await expect(page.getByTestId("proposal-id")).toHaveText(item.id);
    expect(item.task_id).toBe(c.id);
  } finally { held.release(); }
});

test("late approval acknowledgement cannot restore old task; refresh retries original intent", async ({ page, request }) => {
  const a = await createTask(request), b = await createTask(request);
  await page.goto(`/approvals?task=${a.id}`); await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
  const item = (await proposals(request, a.id))[0];
  const held = await hold(page, `/api/v1/proposals/${item.id}/approve`);
  try {
    await page.getByRole("button", { name: "Approve", exact: true }).click(); await held.begin;
    await page.getByRole("button", { name: "Continue on Wearable", exact: true }).click();
    await expect(page.locator(".device-node.current h3")).toHaveText("Wearable");
    await page.selectOption("#task-select", b.id); await expect(page.getByTestId("approvals")).toHaveAttribute("data-task-id", b.id);
    held.release(); await held.complete;
    await expect(page.getByTestId("approvals")).toHaveAttribute("data-task-id", b.id);
    await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
    expect((await proposals(request, b.id))[0].status).toBe("PENDING_APPROVAL");
    await page.goto(`/approvals?task=${a.id}`);
    await page.getByRole("button", { name: "Retry original request", exact: true }).click();
    await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toBeEnabled();
    await page.reload(); await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toBeEnabled();
  } finally { held.release(); }
});

test("Approval Center fits mobile viewport", async ({ page, request }) => {
  const task = await createTask(request); await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/approvals?task=${task.id}`); await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: "test-results/phase3-approval-390px.png", fullPage: true });
});
