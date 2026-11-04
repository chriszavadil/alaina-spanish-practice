"""Append two situations per term; preserve original content, grading and storage."""
from pathlib import Path
import copy,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];BASE='4be9257df1a506c749b96396469fffcbcb2f113a'
def read_old(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT).decode('utf-8')
def edit(path,old,new,count=None):
 p=ROOT/path;s=p.read_text(encoding='utf-8');n=s.count(old)
 assert n>0 and (count is None or n==count),(path,old,n,count)
 p.write_text(s.replace(old,new),encoding='utf-8')
def dump(path,value):(ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
original=json.loads(read_old('history-src/data.json'));assert original['version']=='1.1.0'
p=ROOT/'history-src/data.json';data=json.loads(p.read_text(encoding='utf-8'))
if data['version']=='1.1.1':
 assert len(data['cards'])==15 and all(len(c['scenarios'])==4 for c in data['cards'])
 print('Expansion already materialized.');raise SystemExit(0)
assert data==original,'Source changed; inspect instead of overwriting.'
additions=json.loads((ROOT/'history-src/scenario_additions_1_1_1.json').read_text(encoding='utf-8'))
assert set(additions)=={c['id'] for c in data['cards']} and all(len(v)==2 for v in additions.values())
scenarios=json.loads((ROOT/'history-src/scenarios.json').read_text(encoding='utf-8'))
for c in data['cards']:
 assert c['scenarios']==scenarios[c['id']] and len(c['scenarios'])==2
 for item in additions[c['id']]:
  assert set(item)=={'text','why'} and len(item['text'])>80 and len(item['why'])>50
  assert c['term'].lower() not in item['text'].lower(),c['id']
 c['scenarios']+=copy.deepcopy(additions[c['id']]);scenarios[c['id']]=c['scenarios']
assert len({s['text'] for c in data['cards'] for s in c['scenarios']})==60
for old,c in zip(original['cards'],data['cards']):
 assert c['scenarios'][:2]==old['scenarios']
 assert {k:v for k,v in c.items() if k!='scenarios'}=={k:v for k,v in old.items() if k!='scenarios'}
data['version']='1.1.1';dump('history-src/data.json',data);dump('history-src/scenarios.json',scenarios)
# Version and visible counts only. The selection/rotation/persistence code is unchanged.
for name in ['history-src/shell.html','history-src/sw.js']:
 p=ROOT/name;s=p.read_text(encoding='utf-8');assert '1.1.0' in s,name;p.write_text(s.replace('1.1.0','1.1.1'),encoding='utf-8')
edit('history-src/app.js','30 illustrative situations','60 illustrative situations')
edit('history-src/app.js','Two different examples for every word.','Four different examples for every word.',1)
edit('history-src/app.js','Two illustrative situations showing this word in context.','Four illustrative situations showing this word in context.',1)
edit('history-src/app.js','two per term','four per term',1)
# Existing tests continue to check all scenarios instead of sampling only two.
for p in (ROOT/'tests').glob('history*'):
 if p.suffix not in ['.py','.cjs'] or p.name=='history_scenario_upgrade.py':continue
 s=p.read_text(encoding='utf-8');p.write_text(s.replace('1.1.0','1.1.1'),encoding='utf-8')
edit('tests/history_scenarios.test.cjs','two distinct situations','four distinct situations',1)
edit('tests/history_scenarios.test.cjs','c.scenarios.length,2','c.scenarios.length,4',1)
edit('tests/history_scenarios.test.cjs','new Set(prompts).size,30','new Set(prompts).size,60',1)
edit('tests/history_scenarios.py',"to_have_count(2)","to_have_count(4)",1)
edit('tests/history_scenarios.py','range(2):','range(4):',2)
# The retry loop still has two missed terms, so do not expand that loop.
edit('tests/history_scenarios.py','for i in range(4):right(p);nextq(p)','for i in range(2):right(p);nextq(p)',1)
edit('tests/history_scenarios.py',"if roundno==0:tap(p,'[data-action=again-round]')","if roundno<3:tap(p,'[data-action=again-round]')",1)
edit('tests/history_scenarios.py','all(set(v)=={0,1} for v in seen.values())','all(len(v)==4 and set(v)=={0,1,2,3} for v in seen.values())',1)
edit('tests/history_scenarios.py',"prog['rounds']==2 and prog['perfect']==2","prog['rounds']==4 and prog['perfect']==4",1)
edit('tests/history_scenarios.py',"v['meaning']==2 and v['spelling']==0 and v['correct']==2","v['meaning']==4 and v['spelling']==0 and v['correct']==4",1)
edit('tests/history_scenarios.py',"def resume_and_backup(p):\n start(p,'5');", "def resume_and_backup(p):\n initial=db(p) or {};initial['scenarioLast']={id:2 for id in BY};seed_next_load(p,initial,'fourth-variant-resume')\n start(p,'5');",1)
edit('tests/history_scenarios.py',"snapshot=db(p)['session'];tap", "snapshot=db(p)['session'];assert all(x['scenarioIndex']==3 for x in snapshot['questions']);tap",1)
# Exercise a real installed 1.1.0 -> 1.1.1 update, retaining the old 1.0 test for history.
s=read_old('tests/history_scenario_upgrade.py')
s=s.replace("BASE='2f5a9fac5b193ff4821bcad748b7a6c08fa58ed4'","BASE='"+BASE+"'")
s=s.replace('1.1.0','1.1.1').replace('1.0.0','1.1.0').replace('History 1.0 -> 1.1','History 1.1.0 -> 1.1.1')
(ROOT/'tests/history_expansion_upgrade.py').write_text(s,encoding='utf-8')
# Keep the earlier 1.0 -> current upgrade test useful too.
p=ROOT/'tests/history_scenario_upgrade.py';p.write_text(p.read_text(encoding='utf-8').replace('1.1.0','1.1.1'),encoding='utf-8')
# Update current usage documentation, not historical release records.
p=ROOT/'HISTORY_README.md';s=p.read_text(encoding='utf-8').replace('1.1.0','1.1.1')
s=s.replace('30 original illustrative situations: two for each term','60 original illustrative situations: four for each term').replace('30-scenario collection','60-scenario collection')
s=s.replace('alternate the example used for a term on later rounds','cycle through four examples for each term across later rounds')
s=s.replace('Candidate validation run 41558560290 passed all stages before release. The public-release workflow separately verifies the exact deployed HTML and runs history, scenario and Spanish browser suites.','The expansion keeps all 30 previous scenarios and adds two per term, bringing the total to 60. Candidate tests exercise four complete rounds, fourth-example resume/backup, existing modes, and installed-app upgrades. The public-release workflow verifies the exact deployed HTML and reruns history, scenario and Spanish browser suites.')
p.write_text(s,encoding='utf-8')
# Verify every original Spanish runtime asset remains identical.
spanish=['index.html','docs/index.html','src/core.js','src/data.json','src/unit2.json','sw.js','docs/sw.js','manifest.webmanifest','docs/manifest.webmanifest']
for f in spanish:assert (ROOT/f).read_text(encoding='utf-8')==read_old(f),f
proof={'version':'1.1.1','baseline':BASE,'terms':15,'previous_scenarios_preserved':30,'scenarios_added':30,'scenarios_per_term':4,'total_scenarios':60,'history_storage_key':'alaina-history-studio-v1','rotation_logic_changed':False,'spanish_assets_unchanged':spanish,'live_verified':False}
dump('SCENARIO_EXPANSION_BUILD.json',proof)
lines=['# Scenario expansion: History Studio 1.1.1','','Two additional scenarios for each of 15 terms: four per term, 60 total. All 30 previous examples and explanations remain unchanged.','','The new situations are original illustrative teaching examples, not historical quotations or a teacher answer key. Each one uses the term\'s existing sourced definition and a matching explanation. Sources remain available on each card.','','## Learning and saved progress','','Scenario Practice cycles through all four variants across rounds; 5/10/All still selects a number of terms, not all 60 scenarios in one round. Word list > Scenario examples shows all four together. Existing card IDs, definitions, aliases, topics, grading logic, storage key, achievements and saved-round schema are unchanged. No Spanish files are edited.','','## Added examples']
for c in data['cards']:
 lines+=['','### '+c['term']]
 for i,item in enumerate(c['scenarios'][2:],3):lines+=['',str(i)+'. '+item['text'],'','Matching term: **'+c['term']+'**. '+item['why']]
(ROOT/'SCENARIO_EXPANSION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Expanded to 60 scenarios: 15 terms x 4. Original content and Spanish assets preserved.')
