"""Browser regressions. Speech is simulated; this does not verify audible iPhone output."""
import argparse, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
STORE='alaina-spanish-practice-v1'
parser=argparse.ArgumentParser();parser.add_argument('--url');parser.add_argument('--quick',action='store_true');args=parser.parse_args()
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=None
if not args.url:
 server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
URL=args.url or f'http://127.0.0.1:{server.server_port}/'
OUT=ROOT.parent/'hosting'/'listen-spell-verification';OUT.mkdir(parents=True,exist_ok=True)
report={'url':URL,'speech':'simulated API events, not audible-device testing','checks':[]}
def seed(categories=None,length='10',progress=None):
 return {'settings':{'categories':categories or ['numbers'],'length':length},'progress':progress or {'items':{},'rounds':0,'lastQuiz':None,'perfectRounds':0}}
def saved(page): return page.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
def spoken(page): return page.evaluate('__audio.calls.at(-1).text')
def begin(page,mode='listening'):
 page.locator('[data-action="start"]').tap();page.locator(f'[data-mode="{mode}"]').tap();page.locator('[data-action="begin"]').tap()
def finish_audio(page):
 page.wait_for_function('window.__audio.current===null')
 expect(page.locator('#listen-status')).not_to_contain_text('Listen carefully.')
def next_word(page): page.locator('#quiz-submit').tap()
def check(page,text):
 page.locator('#answer-input').fill(text);page.locator('#quiz-submit').tap()
def replay_limit(page):
 begin(page);finish_audio(page)
 expect(page.locator('.practice-top h1')).to_have_text('Listen & Spell')
 assert page.locator('.quiz-prompt,.quiz-card .card-word,.quiz-card .number-caption').count()==0
 word=spoken(page);assert word not in page.locator('.listen-prompt').inner_text()
 assert word not in (page.locator('#listen-play').get_attribute('aria-label') or '')
 assert page.evaluate('__audio.calls.length')==1
 for remaining in [2,1,0]:
  page.locator('#listen-play').tap();finish_audio(page)
  assert spoken(page)==word
  if remaining: expect(page.locator('#listen-status')).to_contain_text(f'{remaining} replay')
 assert page.evaluate('__audio.calls.length')==4
 expect(page.locator('#listen-play')).to_be_disabled()
 page.evaluate("document.querySelector('#listen-play').disabled=false;document.querySelector('#listen-play').click()")
 assert page.evaluate('__audio.calls.length')==4
 check(page,word);expect(page.locator('.feedback.correct')).to_be_visible()
 next_word(page);finish_audio(page)
 expect(page.locator('.practice-progress-label')).to_contain_text('Question 2 of 10')
 expect(page.locator('#listen-status')).to_contain_text('3 replays left')
 assert sum(v.get('quizCorrect',0) for v in saved(page)['progress']['items'].values())==1
 assert page.evaluate('__audio.calls.length')==5

def failures(page):
 page.evaluate("__audio.mode='fail-before'");begin(page);finish_audio(page)
 expect(page.locator('#listen-error')).to_be_visible();expect(page.locator('#quiz-submit')).to_be_disabled()
 expect(page.locator('#listen-play')).to_have_text('Play Spanish')
 page.evaluate("__audio.mode='ok'");page.locator('#listen-play').tap();finish_audio(page)
 page.evaluate("__audio.mode='fail-after'");page.locator('#listen-play').tap();finish_audio(page)
 expect(page.locator('#listen-status')).to_contain_text('3 replays left')
 page.evaluate("__audio.mode='ok'");page.locator('#listen-play').tap();finish_audio(page)
 expect(page.locator('#listen-status')).to_contain_text('2 replays left')

def rapid_and_stale(page):
 page.evaluate("__audio.mode='hold'");begin(page)
 expect(page.locator('#listen-play')).to_be_disabled()
 page.evaluate("for(let i=0;i<5;i++){let b=document.querySelector('#listen-play');b.disabled=false;b.click()}window.__old=__audio.current")
 assert page.evaluate('__audio.calls.length')==1
 page.locator('#quiz-skip').tap();expect(page.locator('.feedback')).to_be_visible()
 page.evaluate("__audio.mode='ok'");next_word(page);finish_audio(page)
 page.evaluate('__old.onend?.({});__old.onerror?.({error:"audio-hardware"})')
 expect(page.locator('#listen-status')).to_contain_text('3 replays left')
 assert page.evaluate('__audio.calls.length')==2
 expect(page.locator('.practice-progress-label')).to_contain_text('Question 2 of 10')

def exact_form(page):
 begin(page);finish_audio(page);heard=spoken(page)
 card=page.evaluate("text=>JSON.parse(document.querySelector('#vocabulary-data').textContent).cards.find(c=>c.forms.includes(text))",heard)
 other=next(f for f in card['forms'] if f!=heard)
 check(page,other);expect(page.locator('.feedback.correct')).to_have_count(0)
 expect(page.locator('.feedback-answer')).to_have_text(heard)
 expect(page.locator('#listen-play')).to_be_disabled()
 next_word(page);finish_audio(page)
 page.locator('#answer-input').fill('n');page.locator('#answer-input').evaluate('(el)=>el.setSelectionRange(0,1)')
 page.locator('[data-letter="ñ"]').tap();expect(page.locator('#answer-input')).to_have_value('ñ')
 heard=spoken(page);page.locator('#answer-input').fill(heard)
 page.locator('#answer-input').press('Enter');expect(page.locator('.feedback.correct')).to_be_visible()
 page.locator('#quiz-submit').press('Enter');finish_audio(page)
 expect(page.locator('.practice-progress-label')).to_contain_text('Question 3 of 10')
def perfect_round_and_storage(page):
 before=saved(page)['progress'];before_rounds=before.get('rounds',0)
 before_correct=sum(v.get('quizCorrect',0) for v in before['items'].values())
 begin(page)
 for i in range(10):
  finish_audio(page);check(page,spoken(page));expect(page.locator('.feedback.correct')).to_be_visible();next_word(page)
 expect(page.locator('.results')).to_be_visible()
 p=saved(page)['progress'];assert p['rounds']==before_rounds+1
 assert p['lastListening']=={'correct':10,'total':10};assert p['listeningRounds']==1
 assert sum(v.get('quizCorrect',0) for v in p['items'].values())==before_correct+10
 assert sum(v.get('listeningCorrect',0) for v in p['items'].values())==10
 assert p['lastQuiz']==before.get('lastQuiz');assert p['items'].get('number-1',{}).get('futureField')=='preserve'
 page.reload();expect(page.locator('[data-action="achievements"]')).to_be_visible()
 assert saved(page)['progress']==p;assert saved(page)['settings']['mode']=='listening'
 page.locator('[data-action="achievements"]').tap()
 for name in ['Round One','Perfect Round','Spelling Starter']:
  expect(page.locator('.badge-card.unlocked',has_text=name)).to_be_visible()

def old_modes(page):
 begin(page,'quiz')
 for i in range(10):
  label=page.locator('.quiz-prompt .card-word').inner_text()
  answer=page.evaluate("text=>JSON.parse(document.querySelector('#vocabulary-data').textContent).cards.find(c=>c.en===text).forms[0]",label)
  check(page,answer);expect(page.locator('.feedback.correct')).to_be_visible();next_word(page)
 expect(page.locator('.results')).to_be_visible();page.locator('[data-action="new-topics"]').tap()
 page.locator('[data-mode="flashcards"]').tap();page.locator('[data-action="begin"]').tap()
 page.locator('#flip-card').tap();expect(page.locator('#after-flip')).to_be_visible()
 page.locator('#flip-card').tap();expect(page.locator('#before-flip')).to_be_visible();page.locator('#flip-card').tap()
 page.locator('[data-action="rate"][data-correct="true"]').tap();expect(page.locator('.practice-progress-label')).to_contain_text('Card 2 of 10')
def all_vocabulary(page):
 begin(page)
 for i in range(147):
  finish_audio(page)
  assert page.locator('.quiz-card .card-word').count()==0
  page.evaluate("document.querySelector('#answer-input').value=__audio.calls.at(-1).text;document.querySelector('#quiz-submit').click()")
  expect(page.locator('.feedback.correct')).to_be_visible()
  page.evaluate("document.querySelector('#quiz-submit').click()")
 expect(page.locator('.results')).to_be_visible();p=saved(page)['progress']
 assert p['lastListening']=={'correct':147,'total':147}
 assert len(p['items'])==147;assert p['rounds']==1

def timeout_recovery(page):
 page.evaluate("__audio.mode='silent'");begin(page)
 expect(page.locator('#listen-error')).to_be_visible(timeout=10000)
 expect(page.locator('#listen-play')).to_be_enabled();expect(page.locator('#quiz-submit')).to_be_disabled()
 page.evaluate("__audio.mode='ok'");page.locator('#listen-play').tap();finish_audio(page)
 expect(page.locator('#listen-status')).to_contain_text('3 replays left')

def layouts(page):
 page.locator('[data-action="start"]').tap()
 assert page.locator('[data-mode]').count()==3
 page.wait_for_timeout(300)
 page.screenshot(path=str(OUT/'modes-iphone15.png'),full_page=True)
 page.locator('[data-mode="listening"]').tap();page.locator('[data-action="begin"]').tap();finish_audio(page)
 for width,height in [(393,852),(320,740),(852,393)]:
  page.set_viewport_size({'width':width,'height':height})
  assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),(width,height)
 page.set_viewport_size({'width':393,'height':852})
 page.wait_for_timeout(300)
 page.screenshot(path=str(OUT/'listen-iphone15.png'),full_page=True)
legacy={'items':{'number-1':{'seen':3,'quizCorrect':2,'needsReview':False,'futureField':'preserve'}},'rounds':7,'perfectRounds':2,'lastQuiz':{'correct':8,'total':10}}
suite=[(replay_limit,seed()),(failures,seed()),(rapid_and_stale,seed()),(exact_form,seed(['occupations'])),(perfect_round_and_storage,seed(progress=legacy)),(old_modes,seed()),(layouts,seed())]
if not args.quick:suite.extend([(timeout_recovery,seed()),(all_vocabulary,seed(['numbers','personal','greetings','courtesy','occupations','nationalities','languages'],'all'))])
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   browser=getattr(pw,engine).launch(headless=True)
   for test,initial in suite:
    context=browser.new_context(viewport={'width':393,'height':852},device_scale_factor=1,is_mobile=True,has_touch=True,service_workers='block')
    context.add_init_script(path=str(ROOT/'tests/speech_stub.js'))
    context.add_init_script(f"if(!localStorage.getItem('{STORE}'))localStorage.setItem('{STORE}',JSON.stringify({json.dumps(initial)}))")
    page=context.new_page();page.set_default_timeout(10000);errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    try:
     page.goto(URL);expect(page.locator('meta[name="app-version"]')).to_have_attribute('content','1.3.0')
     test(page);assert not errors,errors
     report['checks'].append({'browser':engine,'test':test.__name__,'passed':True})
     print(engine,test.__name__,'PASS',flush=True)
    except Exception:
     page.screenshot(path=str(OUT/f'FAILED-{engine}-{test.__name__}.png'),full_page=True)
     report['checks'].append({'browser':engine,'test':test.__name__,'passed':False,'pageErrors':errors});raise
    finally:context.close()
   browser.close()
finally:
 if server:server.shutdown()
 (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('COMPLETE',len(report['checks']),'browser groups passed.',flush=True)
