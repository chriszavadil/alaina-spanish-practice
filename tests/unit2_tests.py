"""Unit 2 end-to-end checks; speech events are simulated, not a physical audio test."""
import argparse,functools,json,threading,shutil,re
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--engine',default='both');p.add_argument('--url');args=p.parse_args()
STORE='alaina-spanish-practice-v1'
legacy={'settings':{'categories':['numbers','greetings'],'mode':'quiz','length':'10','speed':'0.75'},'progress':{'items':{'number-1':{'seen':3,'quizCorrect':2,'needsReview':False,'futureField':'preserve'},'greeting-kiss':{'seen':1,'quizCorrect':0,'needsReview':True}},'rounds':7,'perfectRounds':2,'lastQuiz':{'correct':8,'total':10},'listeningRounds':2,'lastListening':{'correct':9,'total':10}}}
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=args.url or f'http://127.0.0.1:{server.server_port}/'
report={'physical_iPhone_audio_tested':False,'checks':[]}
def state(page):return page.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
def tap(page,selector):page.locator(selector).tap()
def setup(page,unit='unit2',mode='quiz',all_topics=True,length='all'):
 tap(page,f'[data-unit="{unit}"]');tap(page,'[data-action="start"]');tap(page,f'[data-mode="{mode}"]')
 if all_topics:
  if page.locator('input[name=topic]:checked').count()!=page.locator('input[name=topic]').count():tap(page,'[data-action="toggle-topics"]')
 tap(page,f'[data-length="{length}"]')
def answer(page,mode,i):
 if mode=='listening':
  expect(page.locator('#quiz-submit')).to_be_enabled()
  text=page.evaluate('__audio.calls.at(-1).text')
  assert page.locator('.quiz-prompt,.quiz-card .card-word,.quiz-card .number-caption').count()==0
 else:
  prompt=page.locator('.quiz-prompt .card-word').inner_text()
  text=page.evaluate("en=>JSON.parse(document.querySelector('#vocabulary-data').textContent).cards.find(c=>c.id.startsWith('u2-')&&c.en===en).forms[0]",prompt)
 page.locator('#answer-input').fill(text)
 if i<2:tap(page,'#quiz-submit')
 else:page.locator('#quiz-submit').evaluate('(b)=>b.click()')
 expect(page.locator('.feedback.correct')).to_be_visible()
 if i<2:tap(page,'#quiz-submit')
 else:page.locator('#quiz-submit').evaluate('(b)=>b.click()')
def migration(page):
 expect(page.locator('[data-unit=unit1]')).to_have_attribute('aria-pressed','true')
 tap(page,'[data-unit=unit2]');expect(page.locator('.progress-card h2')).to_have_text('Unit 2 progress')
 assert state(page)['progress']['items']==legacy['progress']['items']
 assert state(page)['progress']['units']['unit1']['rounds']==7
 tap(page,'[data-action=start]');assert page.locator('input[name=topic]').count()==9
 assert page.locator('input[name=topic]:checked').count()==7
 assert page.locator('input[data-extra=true]:checked').count()==0
 # All -> 109, normal vocabulary -> 89. Repeated switches keep the two topic sets separate.
 tap(page,'[data-length=all]');expect(page.locator('#begin-round')).to_contain_text('89')
 tap(page,'[data-unit=unit1]');assert page.locator('input[name=topic]:checked').count()==2
 tap(page,'[data-unit=unit2]');assert page.locator('input[name=topic]:checked').count()==7
 tap(page,'[data-action=word-list]');expect(page.locator('#word-count')).to_contain_text('109')
 page.locator('#word-search').fill('tijeras');expect(page.locator('.word-form')).to_contain_text('las tijeras')
 tap(page,'[data-unit=unit1]');expect(page.locator('#word-count')).to_contain_text('147')
 page.reload();expect(page.locator('[data-unit=unit1]')).to_have_attribute('aria-pressed','true')
 assert state(page)['progress']['items']==legacy['progress']['items']
def full_quiz(page):
 setup(page);tap(page,'#begin-round')
 for i in range(109):answer(page,'quiz',i)
 expect(page.locator('.results')).to_be_visible();s=state(page)['progress']
 assert s['rounds']==8 and s['units']['unit1']['rounds']==7 and s['units']['unit2']['rounds']==1
 assert s['units']['unit2']['lastQuiz']=={'correct':109,'total':109}
 for id,item in legacy['progress']['items'].items():assert s['items'][id]==item
 page.locator('#brand-home').tap();tap(page,'[data-action=achievements]')
 expect(page.locator('.badge-card.unlocked',has_text='Unit 2 Explorer')).to_be_visible()
 expect(page.locator('.badge-card.locked',has_text='Unit 1 Champion')).to_be_visible()
 tap(page,'[data-action=dismiss]');page.reload();assert state(page)['progress']==s
 page.screenshot(path=str(OUT/'unit2-progress.png'),full_page=True)
def full_listening(page):
 setup(page,mode='listening');tap(page,'#begin-round')
 expect(page.locator('#quiz-submit')).to_be_enabled()
 first=page.evaluate('__audio.calls.at(-1).text')
 for _ in range(3):
  tap(page,'#listen-play');expect(page.locator('#quiz-submit')).to_be_enabled()
  assert page.evaluate('__audio.calls.at(-1).text')==first
 assert page.evaluate('__audio.calls.length')==4
 expect(page.locator('#listen-play')).to_be_disabled()
 for i in range(109):answer(page,'listening',i)
 expect(page.locator('.results')).to_be_visible();s=state(page)['progress']
 assert s['lastListening']=={'correct':109,'total':109}
 assert s['units']['unit1']['rounds']==7 and s['units']['unit2']['listeningRounds']==1
 assert sum(v.get('listeningCorrect',0) for k,v in s['items'].items() if k.startswith('u2-'))==109
 for id,item in legacy['progress']['items'].items():assert s['items'][id]==item
 page.reload();assert state(page)['progress']==s

def flash_and_layout(page):
 setup(page,mode='flashcards');page.wait_for_timeout(300)
 page.screenshot(path=str(OUT/'unit2-topics.png'),full_page=True)
 for w,h in [(393,852),(320,740),(852,393),(1200,850)]:
  page.set_viewport_size({'width':w,'height':h});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.set_viewport_size({'width':393,'height':852});tap(page,'#begin-round');zero=False
 for i in range(109):
  if page.locator('#flash-front .card-word').inner_text()=='zero':
   zero=True;expect(page.locator('#flash-front .number-caption')).to_have_text('0')
  page.locator('#flip-card').evaluate('(b)=>b.click()');expect(page.locator('#after-flip')).to_be_visible()
  if i==0:
   page.locator('#flip-card').tap();expect(page.locator('#before-flip')).to_be_visible();tap(page,'#flip-card')
   tap(page,'#after-flip [data-action=speak] >> nth=0')
  page.locator('[data-action=rate][data-correct=true]').evaluate('(b)=>b.click()')
 expect(page.locator('.results')).to_be_visible();assert zero
 assert state(page)['progress']['units']['unit2']['rounds']==1

def review_and_wrong(page):
 setup(page,length='10');tap(page,'#begin-round');page.locator('#answer-input').fill('incorrecto')
 tap(page,'#quiz-submit');expect(page.locator('.feedback.correct')).to_have_count(0);tap(page,'#quiz-submit')
 for _ in range(9):tap(page,'#quiz-skip');tap(page,'#quiz-submit')
 expect(page.locator('.results')).to_be_visible();assert page.locator('.review-row').count()==10
 tap(page,'[data-action=retry-missed]');expect(page.locator('.practice-progress-label')).to_contain_text('Question 1 of 10')
 tap(page,'[data-action=leave]');tap(page,'[data-action=confirm-leave]');tap(page,'[data-unit=unit1]')
 expect(page.locator('.review-toggle')).to_contain_text('1 saved')
 tap(page,'[data-unit=unit2]');expect(page.locator('.review-toggle')).to_contain_text('10 saved')

try:
 with sync_playwright() as pw:
  for engine in (['chromium','webkit'] if args.engine=='both' else [args.engine]):
   extra={'executable_path':shutil.which('chromium')} if engine=='chromium' and shutil.which('chromium') else {}
   b=getattr(pw,engine).launch(headless=True,**extra)
   for fn in [migration,full_quiz,full_listening,flash_and_layout,review_and_wrong]:
    ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block')
    ctx.add_init_script(path=str(ROOT/'tests/speech_stub.js'))
    ctx.add_init_script(f"if(!localStorage.getItem('{STORE}'))localStorage.setItem('{STORE}',JSON.stringify({json.dumps(legacy)}))")
    page=ctx.new_page();page.set_default_timeout(10000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
     page.goto(url);expect(page.locator('meta[name=app-version]')).to_have_attribute('content','1.4.0')
     fn(page);assert not errors,errors;report['checks'].append({'engine':engine,'test':fn.__name__,'passed':True});print(engine,fn.__name__,'PASS',flush=True)
    except Exception:
     page.screenshot(path=str(OUT/f'FAILED-{engine}-{fn.__name__}.png'),full_page=True)
     report['checks'].append({'engine':engine,'test':fn.__name__,'passed':False,'errors':errors});raise
    finally:ctx.close()
   b.close()
finally:
 server.shutdown();(OUT/'unit2-report.json').write_text(json.dumps(report,indent=2))
