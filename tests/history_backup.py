"""Backup restoration accepts only History Studio and escapes restored text."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
import functools,threading,json
root=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(root)));threading.Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   b=getattr(pw,engine).launch();ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block',accept_downloads=True);p=ctx.new_page()
   p.goto(f'http://127.0.0.1:{s.server_port}/history/');p.locator('[data-action=setup]').tap();p.locator('[data-mode=type]').tap();p.locator('#begin-round').tap()
   p.locator('#answer').fill('draft');p.locator('header [data-action=home]').tap();p.locator('#settings').tap()
   with p.expect_download() as dl:p.locator('[data-action=export]').tap()
   raw=json.loads(Path(dl.value.path()).read_text());assert raw['app']=='alaina-history-studio-v1'
   before=p.evaluate("localStorage.getItem('alaina-history-studio-v1')")
   invalid={'name':'wrong.json','mimeType':'application/json','buffer':json.dumps({'app':'spanish','data':raw['data']}).encode()}
   p.locator('#import-file').set_input_files(invalid);expect(p.locator('#toast')).to_contain_text('not a valid')
   assert p.evaluate("localStorage.getItem('alaina-history-studio-v1')")==before
   raw['data']['session']['id']='x\" onclick=\"window.__attack=1'
   text='<img src=x onerror="window.__attack=1">';raw['data']['session']['input']=text
   p.locator('#import-file').set_input_files({'name':'history.json','mimeType':'application/json','buffer':json.dumps(raw).encode()})
   expect(p.locator('#modal-title')).to_have_text('Restore history backup?');p.locator('[data-action=confirm]').tap();p.locator('[data-action=resume]').tap()
   expect(p.locator('#answer')).to_have_value(text);assert p.evaluate('typeof window.__attack')=='undefined'
   assert not p.locator('[data-q]').get_attribute('onclick')
   p.locator('#answer').fill('wrong');p.locator('[data-action=check]').tap();expect(p.locator('[data-result=incorrect]')).to_be_visible()
   print(engine,'backup export, wrong-file rejection, safe restore and escaped imported text PASS',flush=True)
   ctx.close();b.close()
finally:s.shutdown()
