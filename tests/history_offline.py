"""Test first history visit from an installed Spanish app, then both offline."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
import subprocess,threading,tempfile,shutil,os,json
ROOT=Path(__file__).resolve().parents[1];BASE='0c9000dff065170c2489b396789b3a9625614cb3'
OUT=ROOT/'history-test-results';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(active['root']),**kw)
 def log_message(self,*a):pass
checks=[]
with tempfile.TemporaryDirectory() as tmp:
 old=Path(tmp)
 for f in ['index.html','sw.js','manifest.webmanifest','icon-192.png','icon-512.png']:
  (old/f).write_bytes(subprocess.check_output(['git','show',BASE+':'+f],cwd=ROOT));os.utime(old/f,(1577836800,1577836800))
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   active={'root':old};server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
   b=getattr(pw,engine).launch();ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True);p=ctx.new_page();p.set_default_timeout(15000)
   try:
    p.goto(base);p.evaluate('navigator.serviceWorker.ready');p.wait_for_function('!!navigator.serviceWorker.controller')
    p.evaluate("localStorage.setItem('alaina-spanish-practice-v1',JSON.stringify({settings:{unit:'unit2',categories:['u2-days']},progress:{items:{'u2-day-tuesday':{seen:3,quizCorrect:2,needsReview:false}},rounds:4}}))")
    saved=p.evaluate("localStorage.getItem('alaina-spanish-practice-v1')")
    active['root']=ROOT;p.goto(base+'history/');expect(p).to_have_title('Alaina’s History Studio')
    p.wait_for_function("navigator.serviceWorker.controller?.scriptURL.includes('/history/sw.js')")
    p.evaluate("navigator.serviceWorker.getRegistration('../').then(r=>r.update())")
    p.wait_for_function("caches.keys().then(keys=>keys.some(k=>k.includes('route-isolation')))")
    assert p.evaluate("localStorage.getItem('alaina-spanish-practice-v1')")==saved
    p.locator('[data-action=setup]').tap();p.locator('[data-mode=type]').tap();p.locator('#begin-round').tap()
    prompt=p.locator('.prompt').inner_text();term=p.evaluate("text=>JSON.parse(document.querySelector('#history-data').textContent).cards.find(c=>c.definition===text).term",prompt)
    p.locator('#answer').fill(term);p.locator('[data-action=check]').tap();expect(p.locator('[data-result=correct]')).to_be_visible()
    hist=p.evaluate("localStorage.getItem('alaina-history-studio-v1')")
    spanish_cached=p.evaluate("async url=>{const keys=await caches.keys();const k=keys.find(k=>k.includes('route-isolation'));return (await (await caches.open(k)).match(url)).text()}",base+'index.html')
    assert 'id="vocabulary-data"' in spanish_cached and 'id="history-data"' not in spanish_cached
    server.shutdown();server.server_close();p.reload();expect(p).to_have_title('Alaina’s History Studio')
    assert p.evaluate("localStorage.getItem('alaina-history-studio-v1')")==hist
    other=ctx.new_page();other.goto(base);expect(other).to_have_title("Alaina's Spanish Quiz Practice")
    assert other.locator('#vocabulary-data').count()==1 and other.locator('#history-data').count()==0
    assert p.evaluate("localStorage.getItem('alaina-spanish-practice-v1')")==saved
    print(engine,'Spanish-to-history first visit; independent caches; both apps offline; both progress stores preserved PASS',flush=True);checks.append({'engine':engine,'passed':True})
   finally:ctx.close();b.close();server.shutdown();server.server_close()
(OUT/'cache-isolation.json').write_text(json.dumps(checks,indent=2))
