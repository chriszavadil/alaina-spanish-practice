"""Real service-worker upgrade from History 1.0.0 to scenarios 1.1.0."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
import subprocess,threading,tempfile,os,json
ROOT=Path(__file__).resolve().parents[1];BASE='2f5a9fac5b193ff4821bcad748b7a6c08fa58ed4';STORE='alaina-history-studio-v1'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(active['root']),**kwargs)
 def log_message(self,*args):pass
checks=[]
with tempfile.TemporaryDirectory() as tmp:
 old=Path(tmp);(old/'history').mkdir()
 for name in ['index.html','sw.js','manifest.webmanifest','icon-192.png','icon-512.png']:
  p=old/'history'/name;p.write_bytes(subprocess.check_output(['git','show',BASE+':history/'+name],cwd=ROOT));os.utime(p,(1577836800,1577836800))
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   active={'root':old};server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/history/'
   b=getattr(pw,engine).launch();ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True);p=ctx.new_page();p.set_default_timeout(15000)
   try:
    p.goto(url);expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.0.0');p.evaluate('navigator.serviceWorker.ready');p.wait_for_function('!!navigator.serviceWorker.controller')
    p.evaluate("localStorage.setItem('alaina-spanish-practice-v1','UNCHANGED_SPANISH')")
    p.locator('[data-action=setup]').tap();p.locator('[data-mode=type]').tap();p.locator('#begin-round').tap()
    prompt=p.locator('.prompt').inner_text();p.locator('#answer').fill('unfinished answer');p.locator('header [data-action=home]').tap()
    before=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
    active['root']=ROOT;p.reload();expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.0');p.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update())')
    p.wait_for_function("caches.keys().then(xs=>xs.some(x=>x.startsWith('alaina-history-')&&x.endsWith('v1.1.0')))")
    p.locator('[data-action=resume]').tap();expect(p.locator('#answer')).to_have_value('unfinished answer');expect(p.locator('.prompt')).to_have_text(prompt)
    assert p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}")).progress')==before['progress']
    p.locator('header [data-action=home]').tap();p.locator('[data-action=scenario-setup]').tap();p.locator('#begin-round').tap();p.locator('[data-action=confirm]').tap()
    q=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}")).session');assert q['mode']=='scenario';text=p.locator('.prompt').inner_text()
    p.locator('header [data-action=home]').tap();server.shutdown();server.server_close();p.reload()
    expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.0');p.locator('[data-action=resume]').tap();expect(p.locator('.prompt')).to_have_text(text)
    assert p.evaluate("localStorage.getItem('alaina-spanish-practice-v1')")=='UNCHANGED_SPANISH'
    checks.append({'engine':engine,'passed':True});print(engine,'installed History 1.0 -> 1.1, old round preserved, new scenarios work offline PASS',flush=True)
   finally:ctx.close();b.close();server.shutdown();server.server_close()
(ROOT/'history-scenario-results/upgrade.json').write_text(json.dumps(checks,indent=2))
