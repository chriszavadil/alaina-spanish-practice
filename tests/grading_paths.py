"""UI regressions for screenshot IMG_2365.png. Speech is simulated; no student data touched."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import functools,threading,json,argparse
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results/grading';OUT.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args();STORE='alaina-spanish-practice-v1'
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
URL=args.url or f'http://127.0.0.1:{server.server_port}/';report={'url':URL,'physical_iphone_audio_tested':False,'checks':[]}
def state(p):return p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
def tap(p,s):p.locator(s).tap()
def start(p,mode='listening'):
 tap(p,'[data-action=start]');tap(p,f'[data-mode={mode}]');tap(p,'#begin-round')
 expect(p.locator('#quiz-submit')).to_be_enabled()
def next(p):tap(p,'#quiz-submit');expect(p.locator('#quiz-submit')).to_be_enabled()
def tuesday(p,mode='listening'):
 start(p,mode);tap(p,'#quiz-skip');next(p)
 if mode=='listening':assert p.evaluate('__audio.calls.at(-1).text')=='el martes'
 else:expect(p.locator('.quiz-prompt .card-word')).to_have_text('Tuesday')
def assert_right(p):
 expect(p.locator('.feedback.correct')).to_be_visible();expect(p.locator('.feedback-answer')).to_have_text('el martes')
 item=state(p)['progress']['items']['u2-day-tuesday'];assert item['quizCorrect']==1 and item['needsReview'] is False and item['seen']==1

def correct_primary(p):
 tuesday(p);p.locator('#answer-input').fill('el martes');tap(p,'#quiz-submit');assert_right(p)
 p.screenshot(path=str(OUT/'martes-correct-iphone15.png'),full_page=True)
def correct_reveal(p):
 tuesday(p);p.locator('#answer-input').fill('el martes');expect(p.locator('#quiz-skip')).to_have_text('Check & show answer')
 tap(p,'#quiz-skip');assert_right(p);next(p);expect(p.locator('.practice-progress-label')).to_contain_text('Question 3 of 7')
def regular_reveal(p):
 tuesday(p,'quiz');p.locator('#answer-input').fill('MARTES');tap(p,'#quiz-skip');assert_right(p)
def enter_key(p):
 tuesday(p);p.locator('#answer-input').fill('el\u00a0martes');p.locator('#answer-input').press('Enter');assert_right(p)
 p.locator('#quiz-submit').press('Enter');expect(p.locator('.practice-progress-label')).to_contain_text('Question 3 of 7')
def ungraded_reveals(p):
 start(p,'quiz');tap(p,'#quiz-submit');expect(p.locator('#answer-error')).to_contain_text('Type an answer')
 assert not state(p)['progress']['items']
 for i in range(7):
  tap(p,'#quiz-skip');expect(p.locator('[data-result=skipped]')).to_be_visible()
  expect(p.locator('.feedback-heading')).to_contain_text('not graded');assert 'is-wrong' not in p.locator('#answer-input').get_attribute('class')
  tap(p,'#quiz-submit')
 expect(p.locator('.result-breakdown')).to_contain_text('0 incorrect');expect(p.locator('.result-breakdown')).to_contain_text('7 shown without an answer')
 assert sum(c.get('quizCorrect',0) for c in state(p)['progress']['items'].values())==0
 p.screenshot(path=str(OUT/'neutral-reveals-results.png'),full_page=True)
def wrong_reveal(p):
 tuesday(p);p.locator('#answer-input').fill('lunes');tap(p,'#quiz-skip')
 expect(p.locator('[data-result=incorrect]')).to_be_visible();expect(p.locator('.feedback-heading')).to_contain_text('Not quite')
 assert state(p)['progress']['items']['u2-day-tuesday']['quizCorrect']==0

def repeated_events(p):
 tuesday(p);p.locator('#answer-input').fill('el martes');p.evaluate('window.oldAction=document.querySelector("#quiz-submit")')
 p.locator('#quiz-submit').dblclick(delay=30);assert_right(p)
 expect(p.locator('.practice-progress-label')).to_contain_text('Question 2 of 7')
 p.evaluate("oldAction.click();oldAction.click();document.querySelector('#quiz-form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));")
 assert_right(p);expect(p.locator('.practice-progress-label')).to_contain_text('Question 2 of 7')
 p.locator('#quiz-submit').press('Enter');expect(p.locator('.practice-progress-label')).to_contain_text('Question 3 of 7')
 p.evaluate("document.querySelector('#quiz-form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}))")
 assert len(state(p)['progress']['items'])==2

def exact_accents(p):
 start(p)
 for typed,status in [('el lunes','correct'),('el martes','correct'),('miercoles','accent'),('la jueves','incorrect'),('VIERNES','correct'),('sa\u0301bado','correct'),('domingo','correct')]:
  expect(p.locator('#quiz-submit')).to_be_enabled();p.locator('#answer-input').fill(typed);tap(p,'#quiz-skip')
  expect(p.locator('.feedback')).to_have_attribute('data-result',status);tap(p,'#quiz-submit')
 expect(p.locator('.result-breakdown')).to_contain_text('5 correct');expect(p.locator('.result-breakdown')).to_contain_text('2 incorrect')
def all_reveal_vocabulary(p):
 for unit,total in [('unit1',147),('unit2',116)]:
  tap(p,f'[data-unit={unit}]');tap(p,'[data-action=start]')
  if p.locator('input[name=topic]:checked').count()!=p.locator('input[name=topic]').count():tap(p,'[data-action=toggle-topics]')
  tap(p,'[data-length=all]');tap(p,'[data-mode=listening]');tap(p,'#begin-round')
  for i in range(total):
   expect(p.locator('#quiz-submit')).to_be_enabled()
   p.evaluate("document.querySelector('#answer-input').value=__audio.calls.at(-1).text;document.querySelector('#quiz-skip').click()")
   expect(p.locator('[data-result=correct]')).to_be_visible()
   p.locator('#quiz-submit').evaluate('(b)=>b.click()')
  expect(p.locator('.results')).to_be_visible();expect(p.locator('.result-breakdown')).to_contain_text('0 incorrect')
  tap(p,'#brand-home')
 before=state(p);assert len(before['progress']['items'])==263
 assert sum(v.get('quizCorrect',0) for v in before['progress']['items'].values())==263
 p.reload();assert state(p)['progress']==before['progress']

suite=[correct_primary,correct_reveal,regular_reveal,enter_key,ungraded_reveals,wrong_reveal,repeated_events,exact_accents,all_reveal_vocabulary]
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   b=getattr(pw,engine).launch()
   for fn in suite:
    ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block')
    ctx.add_init_script(path=str(ROOT/'tests/speech_stub.js'))
    ctx.add_init_script("Math.random=()=>0.999999;if(!localStorage.getItem('alaina-spanish-practice-v1'))localStorage.setItem('alaina-spanish-practice-v1',JSON.stringify({settings:{unit:'unit2',categories:['u2-days'],length:'all',mode:'listening'},progress:{items:{},rounds:0}}))")
    p=ctx.new_page();p.set_default_timeout(10000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
     p.goto(URL);expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.4.2');fn(p);assert not errors,errors
     report['checks'].append({'engine':engine,'test':fn.__name__,'pass':True});print(engine,fn.__name__,'PASS',flush=True)
    except Exception:
     p.screenshot(path=str(OUT/f'FAILED-{engine}-{fn.__name__}.png'),full_page=True);report['checks'].append({'engine':engine,'test':fn.__name__,'pass':False,'pageErrors':errors});raise
    finally:ctx.close()
   b.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ALL_GRADING_PATH_GROUPS_PASS',len(report['checks']),flush=True)
