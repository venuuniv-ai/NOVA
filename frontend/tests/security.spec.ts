import {test,expect} from "@playwright/test";
test.use({trace:"off"});
const token=process.env.NOVA_TEST_BEARER??"";
test.describe("Phase 8 authenticated local stack",()=>{
 test.skip(!token,"Requires explicit authenticated Phase 8 stack and runtime operator token");

 test("short-lived token login uses an HttpOnly cookie and logout clears it",async({page})=>{
  await page.goto('/auth');await page.getByLabel('Access token').fill('invalid-controlled-token');await page.getByRole('button',{name:'Sign in',exact:true}).click();await expect(page.getByRole('status')).toContainText('Authentication refused');
  await page.getByLabel('Access token').fill(token);await page.getByRole('button',{name:'Sign in',exact:true}).click();await expect(page).toHaveURL(/\/$/);await expect(page.getByRole('heading',{name:'Command Center.'})).toBeVisible();
  const cookie=(await page.context().cookies()).find(c=>c.name==='nova_session');expect(cookie?.httpOnly).toBe(true);expect(cookie?.sameSite).toBe('Strict');
  const status=await page.evaluate(async()=> (await fetch('/auth/session',{method:'DELETE'})).status);expect(status).toBe(200);expect((await page.context().cookies()).some(c=>c.name==='nova_session')).toBe(false);
 });
 test("operations shows actual event receipts and a subscribed draft remains pending",async({page,request})=>{
  test.setTimeout(90000);const headers={Authorization:`Bearer ${token}`};
  const devices=await(await request.get('/api/v1/devices',{headers})).json();const desktop=devices.find((d:{type:string})=>d.type==='DESKTOP'),wearable=devices.find((d:{type:string})=>d.type==='WEARABLE');
  const result=await request.post('/api/v1/tasks',{headers,data:{title:`Phase8 browser ${crypto.randomUUID()}`,origin_device_id:desktop.id}});expect(result.status()).toBe(201);const task=await result.json();
  await page.goto('/auth');await page.getByLabel('Access token').fill(token);await page.getByRole('button',{name:'Sign in',exact:true}).click();await expect(page).toHaveURL(/\/$/);await page.goto('/operations');await page.getByLabel('Operations task').selectOption(task.id);await page.getByRole('button',{name:'Enable fixture proactive review'}).click();await expect(page.getByRole('status')).toContainText('Subscribed');
  await request.post(`/api/v1/tasks/${task.id}/handoff`,{headers,data:{source_device_id:desktop.id,target_device_id:wearable.id,idempotency_key:crypto.randomUUID()}});
  await expect.poll(async()=> (await(await request.get(`/api/v1/operations/tasks/${task.id}`,{headers})).json()).jobs[0]?.state,{timeout:45000}).toBe('DONE');
  const proposals=await(await request.get(`/api/v1/tasks/${task.id}/proposals`,{headers})).json();expect(proposals).toHaveLength(1);expect(proposals[0].status).toBe('PENDING_APPROVAL');
 });
 test("session creation rejects cross-origin requests",async({request})=>{
  const result=await request.post('/auth/session',{data:{token},headers:{Origin:'http://untrusted.invalid'}});expect(result.status()).toBe(403);
 });
});

test.describe("Phase 8 local OIDC provider",()=>{
 test.skip(!process.env.NOVA_TEST_OIDC_PASSWORD,"Requires deliberately provisioned local OIDC provider");
 test("authorization code with PKCE establishes a verified session",async({page})=>{
  await page.goto('/auth/oidc');await expect(page).toHaveURL(/localhost:8180/);await page.getByLabel('Username or email').fill('nova-local-fixture');await page.getByLabel('Password',{exact:true}).fill(process.env.NOVA_TEST_OIDC_PASSWORD!);await page.getByRole('button',{name:'Sign In',exact:true}).click();await expect(page).toHaveURL('http://localhost:3000/');await expect(page.getByRole('heading',{name:'Command Center.'})).toBeVisible();
 });
 test("forged callback state cannot create a session",async({request})=>{const response=await request.get('/auth/oidc/callback?state=forged&code=forged');expect(response.status()).toBe(401);});
});
