"""Final source review: safe imported identifiers, direct references and phone polish."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
p=root/'history-src/app.js';s=p.read_text(encoding='utf-8')
a='id:String(q.id).slice(0,60)';b="id:(String(q.id).replace(/[^a-z0-9_-]/gi,'').slice(0,60)||'restored')"
if a in s:assert s.count(a)==1;s=s.replace(a,b)
else:assert b in s
s=s.replace('m6 6 12 12M18 6 6 6','m6 6 12 12M18 6 6 18')
s=s.replace('<div class="art-badge">A FIELD GUIDE TO BIG IDEAS</div>','')
s=s.replace('<strong>${s.seen}<small>of 15 terms explored</small></strong>','<strong>${s.seen}</strong><small>of 15 terms explored</small>')
p.write_text(s,encoding='utf-8')
p=root/'history-src/data.json';d=json.loads(p.read_text(encoding='utf-8'))
d['sources']['china']['url']='https://asia-archive.si.edu/learn/for-educators/teaching-china-with-the-smithsonian/lesson-plans/beliefs-and-values-in-ancient-china-buddhism-daoism-and-confucianism/'
d['sources']['china']['name']='Smithsonian National Museum of Asian Art · Beliefs and Values in Ancient China'
d['sources']['caravan']={'name':'Oxford Learner’s Dictionaries · Caravan','url':'https://www.oxfordlearnersdictionaries.com/definition/english/caravan'}
d['sources']['luxury']={'name':'Oxford Learner’s Dictionaries · Luxury','url':'https://www.oxfordlearnersdictionaries.com/definition/english/luxury_1'}
for c in d['cards']:
 if c['id']=='caravan':c['sources']=['caravan','silk']
 if c['id']=='luxury-goods':c['sources']=['luxury','silk']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Scope the test to the Cancel action rather than both Cancel and the close icon.
p=root/'tests/history_browser.py';s=p.read_text(encoding='utf-8').replace("f'[data-length={length}]'", "f'[data-length=\"{length}\"]'")
s=s.replace("tap(p,'[data-action=reset]');tap(p,'[data-action=dismiss]');assert", "tap(p,'[data-action=reset]');tap(p,'#modal .button-row [data-action=dismiss]');assert")
p.write_text(s,encoding='utf-8')
print('Finalized safe imports, direct sources, phone polish and precise test locators.')
