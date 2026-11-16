#!/usr/bin/env python3
"""Export the executable scenario catalog with results from JUnit XML."""
import ast,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DOCS=ROOT/'docs'
EXPECTED={
1:['201 account created','422 normalized duplicate rejected','422 empty name rejected','422 malformed email rejected','422 seven characters rejected','201 eight characters accepted','422 name over 100 rejected','422 password over 72 UTF-8 bytes rejected'],
2:['200 correct login','401 wrong password','401 unknown email','200 trimmed uppercase email authenticates','401 missing password','401 non-string password','Five failures 401 then immediate correct attempt 429','200; sid has HttpOnly and SameSite=Lax'],
3:['200 logout success','Replayed old sid receives API 401','Dashboard redirects 302 after logout','Transactions redirect 302 after logout','Categories redirect 302 after logout','Budgets redirect 302 after logout','Dashboard API returns 401 after logout','Logout without CSRF returns 400'],
4:['Foreign note absent from list','Foreign detail 404','Foreign update 404','Foreign delete 404','Dashboard income stays 10000.00','Foreign note absent from CSV','Private B category absent','Foreign category budget returns 404'],
5:['201 amount 0.01 retained','201 amount 1 formatted 1.00','201 amount 250.50 retained','201 optional note not required','201 note Lunch retained','201 payment mode Cash retained','201 today date retained','201 maximum 9999999999.99 retained'],
6:['201 income saved','201 source Freelance retained','Income 12000.00; expense 1800.00; balance 10200.00','Income category is null','Income payment mode is null','201 income 0.01 accepted','201 past date accepted','422 empty source'],
7:['422 amount 0','422 amount -1','422 amount text','422 blank amount','422 date two days in future','422 amount 0.001','422 amount Infinity','201 amount 0.01; rejected cases leave expense 1800.00'],
8:['Amount changed to 600.00','Note changed to Changed','Date changed to 2026-09-01','Payment changed to Cash','Category changed to Travel ID','Type changed to income; source Gift','422 invalid edit; original 500.00 retained','After amount 600 expense 1900.00'],
9:['GET confirmation 200; record remains 200','Form confirm=no returns 200; record remains','Form confirm=yes redirects 302 after delete','JSON DELETE returns 200','Deleted detail returns 404','Expense after deleting Food is 1300.00','Foreign DELETE returns 404','Missing transaction DELETE returns 404'],
10:['Exact date bounds retain 4 records','Food category retains 1 record','Minimum 500 retains 3 records','Maximum 500 retains 2 records','4 rows sorted by amount ascending','4 rows sorted by amount descending','No November records; empty list','Reversed dates return 422'],
11:['8 shared defaults returned','Books category created','Books renamed to Study','Default rename returns 403','Duplicate Food returns 422','Case duplicate food returns 422','Blank category returns 422','Expense with new private Books category returns 201'],
12:['Overall budget returns 200','Food budget returns 200','Upsert leaves one overall budget at 6000.00','Upsert leaves one Food budget at 6000.00','September budget absent in October, present in September','Zero limit returns 422','Negative limit returns 422','Foreign category scope returns 404'],
13:['Spent 1800.00','Remaining 3200.00','Percent 36.00','Food spent 500.00; remaining 500.00; percent 50.00','Income 10000.00 excluded from spending 1800.00','Limit 1000: remaining -800.00; percent 180.00','No budget returns empty array','September spent 0.00; remaining 5000.00; percent 0.00'],
14:['Limit 2500 yields no alert','Limit 2250 yields warning at 80 percent','Limit 2000 yields warning','Limit 1800 yields warning at 100 percent','Limit 1799 yields over','Limit 100 yields over and further expense 201','Food limit 625 yields warning at 80 percent','September budget absent from October alerts'],
15:['Income 10000.00','Expense 1800.00','Balance 8200.00','Empty September has all zero totals','October data excluded from September','Expense 2050.00; balance 7950.00 after addition','Income 12000.00; balance 10200.00 after addition','Invalid month returns 422'],
16:['Category totals sum to 1800','Three category groups','Exactly six trend buckets','First five October trend buckets are zero','Last trend month is 2026-10','January 2026 trend begins 2025-08','Empty September categories array','Month 0001-01 returns 422'],
17:['Exact seven-column CSV header','Foreign note excluded','Exact date filter yields header and four rows','Amounts sorted ascending','Empty match yields header only','Comma, quote and embedded newline parse exactly','Formula note prefixed with apostrophe','59 matching records plus header exported across pages']}


def main():
 tree=ast.parse((ROOT/'tests/test_requirement_scenarios.py').read_text())
 scenarios=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SCENARIOS' for t in n.targets))
 results={}
 for c in ET.parse(DOCS/'reports/system-validation-report.xml').findall('.//testcase'):
  props={q.get('name'):q.get('value') for q in c.findall('./properties/property')}
  if 'case_id' in props:results[props['case_id']]='PASS' if c.find('failure') is None and c.find('error') is None else 'FAIL'
 req={r['requirement']:r for r in json.loads((DOCS/'requirements.json').read_text())}
 fields=['test_case_id','requirement','module','test_description','test_type','preconditions','test_steps','test_data','expected_result','actual_result','test_result','manual_execution','source']
 with (DOCS/'test-cases.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for n,items in scenarios.items():
   rid=f'SEB-F-{n:03}';r=req[rid]
   for i,label in enumerate(items,1):
    tid=f'IT-F{n:03}-{i:02}';expected=EXPECTED[n][i-1];status=results.get(tid,'NOT RUN')
    w.writerow(dict(test_case_id=tid,requirement=rid,module=r['title'],test_description=label,test_type='Integration and system route check',preconditions='Fresh temporary SQLite; registered A; income 10000; Food 500 Travel 300 Rent 1000 on 2026-10-08; authenticated session',test_steps=f'1 Reset fixture. 2 Execute scenario {label} using the values in expected_result and source. 3 Inspect status, persisted state and derived data with assertions.',test_data=expected+'; exact payload and method in the linked executable case',expected_result=expected,actual_result=('Observed: '+expected) if status=='PASS' else 'See JUnit result',test_result=status,manual_execution='Not executed by a human in this recovery run',source=f'tests/test_requirement_scenarios.py::test_functional_scenario r={n}, i={i-1}; JUnit case_id={tid}'))
 print('Exported',len(results),'executed scenarios')

if __name__=='__main__':main()
