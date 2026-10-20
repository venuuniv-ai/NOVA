import { expect, test } from "@playwright/test";

test("owned context draft queues and cancels through the application without model or action execution", async ({ page, request }) => {
  const devices = await (await request.get("/api/v1/devices")).json();
  const desktop = devices.find((device: { type: string }) => device.type === "DESKTOP");
  const task = await (await request.post("/api/v1/tasks", { data: {
    title: `Owned draft ${crypto.randomUUID()}`, origin_device_id: desktop.id,
  } })).json();
  const subject = `browser_${crypto.randomUUID().slice(0, 8)}`;
  const created = await request.post("/api/v1/memory", { data: {
    idempotency_key: crypto.randomUUID(), subject, predicate: "preferred_cuisine", value: "noodles",
  } });
  expect(created.status()).toBe(201);
  const memory = await created.json();
  await page.goto(`/approvals?task=${task.id}`);
  const panel = page.getByRole("region", { name: "Owned evidence drafts" });
  await panel.getByLabel("Preference question").fill(`Which cuisine does ${subject} prefer?`);
  await panel.getByLabel("Supporting memory UUID").fill(memory.id);
  await panel.getByRole("button", { name: "Prepare owned draft", exact: true }).click();
  const draft = panel.locator("[data-draft-id]");
  await expect(draft).toContainText("QUEUED");
  await expect(draft).toContainText("Execution disabled");
  await draft.getByRole("button", { name: "Cancel owned draft" }).click();
  await expect(draft).toContainText("CANCELLED");
  await page.reload();
  await expect(panel.locator("[data-draft-id]")).toContainText("CANCELLED");
  const records = await (await request.get(`/api/v1/tasks/${task.id}/drafts`)).json();
  expect(records).toHaveLength(1);
  expect(records[0].content).toBeNull();
  expect(records[0].execution_enabled).toBe(false);
});

test("scripted draft transport displays every lifecycle state without execution controls", async ({ page, request }) => {
  const task = await (await request.post("/api/v1/tasks", { data: {
    title: `Draft display fixture ${crypto.randomUUID()}`,
    origin_device_id: "00000000-0000-4000-8000-000000000010",
  } })).json();
  const evidenceId = "96b55c85-0acf-4d1c-a3ed-4d3422138d79";
  let state = "PENDING_APPROVAL";
  await page.route(`**/api/v1/tasks/${task.id}/drafts`, route => route.fulfill({ json: [{
    id: "display-fixture", task_id: task.id, state,
    content: state === "PENDING_APPROVAL" ? "Controlled preference quote." : null,
    error: state === "FAILED" ? "DRAFT_INVALID" : null,
    expires_at: "2026-10-19T10:00:00Z", proposal_id: "display-proposal",
    verification: state === "PENDING_APPROVAL" ? "EXACT_SUPPORTED_QUOTES" : "NOT_CURRENTLY_VERIFIED",
    simulation: true, execution_enabled: false,
    evidence: state === "PENDING_APPROVAL" ? [{ id: evidenceId, text: "Controlled preference quote.", origin: "FIXTURE", binding: "fixture" }] : [],
  }] }));
  await page.goto(`/approvals?task=${task.id}`);
  const panel = page.getByRole("region", { name: "Owned evidence drafts" });
  await expect(panel.locator("[data-draft-id]")).toContainText(evidenceId);
  await expect(panel.getByRole("button", { name: "Approve", exact: true })).toHaveCount(0);
  await expect(panel.getByRole("button", { name: "Execute simulation", exact: true })).toHaveCount(0);
  for (const next of ["QUEUED", "RUNNING", "CANCELLED", "REJECTED", "EXPIRED", "FAILED"]) {
    state = next;
    await panel.getByRole("button", { name: "Refresh owned drafts" }).click();
    await expect(panel.locator("[data-draft-id]")).toContainText(next);
    await expect(panel.locator("[data-draft-id]")).not.toContainText(evidenceId);
    await expect(panel.locator("[data-draft-id]")).not.toContainText("Controlled preference quote.");
    await expect(panel.getByRole("button", { name: "Cancel owned draft", exact: true })).toHaveCount(
      ["QUEUED", "RUNNING"].includes(next) ? 1 : 0,
    );
    await expect(panel.getByRole("button", { name: "Reject owned draft", exact: true })).toHaveCount(0);
    if (next === "FAILED") {
      await expect(panel.getByRole("status")).toHaveText("DRAFT_INVALID");
    }
  }
});
