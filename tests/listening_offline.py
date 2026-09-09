"""Cache fallback when origin goes away. Audio uses a test-only speech double."""
import functools,threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
with sync_playwright() as pw:
 for engine in ['webkit','chromium']:
  server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
  threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   browser=getattr(pw,engine).launch();context=browser.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True)
   context.add_init_script(path=str(root/'tests/speech_stub.js'));page=context.new_page();page.set_default_timeout(12000)
   page.goto(f'http://127.0.0.1:{server.server_port}/');page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('navigator.serviceWorker.controller')
   page.locator('[data-action="start"]').tap();page.locator('[data-mode="listening"]').tap();page.locator('[data-action="begin"]').tap()
   expect(page.locator('#quiz-submit')).to_be_enabled();word=page.evaluate('__audio.calls.at(-1).text')
   page.locator('#answer-input').fill(word);page.locator('#quiz-submit').tap();expect(page.locator('.feedback.correct')).to_be_visible()
   stored=page.evaluate("localStorage.getItem('alaina-spanish-practice-v1')")
   server.shutdown();server.server_close();page.reload()
   expect(page.locator('meta[name="app-version"]')).to_have_attribute('content','1.4.1')
   assert page.evaluate("localStorage.getItem('alaina-spanish-practice-v1')")==stored
   page.locator('[data-action="start"]').tap();page.locator('[data-action="begin"]').tap()
   expect(page.locator('#listen-status')).to_contain_text('3 replays left')
   context.close();browser.close();print(engine,'server-unreachable cache fallback and saved progress PASS',flush=True)
  finally:server.shutdown();server.server_close()
