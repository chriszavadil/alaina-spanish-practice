"""Dedicated scenarios: all examples, grading, persistence, migration and phone layouts."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import json,threading,functools,argparse
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'history-scenario-results';OUT.mkdir(exist_ok=True)
D=json.loads((ROOT/'history-src/data.json').read_text(encoding='utf-8'));BY={c['id']:c for c in D['cards']}
STORE='alaina-history-studio-v1';SPAN='alaina-spanish-practice-v1'
p=argparse.ArgumentParser();p.add_argument('--url');p.add_argument('--engine',default='both');p.add_argument('--chromium-path');args=p.parse_args()
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();URL=args.url or f'http://127.0.0.1:{server.server_port}/history/'
def tap(p,s):p.locator(s).tap()
def db(p):return p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
def question(p):
 q=db(p)['session'];c=BY[q['ids'][q['index']]];return q,c,c['scenarios'][q['questions'][q['index']]['scenarioIndex']]
def nextq(p):expect(p.locator('#quiz-action')).to_be_enabled();tap(p,'#quiz-action')
def start(p,length='all'):
 tap(p,'[data-action=scenario-setup]');expect(p.locator('[data-mode=scenario]')).to_have_attribute('aria-pressed','true')
 tap(p,f'[data-length="{length}"]');tap(p,'#begin-round')
def right(p,action='check'):
 q,c,item=question(p);tap(p,f'[data-choice="{c["id"]}"]');tap(p,f'[data-action={action}]')
 expect(p.locator('[data-result=correct]')).to_be_visible();expect(p.locator('#feedback .answer-term')).to_have_text(c['term'])
 expect(p.locator('#feedback .scenario-explanation p')).to_have_text(item['why'])
def entry_points(p):
 expect(p.locator('[data-action=scenario-setup]')).to_be_visible();p.wait_for_timeout(250);p.screenshot(path=str(OUT/'scenario-home.png'),full_page=True)
 tap(p,'[data-action=scenario-setup]');assert p.locator('[data-mode]').count()==5
 expect(p.locator('[data-mode=scenario]')).to_have_attribute('aria-pressed','true');p.wait_for_timeout(250);p.screenshot(path=str(OUT/'scenario-modes.png'),full_page=True)
 tap(p,'header [data-action=library]');assert p.locator('.scenario-examples').count()==15
 p.locator('#search').fill('feudalism');expect(p.locator('.word-entry')).to_have_count(1)
 tap(p,'.scenario-examples summary');expect(p.locator('.scenario-example')).to_have_count(2)
 for line in p.locator('.scenario-example strong').all_inner_texts():assert line=='Matching term: Feudalism'
 p.wait_for_timeout(250);p.screenshot(path=str(OUT/'scenario-library.png'),full_page=True)
def all_examples(p):
 start(p);seen={};first_order=[]
 for roundno in range(2):
  for i in range(15):
   q,c,item=question(p);expect(p.locator('.prompt')).to_have_text(item['text'])
   assert p.locator('#feedback .scenario-explanation').count()==0
   opts=p.locator('[data-choice]').evaluate_all('(xs)=>xs.map(x=>x.dataset.choice)');assert len(set(opts))==4 and c['id'] in opts
   idx=q['questions'][i]['scenarioIndex'];seen.setdefault(c['id'],[]).append(idx)
   if roundno==0:first_order.append(c['id'])
   right(p,'show' if i%2 else 'check')
   if i==0 and roundno==0:
    p.wait_for_timeout(250);p.screenshot(path=str(OUT/'scenario-correct.png'),full_page=True)
   nextq(p)
  expect(p.locator('.score')).to_have_text('15 / 15');expect(p.locator('.breakdown')).to_contain_text('0 incorrect')
  if roundno==0:tap(p,'[data-action=again-round]');assert db(p)['session']['ids']!=first_order
 assert len(seen)==15 and all(set(v)=={0,1} for v in seen.values())
 prog=db(p)['progress'];assert prog['rounds']==2 and prog['perfect']==2
 assert all(v['meaning']==2 and v['spelling']==0 and v['correct']==2 for v in prog['items'].values())
 tap(p,'header [data-action=home]');tap(p,'[data-action=badges]');expect(p.locator('.badge.earned',has_text='Meaning detective')).to_be_visible()
def wrong_skips_and_retry(p):
 start(p,'5');tap(p,'[data-action=check]');expect(p.locator('#answer-error')).to_contain_text('Choose')
 assert not db(p)['progress']['items'];tap(p,'[data-action=show]');expect(p.locator('[data-result=shown]')).to_be_visible();nextq(p)
 q,c,item=question(p);wrong=next(x for x in q['questions'][q['index']]['options'] if x!=c['id']);tap(p,f'[data-choice="{wrong}"]');tap(p,'[data-action=show]')
 expect(p.locator('[data-result=incorrect]')).to_be_visible();expect(p.locator('#feedback .scenario-explanation p')).to_have_text(item['why']);nextq(p)
 for i in range(3):
  q,c,item=question(p);tap(p,f'[data-choice="{c["id"]}"]');p.evaluate('window.__oldCheck=document.querySelector("#quiz-action")');tap(p,'[data-action=check]')
  before=db(p)['progress'];p.evaluate("__oldCheck.click();document.querySelector('#quiz-form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));")
  assert db(p)['progress']==before;nextq(p)
 expect(p.locator('.score')).to_have_text('3 / 4');expect(p.locator('.breakdown')).to_contain_text('1 shown');assert p.locator('.review-item .scenario-explanation').count()==2
 tap(p,'[data-action=retry]');assert db(p)['session']['mode']=='scenario';assert len(db(p)['session']['ids'])==2
 for i in range(2):right(p);nextq(p)
 assert all(not x['review'] for x in db(p)['progress']['items'].values())
def resume_and_backup(p):
 start(p,'5');q,c,item=question(p);tap(p,f'[data-choice="{c["id"]}"]');snapshot=db(p)['session'];tap(p,'header [data-action=home]');p.reload();tap(p,'[data-action=resume]')
 expect(p.locator('.prompt')).to_have_text(item['text']);expect(p.locator(f'[data-choice="{c["id"]}"]')).to_have_attribute('aria-pressed','true')
 assert db(p)['session']['questions']==snapshot['questions'];tap(p,'[data-action=show]');before=db(p)['progress'];p.reload();tap(p,'[data-action=resume]')
 expect(p.locator('[data-result=correct]')).to_be_visible();assert db(p)['progress']==before
 tap(p,'header [data-action=home]');tap(p,'#settings')
 with p.expect_download() as dl:tap(p,'[data-action=export]')
 raw=json.loads(Path(dl.value.path()).read_text());assert raw['data']['session']['mode']=='scenario'
 tap(p,'[data-action=reset]');tap(p,'[data-action=confirm]');assert db(p)['progress']['items']=={}
 tap(p,'#settings');p.locator('#import-file').set_input_files({'name':'scenarios.json','mimeType':'application/json','buffer':json.dumps(raw).encode()});tap(p,'[data-action=confirm]');tap(p,'[data-action=resume]')
 expect(p.locator('.prompt')).to_have_text(item['text']);assert db(p)['progress']==before;nextq(p);expect(p.locator('.progress-label')).to_contain_text('2 of 5')
def old_progress_and_filters(p):
 old={'schema':1,'settings':{'mode':'type','length':'5','topics':['exchange'],'rate':'0.75'},'progress':{'items':{'caravan':{'seen':4,'correct':2,'attempts':3,'meaning':2,'spelling':0,'review':True}},'rounds':8,'perfect':2,'earned':{'first':True,'round':True,'perfect':True}},'session':None,'lastOrder':['caravan']}
 p.evaluate('(x)=>localStorage.setItem("'+STORE+'",JSON.stringify(x))',old);p.reload();start(p)
 assert db(p)['progress']==old['progress'];q=db(p)['session'];assert len(q['ids'])==4 and all(BY[i]['category']=='exchange' for i in q['ids'])
 tap(p,'header [data-action=home]');tap(p,'[data-action=setup]');tap(p,'[data-action=all-topics]');tap(p,'[data-action=all-topics]')
 expect(p.locator('#begin-round')).to_be_disabled();assert db(p)['progress']==old['progress']
 old['session']={'id':'legacy','mode':'type','ids':['caravan'],'index':0,'responses':[],'checked':False,'revealed':False,'input':'Cara','selected':None,'plays':0,'finished':False,'questions':[{'scenario':False,'options':['caravan','dynasty','islam','jihad']}]}
 p.evaluate('(x)=>localStorage.setItem("'+STORE+'",JSON.stringify(x))',old);p.reload();tap(p,'[data-action=resume]');expect(p.locator('#answer')).to_have_value('Cara');expect(p.locator('.prompt')).to_have_text(BY['caravan']['definition'])
def phone_and_storage(p):
 start(p,'5')
 for w,h in [(393,852),(320,740),(852,393),(1200,850)]:
  p.set_viewport_size({'width':w,'height':h});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(w,h)
 p.set_viewport_size({'width':393,'height':852});p.wait_for_timeout(250);p.screenshot(path=str(OUT/'scenario-question-iphone15.png'),full_page=True)
 p.evaluate("() => { Storage.prototype.setItem=function(){throw Error('Blocked storage');}; }")
 right(p);expect(p.locator('#storage-warning')).to_be_visible();nextq(p);expect(p.locator('.progress-label')).to_contain_text('2 of 5')
 assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
suite=[entry_points,all_examples,wrong_skips_and_retry,resume_and_backup,old_progress_and_filters,phone_and_storage]
report={'url':URL,'version':'1.1.0','speech':'not used for scenario questions','checks':[]}
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium'] if args.engine=='both' else [args.engine]:
   opts={'executable_path':args.chromium_path} if engine=='chromium' and args.chromium_path else {}
   b=getattr(pw,engine).launch(**opts)
   for fn in suite:
    ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block',accept_downloads=True)
    ctx.add_init_script(f"if(!localStorage.getItem('{SPAN}'))localStorage.setItem('{SPAN}','SPANISH_UNCHANGED')")
    page=ctx.new_page();page.set_default_timeout(12000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
     page.goto(URL);expect(page.locator('meta[name=app-version]')).to_have_attribute('content','1.1.0');fn(page);assert not errors,errors
     assert page.evaluate(f'localStorage.getItem("{SPAN}")')=='SPANISH_UNCHANGED';report['checks'].append({'engine':engine,'test':fn.__name__,'passed':True});print(engine,fn.__name__,'PASS',flush=True)
    except Exception:
     page.screenshot(path=str(OUT/f'FAILED-{engine}-{fn.__name__}.png'),full_page=True);report['checks'].append({'engine':engine,'test':fn.__name__,'passed':False,'errors':errors});raise
    finally:ctx.close()
   b.close()
finally:server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2))
print('ALL_SCENARIO_GROUPS_PASS',len(report['checks']),flush=True)
