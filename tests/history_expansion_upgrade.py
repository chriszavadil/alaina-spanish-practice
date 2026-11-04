"""Real installed-history upgrade; wait for activation and inspect cached version before offline."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
import subprocess,threading,tempfile,os,json
ROOT=Path(__file__).resolve().parents[1];BASE='4be9257df1a506c749b96396469fffcbcb2f113a';STORE='alaina-history-studio-v1'
OUT=ROOT/'history-scenario-results';OUT.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(active['root']),**kwargs)
 def log_message(self,*args):pass
# Merely creating a new cache does not mean installation or activation has completed.
VERSION_PROBE="""() => new Promise(resolve=>{
 const worker=navigator.serviceWorker.controller;
 if(!worker||worker.state!=='activated'){resolve(false);return;}
 const channel=new MessageChannel();
 const finish=value=>{clearTimeout(timer);channel.port1.close();resolve(value);};
 const timer=setTimeout(()=>finish(false),400);
 channel.port1.onmessage=e=>finish(e.data?.version==='v1.1.1');
 worker.postMessage({type:'HISTORY_CACHE_VERSION'},[channel.port2]);
})"""
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
    p.goto(url);expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.0');p.evaluate('navigator.serviceWorker.ready');p.wait_for_function('!!navigator.serviceWorker.controller')
    p.evaluate("localStorage.setItem('alaina-spanish-practice-v1','UNCHANGED_SPANISH')")
    p.locator('[data-action=setup]').tap();p.locator('[data-mode=type]').tap();p.locator('#begin-round').tap()
    prompt=p.locator('.prompt').inner_text();p.locator('#answer').fill('unfinished answer');p.locator('header [data-action=home]').tap()
    before=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
    active['root']=ROOT;p.reload();expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.1');p.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update())')
    p.wait_for_function(VERSION_PROBE,timeout=15000,polling=500)
    cached=p.evaluate("""async () => {
     const keys=await caches.keys();const name=keys.find(x=>x.startsWith('alaina-history-')&&x.endsWith('v1.1.1'));
     const cache=await caches.open(name);return await Promise.all(['./','./index.html'].map(async path=>{const r=await cache.match(new URL(path,location.href).href);return r?await r.text():'';}));
    }""")
    assert len(cached)==2 and all('name="app-version" content="1.1.1"' in h for h in cached),'New cache must contain only new-version entry pages'
    p.locator('[data-action=resume]').tap();expect(p.locator('#answer')).to_have_value('unfinished answer');expect(p.locator('.prompt')).to_have_text(prompt)
    assert p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}")).progress')==before['progress']
    p.locator('header [data-action=home]').tap();p.locator('[data-action=scenario-setup]').tap();p.locator('#begin-round').tap();p.locator('[data-action=confirm]').tap()
    q=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}")).session');assert q['mode']=='scenario';text=p.locator('.prompt').inner_text()
    p.locator('header [data-action=home]').tap();server.shutdown();server.server_close()
    for _ in range(2):
     p.reload();expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.1');p.locator('[data-action=resume]').tap();expect(p.locator('.prompt')).to_have_text(text);p.locator('header [data-action=home]').tap()
    assert p.evaluate("localStorage.getItem('alaina-spanish-practice-v1')")=='UNCHANGED_SPANISH'
    checks.append({'engine':engine,'passed':True,'active_worker_version':'v1.1.1','cached_entry_versions':['1.1.1','1.1.1'],'offline_reloads':2});print(engine,'installed History 1.1.0 -> 1.1.1; activated worker and fresh cache verified; old round preserved; scenarios survive repeated offline reloads PASS',flush=True)
   except Exception:
    p.screenshot(path=str(OUT/f'FAILED-{engine}-cached-upgrade.png'),full_page=True)
    (OUT/f'cache-diagnostic-{engine}.json').write_text(json.dumps(p.evaluate("async()=>({controller:navigator.serviceWorker.controller?.state,caches:await caches.keys(),version:document.querySelector('meta[name=app-version]')?.content})"),indent=2));raise
   finally:ctx.close();b.close();server.shutdown();server.server_close()
(OUT/'upgrade.json').write_text(json.dumps(checks,indent=2))
