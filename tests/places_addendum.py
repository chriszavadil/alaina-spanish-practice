"""Seven-word release and 1.4.0 progress migration. Speech uses a test-only API double."""
import argparse,functools,json,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];STORE='alaina-spanish-practice-v1'
u2=json.loads((ROOT/'src/unit2.json').read_text(encoding='utf-8'))
new=[c for c in u2['cards'] if c.get('introduced')=='1.4.1'];assert len(new)==7
old=[c for c in u2['cards'] if not c.get('introduced')];assert len(old)==109
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();url=args.url or f'http://127.0.0.1:{server.server_port}/'
report={'url':url,'physical_iphone_audio_tested':False,'checks':[]};out=ROOT/'test-results';out.mkdir(exist_ok=True)
def tap(p,s):p.locator(s).tap()
def state(p):return p.evaluate(f'JSON.parse(localStorage.getItem("{STORE}"))')
def seed(full=False,subset=False):
 items={c['id']:{'seen':1,'quizCorrect':1,'needsReview':False} for c in old} if full else {}
 items['number-1']={'seen':5,'quizCorrect':3,'needsReview':False,'futureField':'preserve'}
 cats=['u2-days'] if subset else [c['id'] for c in u2['categories'] if not c['supplemental'] and not c.get('introduced')]
 return {'settings':{'unit':'unit2','mode':'quiz','length':'all','categories':cats,'categoriesByUnit':{'unit1':['numbers'],'unit2':cats}},'progress':{'items':items,'rounds':12,'perfectRounds':3,'lastQuiz':{'correct':8,'total':10},'units':{'unit1':{'rounds':7,'perfectRounds':2},'unit2':{'rounds':5,'perfectRounds':1}}}}
def migration(p,initial,subset):
 tap(p,'[data-action=start]');expected=1 if subset else 9
 assert p.locator('input[name=topic]:checked').count()==expected
 assert p.locator('input[data-extra=true]:checked').count()==0
 assert state(p)['progress']['items']==initial['progress']['items']
 p.locator('#brand-home').tap();tap(p,'[data-action=achievements]')
 expect(p.locator('.badge-card.unlocked',has_text='Unit 2 Explorer')).to_be_visible()
 tap(p,'[data-action=dismiss]');tap(p,'[data-action=start]');tap(p,'[data-mode=quiz]')
 assert state(p)['settings']['placesRevision']==1 and state(p)['progress']['earnedAchievements']['unit2']
 p.reload();tap(p,'[data-action=achievements]');expect(p.locator('.badge-card.unlocked',has_text='Unit 2 Explorer')).to_be_visible()
 tap(p,'[data-action=dismiss]');tap(p,'[data-action=start]');assert p.locator('input[name=topic]:checked').count()==expected
 for id,item in initial['progress']['items'].items():assert state(p)['progress']['items'][id]==item

def round_of_seven(p,initial,mode):
 tap(p,'[data-action=start]');tap(p,f'[data-mode={mode}]')
 for el in p.locator('input[name=topic]').all():el.set_checked(el.get_attribute('value') in ['u2-places','u2-origin'])
 expect(p.locator('#begin-round')).to_contain_text('7');tap(p,'#begin-round');visited=set()
 for i in range(7):
  if mode=='listening':
   expect(p.locator('#quiz-submit')).to_be_enabled();heard=p.evaluate('__audio.calls.at(-1).text');c=next(c for c in new if c['forms'][0]==heard)
   assert p.locator('.quiz-prompt,.quiz-card .card-word').count()==0
   if i==0:
    for _ in range(3):tap(p,'#listen-play');expect(p.locator('#quiz-submit')).to_be_enabled()
    expect(p.locator('#listen-play')).to_be_disabled();assert p.evaluate('__audio.calls.length')==4
  else:
   label=p.locator('#flash-front .card-word' if mode=='flashcards' else '.quiz-prompt .card-word').inner_text();c=next(c for c in new if c['en']==label)
  visited.add(c['id'])
  if mode=='flashcards':
   tap(p,'#flip-card');expect(p.locator('#flash-back')).to_contain_text(c['forms'][0]);tap(p,'#after-flip [data-action=speak]');assert p.evaluate('__audio.calls.at(-1).text')==c['forms'][0]
   tap(p,'[data-action=rate][data-correct=true]')
  else:
   p.locator('#answer-input').fill(c['forms'][0]);tap(p,'#quiz-submit');expect(p.locator('.feedback.correct')).to_be_visible();tap(p,'#quiz-submit')
 assert visited=={c['id'] for c in new};expect(p.locator('.results')).to_be_visible()
 saved=state(p)['progress'];assert saved['rounds']==13 and saved['units']['unit1']['rounds']==7 and saved['units']['unit2']['rounds']==6
 assert saved['items']['number-1']==initial['progress']['items']['number-1']
 p.reload();assert state(p)['progress']==saved
try:
 with sync_playwright() as pw:
  for engine in ['webkit','chromium']:
   b=getattr(pw,engine).launch(headless=True)
   for name in ['default-migration','filtered-migration','flashcards','quiz','listening']:
    initial=seed(full='migration' in name,subset=name=='filtered-migration')
    ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block')
    ctx.add_init_script(path=str(ROOT/'tests/speech_stub.js'))
    ctx.add_init_script(f"if(!localStorage.getItem('{STORE}'))localStorage.setItem('{STORE}',JSON.stringify({json.dumps(initial)}))")
    p=ctx.new_page();p.set_default_timeout(10000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
     p.goto(url);expect(p.locator('meta[name=app-version]')).to_have_attribute('content','1.4.1')
     if 'migration' in name:migration(p,initial,name=='filtered-migration')
     else:round_of_seven(p,initial,name)
     assert not errors,errors;report['checks'].append({'engine':engine,'test':name,'passed':True});print(engine,name,'PASS',flush=True)
    except Exception:
     p.screenshot(path=str(out/f'places-FAILED-{engine}-{name}.png'),full_page=True)
     report['checks'].append({'engine':engine,'test':name,'passed':False,'pageErrors':errors});raise
    finally:ctx.close()
   b.close()
finally:
 server.shutdown();(out/'places-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PLACES_ALL_TEN_GROUPS_PASS',flush=True)
