#!/usr/bin/env python3
"""TC-PORT-01: fresh stable browser + desktop/360px, full synthetic UI flows.

Selenium Manager downloads the stable channel into an isolated cache. No normal
browser profile, real account or personal SQLite database is accessed.
"""
import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from smartexpense import create_app
from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--browser',choices=['chrome','edge','firefox'],required=True);args=parser.parse_args()
    name=args.browser
    out=ROOT/'docs/reports/browser-acceptance'/name;out.mkdir(parents=True,exist_ok=True)
    checks=[];errors=[];versions=[]
    with tempfile.TemporaryDirectory(prefix='smartexpense-browser-') as folder:
        app=create_app({'SECRET_KEY':os.urandom(32).hex(),'SQLALCHEMY_DATABASE_URI':'sqlite:///'+folder+'/test.db'})
        with app.app_context():
            result=app.test_cli_runner().invoke(args=['init-db']);assert result.exit_code==0,result.output
        server=make_server('127.0.0.1',0,app,threaded=True);thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            for width in [1280,360]:
                downloads=Path(folder)/f'downloads-{width}';downloads.mkdir()
                if name=='firefox':
                    options=webdriver.FirefoxOptions();options.add_argument('-headless')
                    options.set_preference('browser.download.folderList',2);options.set_preference('browser.download.dir',str(downloads))
                    options.set_preference('browser.helperApps.neverAsk.saveToDisk','text/csv,application/csv,application/octet-stream')
                    options.set_preference('pdfjs.disabled',True)
                    factory=webdriver.Firefox
                else:
                    options=webdriver.ChromeOptions() if name=='chrome' else webdriver.EdgeOptions()
                    options.add_argument('--headless=new');options.add_argument('--no-sandbox');options.add_argument('--disable-dev-shm-usage')
                    options.add_experimental_option('prefs',{'download.default_directory':str(downloads),'download.prompt_for_download':False})
                    factory=webdriver.Chrome if name=='chrome' else webdriver.Edge
                options.browser_version='stable'
                driver=factory(options=options);wait=WebDriverWait(driver,25)
                versions.append({'width':width,'capabilities':{k:driver.capabilities.get(k) for k in ['browserName','browserVersion','platformName']}})
                try:
                    driver.set_window_size(width,900)
                    if name in ('chrome','edge'):
                        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':width,'height':900,'deviceScaleFactor':1,'mobile':width==360})
                    else:
                        for _ in range(2):
                            delta=driver.execute_script('return window.outerWidth-window.innerWidth')
                            driver.set_window_size(width+delta,1000)
                    actual=driver.execute_script('return window.innerWidth')
                    assert actual==width,f'Viewport requested {width}; actual {actual}'
                    def field(selector,value):
                        element=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,selector)))
                        element.clear();element.send_keys(value);return element
                    def button(text):
                        wait.until(EC.element_to_be_clickable((By.XPATH,f'//button[normalize-space()="{text}"]'))).click()
                    def visit(path):
                        driver.get(base+path);wait.until(EC.presence_of_element_located((By.TAG_NAME,'main')))
                    def record(label):
                        overflow=driver.execute_script('return document.documentElement.scrollWidth>window.innerWidth')
                        assert not overflow,f'{label}: document overflow at {width}px'
                        driver.save_screenshot(str(out/f'{width}-{len(checks):02}-{label}.png'))
                        checks.append({'viewport_width':width,'case':label,'result':'PASS','actual_inner_width':driver.execute_script('return window.innerWidth')})
                    email=f'{name}-{width}@example.test'
                    visit('/register');field('[name=name]','Browser Tester');field('[name=email]',email);field('[name=password]','SyntheticPass123!');record('registration-layout');button('Create account')
                    wait.until(EC.url_contains('/login'));field('[name=email]',email);field('[name=password]','SyntheticPass123!');record('login-layout');button('Log in');wait.until(EC.url_contains('/dashboard'));record('login-dashboard')
                    visit('/categories');field('form [name=name]','Books');button('Add category');wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'[aria-label="Rename Books"]')))
                    field('[aria-label="Rename Books"]','Study');button('Rename');wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'[aria-label="Rename Study"]')));record('category-create-rename')
                    def save(kind,amount,source='',note=''):
                        visit('/transactions');Select(driver.find_element(By.CSS_SELECTOR,'form [name=type]')).select_by_value(kind)
                        field('form [name=amount]',amount)
                        driver.execute_script("arguments[0].value='2026-10-08';arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",driver.find_element(By.CSS_SELECTOR,'form [name=date]'))
                        if kind=='expense':Select(driver.find_element(By.CSS_SELECTOR,'form [name=category_id]')).select_by_visible_text('Food');field('[name=payment_mode]','UPI')
                        else:field('[name=source]',source)
                        field('[name=note]',note);button('Save transaction');wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'tbody tr')))
                    save('income','10000','Scholarship');save('expense','250',note='Lunch, "meal"');record('income-expense-create')
                    def set_budget(limit):
                        visit('/budgets?month=2026-10')
                        driver.execute_script("arguments[0].value='2026-10';",driver.find_element(By.CSS_SELECTOR,'[name=month]'))
                        field('[name=limit]',limit);button('Save budget');wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'tbody tr')))
                    set_budget('500');record('budget-save');visit('/dashboard?month=2026-10')
                    body=driver.find_element(By.TAG_NAME,'body').text
                    for value in ['10000.00','250.00','9750.00','50.00']:assert value in body,(value,body)
                    assert driver.execute_script('return [...document.querySelectorAll("canvas")].length')==2
                    record('dashboard-correct-totals-charts')
                    visit('/transactions');driver.find_elements(By.LINK_TEXT,'Edit')[0].click();field('[name=amount]','300');field('[name=note]','=1+1');button('Save changes');wait.until(EC.url_contains('/transactions'));assert '300.00' in driver.find_element(By.CSS_SELECTOR,'tbody').text;record('edit-persists')
                    driver.find_elements(By.LINK_TEXT,'Delete')[0].click();record('delete-confirmation');driver.find_element(By.LINK_TEXT,'Cancel').click();assert len(driver.find_elements(By.CSS_SELECTOR,'tbody tr'))==2;record('delete-cancel-preserves')
                    visit('/transactions?start=2026-10-01&end=2026-10-31&min_amount=250&max_amount=300&sort=amount_asc');assert len(driver.find_elements(By.CSS_SELECTOR,'tbody tr'))==1;record('filters-and-sort')
                    driver.find_element(By.LINK_TEXT,'Export filtered CSV').click()
                    def completed_csv(_):
                        files=list(downloads.glob('*.csv'));return files[0] if files and not list(downloads.glob('*.part')) and not list(downloads.glob('*.crdownload')) else False
                    csvpath=wait.until(completed_csv)
                    with csvpath.open(newline='') as f:rows=list(csv.reader(f))
                    assert len(rows)==2 and rows[1][3]=='300.00' and rows[1][-1]=="'=1+1",rows
                    record('csv-download-filter-and-formula-safety')
                    visit('/transactions');driver.find_elements(By.LINK_TEXT,'Delete')[0].click();button('Confirm delete');wait.until(EC.url_contains('/transactions'));assert len(driver.find_elements(By.CSS_SELECTOR,'tbody tr'))==1;record('delete-confirm-removes')
                    visit('/dashboard?month=2026-10');assert '0.00' in driver.find_element(By.TAG_NAME,'body').text;record('dashboard-after-delete')
                    button('Log out');wait.until(EC.url_contains('/login'));visit('/dashboard');wait.until(EC.url_contains('/login'));record('logout-protects-dashboard')
                except Exception as exc:
                    driver.save_screenshot(str(out/f'{width}-FAIL.png'));errors.append({'viewport_width':width,'error':str(exc)});raise
                finally:driver.quit()
        finally:
            server.shutdown();thread.join(timeout=5)
            report={'requirement':'SEB-NF-005','test_case':'TC-PORT-01','browser':name,'requested_release':'stable','checked_at':datetime.now(timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'versions':versions,'checks':checks,'errors':errors,'status':'PASS' if not errors and len(checks)==30 else 'FAIL'}
            (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    assert report['status']=='PASS',report

if __name__=='__main__':main()
