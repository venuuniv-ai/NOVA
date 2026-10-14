import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import type { Task } from "../lib/api";
import type { ModelCall } from "../lib/models";

async function createTask(request: APIRequestContext, title = `Model routing acceptance ${crypto.randomUUID().slice(0, 8)}`): Promise<Task> {
  const response = await request.post("/api/v1/tasks", { data: {
    title,
    origin_device_id: "00000000-0000-4000-8000-000000000010",
  } }); expect(response.status()).toBe(201); return response.json();
}
async function calls(request: APIRequestContext, taskId: string): Promise<ModelCall[]> {
  const response = await request.get(`/api/v1/tasks/${taskId}/model-calls`);
  expect(response.ok()).toBeTruthy(); return response.json();
}
async function hold(page: Page, path: string) {
  let release!: () => void, markStarted!: () => void, markDone!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  const started = new Promise<void>(resolve => { markStarted = resolve; });
  const done = new Promise<void>(resolve => { markDone = resolve; });
  await page.route(`**${path}`, async route => {
    const response = await route.fetch(); markStarted(); await gate;
    await route.fulfill({ response }).catch(() => undefined); markDone();
  }, { times: 1 }); return { release, started, done };
}

test("Model Router shows configured status, simple route, cache accounting and refresh persistence", async ({ page, request }) => {
  const task = await createTask(request); await page.goto(`/models?task=${task.id}`);
  await expect(page.getByRole("button", { name: "Evaluate route", exact: true })).toBeEnabled();
  await expect(page.locator(".provider-grid")).toContainText("DISABLED");
  await expect(page.locator(".provider-grid")).toContainText("NOT AN LLM");
  await expect(page.locator(".model-disclosure")).toContainText("NO PAID PROVIDERS ENABLED");
  await expect(page.locator(".requested-model-input")).toContainText("Summarize tomorrow's schedule.");
  await page.getByRole("button", { name: "Evaluate route", exact: true }).click();
  await expect(page.locator(".model-call")).toHaveCount(1);
  await expect(page.getByTestId("routing-decision")).toContainText("PERSONAL");
  await expect(page.getByTestId("routing-decision")).toContainText("LOW");
  await expect(page.getByTestId("routing-decision")).toContainText("FIXTURE_FALLBACK");
  await expect(page.locator(".model-call")).toContainText("MISS");
  await page.getByRole("button", { name: "Evaluate route", exact: true }).click();
  await expect(page.locator(".model-call")).toHaveCount(2);
  await expect(page.locator(".model-call").first()).toContainText("HIT");
  await expect(page.locator(".model-call").first()).toContainText("NO FRESH INVOCATION");
  const original = await calls(request, task.id); expect(original[0].response?.output).toBeNull();
  await page.reload(); await expect(page.locator(".model-call")).toHaveCount(2);
  expect(await calls(request, task.id)).toEqual(original);
  await expect(page.locator(".budget-panel")).toContainText("UTC");
  await page.screenshot({ path: "test-results/phase4-model-router-desktop.png", fullPage: true });
});

test("reasoning, local-only privacy, budget denial and provider failure have explicit persisted reasons", async ({ page, request }) => {
  const task = await createTask(request); await page.goto(`/models?task=${task.id}`);
  await expect(page.getByRole("button", { name: "Evaluate route", exact: true })).toBeEnabled();
  for (const [scenario, reason] of [["REASONING", "REASONING_REPLAY_LIMITATION"], ["PRIVACY", "PRIVACY_LOCAL_ONLY"], ["BUDGET", "BUDGET_DOWNGRADE"], ["FAILURE", "FALLBACK_USED"]]) {
    await page.getByRole("combobox", { name: "Routing scenario", exact: true }).selectOption(scenario);
    await page.getByRole("button", { name: "Evaluate route", exact: true }).click();
    await expect(page.getByTestId("routing-decision")).toContainText(reason);
    await expect(page.getByRole("button", { name: "Evaluate route", exact: true })).toBeEnabled();
  }
  const history = await calls(request, task.id); expect(history).toHaveLength(4);
  expect(history.find(call => call.decision.privacy_class === "SENSITIVE_LOCAL_ONLY")?.response?.cache_status).toBe("BYPASS");
  const budget = history.find(call => call.decision.reason_codes.includes("BUDGET_DOWNGRADE"))!;
  expect(budget.response?.mode).toBe("POLICY_REPLAY");
  expect(budget.attempts.some(attempt => attempt.provider === "test-priced-probe" && attempt.invoked)).toBe(false);
  expect(history[0].attempts[0].error).toBe("UNAVAILABLE");
});

test("late model response cannot replace rapid task selection and duplicate clicks do not repeat POST", async ({ page, request }) => {
  const a = await createTask(request), b = await createTask(request), c = await createTask(request);
  await page.goto(`/models?task=${a.id}`); await expect(page.getByRole("button", { name: "Evaluate route", exact: true })).toBeEnabled();
  const posts: string[] = [];
  page.on("request", req => { if (req.method() === "POST" && req.url().endsWith("/model-router/evaluate")) posts.push(req.postData() ?? ""); });
  const held = await hold(page, "/api/v1/model-router/evaluate");
  try {
    await page.evaluate(() => { const button = [...document.querySelectorAll<HTMLButtonElement>("button")].find(item => item.textContent === "Evaluate route"); button?.click(); button?.click(); });
    await held.started; expect(posts).toHaveLength(1);
    await page.selectOption("#task-select", b.id); await expect(page).toHaveURL(new RegExp(`task=${b.id}$`));
    await page.selectOption("#task-select", c.id); await expect(page.getByTestId("model-workspace")).toHaveAttribute("data-task-id", c.id);
    await expect(page.getByRole("button", { name: "Evaluate route", exact: true })).toBeEnabled();
    held.release(); await held.done;
    await expect(page.getByTestId("model-workspace")).toHaveAttribute("data-task-id", c.id);
    await expect(page.locator(".model-call")).toHaveCount(0);
    expect(await calls(request, a.id)).toHaveLength(1); expect(await calls(request, b.id)).toHaveLength(0);
    await page.getByRole("button", { name: "Evaluate route", exact: true }).click();
    await expect(page.locator(".model-call")).toHaveCount(1); expect(await calls(request, c.id)).toHaveLength(1);
  } finally { held.release(); }
});

test("late task model-call history response is ignored after a newer selection", async ({ page, request }) => {
  const a = await createTask(request), b = await createTask(request), c = await createTask(request);
  await page.goto(`/models?task=${a.id}`); await expect(page.getByRole("button", { name: "Evaluate route", exact: true })).toBeEnabled();
  const held = await hold(page, `/api/v1/tasks/${b.id}/model-calls`);
  try {
    await page.selectOption("#task-select", b.id); await held.started;
    await page.selectOption("#task-select", c.id);
    await expect(page.getByTestId("model-workspace")).toHaveAttribute("data-task-id", c.id);
    await expect(page.getByRole("button", { name: "Evaluate route", exact: true })).toBeEnabled();
    held.release(); await held.done;
    await expect(page.getByTestId("model-workspace")).toHaveAttribute("data-task-id", c.id);
    await expect(page.getByTestId("identity-id")).toHaveText(c.id);
  } finally { held.release(); }
});

test("refresh and handoff preserve unacknowledged request identity without another call", async ({ page, request }) => {
  const task = await createTask(request); await page.goto(`/models?task=${task.id}`);
  await expect(page.getByRole("button", { name: "Evaluate route", exact: true })).toBeEnabled();
  const held = await hold(page, "/api/v1/model-router/evaluate");
  try {
    await page.getByRole("button", { name: "Evaluate route", exact: true }).click(); await held.started;
    const first = (await calls(request, task.id))[0];
    await page.getByRole("button", { name: "Continue on Wearable", exact: true }).click();
    await expect(page.locator(".device-node.current h3")).toHaveText("Wearable");
    await page.reload(); held.release(); await held.done;
    await page.getByRole("button", { name: "Retry original model request", exact: true }).click();
    await expect(page.getByTestId("routing-decision")).toContainText("Original request metadata replayed");
    const history = await calls(request, task.id); expect(history).toHaveLength(1);
    expect(history[0].request_id).toBe(first.request_id); expect(history[0].trace_id).toBe(first.trace_id);
    expect(history[0].decision.device_context).toBe("DESKTOP");
  } finally { held.release(); }
});

test("Model Router fits the 390px viewport", async ({ page, request }) => {
  const task = await createTask(request); await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/models?task=${task.id}`); await page.getByRole("button", { name: "Evaluate route", exact: true }).click();
  await expect(page.locator(".model-call")).toHaveCount(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: "test-results/phase4-model-router-mobile.png", fullPage: true });
});

test("routed agents identify the routed service and a routed draft remains unapproved", async ({ page, request }) => {
  const task = await createTask(request, "Find somewhere for dinner with Sarah tomorrow after my meeting.");
  const result = await request.post(`/api/v1/tasks/${task.id}/run-routed-agents`, { data: { idempotency_key: crypto.randomUUID() } });
  expect(result.status()).toBe(201);
  expect((await result.json()).execution.status).toBe("DONE");
  await page.goto(`/intelligence?task=${task.id}`);
  await expect(page.locator(".intelligence-disclosure")).toContainText("ROUTED / APPLICATION POLICY");
  await page.getByRole("link", { name: "Recorded model providers", exact: true }).click();
  await expect(page.locator(".model-call")).toHaveCount(4);
  const proposalTask = await createTask(request);
  const draft = await request.post("/api/v1/proactive/evaluate-routed", { data: { task_id: proposalTask.id, idempotency_key: crypto.randomUUID() } });
  expect(draft.status()).toBe(200);
  const evaluated = await draft.json(); expect(evaluated.proposal.status).toBe("PENDING_APPROVAL");
  await page.goto(`/approvals?task=${proposalTask.id}`);
  await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
  await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toHaveCount(0);
  await expect(page.getByTestId("proposal-id")).toHaveText(evaluated.proposal.id);
});
