import {test,expect} from '@playwright/test';
test('inference registry labels fixture and unavailable real model honestly',async({page,request})=>{
 const devices=await(await request.get('/api/v1/devices')).json();const desktop=devices.find((d:{type:string})=>d.type==='DESKTOP');
 await request.post('/api/v1/tasks',{data:{title:`Inference browser ${crypto.randomUUID()}`,origin_device_id:desktop.id}});
 await page.goto('/inference');await expect(page.getByRole('heading',{name:'Inference workspace'})).toBeVisible();
 await expect(page.getByText('NOT_INSTALLED',{exact:false})).toBeVisible();
 await page.getByLabel('Inference mode').selectOption('LOCAL_REAL');await page.getByRole('button',{name:'Run grounded inference',exact:true}).click();await expect(page.getByRole('status')).toContainText('MODEL_NOT_CONFIGURED');
 await page.getByLabel('Inference mode').selectOption('DISABLED');await page.getByRole('button',{name:'Run grounded inference',exact:true}).click();await expect(page.getByRole('status')).toContainText('INFERENCE_DISABLED');
 await page.getByLabel('Inference mode').selectOption('FIXTURE');await page.getByRole('button',{name:'Run grounded inference',exact:true}).click();await expect(page.getByRole('status')).toContainText('FIXTURE · DONE');
 await page.getByRole('button',{name:'Evaluate fixture retrieval',exact:true}).click();await expect(page.getByRole('table')).toContainText('LEXICAL');await expect(page.getByText('Real embeddings: NOT_EXECUTED')).toBeVisible();
});
test('inference workspace at 390px has no horizontal overflow',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/inference');await expect(page.getByRole('heading',{name:'Inference workspace'})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});
test('scripted fixture transport renders citation and abstention fields without model calls',async({page,request})=>{
 const devices=await(await request.get('/api/v1/devices')).json();
 const desktop=devices.find((d:{type:string})=>d.type==='DESKTOP');
 const task=await(await request.post('/api/v1/tasks',{data:{title:`Rendering fixture ${crypto.randomUUID()}`,origin_device_id:desktop.id}})).json();
 const evidenceId='96b55c85-0acf-4d1c-a3ed-4d3422138d79';
 let abstain=false;
 await page.route('**/api/v1/inference/generate',route=>route.fulfill({json:{id:crypto.randomUUID(),state:'DONE',mode:'FIXTURE',error:null,output:{abstain,claims:abstain?[]:[{evidence_id:evidenceId,quote:'Controlled rendering fixture.'}],response:abstain?null:'Controlled rendering fixture.'}}}));
 await page.goto('/inference');await page.getByLabel('Inference task').selectOption(task.id);
 await page.getByRole('button',{name:'Run grounded inference',exact:true}).click();
 await expect(page.getByRole('status')).toContainText('FIXTURE · DONE');
 const output=page.locator('section').filter({has:page.getByRole('heading',{name:'Owned task inference'})}).locator('pre');
 await expect(output).toContainText(evidenceId);await expect(output).toContainText('Controlled rendering fixture.');
 abstain=true;await page.getByRole('button',{name:'Run grounded inference',exact:true}).click();
 await expect(output).toContainText('"abstain": true');await expect(output).toContainText('"claims": []');
 await expect(output).toContainText('"response": null');await expect(output).not.toContainText(evidenceId);
});
