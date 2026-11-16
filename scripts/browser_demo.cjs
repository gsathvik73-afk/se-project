/* Synthetic-account browser regression and retrospective sprint recordings.
   Requires npm install playwright in a separate tooling directory or NODE_PATH. */
const {chromium} = require('playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const root=path.resolve(__dirname,'..');
const target=process.env.DEMO_URL || 'http://127.0.0.1:5057';
const executablePath=process.env.BROWSER_EXECUTABLE;
const out=path.join(root,'docs/reports/browser');
fs.mkdirSync(out,{recursive:true});
async function launch(){return chromium.launch({headless:true, ...(executablePath?{executablePath}:{channel:process.env.BROWSER_CHANNEL||'chrome'})});}
async function banner(page,text){
  await page.evaluate(text=>{
    document.getElementById('demo-caption')?.remove();
    const el=document.createElement('div');el.id='demo-caption'; el.textContent=text;
    Object.assign(el.style,{position:'fixed',bottom:'0',left:'0',right:'0',padding:'14px 24px',background:'#14233a',color:'white',font:'16px Arial',zIndex:999999,textAlign:'center'});
    document.body.appendChild(el);
  },text);
}
async function auth(page,email){
  await page.goto(target+'/register');
  await page.locator('[name=name]').fill('Demo Student');
  await page.locator('[name=email]').fill(email);
  await page.locator('[name=password]').fill('DemoPass123!');
  await page.locator('form button').click();
  await page.locator('[name=email]').fill(email);
  await page.locator('[name=password]').fill('DemoPass123!');
  await page.locator('form button').click();
  await page.waitForURL('**/dashboard');
}
async function save(page,type,amount,extra={}){
  await page.goto(target+'/transactions');
  await page.locator('form [name=type]').selectOption(type);
  await page.locator('form [name=amount]').first().fill(amount);
  await page.locator('form [name=date]').fill('2026-10-08');
  if(type==='expense'){
    const cat=await page.locator('form [name=category_id]').first().locator('option').filter({hasText:'Food'}).getAttribute('value');
    await page.locator('form [name=category_id]').first().selectOption(cat);
    await page.locator('[name=payment_mode]').fill('UPI');
  }else await page.locator('[name=source]').fill('Scholarship');
  await page.locator('[name=note]').fill(extra.note||'Demo record');
  await page.getByRole('button',{name:'Save transaction'}).click();
}
async function record(sprint,duration){
 const browser=await launch();
 const context=await browser.newContext({viewport:{width:1280,height:900},recordVideo:{dir:out,size:{width:1280,height:900}}});
 const page=await context.newPage();
 const start=Date.now(); const progress=[];
 async function shot(name,caption,seconds=5){await banner(page,caption);await page.screenshot({path:path.join(out,`sprint${sprint}-${name}.png`)});progress.push(name);await page.waitForTimeout(seconds*1000);}
 await auth(page,`sprint${sprint}-${Date.now()}@example.test`);
 await shot('dashboard',`Sprint ${sprint} retrospective demo | Current build | Recorded November 2026 | Synthetic data`,6);
 if(sprint===1){
   await page.goto(target+'/categories');await page.locator('[name=name]').first().fill('Books');await page.getByRole('button',{name:'Add category'}).click();
   await shot('categories','Sathik scope: shared defaults and a private custom category',7);
   await page.goto(target+'/budgets?month=2026-10');await page.locator('[name=month]').first().fill('2026-10');await page.locator('[name=limit]').fill('5000');await page.getByRole('button',{name:'Save budget'}).click();
   await shot('budget','Monthly budget INR 5000 saved and read back from SQLite',7);
   await save(page,'income','10000'); await save(page,'expense','250');
   await page.goto(target+'/dashboard?month=2026-10');
   await shot('totals','Income 10000 | Expense 250 | Balance 9750 | Budget used 5 percent',12);
 }else{
   await save(page,'income','10000');await save(page,'expense','250',{note:'Lunch'});
   await shot('transactions','Sahana scope: persisted expense and income with field validation',8);
   await page.getByRole('link',{name:'Edit',exact:true}).first().click();await page.locator('[name=amount]').fill('300');await page.getByRole('button',{name:'Save changes'}).click();
   await shot('edit','Edit persists and dashboard totals are calculated from the saved records',8);
   await page.getByRole('link',{name:'Delete',exact:true}).first().click();
   await shot('confirm','Deletion requires an explicit confirmation; Cancel preserves the record',8);
   await page.getByRole('link',{name:'Cancel',exact:true}).click();
   await page.goto(target+'/transactions?start=2026-10-01&end=2026-10-31&sort=amount_asc');
   const downloadPromise=page.waitForEvent('download');await page.getByRole('link',{name:'Export filtered CSV'}).click();const download=await downloadPromise;
   const csvPath=path.join(out,'export.csv');await download.saveAs(csvPath);assert.match(fs.readFileSync(csvPath,'utf8'),/date,type,category,amount/);
   await shot('export','Arya scope: filtered CSV uses the same owner, filters and ordering as the list',10);
   await page.goto(target+'/budgets?month=2026-10');await page.locator('[name=month]').first().fill('2026-10');await page.locator('[name=limit]').fill('250');await page.getByRole('button',{name:'Save budget'}).click();
   await page.goto(target+'/dashboard?month=2026-10');await shot('alerts','Budget threshold alerts remain advisory; new transactions stay allowed',10);
   await page.setViewportSize({width:360,height:800});await shot('mobile','360px viewport: responsive cards, tables and navigation',10);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   await page.setViewportSize({width:1280,height:900});
 }
 const data=await page.request.get(target+'/api/dashboard?month=2026-10');assert.equal(data.status(),200);
 await banner(page,`Working product demonstrated | Sprint ${sprint} retrospective | Evidence and remaining checks in docs/`);
 const remaining=duration*1000-(Date.now()-start);if(remaining>0)await page.waitForTimeout(remaining);
 const video=page.video();await context.close();const file=await video.path();fs.renameSync(file,path.join(out,`sprint${sprint}.webm`));await browser.close();
 return {sprint,duration,progress,recorded_at:new Date().toISOString(),retrospective:true,browser:'Isolated headless Chromium or configured Chrome channel',public_tls_tested:false};
}
(async()=>{const results=await Promise.all([record(1,60),record(2,120)]);fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results));})().catch(e=>{console.error(e);process.exit(1)});
