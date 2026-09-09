"""Real touch/click/keyboard accent-input checks on both browser engines."""
import functools,json,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   b=getattr(pw,engine).launch()
   for mode in ['quiz','listening']:
    ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block')
    ctx.add_init_script(path=str(root/'tests/speech_stub.js'));p=ctx.new_page();p.set_default_timeout(10000)
    p.goto(f'http://127.0.0.1:{server.server_port}/')
    p.locator('[data-unit=unit2]').tap();p.locator('[data-action=start]').tap();p.locator(f'[data-mode={mode}]').tap();p.locator('#begin-round').tap()
    expect(p.locator('#quiz-submit')).to_be_enabled()
    for letter in 'áéíóúüñ':
     p.locator('#answer-input').fill('abc');p.locator('#answer-input').evaluate('(el)=>el.setSelectionRange(1,2)')
     p.locator(f'[data-letter="{letter}"]').tap();expect(p.locator('#answer-input')).to_have_value('a'+letter+'c')
    p.locator('#answer-input').fill('n');p.locator('#answer-input').evaluate('(el)=>el.setSelectionRange(0,1)')
    p.locator('[data-letter="ñ"]').click();expect(p.locator('#answer-input')).to_have_value('ñ')
    p.locator('#answer-input').fill('a');p.locator('#answer-input').evaluate('(el)=>el.setSelectionRange(0,1)')
    p.locator('[data-letter="á"]').focus();p.locator('[data-letter="á"]').press('Enter');expect(p.locator('#answer-input')).to_have_value('á')
    p.locator('#quiz-submit').tap();expect(p.locator('#answer-input')).to_be_disabled()
    for letter in 'áéíóúüñ':expect(p.locator(f'[data-letter="{letter}"]')).to_be_disabled()
    print(engine,mode,'all 7 accents; selection replacement; touch, mouse, keyboard; disabled-after-answer PASS',flush=True)
    ctx.close()
   b.close()
finally:server.shutdown()
