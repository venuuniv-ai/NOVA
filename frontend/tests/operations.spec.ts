import { expect, test } from "@playwright/test";

// Explicitly scripted metadata transport; not real event delivery or model evidence.
const taskA = "11111111-1111-4111-8111-111111111111";
const taskB = "22222222-2222-4222-8222-222222222222";
async function setup(page: import("@playwright/test").Page) {
  await page.route("**/api/v1/tasks", route => route.fulfill({ json: [
    { id: taskA, title: "First scripted task" }, { id: taskB, title: "Second scripted task" },
  ] }));
  await page.route("**/api/v1/operations/events", route => route.fulfill({ json: { delivery: "AT_LEAST_ONCE" } }));
}
const snapshot = (id: string) => ({ task_id: id, events: [], jobs: [], projection_sequence: null,
  page: { through: 40, next_after: null as number | null, next_jobs_after: null as number | null } });

test("scripted operations pages preserve snapshot and show safe metadata", async ({ page }) => {
  await setup(page);
  await page.route(`**/api/v1/operations/tasks/${taskA}?*`, route => {
    const url = new URL(route.request().url());
    expect(url.searchParams.get("limit")).toBe("20");
    const more = url.searchParams.has("after");
    if (more) expect(url.searchParams.get("through")).toBe("40");
    return route.fulfill({ json: { ...snapshot(taskA), events: [{ id: more ? "event-2" : "event-1", sequence: more ? 40 : 20,
      type: "ContextEvent.changed", state: "PUBLISHED", attempts: 1, consumers: ["proactive"] }],
      jobs: [{ id: "job-1", sequence: 20, state: "DEAD", attempts: 1, result_id: null, diagnostic: "TERMINAL_JOB_FAILURE" }],
      page: { through: 40, next_after: more ? null : 20, next_jobs_after: null } } });
  });
  await page.goto("/operations");
  await page.getByLabel("Operations task").selectOption(taskA);
  const panel = page.getByRole("region", { name: "Task delivery evidence" });
  await expect(panel.locator("[data-event-id]")).toHaveCount(1);
  await expect(panel).toContainText("TERMINAL_JOB_FAILURE");
  await panel.getByRole("button", { name: "Load more events" }).click();
  await expect(panel.locator("[data-event-id]")).toHaveCount(2);
  await expect(panel.getByRole("button", { name: "Load more events" })).toHaveCount(0);
  await expect(panel.locator("[data-job-id]")).toHaveCount(1);
  await expect(panel.getByRole("button", { name: "Execute", exact: true })).toHaveCount(0);
});

test("scripted operations errors recover and old task responses do not leak", async ({ page }) => {
  await setup(page);
  let refuse = true;
  await page.route(`**/api/v1/operations/tasks/${taskA}?*`, async route => {
    if (refuse) return route.fulfill({ status: 503, json: { error: { message: "Controlled unavailable", code: "UNAVAILABLE" } } });
    await new Promise(resolve => setTimeout(resolve, 300));
    return route.fulfill({ json: { ...snapshot(taskA), events: [{ id: "stale-task-event", sequence: 1, type: "Task.changed", state: "PENDING", attempts: 0, consumers: [] }] } });
  });
  await page.route(`**/api/v1/operations/tasks/${taskB}?*`, route => route.fulfill({ json: snapshot(taskB) }));
  await page.goto("/operations");
  await page.getByLabel("Operations task").selectOption(taskA);
  await expect(page.getByRole("alert")).toBeVisible();
  refuse = false;
  await page.getByRole("button", { name: "Refresh delivery records" }).click();
  await expect(page.getByRole("status")).toContainText("Loading");
  await page.getByLabel("Operations task").selectOption(taskB);
  await expect(page.getByRole("region", { name: "Task delivery evidence" })).toContainText("No delivery events.");
  await expect(page.getByRole("region", { name: "Task delivery evidence" })).toContainText("No durable jobs.");
  await expect(page.locator("[data-event-id='stale-task-event']")).toHaveCount(0);
});
