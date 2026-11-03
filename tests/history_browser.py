"""History Studio end-to-end checks. Speech events simulated, never physical audio certification."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import argparse,functools,threading,json
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'history-test-results';OUT.mkdir(exist_ok=True)
D=json.loads((ROOT/'history-src/data.json').read_text(encoding='utf-8'));CARDS=D['cards'];STORE='alaina-history-studio-v1';SPAN='alaina-spanish-practice-v1'
parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();URL=args.url or f'http://127.0.0.1:{server.server_port}/history/'
STUB="""window.__audio={calls:[],mode:'ok',current:null};
Object.defineProperty(window,'SpeechSynthesisUtterance',{configurable:true,value:class{constructor(text){this.text=text;}}});
Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{getVoices(){return [{lang:'en-US',name:'Test English',voiceURI:'test-en'}]},addEventListener(){},resume(){},cancel(){let u=__audio.current;__audio.current=null;u?.onerror?.({error:'canceled'});},speak(u){let a=__audio,m=a.mode;a.calls.push({text:u.text,lang:u.lang});a.current=u;if(m==='throw')throw Error('test');if(m==='silent')return;queueMicrotask(()=>{if(a.current!==u)return;if(m==='fail'){a.current=null;u.onerror?.({error:'not-allowed'});return;}u.onstart?.({});if(m==='hold')return;setTimeout(()=>{if(a.current!==u)return;a.current=null;u.onend?.({});},30);});}}});"""
def tap(p,sel):p.locator(sel).tap()
def stored(p):return p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
def begin(p,mode='type',length='all'):
 tap(p,'[data-action=setup]');tap(p,f'[data-mode={mode}]');tap(p,f'[data-length="{length}"]');tap(p,'#begin-round')
def nextq(p):
 expect(p.locator('#quiz-action')).to_be_enabled();tap(p,'#quiz-action')
def card_for_prompt(p):
 prompt=p.locator('.prompt').inner_text();return next(c for c in CARDS if prompt in [c['definition'],c['scenario']])
def answer(p,text,action='check'):
 p.locator('#answer').fill(text)
 if action=='enter':p.locator('#answer').press('Enter')
 else:tap(p,'[data-action='+action+']')
 expect(p.locator('[data-result=correct]')).to_be_visible()
def home(p):tap(p,'header [data-action=home]')
def onboarding(p):
 expect(p).to_have_title('Alaina’s History Studio');p.screenshot(path=str(OUT/'history-home.png'),full_page=True)
 tap(p,'[data-action=setup]');assert p.locator('[data-mode]').count()==5;assert p.locator('input[name=topic]:checked').count()==3
 tap(p,'[data-action=all-topics]');expect(p.locator('#begin-round')).to_be_disabled();tap(p,'[data-action=all-topics]')
 tap(p,'[data-length=all]');expect(p.locator('#begin-round')).to_contain_text('15')
 for w,h in [(320,740),(393,852),(852,393),(1200,850)]:
  p.set_viewport_size({'width':w,'height':h});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(w,h)
 p.set_viewport_size({'width':393,'height':852});p.screenshot(path=str(OUT/'history-modes.png'),full_page=True)
 tap(p,'header [data-action=library]');assert p.locator('.word-entry').count()==15
 p.locator('#search').fill('Taoism');assert p.locator('.word-entry').count()==1;expect(p.locator('.word-entry h2')).to_have_text('Daoism')
 p.locator('#search').fill('<script>alert(1)</script>');assert p.locator('.word-entry').count()==0

def flashcards(p):
 begin(p,'flash');seen=[]
 for i in range(15):
  seen.append(p.locator('.term').inner_text());tap(p,'#flip');expect(p.locator('.answer-extras')).to_be_visible()
  if i==0:
   tap(p,'[data-action=speak]');p.wait_for_timeout(80);assert p.evaluate('__audio.calls.at(-1).lang')=='en-US'
   tap(p,'#flip');expect(p.locator('.term')).to_be_visible();tap(p,'#flip')
  tap(p,'[data-action='+('again' if i<3 else 'known')+']')
 expect(p.locator('.results')).to_be_visible();assert len(set(seen))==15
 s=stored(p);assert s['progress']['rounds']==1;assert sum(x['review'] for x in s['progress']['items'].values())==3
 assert sum(x['meaning'] for x in s['progress']['items'].values())==0
 p.reload();assert stored(p)['progress']==s['progress']

def meaning(p):
 begin(p,'choice')
 for i in range(15):
  c=card_for_prompt(p);assert p.locator('.choice').count()==4
  if i==0:
   tap(p,'[data-action=check]');expect(p.locator('#answer-error')).to_contain_text('Choose')
  tap(p,f'[data-choice="{c["id"]}"]');tap(p,'[data-action='+('show' if i%2 else 'check')+']')
  expect(p.locator('[data-result=correct]')).to_be_visible();nextq(p)
 expect(p.locator('.score')).to_have_text('15 / 15');s=stored(p)['progress'];assert s['perfect']==1
 assert sum(x['meaning'] for x in s['items'].values())==15
 assert sum(x['correct'] for x in s['items'].values())==15

def recall(p):
 begin(p,'type')
 for i in range(15):
  c=card_for_prompt(p);text=(c['aliases'][0] if c['aliases'] else c['term']).upper()
  answer(p,text,['show','check','enter'][i%3]);assert stored(p)['session']['responses'][-1]['status']=='correct'
  if i==0:
   idx=stored(p)['session']['index'];p.evaluate("document.querySelector('#quiz-form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}))")
   assert stored(p)['session']['index']==idx
  nextq(p)
 expect(p.locator('.score')).to_have_text('15 / 15')
 assert sum(x['meaning'] for x in stored(p)['progress']['items'].values())==15

def listening(p):
 begin(p,'listen')
 for i in range(15):
  expect(p.locator('#quiz-action')).to_be_enabled();term=p.evaluate('__audio.calls.at(-1).text')
  assert term not in p.locator('.audio').inner_text();assert p.locator('.prompt,.term').count()==0
  if i==0:
   for _ in range(3):tap(p,'#listen-play');expect(p.locator('#quiz-action')).to_be_enabled();assert p.evaluate('__audio.calls.at(-1).text')==term
   expect(p.locator('#listen-play')).to_be_disabled();assert p.evaluate('__audio.calls.length')==4
  answer(p,term,'show');nextq(p)
 expect(p.locator('.score')).to_have_text('15 / 15');assert sum(x['spelling'] for x in stored(p)['progress']['items'].values())==15
 assert sum(x['meaning'] for x in stored(p)['progress']['items'].values())==0

def review_resume(p):
 begin(p,'type','5');c=card_for_prompt(p);p.locator('#answer').fill(c['term']);home(p)
 expect(p.locator('[data-action=resume]')).to_be_visible();p.reload();tap(p,'[data-action=resume]');expect(p.locator('#answer')).to_have_value(c['term'])
 tap(p,'[data-action=check]');expect(p.locator('[data-result=correct]')).to_be_visible();p.reload();tap(p,'[data-action=resume]')
 expect(p.locator('[data-result=correct]')).to_be_visible();assert stored(p)['progress']['items'][c['id']]['correct']==1;nextq(p)
 p.locator('#answer').fill('wrong answer');tap(p,'[data-action=show]');expect(p.locator('[data-result=incorrect]')).to_be_visible();nextq(p)
 for _ in range(3):tap(p,'[data-action=show]');expect(p.locator('[data-result=shown]')).to_be_visible();nextq(p)
 expect(p.locator('.score')).to_have_text('1 / 2');expect(p.locator('.breakdown')).to_contain_text('1 incorrect');expect(p.locator('.breakdown')).to_contain_text('3 shown')
 assert p.locator('.review-item').count()==4;p.screenshot(path=str(OUT/'history-results.png'),full_page=True)
 tap(p,'[data-action=retry]');expect(p.locator('.progress-label')).to_contain_text('1 of 4')
 home(p);tap(p,'[data-action=setup]');p.locator('#review-only').check();expect(p.locator('#begin-round')).to_contain_text('4')

def audio_recovery(p):
 p.evaluate("__audio.mode='fail'");begin(p,'listen','5')
 expect(p.locator('#audio-error')).to_contain_text('not finish');expect(p.locator('#quiz-action')).to_be_disabled();assert stored(p)['session']['plays']==0
 p.evaluate("__audio.mode='ok'");tap(p,'#listen-play');expect(p.locator('#quiz-action')).to_be_enabled();assert stored(p)['session']['plays']==1
 p.evaluate("__audio.mode='hold'");tap(p,'#listen-play');expect(p.locator('#listen-play')).to_be_disabled()
 tap(p,'#settings');tap(p,'[data-action=dismiss]');expect(p.locator('#listen-play')).to_be_enabled();assert stored(p)['session']['plays']==1
 p.evaluate("__audio.mode='ok'");tap(p,'#listen-play');expect(p.locator('#quiz-action')).to_be_enabled();assert stored(p)['session']['plays']==2
 answer(p,p.evaluate('__audio.calls.at(-1).text'),'show');nextq(p);expect(p.locator('#quiz-action')).to_be_enabled();assert stored(p)['session']['plays']==1

def reset_isolation(p):
 begin(p,'type','5');c=card_for_prompt(p);answer(p,c['term']);home(p);before=stored(p)['progress']
 tap(p,'#settings');tap(p,'[data-action=reset]');tap(p,'#modal .button-row [data-action=dismiss]');assert stored(p)['progress']==before
 tap(p,'#settings');tap(p,'[data-action=reset]');tap(p,'[data-action=confirm]');assert stored(p)['progress']['items']=={}
 assert p.evaluate(f'localStorage.getItem("{SPAN}")')=='SPANISH_SENTINEL_DO_NOT_TOUCH'

def blocked_storage(p):
 p.evaluate("() => { Storage.prototype.setItem=function(){throw new Error('Blocked by browser')}; }")
 begin(p,'type','5');expect(p.locator('#storage-warning')).to_be_visible();answer(p,card_for_prompt(p)['term']);nextq(p)
 expect(p.locator('.progress-label')).to_contain_text('2 of 5')

report={'url':URL,'physical_iphone_audio_tested':False,'checks':[]}
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   b=getattr(pw,engine).launch()
   for fn in [onboarding,flashcards,meaning,recall,listening,review_resume,audio_recovery,reset_isolation,blocked_storage]:
    ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block');ctx.add_init_script(STUB)
    ctx.add_init_script(f"if(!localStorage.getItem('{SPAN}'))localStorage.setItem('{SPAN}','SPANISH_SENTINEL_DO_NOT_TOUCH')")
    p=ctx.new_page();p.set_default_timeout(12000);errors=[];p.on('pageerror',lambda err:errors.append(str(err)))
    try:
     p.goto(URL);expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.1.0');fn(p)
     assert not errors,errors;assert p.evaluate(f'localStorage.getItem("{SPAN}")')=='SPANISH_SENTINEL_DO_NOT_TOUCH'
     report['checks'].append({'engine':engine,'test':fn.__name__,'passed':True});print(engine,fn.__name__,'PASS',flush=True)
    except Exception:
     p.screenshot(path=str(OUT/f'FAILED-{engine}-{fn.__name__}.png'),full_page=True);report['checks'].append({'engine':engine,'test':fn.__name__,'passed':False,'errors':errors});raise
    finally:ctx.close()
   b.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2))
print('ALL_HISTORY_BROWSER_GROUPS_PASS',len(report['checks']),flush=True)
