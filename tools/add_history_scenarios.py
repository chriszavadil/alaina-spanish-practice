"""Assertion-checked 1.0.0 -> 1.1.0 scenario section. Spanish files are never edited."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'history-src'
p=SRC/'app.js';s=p.read_text(encoding='utf-8')
if "['scenario','Scenario Practice'" in s:
 print('Scenario source already applied.');raise SystemExit(0)
assert hashlib.sha1(b'blob '+str(len(s.encode())).encode()+b'\0'+s.encode()).hexdigest()=='704b0ac2bc4558e22e2c1cc80607ad26b47e8033','History app changed; reconcile instead of overwriting.'
def change(a,b,count=1):
 global s
 assert s.count(a)==count,(a[:100],s.count(a),count)
 s=s.replace(a,b)
change("['type','Recall Challenge'", "['scenario','Scenario Practice','Read a situation. Choose the matching term.','book'],['type','Recall Challenge'")
change("session:null,lastOrder:[]", "session:null,lastOrder:[],scenarioLast:{}")
change("function integer(x)", "function isChoice(mode){return mode==='choice'||mode==='scenario';}\nfunction scenarioIndex(card,value){return Number.isInteger(value)&&value>=0&&value<card.scenarios.length?value:0;}\nfunction situation(card,question){return card.scenarios[scenarioIndex(card,question?.scenarioIndex)];}\nfunction integer(x)")
change(" if(Array.isArray(raw.lastOrder))", " for(const c of CARDS)if(Number.isInteger(raw.scenarioLast?.[c.id])&&raw.scenarioLast[c.id]>=0&&raw.scenarioLast[c.id]<c.scenarios.length)out.scenarioLast[c.id]=raw.scenarioLast[c.id];\n if(Array.isArray(raw.lastOrder))")
change("({scenario:!!x?.scenario,options:", "({scenario:!!x?.scenario,scenarioIndex:scenarioIndex(BY.get(q.ids[i]),x?.scenarioIndex),options:")
change("({scenario:false,options:", "({scenario:false,scenarioIndex:0,options:")
change("session().mode==='choice'||session().mode==='type'", "isChoice(session().mode)||session().mode==='type'")
change('Answer a meaning or recall question correctly twice for every term.', 'Answer meaning, scenario, or recall questions correctly twice for every term.')
change('4 ways to practice','5 ways to practice')
change('two correct Meaning Quiz or Recall Challenge answers per term.', 'two correct Meaning Quiz, Scenario Practice, or Recall Challenge answers per term.')
change(' <section class="dashboard">', ''' <section class="scenario-feature"><div><p class="eyebrow">New · 30 illustrative situations</p><h2>Which word fits the story?</h2><p>Read a situation, choose the term, and find out why it fits. Two different examples for every word.</p></div>${button('scenario-setup','Scenario Practice '+icon('arrow'),'secondary')}</section>
 <section class="dashboard">''')
change("db.settings.mode==='listen'?'English audio:", "db.settings.mode==='scenario'?'Read the illustrative situation and choose the term it demonstrates. Check your answer to see why it fits. New rounds alternate between two examples per term.':db.settings.mode==='listen'?'English audio:")
change("questions:chosen.map(id=>({scenario:Math.random()<.5,options:options(BY.get(id),CARDS)}))", "questions:chosen.map(id=>{const c=BY.get(id);let variant=0;if(mode==='scenario'){const last=db.scenarioLast[id];variant=Number.isInteger(last)?(last+1)%c.scenarios.length:Math.floor(Math.random()*c.scenarios.length);db.scenarioLast[id]=variant;}return {scenario:Math.random()<.5,scenarioIndex:variant,options:options(c,CARDS)};})")
# Existing Meaning Quiz questions keep their original wording and saved prompt flag.
change("q.mode==='choice'?'WHICH TERM FITS?':'CAN YOU NAME THE TERM?'", "q.mode==='scenario'?'READ THE SITUATION — WHICH TERM FITS?':q.mode==='choice'?'WHICH TERM FITS?':'CAN YOU NAME THE TERM?'")
change("e(q.mode==='choice'&&q.questions[q.index].scenario?c.scenario:c.definition)", "e(q.mode==='scenario'?situation(c,q.questions[q.index]).text:q.mode==='choice'&&q.questions[q.index].scenario?c.scenario:c.definition)")
change("let body=prompt;", "let body=prompt+(q.mode==='scenario'?'<p class=\"note scenario-note\">Illustrative learning scenario—not a quotation or a report of a specific event.</p>':'');")
# Shared choice controls and grading; no changes to typed/listening grading.
change("${q.mode==='choice'?`<div class=\"choice-list\"", "${isChoice(q.mode)?`<div class=\"choice-list\"")
change("q.mode==='choice'?(q.selected?", "isChoice(q.mode)?(q.selected?")
change("const typed=q.mode==='choice'?", "const typed=isChoice(q.mode)?")
change("q.input=q.mode==='choice'?'':typed", "q.input=isChoice(q.mode)?'':typed")
change("let result=q.mode==='choice'?", "let result=isChoice(q.mode)?")
change("textContent=q.mode==='choice'?'Choose", "textContent=isChoice(q.mode)?'Choose")
change("answer:q.mode==='choice'?", "answer:isChoice(q.mode)?")
change("function feedbackHTML(c,r)", '''function scenarioExplanation(c,question){const item=situation(c,question);return `<div class="scenario-explanation"><h3>Why this term fits</h3><p>${e(item.why)}</p></div>`;}
function scenarioExamples(c){return `<details class="scenario-examples"><summary>Scenario examples → ${e(c.term)}</summary><p class="note">Two illustrative situations showing this word in context.</p>${c.scenarios.map(item=>`<div class="scenario-example"><p>${e(item.text)}</p><p><strong>Matching term: ${e(c.term)}</strong></p><p class="note">${e(item.why)}</p></div>`).join('')}</details>`;}
function feedbackHTML(c,r)''')
change('<div class="answer-term">${e(c.term)}</div><p class="definition">', '<div class="answer-term">${e(c.term)}</div>${session().mode===\'scenario\'?scenarioExplanation(c,session().questions[session().index]):\'\'}<p class="definition">')
change('${e(c.note)}</p></div><details>', '${e(c.note)}</p></div>${scenarioExamples(c)}<details>')
change('<p class="definition">${e(c.definition)}</p></article>`;}).join', '<p class="definition">${e(c.definition)}</p>${q.mode===\'scenario\'?`<p class="review-scenario">${e(situation(c,q.questions[q.ids.indexOf(r.id)]).text)}</p>${scenarioExplanation(c,q.questions[q.ids.indexOf(r.id)])}`:\'\'}</article>`;}).join')
change("case 'setup':setup();break;", "case 'setup':setup();break;case 'scenario-setup':db.settings.mode='scenario';save();setup();break;")
change('Meaning Quiz uses definitions and short situations. Recall Challenge uses definitions.', 'Scenario Practice has its own 30 illustrative situations, two per term, with explanations after checking. Scenario examples are also available in the Word list and on revealed flashcards. Meaning Quiz keeps its original mix; Recall Challenge uses definitions.')
p.write_text(s,encoding='utf-8')
data=json.loads((SRC/'data.json').read_text());extra=json.loads((SRC/'scenarios.json').read_text());assert set(extra)=={c['id'] for c in data['cards']}
for c in data['cards']:
 assert len(extra[c['id']])==2 and all(set(x)=={'text','why'} and x['text'] and x['why'] for x in extra[c['id']])
 c['scenarios']=extra[c['id']]
data['version']='1.1.0';(SRC/'data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['shell.html','sw.js']:
 p=SRC/name;t=p.read_text();assert '1.0.0' in t;p.write_text(t.replace('1.0.0','1.1.0'),encoding='utf-8')
p=SRC/'style.css';p.write_text(p.read_text()+'''\n/* Dedicated scenario section; uses the established history palette. */
.scenario-feature{display:flex;align-items:center;justify-content:space-between;gap:22px;padding:24px;background:var(--mint);border:1px solid var(--line);border-radius:var(--radius);margin:24px 0}
.scenario-feature h2{font:700 27px/1.2 Georgia,serif;margin:0 0 10px}.scenario-feature p:not(.eyebrow){font-size:14px;margin:0;max-width:480px}.scenario-feature .secondary{flex-shrink:0}
.mode[data-mode=scenario]{grid-column:1/-1;min-height:130px;border-color:var(--green)}.mode[data-mode=scenario] p{max-width:none}
.scenario-note{font-size:11px;margin:-10px 0 20px}.scenario-explanation{margin:16px 0;padding:16px;border-left:3px solid var(--green);background:var(--card);border-radius:0 10px 10px 0}.scenario-explanation h3{font-size:15px;margin:0 0 7px}.scenario-explanation p{margin:0;font-size:15px;line-height:1.55}.scenario-example{margin-top:14px;padding-top:14px;border-top:1px solid var(--line)}.scenario-example p{font-size:14px;line-height:1.6}.review-scenario{font-size:15px;border-top:1px solid var(--line);padding-top:12px}
@media(max-width:700px){.scenario-feature{flex-direction:column;align-items:stretch;padding:20px}.scenario-feature .secondary{width:100%}.scenario-feature h2{font-size:25px}.mode[data-mode=scenario]{min-height:125px}.practice .topline h1{overflow-wrap:anywhere}}
''',encoding='utf-8')
p=ROOT/'tests/history_browser.py';t=p.read_text();t=t.replace(".count()==4;assert p.locator('input[name=topic]", ".count()==5;assert p.locator('input[name=topic]")
t=t.replace("to_have_attribute('content','1.0.0')", "to_have_attribute('content','1.1.0')");p.write_text(t,encoding='utf-8')
# Verify the public version dynamically rather than freezing the first release in CI.
p=ROOT/'tools/verify_history_live.py'
if p.exists():
 t=p.read_text().replace("proof=json.loads((ROOT/'HISTORY_BUILD.json').read_text())", "proof=json.loads((ROOT/'HISTORY_BUILD.json').read_text())\nVERSION=json.loads((ROOT/'history-src/data.json').read_text())['version']")
 t=t.replace("H+'?v=1.0.0'", "H+'?v='+VERSION").replace("'history_version':'1.0.0'", "'history_version':VERSION")
 t=t.replace("[sys.executable,'tests/listening_browser.py'", "[sys.executable,'tests/history_scenarios.py','--url',H+'?v='+VERSION],[sys.executable,'tests/listening_browser.py'")
 t=t.replace('history_browser_groups_passed=18,spanish_regression_groups_passed=14','history_browser_groups_passed=18,scenario_browser_groups_passed=12,spanish_regression_groups_passed=14');p.write_text(t,encoding='utf-8')
print('Scenario Practice added: 30 scenarios, 15 unchanged terms, same history storage key. Spanish files untouched.')
