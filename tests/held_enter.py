"""Holding Enter cannot advance past feedback; normal Next still works."""
from pathlib import Path
import functools,threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(ROOT)));threading.Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   b=getattr(pw,engine).launch();ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block')
   ctx.add_init_script(path=str(ROOT/'tests/speech_stub.js'));p=ctx.new_page()
   p.goto(f'http://127.0.0.1:{s.server_port}/');p.locator('[data-action=start]').tap();p.locator('[data-mode=listening]').tap();p.locator('#begin-round').tap()
   expect(p.locator('#quiz-submit')).to_be_enabled();p.locator('#answer-input').fill(p.evaluate('__audio.calls.at(-1).text'))
   p.keyboard.down('Enter');expect(p.locator('.feedback.correct')).to_be_visible()
   p.keyboard.down('Enter');p.keyboard.down('Enter');p.keyboard.up('Enter')
   expect(p.locator('.practice-progress-label')).to_contain_text('Question 1 of 10')
   p.locator('#quiz-submit').press('Enter');expect(p.locator('.practice-progress-label')).to_contain_text('Question 2 of 10')
   print(engine,'held Enter stays on feedback; explicit Next advances once PASS',flush=True)
   ctx.close();b.close()
finally:s.shutdown()
