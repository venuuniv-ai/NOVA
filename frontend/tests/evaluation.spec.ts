import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
test.setTimeout(120000);
async function start(request:APIRequestContext,suite="SMOKE",configuration="BASELINE"){
 const r=await request.post("/api/v1/evaluation/runs",{data:{idempotency_key:crypto.randomUUID(),suite,configuration}});expect(r.status()).toBe(202);return (await r.json()).id as string;
}
async function complete(request:APIRequestContext,id:string){await expect.poll(async()=>{const r=await request.get(`/api/v1/evaluation/runs/${id}`);return(await r.json()).status;},{timeout:90000}).not.toBe("RUNNING");}
async function hold(page:Page,path:string){let release!:()=>void,signal!:()=>void;const gate=new Promise<void>(r=>{release=r;}),started=new Promise<void>(r=>{signal=r;});await page.route(`**${path}`,async route=>{const response=await route.fetch();signal();await gate;await route.fulfill({response}).catch(()=>undefined);},{times:1});return{release,started};}

test("SMOKE evaluates actual state, explains denominators and survives refresh",async({page,request})=>{
 await page.goto('/evals');await expect(page.getByLabel('Evaluation dataset')).toContainText('nova-golden');await expect(page.getByRole('button',{name:'Run Evaluation',exact:true})).toBeEnabled();await page.getByRole('button',{name:'Run Evaluation',exact:true}).click();await expect(page.getByTestId('evaluation-run')).toBeVisible();const id=(await page.getByTestId('evaluation-run').getAttribute('data-run-id'))!;await complete(request,id);
 await expect(page.getByTestId('evaluation-run')).toContainText('SMOKE / DONE');await expect(page.getByTestId('evaluation-run')).toContainText('Critical violations: 0');await page.getByText('Methodology / denominator 10',{exact:true}).first().click();await expect(page.getByTestId('evaluation-run')).toContainText('Passing scenarios / executed scenarios');await page.getByRole('button',{name:'agents.dinner / PASS',exact:true}).click();await expect(page.getByTestId('scenario-inspector')).toContainText('Expected:');await expect(page.getByTestId('scenario-inspector')).toContainText('Observed:');await page.reload();await expect(page.getByTestId('evaluation-run')).toHaveAttribute('data-run-id',id);
});

test("FULL displays 104 real results and fixture disclosure",async({page,request})=>{
 const id=await start(request,'FULL');await complete(request,id);await page.goto(`/evals?run=${id}`);await expect(page.getByTestId('evaluation-run')).toContainText('Scenarios 104 / 104');await expect(page.locator('.eval-scenario')).toHaveCount(104);await expect(page.locator('.eval-disclosure')).toContainText('NOT PRODUCTION RELIABILITY');await expect(page.locator('.eval-disclosure')).toContainText('REAL LLM JUDGE NOT CONFIGURED');
});

test("candidate regression exposes expected and observed failure evidence",async({page,request})=>{
 const id=await start(request,'SMOKE','CAUTIOUS_THRESHOLD');await complete(request,id);await page.goto(`/evals?run=${id}`);await expect(page.getByTestId('evaluation-run')).toContainText('Regression gates / FAIL');await page.getByRole('button',{name:'proactive.pending / FAIL',exact:true}).click();await expect(page.getByTestId('scenario-inspector')).toContainText('PENDING_APPROVAL');await expect(page.getByTestId('scenario-inspector')).toContainText('Observed: null');
});

test("duplicate clicks send one request and late acknowledgment cannot restore old selection",async({page,request})=>{
 const prior=await start(request);await complete(request,prior);await page.goto('/evals');await expect(page.getByRole('button',{name:'Run Evaluation',exact:true})).toBeEnabled();const held=await hold(page,'/api/v1/evaluation/runs');let posts=0;page.on('request',r=>{if(r.method()==='POST'&&r.url().endsWith('/api/v1/evaluation/runs'))++posts;});
 try{await page.evaluate(()=>{const button=[...document.querySelectorAll<HTMLButtonElement>('button')].find(b=>b.textContent==='Run Evaluation');button?.click();button?.click();});await held.started;expect(posts).toBe(1);await page.getByLabel('Recorded evaluation').selectOption(prior);held.release();await expect(page.getByTestId('evaluation-run')).toHaveAttribute('data-run-id',prior);await expect.poll(async()=>{const rows=await(await request.get('/api/v1/evaluation/runs')).json();return rows.some((r:{status:string})=>r.status==='RUNNING');},{timeout:90000}).toBe(false);}finally{held.release();}
});

test("late run read cannot overwrite a newer selection",async({page,request})=>{
 const a=await start(request);await complete(request,a);const b=await start(request);await complete(request,b);await page.goto('/evals');await expect(page.getByLabel('Recorded evaluation')).toBeVisible();const held=await hold(page,`/api/v1/evaluation/runs/${a}`);
 try{await page.getByLabel('Recorded evaluation').selectOption(a);await held.started;await page.getByLabel('Recorded evaluation').selectOption(b);await expect(page.getByTestId('evaluation-run')).toHaveAttribute('data-run-id',b);held.release();await expect(page.getByTestId('evaluation-run')).toHaveAttribute('data-run-id',b);}finally{held.release();}
});

test("shadow and canary comparisons preserve stable assignments",async({page,request})=>{
 for(const mode of ['SHADOW','CANARY']){
  const create=await request.post('/api/v1/experiments',{data:{idempotency_key:crypto.randomUUID(),name:`Browser ${mode}`,mode,suite:'SMOKE',candidate_percentage:20}});expect(create.status()).toBe(201);const definition=await create.json();expect((await request.post(`/api/v1/experiments/${definition.id}/run`,{data:{idempotency_key:'browser'}})).status()).toBe(202);
  await expect.poll(async()=>{const r=await request.get(`/api/v1/experiments/${definition.id}`);return(await r.json()).results[0].status;},{timeout:90000}).toBe('DONE');const before=await(await request.get(`/api/v1/experiments/${definition.id}`)).json();await page.goto('/evals');const card=page.locator(`.eval-experiment[data-experiment-id="${definition.id}"]`);await expect(card).toContainText(`${mode} SIMULATION`);await card.getByText('Stable variant assignments',{exact:true}).click();await expect(card).toContainText('bucket');await expect(card).toContainText('INSUFFICIENT SAMPLE SIZE');await page.reload();const after=await(await request.get(`/api/v1/experiments/${definition.id}`)).json();expect(after.assignments).toEqual(before.assignments);expect(after.results[0].comparison.authoritative_user_state_modified).toBe(false);
 }
});

test("critical fault remains visible through an operator-only Python hook",async({page})=>{
 const code="from app.evaluation.runner import EvaluationRunner; from app.evaluation.contracts import RunInput; from uuid import uuid4; r=EvaluationRunner(); id,_=r.claim(RunInput(idempotency_key=str(uuid4()))); r.execute(id,fault=lambda s,o: dict(o,retrieved=True) if s.scenario_id=='memory.deleted' else o); print(id)";
 const id=execFileSync('docker',['compose','exec','-T','backend','python','-c',code],{cwd:'..',encoding:'utf8',timeout:60000}).trim().split('\n').at(-1)!;
 await page.goto(`/evals?run=${id}`);await expect(page.getByTestId('evaluation-run')).toContainText('Critical violations: 1');await expect(page.getByTestId('evaluation-run')).toContainText('critical_violations: FAIL');await page.getByRole('button',{name:'memory.deleted / FAIL',exact:true}).click();await expect(page.getByTestId('scenario-inspector')).toContainText('CRITICAL');
});

test("Evaluation Lab fits a 390px viewport",async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/evals');await expect(page.getByRole('heading',{name:'Evaluation Lab.',exact:true})).toBeVisible();await expect(page.getByLabel('Evaluation suite')).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:'test-results/phase7-evaluation-390px.png'});
});

test("visual candidate preflight holds the mutation guard before its POST",async({page,request})=>{
 const created=await request.post('/api/v1/tasks',{data:{title:'Phase 7 preflight guard',origin_device_id:'00000000-0000-4000-8000-000000000010'}});const task=await created.json();
 expect((await request.post(`/api/v1/tasks/${task.id}/handoff`,{data:{source_device_id:'00000000-0000-4000-8000-000000000010',target_device_id:'00000000-0000-4000-8000-000000000020',idempotency_key:'wearable'}})).status()).toBe(200);
 const media=await(await request.post(`/api/v1/tasks/${task.id}/media/fixture`,{data:{idempotency_key:'frame'}})).json();const perception=await(await request.post(`/api/v1/tasks/${task.id}/perception`,{data:{media_id:media.id,idempotency_key:'perception'}})).json();const cup=perception.observations.find((o:{label:string})=>o.label==='coffee_cup_present');
 expect((await request.post('/api/v1/memory/candidates/visual',{data:{task_id:task.id,observation_id:cup.id,idempotency_key:crypto.randomUUID()}})).status()).toBe(201);
 await page.goto(`/memory?task=${task.id}`);await expect(page.getByRole('button',{name:'Create visual candidate',exact:true})).toBeEnabled();const held=await hold(page,`/api/v1/tasks/${task.id}/perception`);let reads=0;page.on('request',r=>{if(r.method()==='GET'&&r.url().endsWith(`/tasks/${task.id}/perception`))++reads;});
 try{await page.evaluate(()=>{const b=[...document.querySelectorAll<HTMLButtonElement>('button')].find(b=>b.textContent==='Create visual candidate');b?.click();b?.click();});await held.started;expect(reads).toBe(1);await expect(page.getByRole('button',{name:'Create visual candidate',exact:true})).toBeDisabled();await expect(page.getByRole('button',{name:'Remember preference',exact:true})).toBeDisabled();for(const button of await page.getByRole('button',{name:'Edit & confirm',exact:true}).all())await expect(button).toBeDisabled();held.release();await expect(page.getByRole('button',{name:'Create visual candidate',exact:true})).toBeEnabled();}finally{held.release();}
});
