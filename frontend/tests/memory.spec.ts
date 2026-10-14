import { expect,test,type APIRequestContext,type Page } from "@playwright/test";
import type { Task } from "../lib/api";

async function createTask(request:APIRequestContext,title=`Plan dinner tomorrow / memory ${crypto.randomUUID().slice(0,8)}`):Promise<Task>{
 const response=await request.post("/api/v1/tasks",{data:{title,origin_device_id:"00000000-0000-4000-8000-000000000010"}});expect(response.status()).toBe(201);return response.json();
}
async function hold(page:Page,path:string){
 let release!:()=>void,mark!:()=>void,finish!:()=>void;const gate=new Promise<void>(r=>{release=r;}),started=new Promise<void>(r=>{mark=r;}),done=new Promise<void>(r=>{finish=r;});
 await page.route(`**${path}`,async route=>{const response=await route.fetch();mark();await gate;await route.fulfill({response}).catch(()=>undefined);finish();},{times:1});return{release,started,done};
}
async function load(page:Page,task:Task){await page.goto(`/memory?task=${task.id}`);await expect(page.getByRole("button",{name:"Remember preference",exact:true})).toBeEnabled();}

test("explicit memory, cross-task planning, correction, supersession and deletion use persistent state",async({page,request})=>{
 const a=await createTask(request);await load(page,a);const value=`quiet Italian restaurants ${crypto.randomUUID().slice(0,8)}`;
 await page.getByLabel("Explicit preference",{exact:true}).fill(value);await page.getByRole("button",{name:"Remember preference",exact:true}).click();
 const original=page.locator(".memory-card").filter({has:page.getByRole("heading",{name:value,exact:true})});await expect(original).toContainText("USER_EXPLICIT");await expect(original).toContainText("ACTIVE / USER");
 const id=(await original.getAttribute("data-memory-id"))!;
 const b=await createTask(request);await load(page,b);await page.getByLabel("Memory query",{exact:true}).fill(value);await page.getByRole("button",{name:"Search memory",exact:true}).click();await expect(page.locator(".memory-hit").filter({hasText:id})).toContainText("SEMANTIC_MATCH");
 const result=await request.post(`/api/v1/tasks/${b.id}/run-agents`,{data:{idempotency_key:crypto.randomUUID()}});expect((await result.json()).execution.status).toBe("DONE");
 await page.goto(`/tasks/${b.id}`);await expect(page.getByTestId("memory-workspace")).toContainText(value);await load(page,b);
 await original.getByRole("button",{name:"Correct",exact:true}).click();const changed=value.replace("Italian","Japanese");await page.getByLabel("Corrected memory",{exact:true}).fill(changed);await page.getByRole("button",{name:"Save correction",exact:true}).click();
 const corrected=page.locator(".memory-card").filter({has:page.getByRole("heading",{name:changed,exact:true})});await expect(corrected).toContainText("USER_CORRECTION");await expect(original).toContainText("SUPERSEDED");
 await original.getByRole("button",{name:"History",exact:true}).click();await expect(page.locator(".memory-history")).toContainText("MEMORY_SUPERSEDED");
 await corrected.getByRole("button",{name:"Delete",exact:true}).click();await expect(corrected).toContainText("DELETED");await page.reload();await expect(corrected).toContainText("DELETED");
 const retrieval=await(await request.post('/api/v1/memory/search',{data:{task_id:b.id,query:changed,subject:"demo_user"}})).json();expect(retrieval.hits.some((h:{memory_id:string})=>h.memory_id===id)).toBe(false);
});

test("visual candidate stays unconfirmed, can be edited and confirmed, and a second candidate can be rejected",async({page,request})=>{
 const task=await createTask(request);await page.goto(`/perception?task=${task.id}`);await page.getByRole("button",{name:"Continue on Wearable",exact:true}).click();await page.getByRole("button",{name:"Attach wearable fixture",exact:true}).click();await expect(page.locator(".visual-evidence")).toBeVisible();await page.getByRole("button",{name:"Run perception",exact:true}).click();await expect(page.locator(".observation-card")).toHaveCount(5);
 await load(page,task);await page.getByRole("button",{name:"Create visual candidate",exact:true}).click();const candidate=page.locator(".memory-card").filter({has:page.getByRole("heading",{name:"Possible coffee-related preference",exact:true})}).filter({hasText:"PENDING_CONFIRMATION"});await expect(candidate).toContainText("VISUAL_OBSERVATION / INFERRED");
 await candidate.getByRole("button",{name:"Edit & confirm",exact:true}).click();const value=`Coffee ${crypto.randomUUID().slice(0,8)}`;await page.getByLabel("Corrected memory",{exact:true}).fill(value);await page.getByRole("button",{name:"Save correction",exact:true}).click();const confirmed=page.locator(".memory-card").filter({has:page.getByRole("heading",{name:value,exact:true})});await expect(confirmed).toContainText("CONFIRMED");await expect(confirmed).toContainText("VISUAL_OBSERVATION");await confirmed.getByRole("button",{name:"Delete",exact:true}).click();await expect(confirmed).toContainText("DELETED");
 await page.getByRole("button",{name:"Create visual candidate",exact:true}).click();await expect(candidate).toBeVisible();const rejectedId=await candidate.getAttribute("data-memory-id");await candidate.getByRole("button",{name:"Reject",exact:true}).click();await expect(page.locator(`.memory-card[data-memory-id="${rejectedId}"]`)).toContainText("REJECTED");
 await page.getByRole("button",{name:"Continue on Mobile",exact:true}).click();await page.reload();await expect(page.locator(".device-node.current h3")).toHaveText("Mobile");
});

test("duplicate memory clicks and late acknowledgment cannot restore old task",async({page,request})=>{
 const a=await createTask(request),b=await createTask(request);await load(page,a);const testValue=`temporary task note ${crypto.randomUUID().slice(0,8)}`;await page.getByLabel("Explicit preference",{exact:true}).fill(testValue);
 const held=await hold(page,"/api/v1/memory");let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/api/v1/memory"))++posts;});
 try{await page.evaluate(()=>{const button=[...document.querySelectorAll<HTMLButtonElement>("button")].find(b=>b.textContent==="Remember preference");button?.click();button?.click();});await held.started;expect(posts).toBe(1);await page.selectOption("#task-select",b.id);await expect(page.getByTestId("memory-workspace")).toHaveAttribute("data-task-id",b.id);held.release();await held.done;await expect(page.getByTestId("identity-id")).toHaveText(b.id);
 const memories=await(await request.get("/api/v1/memory")).json();const created=memories.find((m:{id:string;value:string})=>m.value===testValue);
 if(created)expect((await request.delete(`/api/v1/memory/${created.id}`,{data:{idempotency_key:crypto.randomUUID()}})).status()).toBe(200);
 }finally{held.release();}
});

test("late retrieval result cannot become another task's context",async({page,request})=>{
 const a=await createTask(request),b=await createTask(request),c=await createTask(request);await load(page,a);const held=await hold(page,"/api/v1/memory/search");
 try{await page.getByRole("button",{name:"Search memory",exact:true}).click();await held.started;await page.selectOption("#task-select",b.id);await page.selectOption("#task-select",c.id);await expect(page.getByTestId("memory-workspace")).toHaveAttribute("data-task-id",c.id);held.release();await held.done;await expect(page.getByTestId("identity-id")).toHaveText(c.id);}finally{held.release();}
});

test("Memory Center fits 390px and explains fixture rank relevance",async({page,request})=>{
 const task=await createTask(request);await page.setViewportSize({width:390,height:844});await load(page,task);await expect(page.getByTestId("memory-workspace")).toContainText("NOT A REAL SEMANTIC MODEL");await page.getByRole("button",{name:"Search memory",exact:true}).click();await expect(page.locator(".memory-hit").first()).toContainText("Ranks:");expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:"test-results/phase6-memory-mobile.png",fullPage:true});
});

test("approval acknowledgment survives a pending same-task background refresh",async({page,request})=>{
 const task=await createTask(request);await page.goto(`/approvals?task=${task.id}`);await expect(page.getByRole("button",{name:"Approve",exact:true})).toBeEnabled();
 const proposal=await(await request.get(`/api/v1/tasks/${task.id}/proposals`)).json();
 const ack=await hold(page,`/api/v1/proposals/${proposal[0].id}/approve`);
 const read=await hold(page,`/api/v1/tasks/${task.id}`);
 try{
  await page.getByRole("button",{name:"Approve",exact:true}).click();await ack.started;
  await page.evaluate(()=>window.dispatchEvent(new Event("focus")));await read.started;
  ack.release();await ack.done;
  await expect(page.getByRole("button",{name:"Retry original request",exact:true})).toHaveCount(0);
  read.release();await read.done;
  await expect(page.getByRole("button",{name:"Execute simulation",exact:true})).toBeEnabled();
 }finally{ack.release();read.release();}
});

test("restored approval intent waits for its owned proposal snapshot before retry",async({page,request})=>{
 const task=await createTask(request);await page.goto(`/approvals?task=${task.id}`);await expect(page.getByRole("button",{name:"Approve",exact:true})).toBeEnabled();
 const proposals=await(await request.get(`/api/v1/tasks/${task.id}/proposals`)).json();const ack=await hold(page,`/api/v1/proposals/${proposals[0].id}/approve`);
 try{
  await page.getByRole("button",{name:"Approve",exact:true}).click();await ack.started;
  const read=await hold(page,`/api/v1/tasks/${task.id}/proposals`);
  try{
   await page.reload();await read.started;
   await expect(page.getByRole("button",{name:"Retry original request",exact:true})).toBeDisabled();
   ack.release();await ack.done;read.release();await read.done;
   await page.getByRole("button",{name:"Retry original request",exact:true}).click();
   await expect(page.getByRole("button",{name:"Execute simulation",exact:true})).toBeEnabled();
  }finally{read.release();}
 }finally{ack.release();}
});
