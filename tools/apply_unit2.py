"""One-time, assertion-checked migration of the deployed 1.3.0 app to 1.4.0.
Keeps all original vocabulary IDs, artwork, storage keys, modes and hosting paths.
"""
from pathlib import Path
import json,re,hashlib,sys
from unit2_data import build_unit2
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'index.html').read_text(encoding='utf-8')
if 'name="app-version" content="1.4.0"' in source:
    assert (ROOT/'docs/index.html').read_text(encoding='utf-8')==source
    print('Unit 2 already materialized; continuing to validation.');sys.exit(0)
assert hashlib.sha256(source.encode()).hexdigest()=='42aebdb65a1abae447d51972f413dad6c870776a8f45ba8cd73ce8f60722b6ec','Baseline changed: inspect rather than overwrite.'
old_source=source
match=re.search(r'(<script id="vocabulary-data" type="application/json">)(.*?)(</script>)',source,re.S)
old_data=json.loads(match[2]);assert len(old_data['cards'])==147
assert old_data==json.loads((ROOT/'src/data.json').read_text())
u2=build_unit2(old_data)
data={**old_data,'version':2,'units':[{'id':'unit1','name':'Unit 1','count':147},{'id':'unit2','name':'Unit 2','count':109}],'categories':old_data['categories']+u2['categories'],'cards':old_data['cards']+u2['cards']}
source=source[:match.start(2)]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+source[match.end(2):]
def replace(old,new,count=1):
    global source
    found=source.count(old)
    assert found==count,(old[:85],found,count)
    source=source.replace(old,new)
def function(name,text,next_name):
    global source
    start=source.index('function '+name+'(');end=source.index('function '+next_name+'(',start)
    source=source[:start]+text+'\n'+source[end:]
replace('name="app-version" content="1.3.0"','name="app-version" content="1.4.0"')
replace('spelling practice for Unit 1.','spelling practice for Units 1 and 2.')
replace('Made for your first Spanish test.','Made for your Spanish practice. <span class="app-version">v1.4.0</span>')
replace('</style>',(ROOT/'src/units_style.css').read_text()+'\n</style>')
# Extend noun-article handling without changing existing Unit 1 normalization.
core=(ROOT/'src/core.js').read_text()
core=core.replace('  function acceptedAnswers(card) {', '''  function forCard(card, text) {
    const value=normalize(text);
    return card.punctuationOptional ? value.replace(/[¡¿!?.,;:…]+/gu,' ').replace(/\\s+/gu,' ').trim() : value;
  }
  function acceptedAnswers(card) {''')
core=core.replace('.map(normalize);','.map(text=>forCard(card,text));')
core=core.replace("/^(el|la) /u.test(text)","card.articleOptional!==false && /^(el|la|los|las) /u.test(text)")
core=core.replace("text.replace(/^(el|la) /u, '')","text.replace(/^(el|la|los|las) /u, '')")
core=core.replace('const value = normalize(input), answers = acceptedAnswers(card);','const value = forCard(card,input), answers = acceptedAnswers(card);')
old_core=(ROOT/'src/core.js').read_text().strip();assert old_core in source
replace(old_core,core.strip())
# Remember topic selections independently; old preferences become Unit 1 preferences.
insert="""const selectedUnit=['unit1','unit2'].includes(saved?.settings?.unit)?saved.settings.unit:'unit1';
const topicMemory={};
for(const id of ['unit1','unit2']) {
  const possible=DATA.categories.filter(c=>(c.unit||'unit1')===id);
  const stored=saved?.settings?.categoriesByUnit?.[id];
  const legacy=id===selectedUnit && Array.isArray(saved?.settings?.categories)?saved.settings.categories:null;
  const chosen=Array.isArray(stored)?stored:legacy;
  topicMemory[id]=chosen?chosen.filter(c=>possible.some(p=>p.id===c)):possible.filter(c=>!c.supplemental).map(c=>c.id);
}
"""
replace('const settings = {',insert+'const settings = {\n  unit:selectedUnit,categoriesByUnit:topicMemory,')
replace('categories: storedCategories.length ? storedCategories : DATA.categories.map(c=>c.id),','categories: [...topicMemory[selectedUnit]],')
replace('let afterConfirm = null;','let afterConfirm = null;\n'+(ROOT/'src/units_ui.js').read_text())
replace('function save() {','function save() {\n  settings.categoriesByUnit[settings.unit]=[...settings.categories];')
replace('function needsReviewCards() { return CARDS.filter(c=>progress.items[c.id]?.needsReview===true); }','function needsReviewCards() { return unitCards().filter(c=>progress.items[c.id]?.needsReview===true); }')
replace("{id:'all',icon:'👑',name:'Unit 1 Champion',desc:'Explore all 147 cards.',unlocked:explored>=CARDS.length}","{id:'all',icon:'👑',name:'Unit 1 Champion',desc:'Explore all 147 Unit 1 cards.',unlocked:unitCards('unit1').every(c=>progress.items[c.id]?.seen>0)},\n {id:'unit2',icon:'🌻',name:'Unit 2 Explorer',desc:'Explore all 109 Unit 2 cards, including extras.',unlocked:unitCards('unit2').every(c=>progress.items[c.id]?.seen>0)}")
# Home: choose a unit and see only that unit's progress; all old badges survive.
replace('<button class="primary" data-action="start">','${unitSwitcher()}<button class="primary" data-action="start">')
replace("${icon('cards')}147 study cards","${icon('cards')}${unitName()} · ${unitCards().length} cards")
start=source.index('    ${explored?`<section class="progress-card"')
end=source.index('\n  </div>`);',start)
source=source[:start]+'    ${progressPanel()}'+source[end:]
# Setup and word list: no unit mixing, extra rows start unchecked.
replace('<div class="mode-grid" aria-label="Practice mode">','${unitSwitcher()}<div class="mode-grid" aria-label="Practice mode">')
setup_start=source.index('function renderSetup(');setup_end=source.index('function eligibleCards(',setup_start)
setup=source[setup_start:setup_end]
setup=setup.replace('DATA.categories.length','unitCategories().length').replace('DATA.categories.map(c=>','unitCategories().map(c=>')
setup=setup.replace('name="topic" value="${c.id}"','name="topic" data-extra="${!!c.supplemental}" value="${c.id}"')
setup=setup.replace('<div class="setup-options">',"${settings.unit==='unit2'?'<p class=\"topic-extra-note\">The two “Extra” topics are optional phrases and map labels from these pages. Leave them unchecked to focus on the 89 main cards.</p>':''}<div class=\"setup-options\">")
source=source[:setup_start]+setup+source[setup_end:]
replace('function eligibleCards() {return CARDS.filter','function eligibleCards() {return unitCards().filter')
replace("session={mode:overrideMode||settings.mode,cards,", "session={unit:settings.unit,mode:overrideMode||settings.mode,cards,")
replace('function categoryPill(card) { return `<span class="pill">${e(categoryName(card))}</span>`; }','function categoryPill(card) { return `<span class="pill">${unitName(unitOf(card))} · ${e(categoryName(card))}</span>`; }')
replace('${card.number?', '${card.number!==undefined?',2)
replace("  view='results';progress.rounds++;", """  const up=unitProgress(session.unit);up.rounds=(Number(up.rounds)||0)+1;
  if(session.responses.every(r=>r.correct))up.perfectRounds=(Number(up.perfectRounds)||0)+1;
  if(session.mode==='listening'){up.listeningRounds=(Number(up.listeningRounds)||0)+1;up.lastListening={correct:session.responses.filter(r=>r.correct).length,total:session.cards.length};}
  if(session.mode==='quiz')up.lastQuiz={correct:session.responses.filter(r=>r.correct).length,total:session.cards.length};
  view='results';progress.rounds++;""")
# Keep complete sentence starters intact while optional articles apply to vocabulary nouns.
source=source.replace('el / la is optional.','el / la / los / las is optional.').replace('El / la is optional.','El / la / los / las is optional.')
replace('<div class="wordlist-tools">','${unitSwitcher()}<div class="wordlist-tools">')
replace('Your Unit 1 word collection','Your ${unitName()} word collection')
replace('Every printed entry from your five vocabulary photos.','${settings.unit===\'unit2\'?\'Main vocabulary and optional extras from your six new photos.\':\'The original 147 entries from your five vocabulary photos.\'}')
replace('${DATA.categories.map(c=>`<option value="${c.id}">','${unitCategories().map(c=>`<option value="${c.id}">')
replace('const matches=CARDS.filter(c=>','const matches=unitCards().filter(c=>')
replace('`${matches.length} of ${CARDS.length} entries`','`${matches.length} of ${unitCards().length} entries · ${unitName()}`')
replace("function openAbout() {", "function openAbout() {\n  if(settings.unit==='unit2'){aboutUnit2();return;}")
replace('${DATA.categories.map(c=>`<tr>','${unitCategories(\'unit1\').map(c=>`<tr>')
replace("case 'start':goSetup();break;","case 'start':goSetup();break;\n    case 'unit':switchUnit(button.dataset.unit);break;")
replace("case 'toggle-topics':settings.categories=settings.categories.length===DATA.categories.length?[]:DATA.categories.map(c=>c.id);", "case 'toggle-topics':settings.categories=settings.categories.length===unitCategories().length?[]:unitCategories().map(c=>c.id);")
replace("b.textContent=settings.categories.length===DATA.categories.length?'Clear selection':'Select all topics';","b.textContent=settings.categories.length===unitCategories().length?'Clear selection':'Select all topics';")
replace("This clears the saved practice counts and tricky-word list on this device,", "This clears the saved practice counts and tricky-word lists for BOTH units on this device,")
replace('renderHome();\n})();','unitProgress(\'unit1\');unitProgress(\'unit2\');\nrenderHome();\n})();')
assert 'elena' not in source.lower()
# Existing artwork and every old data object must survive byte-for-byte / field-for-field.
assert re.findall(r'data:image/webp;base64,[A-Za-z0-9+/=]+',source)==re.findall(r'data:image/webp;base64,[A-Za-z0-9+/=]+',old_source)
assert data['cards'][:147]==old_data['cards'] and data['categories'][:7]==old_data['categories']
hint_start=source.index('<p class="answer-hint" id="answer-hint">')
hint_end=source.index('</p>',hint_start)
source=source[:hint_start]+'<p class="answer-hint" id="answer-hint">${answerHint(card)}'+source[hint_end:]
for p in ['index.html','docs/index.html']:(ROOT/p).write_text(source,encoding='utf-8')
(ROOT/'src/core.js').write_text(core,encoding='utf-8')
(ROOT/'src/unit2.json').write_text(json.dumps(u2,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in ['sw.js','docs/sw.js']:
    s=(ROOT/p).read_text();assert "'v1.3.0'" in s;(ROOT/p).write_text(s.replace("'v1.3.0'","'v1.4.0'"))
for p in ['tests/listening_browser.py','tests/listening_offline.py']:
    s=(ROOT/p).read_text();(ROOT/p).write_text(s.replace("'1.3.0'","'1.4.0'"))
# Clear audit: scope, source pages, grouped alternatives and deliberate exclusions.
lines=['# Unit 2 vocabulary audit — app v1.4.0','','Source: the six supplied textbook photos. “Unit 2” is the requested app label; the photographed book says Unidad 0.','','109 study cards: 89 main cards selected by default, plus 20 optional date/question and map-label cards. Original Unit 1 remains unchanged (147 cards). All three modes are available.','','## Scope notes','','- Same-meaning expressions share a card: 16 greeting/farewell expressions occupy 13 cards.','- Numbers are exactly 0–31. Number 21 shows all three printed forms with grammatical context.','- Weather includes 10 condition prompts (two with alternative phrases), plus the printed infinitives nevar and llover.','- las tijeras remains plural. el marcador is translated marker / highlighter to match the picture.','- Sentence starters are quizzed only as the visible phrase; ellipses do not request private/personal answers.','- The printed example Hoy es 31 de diciembre is expanded to number words for spelling/audio practice.','- Map labels add el for noun practice; it is optional. ecuador is the equator in this context, not the country.','- No unheard exercise answers, hidden pages, missing holiday dates, country lists, textbook photos, or personal notes were added. The Halloween event caption is not a Spanish vocabulary target.','','## Grading','','Unit 1 grading is retained. Unit 2 ignores punctuation, not accents or letters. Correct noun articles el/la/los/las are optional, but wrong articles are rejected. Sentence starters keep their grammatical articles. Listen & Spell grades the exact form spoken and retains one initial listen plus three replays.','','## Reference checks','','- https://www.rae.es/dpd/uno — agreement and apocope, including veintiún and veintiuna.','- https://www.rae.es/dpd/tijera — tijera / tijeras.','','## Complete transcription']
for cat in u2['categories']:
    lines+=['','### '+cat['name']+' — '+str(cat['count'])+' cards','','| English prompt | Spanish forms | Source |','|---|---|---|']
    lines += ['| '+c['en']+' | '+' / '.join(c['forms'])+' | '+c['source']+' |' for c in u2['cards'] if c['category']==cat['id']]
(ROOT/'UNIT2_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Built v1.4.0: 147 unchanged Unit 1 cards + 109 Unit 2 cards; artwork preserved.')
print('HTML SHA256',hashlib.sha256(source.encode()).hexdigest())
