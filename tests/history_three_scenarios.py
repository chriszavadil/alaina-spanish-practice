"""Restore both old variants, then use new variant 3 and cycle back to variant 1."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import argparse,copy,functools,json,threading
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'history-scenario-results';OUT.mkdir(exist_ok=True)
D=json.loads((ROOT/'history-src/data.json').read_text(encoding='utf-8'));BY={c['id']:c for c in D['cards']};STORE='alaina-history-studio-v1';SPAN='alaina-spanish-practice-v1'
p=argparse.ArgumentParser();p.add_argument('--url');args=p.parse_args()
class H(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
URL=args.url or f'http://127.0.0.1:{server.server_port}/history/'
def tap(p,s):p.locator(s).tap()
def db(p):return p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
base={'schema':1,'settings':{'mode':'scenario','length':'5','topics':['exchange'],'rate':'0.75','voice':''},'progress':{'items':{'caravan':{'seen':4,'correct':2,'attempts':3,'meaning':2,'spelling':0,'review':True}},'rounds':8,'perfect':2,'earned':{'first':True,'round':True,'perfect':True}},'lastOrder':['caravan']}
checks=[]
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   b=getattr(pw,engine).launch()
   for variant in [0,1]:
    fixture=copy.deepcopy(base);fixture['scenarioLast']={'caravan':variant};fixture['session']={'id':'saved-old-scenario','mode':'scenario','ids':['caravan'],'index':0,'responses':[],'checked':False,'revealed':False,'input':'','selected':'caravan','plays':0,'finished':False,'questions':[{'scenario':False,'scenarioIndex':variant,'options':['caravan','dynasty','islam','jihad']}]}
    ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block')
    ctx.add_init_script(f"if(!localStorage.getItem('{STORE}'))localStorage.setItem('{STORE}',JSON.stringify({json.dumps(fixture)}));if(!localStorage.getItem('{SPAN}'))localStorage.setItem('{SPAN}','SPANISH_UNCHANGED')")
    page=ctx.new_page();page.set_default_timeout(12000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
     page.goto(URL);expect(page.locator('meta[name=app-version]')).to_have_attribute('content','1.1.1')
     tap(page,'[data-action=resume]');expect(page.locator('.prompt')).to_have_text(BY['caravan']['scenarios'][variant]['text']);expect(page.locator('[data-choice=caravan]')).to_have_attribute('aria-pressed','true')
     assert db(page)['progress']==base['progress'];assert db(page)['settings']==base['settings']
     tap(page,'[data-action=show]');expect(page.locator('[data-result=correct]')).to_be_visible();before=db(page)['progress']
     page.reload();tap(page,'[data-action=resume]');assert db(page)['progress']==before;expect(page.locator('#feedback .scenario-explanation p')).to_have_text(BY['caravan']['scenarios'][variant]['why'])
     expect(page.locator('#quiz-action')).to_be_enabled();tap(page,'#quiz-action');expect(page.locator('.results')).to_be_visible()
     observed=[]
     for step in range(1,4):
      tap(page,'[data-action=again-round]');expected=(variant+step)%3;observed.append(db(page)['session']['questions'][0]['scenarioIndex']);assert observed[-1]==expected
      expect(page.locator('.prompt')).to_have_text(BY['caravan']['scenarios'][expected]['text']);tap(page,'[data-choice=caravan]');tap(page,'[data-action=check]');expect(page.locator('[data-result=correct]')).to_be_visible()
      expect(page.locator('#feedback .scenario-explanation p')).to_have_text(BY['caravan']['scenarios'][expected]['why']);expect(page.locator('#quiz-action')).to_be_enabled();tap(page,'#quiz-action')
     assert set(observed)=={0,1,2};assert db(page)['progress']['items']['caravan']['correct']==6
     assert db(page)['progress']['earned']['perfect'] is True;assert page.evaluate(f'localStorage.getItem("{SPAN}")')=='SPANISH_UNCHANGED';assert not errors,errors
     checks.append({'engine':engine,'legacy_variant':variant,'passed':True});print(engine,'legacy scenario',variant,'preserved; new third example and wraparound PASS',flush=True)
    except Exception:
     page.screenshot(path=str(OUT/f'FAILED-{engine}-legacy-variant-{variant}.png'),full_page=True);raise
    finally:ctx.close()
   b.close()
finally:
 server.shutdown();(OUT/'three-scenarios-legacy.json').write_text(json.dumps(checks,indent=2))
