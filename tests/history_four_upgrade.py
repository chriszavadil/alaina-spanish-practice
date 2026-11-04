"""Installed three-example app -> four examples; preserve a selected third-example question."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
import subprocess,tempfile,threading,os,json
R=Path(__file__).resolve().parents[1];BASE='36dec311f5240cc8efbb95251064cdf49f793dcf';STORE='alaina-history-studio-v1';SPAN='alaina-spanish-practice-v1'
data=json.loads((R/'history-src/data.json').read_text());checks=[]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(active['root']),**kw)
 def log_message(self,*a):pass
with tempfile.TemporaryDirectory() as tmp:
 old=Path(tmp);(old/'history').mkdir()
 for name in ['index.html','sw.js','manifest.webmanifest','icon-192.png','icon-512.png']:
  p=old/'history'/name;p.write_bytes(subprocess.check_output(['git','show',BASE+':history/'+name],cwd=R));os.utime(p,(1577836800,1577836800))
 initial={'schema':1,'scenarioLast':{c['id']:1 for c in data['cards']},'settings':{'mode':'scenario','length':'5','topics':[c['id'] for c in data['categories']]},'progress':{'rounds':4,'perfect':1,'earned':{'first':True,'round':True},'items':{'dynasty':{'seen':3,'correct':2,'attempts':2,'meaning':2,'spelling':0,'review':False}}}}
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   active={'root':old};server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/history/'
   b=getattr(pw,engine).launch();ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True)
   ctx.add_init_script(f"if(!localStorage.getItem('{STORE}'))localStorage.setItem('{STORE}',JSON.stringify({json.dumps(initial)}));if(!localStorage.getItem('{SPAN}'))localStorage.setItem('{SPAN}','SPANISH_UNTOUCHED');")
   p=ctx.new_page();p.set_default_timeout(15000)
   try:
    p.goto(url);expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.1');p.evaluate('navigator.serviceWorker.ready');p.wait_for_function('!!navigator.serviceWorker.controller')
    p.locator('[data-action=scenario-setup]').tap();p.locator('#begin-round').tap()
    state=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))');s=state['session'];assert all(q['scenarioIndex']==2 for q in s['questions']);term=s['ids'][0]
    p.locator(f'[data-choice="{term}"]').tap();before=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))');prompt=p.locator('.prompt').inner_text()
    p.locator('header [data-action=home]').tap();active['root']=R;p.reload()
    expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.2')
    p.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update())');p.wait_for_function("caches.keys().then(ks=>ks.some(k=>k.endsWith('v1.1.2')))")
    p.locator('[data-action=resume]').tap();expect(p.locator('.prompt')).to_have_text(prompt)
    after=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))');assert after['progress']==before['progress'];assert after['session']['selected']==term and after['session']['questions']==before['session']['questions']
    p.locator('[data-action=check]').tap();expect(p.locator('[data-result=correct]')).to_be_visible();snapshot=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
    server.shutdown();server.server_close()
    for _ in range(2):
     p.reload();expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.2');p.locator('[data-action=resume]').tap();expect(p.locator('[data-result=correct]')).to_be_visible();assert p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')["progress"]==snapshot['progress']
    assert p.evaluate(f'localStorage.getItem("{SPAN}")')=='SPANISH_UNTOUCHED'
    checks.append({'engine':engine,'passed':True});print(engine,'installed 1.1.1 -> 1.1.2; third example unchanged; selection, progress, badges and offline reloads PASS',flush=True)
   finally:ctx.close();b.close();server.shutdown();server.server_close()
(R/'history-scenario-results/four-upgrade.json').write_text(json.dumps(checks,indent=2))
