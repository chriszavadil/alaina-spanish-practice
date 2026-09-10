"""Verify an installed 1.4.1 cache upgrades on the same origin without losing progress."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import functools,json,subprocess,tempfile,threading,os
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];STORE='alaina-spanish-practice-v1'
files=['index.html','sw.js','manifest.webmanifest','icon-192.png','icon-512.png']
with tempfile.TemporaryDirectory(prefix='alaina-upgrade-') as folder:
 oldroot=Path(folder)
 for f in files:
  (oldroot/f).write_bytes(subprocess.check_output(['git','show','85ddbd9:'+f],cwd=ROOT))
  # Model real release chronology: the old release predates the new one.
  # Otherwise this artificial directory swap can yield an incorrect HTTP 304.
  os.utime(oldroot/f,(1577836800,1577836800))
 active={'root':oldroot}
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*a,**kw):super().__init__(*a,directory=str(active['root']),**kw)
  def log_message(self,*a):pass
 u2=json.loads((ROOT/'src/unit2.json').read_text(encoding='utf-8'))
 initial={'settings':{'unit':'unit2','categories':[c['id'] for c in u2['categories'] if not c['supplemental'] and not c.get('introduced')]},'progress':{'items':{c['id']:{'seen':2,'quizCorrect':1,'needsReview':False} for c in u2['cards'] if not c.get('introduced')},'rounds':11,'perfectRounds':1}}
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   active['root']=oldroot
   server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
   b=getattr(pw,engine).launch();ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True)
   ctx.add_init_script(path=str(ROOT/'tests/speech_stub.js'))
   ctx.add_init_script(f"if(!localStorage.getItem('{STORE}'))localStorage.setItem('{STORE}',JSON.stringify({json.dumps(initial)}))")
   p=ctx.new_page();p.set_default_timeout(12000)
   try:
    p.goto(f'http://127.0.0.1:{server.server_port}/');p.evaluate('navigator.serviceWorker.ready');p.wait_for_function('!!navigator.serviceWorker.controller')
    expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.4.1')
    p.locator('[data-action=achievements]').tap();expect(p.locator('.badge-card.unlocked',has_text='Unit 2 Explorer')).to_be_visible();p.locator('[data-action=dismiss]').tap()
    before=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
    active['root']=ROOT;p.reload()
    expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.4.2')
    p.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update())')
    p.wait_for_function("caches.keys().then(keys=>keys.some(k=>k.endsWith('v1.4.2')))")
    p.locator('[data-action=start]').tap();assert p.locator('input[name=topic]:checked').count()==9
    p.locator('[data-mode=quiz]').tap()
    after=p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
    assert after['progress']['items']==before['progress']['items']
    assert after['progress']['rounds']==before['progress']['rounds']
    assert after['progress']['earnedAchievements']['unit2'] is True
    assert after['settings']['placesRevision']==1
    p.reload();p.locator('[data-action=achievements]').tap();expect(p.locator('.badge-card.unlocked',has_text='Unit 2 Explorer')).to_be_visible()
    print(engine,'cached 1.4.1 -> 1.4.2, same origin, progress and earned badge preserved PASS',flush=True)
   finally:ctx.close();b.close();server.shutdown();server.server_close()
