"""v1.4.1 addendum to the materialized Unit 2 release; safe to run once or repeat."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html';html=p.read_text(encoding='utf-8')
if 'name="app-version" content="1.4.1"' in html:
    print('Places update already applied.');raise SystemExit(0)
assert hashlib.sha256(html.encode()).hexdigest()=='a5b35bcf8fcac3512165a51b672ed0923416969542c49b6b5face2b5b96b7e0f','Baseline changed; inspect first.'
baseline=html
match=re.search(r'(<script id="vocabulary-data" type="application/json">)(.*?)(</script>)',html,re.S)
data=json.loads(match[2]);old_cards=json.loads(json.dumps(data['cards']))
u2=json.loads((ROOT/'src/unit2.json').read_text(encoding='utf-8'));assert len(u2['cards'])==109
source='81068452128__8FC16A2D-B990-4F9D-986E-7FFBBF334FAB.jpeg'
newcats=[dict(id='u2-places',name='Places',spanish='Los lugares',symbol='◎',description='Neighborhood, capital, city, state, country & town',unit='unit2',supplemental=False,count=6,introduced='1.4.1'),dict(id='u2-origin',name='Origin',spanish='El origen',symbol='Aa',description='The printed Mexican-origin sentence',unit='unit2',supplemental=False,count=1,introduced='1.4.1')]
new=[]
for id,en,es in [('neighborhood','neighborhood','el barrio'),('capital','capital','la capital'),('city','city','la ciudad'),('state','state','el estado'),('country','country','el país'),('town','town / village','el pueblo')]:
    new.append(dict(id='u2-place-'+id,category='u2-places',en=en,forms=[es],source=source,note='Use the word printed on the sheet. A matching el or la is optional; país keeps its accent.' if id=='country' else 'Use the word printed on the sheet. A matching el or la is optional.',punctuationOptional=True,introduced='1.4.1'))
new.append(dict(id='u2-origin-mexican',category='u2-origin',en='I am of Mexican origin.',forms=['Soy de origen mexicano.'],source=source,note='Practice the complete printed sentence, including de origen. The final period is optional.',punctuationOptional=True,articleOptional=False,introduced='1.4.1'))
u2['cards']+=new;u2['categories'][7:7]=newcats
u2['description']='Greetings, calendar, weather, classroom, places & origin'
u2['source']='Six textbook photos plus the printed Places / Origin worksheet; app Unit 2'
data['cards']+=new;data['categories'][14:14]=newcats
for unit in data['units']:
    if unit['id']=='unit2':unit['count']=116
assert len(data['cards'])==263 and data['cards'][:256]==old_cards
assert len(u2['cards'])==116 and sum(c['count'] for c in u2['categories'] if not c['supplemental'])==96
html=html[:match.start(2)]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+html[match.end(2):]
def patch(old,new,count=1):
    global html
    assert html.count(old)==count,(old[:90],html.count(old),count);html=html.replace(old,new)
patch('name="app-version" content="1.4.0"','name="app-version" content="1.4.1"')
patch('class="app-version">v1.4.0','class="app-version">v1.4.1')
patch('on the 89 main cards','on the 96 main cards')
patch('Explore all 109 Unit 2 cards, including extras.','Explore all 116 Unit 2 cards, including extras.')
old="  topicMemory[id]=chosen?chosen.filter(c=>possible.some(p=>p.id===c)):possible.filter(c=>!c.supplemental).map(c=>c.id);"
patch(old,old+"""
  // Add new core topics once for a learner who previously selected all core topics.
  // Preserve deliberate single-topic or empty selections and unchecked extras.
  if(id==='unit2' && saved?.settings?.placesRevision!==1 && chosen && possible.filter(c=>!c.supplemental&&!c.introduced).every(c=>chosen.includes(c.id))) {
    topicMemory[id]=[...new Set([...topicMemory[id],...possible.filter(c=>c.introduced==='1.4.1').map(c=>c.id)])];
  }""")
patch('unit:selectedUnit,categoriesByUnit:topicMemory,','unit:selectedUnit,categoriesByUnit:topicMemory,placesRevision:1,')
patch('function save() {','function save() {\n  rememberAchievements();')
patch('];}\nfunction achievementCount()',"].map(a=>({...a,unlocked:a.unlocked||progress.earnedAchievements?.[a.id]===true}));}\nfunction achievementCount()")
patch('function achievementCount(){',"""function rememberAchievements(){
  if(!progress.earnedAchievements || typeof progress.earnedAchievements!=='object' || Array.isArray(progress.earnedAchievements))progress.earnedAchievements={};
  for(const a of achievements())if(a.unlocked)progress.earnedAchievements[a.id]=true;
}
function achievementCount(){""")
patch("unitProgress('unit1');unitProgress('unit2');\nrenderHome();", """unitProgress('unit1');unitProgress('unit2');
// Do not relock an achievement earned before this seven-card expansion.
if(saved && saved.settings?.placesRevision!==1) {
  const earlierCards=unitCards('unit2').filter(c=>c.introduced!=='1.4.1');
  if(earlierCards.length===109 && earlierCards.every(c=>progress.items[c.id]?.seen>0)) {
    if(!progress.earnedAchievements || typeof progress.earnedAchievements!=='object' || Array.isArray(progress.earnedAchievements))progress.earnedAchievements={};
    progress.earnedAchievements.unit2=true;
  }
}
rememberAchievements();
renderHome();""")
ui=(ROOT/'src/units_ui.js').read_text(encoding='utf-8')
assert ui in html
updated=ui.replace('109','116').replace('89','96').replace('six new photos','six textbook photos and the Places / Origin sheet').replace('the six new photos','the six textbook photos and Places / Origin sheet')
updated=updated.replace('<h3>Careful spellings</h3>','<h3>New: places and origin</h3><p>Seven printed entries are included: el barrio, la capital, la ciudad, el estado, el país, el pueblo, and Soy de origen mexicano. Handwritten notes are excluded; El origen is a heading, not an extra vocabulary card.</p><h3>Careful spellings</h3>')
patch(ui,updated);(ROOT/'src/units_ui.js').write_text(updated,encoding='utf-8')
html=html.replace('Main vocabulary and optional extras from your six new photos.','Main vocabulary and optional extras from your Unit 2 pages.')
for name in ['index.html','docs/index.html']:(ROOT/name).write_text(html,encoding='utf-8')
(ROOT/'src/unit2.json').write_text(json.dumps(u2,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['sw.js','docs/sw.js']:
    f=ROOT/name;s=f.read_text(encoding='utf-8');assert "'v1.4.0'" in s;f.write_text(s.replace("'v1.4.0'","'v1.4.1'"),encoding='utf-8')
for name in ['tests/unit2_tests.py','tests/unit2.test.cjs','tests/listening_browser.py','tests/listening_offline.py']:
    f=ROOT/name;s=f.read_text(encoding='utf-8');s=s.replace('1.4.0','1.4.1').replace('109','116').replace('256','263').replace('89','96')
    if name.endswith('unit2_tests.py'):
        s=s.replace("input[name=topic]').count()==9","input[name=topic]').count()==11").replace('count()==7','count()==9')
    if name.endswith('unit2.test.cjs'):s=s.replace('[13,7,32,12,4,12,9,12,8]','[13,7,32,12,4,12,9,6,1,12,8]')
    f.write_text(s,encoding='utf-8')
audit=(ROOT/'UNIT2_AUDIT.md').read_text(encoding='utf-8').replace('v1.4.0','v1.4.1').replace('109 study cards: 89 main cards','116 study cards: 96 main cards')
audit+='\n## Places / Origin addendum\n\nThe additional worksheet contributes exactly seven printed entries; headings and handwriting are excluded. Unit 1 and all earlier Unit 2 card IDs and forms are retained. Country is intentionally available in both units with independent progress.\n\n| English | Spanish | Topic |\n|---|---|---|\n'
audit+='\n'.join('| '+c['en']+' | '+c['forms'][0]+' | '+c['category']+' |' for c in new)+'\n'
audit+='\nSource: '+source+' (transcribed; photo not published). Matching noun articles are optional; país still requires its accent. The origin sentence is tested in full. All three modes and the existing replay rule apply.\n'
(ROOT/'UNIT2_AUDIT.md').write_text(audit,encoding='utf-8')
assert re.findall(r'data:image/webp;base64,[A-Za-z0-9+/=]+',html)==re.findall(r'data:image/webp;base64,[A-Za-z0-9+/=]+',baseline)
print('Built v1.4.1: 7 additions; 116 Unit 2 cards (96 main + 20 extras); old 256 cards and artwork unchanged.')
print('HTML_SHA256_LF',hashlib.sha256(html.encode()).hexdigest())
