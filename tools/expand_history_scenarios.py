"""Expand 30 scenarios to 45; keep existing examples, term IDs and learner storage.
Run once against the released 1.1.0 source, then use tools/build_history.py.
"""
from pathlib import Path
import copy,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='4be9257df1a506c749b96396469fffcbcb2f113a'
THIRD={
 'caliphate':{
  'text':'Officials in several cities report to a ruler called a caliph, who claims leadership of the Muslim community as well as political authority. What term describes the larger state those cities belong to?',
  'why':'The state is a caliphate because it is ruled by a caliph. A city within that state is not an independent city-state simply because it has local officials.'},
 'christianity':{
  'text':'A museum visitor reads a Gospel passage about Jesus and sees an exhibit explaining belief in his resurrection. The guide says these beliefs unite many different churches. Which religion connects the exhibit?',
  'why':'The focus on Jesus Christ and his resurrection points to Christianity. Different churches can share this central religious identity without having identical practices.'},
 'city-state':{
  'text':'A harbor city makes its own treaty with a neighboring country and governs the countryside around its port. It answers to no larger national government. What kind of political unit is the city and its territory?',
  'why':'The city and its surrounding land form an independent city-state. Making its own decisions as a state, rather than simply having a busy port, is the important clue.'},
 'caravan':{
  'text':'Before crossing a mountain pass, a guide brings several merchants together with their loaded mules. The people and animals will make the long journey as one group. What term names that group?',
  'why':'The travelers and pack animals form a caravan. The animals can be mules rather than camels; the defining feature is the group traveling together, not a particular animal or landscape.'},
 'feudalism':{
  'text':'In a medieval-history simulation, a knight is called to provide military service to a lord. The knight holds land rights in return for this service and loyalty. Which system explains the obligation?',
  'why':'The land rights and the promise of loyal service illustrate the lord-vassal relationships associated with feudalism. This is a simplified classroom example, not a rule for every medieval society.'},
 'silk-road':{
  'text':'For a class project, a student traces how craft techniques and religious ideas spread through trading towns between Asia, the Middle East, and Europe. Which connected trade network should the project identify?',
  'why':'The Silk Road connected trading communities and helped carry ideas and techniques as well as goods. The question asks for the network, not the people traveling in a caravan.'},
 'black-plague':{
  'text':'In a history simulation set in the mid-1300s, many towns lose large numbers of residents during a widespread plague pandemic. The class must name the event behind this population decline. Which term fits?',
  'why':'The time period and devastating plague pandemic identify the Black Plague, also called the Black Death. This is an illustrative simulation of the event, not a claim about one particular town.'},
 'daoism':{
  'text':'A learner wants every plan to follow their wishes. A teacher drawing on Laozi instead asks them to observe natural patterns and live in harmony with the Way. Which Chinese tradition guides this advice?',
  'why':'Laozi and harmony with the Dao, or Way, are specific clues for Daoism. The advice illustrates the tradition without claiming that simply enjoying nature makes someone a follower.'},
 'islam':{
  'text':'During a school visit, a community member explains that they read the Quran, worship Allah alone, and follow Muhammad as a prophet rather than a god. Which religion are they describing?',
  'why':'The Quran, worship of one God, and Muhammad as a prophet identify Islam. The question is about the religion, not a political institution such as a caliphate.'},
 'luxury-goods':{
  'text':'A household already has everyday dishes but spends much more on an ornate gold cup to impress guests. The purchase is mainly for beauty and status rather than a basic need. Which category best describes it?',
  'why':'The cup is an example of luxury goods because its special value here is beauty and status, not meeting a basic need. The situation explains why this particular purchase is a luxury.'},
 'jihad':{
  'text':'A Muslim learner keeps setting aside distractions to study their faith and live according to God\u2019s guidance. They describe this sustained effort as striving in God\u2019s path. Which word names the effort?',
  'why':'This religious striving is an example of jihad in its spiritual sense. The term can have other meanings in different historical and legal contexts; this scenario concerns learning and faithful living.'},
 'dynasty':{
  'text':'In a fictional kingdom, power passes from a queen to her son and later to her granddaughter. A historian groups their reigns together because all three belong to the same ruling family. What is that line of rulers called?',
  'why':'A succession of rulers from the same family forms a dynasty. The family connection across reigns matters, rather than any single ruler\u2019s wealth or achievements.'},
 'confucianism':{
  'text':'An official studying Confucius tries to govern honestly, care for family responsibilities, and set a good moral example for others. Which tradition connects the official\u2019s public conduct and family duties?',
  'why':'Confucianism emphasizes moral conduct and responsibilities within family and society. Confucius is the specific clue; honesty or family care alone would not identify just one tradition.'},
 'meritocracy':{
  'text':'A school awards a scholarship using demonstrated skills and achievement. The judges assess the work without giving preference to famous parents or influential friends. Which principle is the selection meant to follow?',
  'why':'Choosing by ability and achievement illustrates the ideal of meritocracy. It contrasts with inherited advantages or personal connections, although this example does not prove that every applicant had equal opportunities.'},
 'buddhism':{
  'text':'At a study group, a learner asks how to respond to suffering without harming others. The group turns to the Buddha\u2019s teachings and a path of ethical action and wisdom toward liberation. Which tradition guides the discussion?',
  'why':'The Buddha\u2019s teachings about suffering and liberation identify Buddhism. The scenario applies those teachings to a learner\u2019s concern rather than treating meditation as the tradition\u2019s only practice.'}
}

def replace_file(name,pairs):
 p=ROOT/name;s=p.read_text(encoding='utf-8')
 for a,b in pairs:
  assert a in s,(name,'expected text missing',a)
  s=s.replace(a,b)
 p.write_text(s,encoding='utf-8')

p=ROOT/'history-src/data.json';data=json.loads(p.read_text(encoding='utf-8'))
if data['version']=='1.1.1':
 assert all(len(c['scenarios'])==3 and c['scenarios'][2]==THIRD[c['id']] for c in data['cards'])
 print('Three-scenario source already materialized.');raise SystemExit(0)
assert data['version']=='1.1.0'
old=copy.deepcopy(data)
scenarios=json.loads((ROOT/'history-src/scenarios.json').read_text(encoding='utf-8'))
assert set(THIRD)=={c['id'] for c in data['cards']} and len(data['cards'])==15
for c in data['cards']:
 assert len(c['scenarios'])==2 and c['scenarios']==scenarios[c['id']]
 c['scenarios'].append(THIRD[c['id']]);scenarios[c['id']]=c['scenarios']
data['version']='1.1.1'
for previous,current in zip(old['cards'],data['cards']):
 check=copy.deepcopy(current);check['scenarios']=check['scenarios'][:2];assert check==previous
assert data['sources']==old['sources'] and data['categories']==old['categories']
assert len({s['text'] for c in data['cards'] for s in c['scenarios']})==45
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'history-src/scenarios.json').write_text(json.dumps(scenarios,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
replace_file('history-src/app.js',[
 ('New · 30 illustrative situations','45 illustrative situations'),
 ('Two different examples for every word.','Three different examples for every word.'),
 ('New rounds alternate between two examples per term.','New rounds cycle through three examples per term.'),
 ('own 30 illustrative situations, two per term','own 45 illustrative situations, three per term')])
for name in ['history-src/shell.html','history-src/sw.js']:
 replace_file(name,[('1.1.0','1.1.1')])
# Assertions of the current release change; old release fixtures remain historical.
for name in ['tests/history.test.cjs','tests/history_scenarios.test.cjs','tests/history_browser.py','tests/history_scenarios.py','tests/history_backup.py','tests/history_scenario_upgrade.py']:
 p=ROOT/name;s=p.read_text(encoding='utf-8');s=s.replace('1.1.0','1.1.1');p.write_text(s,encoding='utf-8')
replace_file('tests/history_scenarios.test.cjs',[
 ('have two distinct situations','have three distinct situations'),
 ('c.scenarios.length,2','c.scenarios.length,3'),
 ('new Set(prompts).size,30','new Set(prompts).size,45')])
replace_file('tests/history_scenarios.py',[
 ("expect(p.locator('.scenario-example')).to_have_count(2)","expect(p.locator('.scenario-example')).to_have_count(3)"),
 ('for roundno in range(2):','for roundno in range(3):'),
 ("if roundno==0:tap(p,'[data-action=again-round]')","if roundno<2:tap(p,'[data-action=again-round]')"),
 ('set(v)=={0,1}','set(v)=={0,1,2}'),
 ("prog['rounds']==2 and prog['perfect']==2","prog['rounds']==3 and prog['perfect']==3"),
 ("v['meaning']==2 and v['spelling']==0 and v['correct']==2","v['meaning']==3 and v['spelling']==0 and v['correct']==3")])
# Force the third variant in the existing full backup/restore + pause/resume test.
replace_file('tests/history_scenarios.py',[("def resume_and_backup(p):\n start(p,'5');", "def resume_and_backup(p):\n legacy={'schema':1,'settings':{'mode':'scenario','length':'5','topics':['power','belief','exchange']},'progress':{'items':{},'rounds':0,'perfect':0,'earned':{}},'session':None,'lastOrder':[],'scenarioLast':{id:1 for id in BY}}\n seed_next_load(p,legacy,'seed-third-backup');start(p,'5');assert all(x['scenarioIndex']==2 for x in db(p)['session']['questions']);")])
# Keep the original 1.0 upgrade test and add an installed 1.1 upgrade with the same cache checks.
s=(ROOT/'tests/history_scenario_upgrade.py').read_text(encoding='utf-8')
s=s.replace("BASE='2f5a9fac5b193ff4821bcad748b7a6c08fa58ed4'",f"BASE='{BASE}'")
s=s.replace("to_have_attribute('content','1.0.0')","to_have_attribute('content','1.1.0')")
s=s.replace("OUT/'upgrade.json'","OUT/'three-scenarios-upgrade.json'")
s=s.replace('installed History 1.0 -> 1.1','installed History 1.1.0 -> 1.1.1 (45 scenarios)')
(ROOT/'tests/history_three_scenario_upgrade.py').write_text(s,encoding='utf-8')
replace_file('HISTORY_README.md',[
 ('1.1.0','1.1.1'),('30 original illustrative situations: two for each term','45 original illustrative situations: three for each term'),
 ('alternate the example used for a term on later rounds','cycle through all three examples for a term on later rounds'),
 ('Candidate validation run 41558560290 passed all stages before release.','The three-scenario release is gated on all 45 examples, three-round rotation, legacy saves, third-example backup/restore, and the installed 1.1.0-to-1.1.1 offline upgrade.')])
# Prove the question rotation was not hardcoded to two and no Spanish files changed.
app=(ROOT/'history-src/app.js').read_text(encoding='utf-8')
assert '(last+1)%c.scenarios.length' in app and "STORE='alaina-history-studio-v1'" in app
for f in ['index.html','docs/index.html','src/core.js','src/data.json','src/unit2.json','sw.js','docs/sw.js']:
 assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show',BASE+':'+f],cwd=ROOT),f
print('Expanded to 45 scenarios: all 15 terms have 3; the original 30 and all definitions/sources are unchanged.')
