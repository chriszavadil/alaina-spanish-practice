"""Reconcile the corrected four-per-term request without replacing live examples."""
from pathlib import Path
import json,subprocess,hashlib,re,sys
R=Path(__file__).resolve().parents[1]
BASE='36dec311f5240cc8efbb95251064cdf49f793dcf'
ORIGINAL='4be9257df1a506c749b96396469fffcbcb2f113a'
TESTED_FOUR='cb339d778b8ea5fd5e6835f10974381b7786aa23'
def at(ref,f):return subprocess.check_output(['git','show',ref+':'+f],cwd=R).decode('utf-8')
def dump(f,d):(R/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=json.loads(at(BASE,'history-src/data.json'));original=json.loads(at(ORIGINAL,'history-src/data.json'))
assert old['version']=='1.1.1' and all(len(c['scenarios'])==3 for c in old['cards'])
for a,b in zip(original['cards'],old['cards']):assert a['scenarios']==b['scenarios'][:2]
SPAN=['index.html','docs/index.html','src/core.js','src/data.json','src/unit2.json','sw.js','docs/sw.js','manifest.webmanifest','docs/manifest.webmanifest']
labels={'45 illustrative situations':'60 illustrative situations','Three different examples for every word.':'Four different examples for every word.','three per term':'four per term'}
app=at(BASE,'history-src/app.js')
for a,b in labels.items():
 assert a in app,a
 app=app.replace(a,b)
if '--audit' not in sys.argv:
 d=json.loads((R/'history-src/data.json').read_text(encoding='utf-8'))
 if d['version']=='1.1.1':
  assert d==old
  candidates=json.loads((R/'history-src/four_scenario_candidates.json').read_text(encoding='utf-8'))
  selection={c['id']:1 for c in d['cards']};selection.update({'christianity':0,'black-plague':0,'confucianism':0})
  for c in d['cards']:
   s=candidates[c['id']][selection[c['id']]]
   if c['id']=='feudalism':s={'text':'A medieval noble receives land rights from a more powerful lord in return for loyal service. The same noble grants some land rights to another vassal who promises service in return. Which system connects these relationships?','why':'These linked lord-vassal exchanges illustrate feudalism in the simplified classroom model. A person could be a vassal in one relationship and a lord in another; actual medieval arrangements varied.'}
   if c['id']=='meritocracy':s={'text':'A research fund compares applicants by the quality of their work and demonstrated ability. It does not award funding simply because an applicant comes from a wealthy family or knows the judges. Which selection principle is it trying to follow?','why':'Meritocracy favors demonstrated ability and achievement rather than inherited status or personal connections. This describes the selection ideal, not a guarantee that every applicant had equal opportunities.'}
   assert c['term'].lower() not in s['text'].lower()
   assert s not in c['scenarios'];c['scenarios'].append(s)
  d['version']='1.1.2';dump('history-src/data.json',d);dump('history-src/scenarios.json',{c['id']:c['scenarios'] for c in d['cards']})
 else:assert d['version']=='1.1.2'
 (R/'history-src/app.js').write_text(app,encoding='utf-8')
 for f in ['history-src/shell.html','history-src/sw.js']:
  s=at(BASE,f);assert '1.1.1' in s;(R/f).write_text(s.replace('1.1.1','1.1.2'),encoding='utf-8')
 # Reuse the successfully tested four-variant suites, including the safe fresh-storage fixture.
 for f in ['tests/history_scenarios.py','tests/history_scenarios.test.cjs','tests/history_browser.py','tests/history.test.cjs','tests/history_backup.py']:
  (R/f).write_text(at(TESTED_FOUR,f).replace('1.1.1','1.1.2'),encoding='utf-8')
 p=R/'tests/history_scenarios.py';s=p.read_text();needle=" for line in p.locator('.scenario-example strong')"
 assertion=" expect(p.locator('.scenario-examples > .note')).to_contain_text('4 illustrative situations')\n"
 if assertion not in s:
  assert needle in s;s=s.replace(needle,assertion+needle)
 p.write_text(s)
 s=at(BASE,'HISTORY_README.md').replace('1.1.1','1.1.2').replace('45 original illustrative situations: three for each term','60 original illustrative situations: four for each term').replace('all three examples','all four examples').replace('45-scenario collection','60-scenario collection')
 start=s.index('The three-scenario release is gated on');end=s.index('\n',start)
 s=s[:start]+'The four-scenario release retains all 45 examples from the briefly published three-example update, then adds the fourth. This is 60 total, or two more per term than the original 30-scenario collection. Tests cover four-round rotation, old saved rounds, fourth-example backups, the installed 1.1.1-to-1.1.2 update and the public app.'+s[end:]
 (R/'HISTORY_README.md').write_text(s,encoding='utf-8')
# Both before and after building, check every existing card field and every published example.
d=json.loads((R/'history-src/data.json').read_text());assert d['version']=='1.1.2' and len(d['cards'])==15
assert d['sources']==old['sources'] and d['categories']==old['categories']
for a,b in zip(old['cards'],d['cards']):
 assert len(b['scenarios'])==4 and b['scenarios'][:3]==a['scenarios']
 assert {k:v for k,v in a.items() if k!='scenarios'}=={k:v for k,v in b.items() if k!='scenarios'}
assert len({s['text'] for c in d['cards'] for s in c['scenarios']})==60
assert (R/'history-src/app.js').read_text()==app
assert (R/'history-src/core.js').read_text()==at(BASE,'history-src/core.js')
for f in SPAN:assert (R/f).read_text()==at(BASE,f),f
proof={'version':'1.1.2','release_base':BASE,'original_two_example_base':ORIGINAL,'terms':15,'scenarios_per_term':4,'total_scenarios':60,'original_examples_preserved':30,'intermediate_published_examples_preserved':45,'added_relative_to_original':30,'storage_key':'alaina-history-studio-v1','grading_rotation_storage_logic_unchanged':True,'spanish_files_unchanged':SPAN,'live_verified':False}
if '--audit' in sys.argv:
 h=(R/'history/index.html').read_text();assert h==(R/'docs/history/index.html').read_text()
 embedded=json.loads(re.search(r'<script id="history-data" type="application/json">(.*?)</script>',h,re.S)[1]);assert embedded==d
 assert '60 illustrative situations' in h and 'Four different examples for every word.' in h
 assert '45 illustrative situations' not in h
 proof['history_sha256']=hashlib.sha256(h.encode()).hexdigest();proof['content_audit_passed']=True
 dump('FOUR_SCENARIO_BUILD.json',proof)
 print('FOUR_SCENARIOS_AUDIT_PASS',proof['history_sha256'],flush=True)
else:print('Prepared 1.1.2: 60 scenarios, all 45 published examples preserved, Spanish untouched.',flush=True)
