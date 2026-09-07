"""Audio interruption and unavailable voice regressions; simulated speech only."""
import functools,threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   browser=getattr(pw,engine).launch()
   for failure in ['interrupted','canceled','throw','no-spanish']:
    context=browser.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block')
    context.add_init_script(path=str(ROOT/'tests/speech_stub.js'))
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{server.server_port}/')
    page.evaluate("__audio.mode='hold';window.__normalVoices=speechSynthesis.getVoices")
    if failure=='throw': page.evaluate("__audio.mode='throw'")
    if failure=='no-spanish': page.evaluate("speechSynthesis.getVoices=()=>[{lang:'en-US',name:'English',voiceURI:'english'}]")
    page.locator('[data-action="start"]').tap();page.locator('[data-mode="listening"]').tap();page.locator('[data-action="begin"]').tap()
    if failure in ['interrupted','canceled']: page.evaluate("error=>{let u=__audio.current;__audio.current=null;u.onerror({error})}",failure)
    expect(page.locator('#listen-error')).to_be_visible(timeout=2000)
    expect(page.locator('#listen-play')).to_be_enabled();expect(page.locator('#quiz-submit')).to_be_disabled()
    page.evaluate("__audio.mode='ok';speechSynthesis.getVoices=__normalVoices")
    page.locator('#listen-play').tap();expect(page.locator('#listen-status')).to_contain_text('3 replays left')
    assert not errors,errors
    print(engine,failure,'recovers without spending a listen PASS',flush=True);context.close()
   browser.close()
finally:
 server.shutdown();server.server_close()
