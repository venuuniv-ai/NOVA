import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import type { Task } from "../lib/api";

async function create(request: APIRequestContext) {
  const response = await request.post("/api/v1/tasks", { data: { title: `Dinner after my meeting with Sarah / visual ${crypto.randomUUID().slice(0,8)}`, origin_device_id: "00000000-0000-4000-8000-000000000010" } });
  expect(response.status()).toBe(201); return response.json() as Promise<Task>;
}
async function wearable(request: APIRequestContext, task: Task) {
  const response = await request.post(`/api/v1/tasks/${task.id}/handoff`, { data: { source_device_id: "00000000-0000-4000-8000-000000000010", target_device_id: "00000000-0000-4000-8000-000000000020", idempotency_key: crypto.randomUUID() } });
  expect(response.status()).toBe(200);
}
async function frame(page: Page) {
  await page.getByRole("button", { name: "Attach wearable fixture", exact: true }).click();
  await expect(page.locator(".visual-evidence")).toContainText("FIXTURE MEDIA");
  await page.getByRole("button", { name: "Run perception", exact: true }).click();
  await expect(page.locator(".observation-card")).toHaveCount(5);
}
async function hold(page: Page, path: string) {
  let release!: () => void, mark!: () => void, finish!: () => void;
  const gate = new Promise<void>(r => { release = r; }), started = new Promise<void>(r => { mark = r; }), done = new Promise<void>(r => { finish = r; });
  await page.route(`**${path}`, async route => { const response = await route.fetch(); mark(); await gate; await route.fulfill({ response }).catch(() => undefined); finish(); }, { times: 1 });
  return { release, started, done };
}

test("wearable fixture, perception evidence, VISION route, reasoning and human approval persist on Mobile", async ({ page, request }) => {
  const task = await create(request); await page.goto(`/perception?task=${task.id}`);
  await page.getByRole("button", { name: "Continue on Wearable", exact: true }).click();
  await expect(page.locator(".device-node.current h3")).toHaveText("Wearable");
  await frame(page);
  await expect(page.locator(".visual-image img")).toBeVisible();
  expect(await page.locator(".visual-image img").evaluate(img => (img as HTMLImageElement).naturalWidth)).toBe(480);
  await expect(page.locator(".pipeline-stage")).toContainText(["INGEST", "CLIP / SKIPPED", "DINOV2 / SKIPPED", "FIXTURE_VISION / DONE", "FIXTURE_VLM / DONE", "SAM / SKIPPED"]);
  await expect(page.locator(".observation-card").first()).toContainText("SIMULATED / FIXTURE");
  await expect(page.locator(".visual-interpretation")).toContainText("consistent with a meeting/work environment");
  await expect(page.locator(".actual-region")).toHaveCount(0);
  const before = await (await request.get(`/api/v1/tasks/${task.id}/perception`)).json();
  await page.getByRole("button", { name: "Reason with visual context", exact: true }).click();
  await expect(page.getByText(/Proposal: PENDING_APPROVAL/)).toBeVisible();
  await page.getByRole("button", { name: "Continue on Mobile", exact: true }).click();
  await expect(page.locator(".device-node.current h3")).toHaveText("Mobile");
  await page.reload(); await expect(page.locator(".observation-card")).toHaveCount(5);
  expect(await (await request.get(`/api/v1/tasks/${task.id}/perception`)).json()).toEqual(before);
  await page.getByRole("link", { name: "Inspect VISION route", exact: true }).click();
  await expect(page.locator(".model-call").first()).toContainText("VISION_REQUIRED");
  await expect(page.locator(".model-call").first()).toContainText("fixture-vlm");
  await page.goto(`/approvals?task=${task.id}`);
  await expect(page.getByRole("button", { name: "Approve", exact: true })).toBeEnabled();
  await expect(page.getByRole("button", { name: "Execute simulation", exact: true })).toHaveCount(0);
  await page.goto(`/tasks/${task.id}`); await expect(page.getByTestId("perception-workspace")).toContainText("4 fixture observations");
});

test("duplicate clicks and late perception acknowledgment preserve newer task ownership", async ({ page, request }) => {
  const a = await create(request), b = await create(request); await wearable(request,a);
  await page.goto(`/perception?task=${a.id}`); await page.getByRole("button", { name: "Attach wearable fixture", exact: true }).click();
  await expect(page.locator(".visual-evidence")).toBeVisible();
  const held = await hold(page, `/api/v1/tasks/${a.id}/perception`);
  let posts = 0; page.on("request", req => { if (req.method() === "POST" && req.url().endsWith(`/tasks/${a.id}/perception`)) ++posts; });
  try {
    await page.evaluate(() => { const button = [...document.querySelectorAll<HTMLButtonElement>("button")].find(b => b.textContent === "Run perception"); button?.click(); button?.click(); });
    await held.started; expect(posts).toBe(1);
    await page.selectOption("#task-select", b.id); await expect(page.getByTestId("perception-workspace")).toHaveAttribute("data-task-id",b.id);
    held.release(); await held.done;
    await expect(page.getByTestId("identity-id")).toHaveText(b.id); await expect(page.locator(".observation-card")).toHaveCount(0);
  } finally { held.release(); }
});

test("late perception history cannot replace task C after A to B to C", async ({ page, request }) => {
  const a=await create(request),b=await create(request),c=await create(request); await page.goto(`/perception?task=${a.id}`);
  await expect(page.getByRole("button",{name:"Attach wearable fixture",exact:true})).toBeEnabled();
  const held=await hold(page,`/api/v1/tasks/${b.id}/perception`);
  try {
    await page.selectOption("#task-select",b.id); await held.started; await page.selectOption("#task-select",c.id);
    await expect(page.getByTestId("perception-workspace")).toHaveAttribute("data-task-id",c.id);
    held.release();await held.done;await expect(page.getByTestId("identity-id")).toHaveText(c.id);
    await expect(page.locator(".observation-card")).toHaveCount(0);
  } finally {held.release();}
});

test("upload sanitization and malformed image error use real backend validation", async ({page,request}) => {
  const task=await create(request);await wearable(request,task);await page.goto(`/perception?task=${task.id}`);await frame(page);
  const list=await (await request.get(`/api/v1/tasks/${task.id}/media`)).json();
  const image=await request.get(`/api/v1/tasks/${task.id}/media/${list[0].id}/content`);
  await page.getByLabel("Upload image",{exact:true}).setInputFiles({name:"../../untrusted.jpg",mimeType:"image/png",buffer:await image.body()});
  await expect.poll(async () => (await (await request.get(`/api/v1/tasks/${task.id}/media`)).json()).length).toBe(2);
  await expect(page.getByRole("button", { name: "Attach wearable fixture", exact: true })).toBeEnabled();
  await page.getByLabel("Upload image",{exact:true}).setInputFiles({name:"fake.jpg",mimeType:"image/jpeg",buffer:Buffer.from("not an image")});
  await expect(page.getByRole("alert", { name: "Perception error" })).toContainText("safely decoded");
});

test("perception fits 390px with no invented geometry",async ({page,request}) => {
  const task=await create(request);await wearable(request,task);await page.setViewportSize({width:390,height:844});await page.goto(`/perception?task=${task.id}`);await frame(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await expect(page.locator(".actual-region")).toHaveCount(0);
  await page.screenshot({path:"test-results/phase5-perception-mobile.png",fullPage:true});
});

test("refresh preserves the original perception request key after a handoff", async ({page,request}) => {
  const task=await create(request);await wearable(request,task);await page.goto(`/perception?task=${task.id}`);
  await page.getByRole("button",{name:"Attach wearable fixture",exact:true}).click();await expect(page.locator(".visual-evidence")).toBeVisible();
  const held=await hold(page,`/api/v1/tasks/${task.id}/perception`);
  try {
    await page.getByRole("button",{name:"Run perception",exact:true}).click();await held.started;
    const before=await (await request.get(`/api/v1/tasks/${task.id}/perception`)).json();
    await page.getByRole("button",{name:"Continue on Mobile",exact:true}).click();
    await expect(page.locator(".device-node.current h3")).toHaveText("Mobile");
    await page.reload();held.release();await held.done;
    await page.getByRole("button",{name:"Retry original perception",exact:true}).click();
    await expect(page.locator(".observation-card")).toHaveCount(5);
    expect(await (await request.get(`/api/v1/tasks/${task.id}/perception`)).json()).toEqual(before);
  } finally {held.release();}
});
