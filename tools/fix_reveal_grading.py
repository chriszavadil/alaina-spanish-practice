"""Targeted 1.4.1 -> 1.4.2 fix for typed answers discarded by Show answer."""
from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
h=(ROOT/'index.html').read_text(encoding='utf-8');old=h
assert hashlib.sha256(h.encode()).hexdigest()=='4c72cc263afba482259a12ea68cc99b79ff78b594ea0fbd20a84ae189334d557'
def change(a,b,count=1):
 global h
 assert h.count(a)==count,(a[:90],h.count(a),count)
 h=h.replace(a,b)
core=(ROOT/'src/core.js').read_text(encoding='utf-8');basecore=core
addition="""  // A reveal request must never discard a submitted correct answer.
  // Only an empty response may become an ungraded reveal.
  function gradeSubmission(card, input, reveal = false) {
    const result = grade(card, input);
    return reveal === true && result.status === 'empty'
      ? {...result, status:'skipped'} : result;
  }
"""
core=core.replace('  function shuffle(',addition+'  function shuffle(')
core=core.replace('acceptedAnswers, grade, shuffle','acceptedAnswers, grade, gradeSubmission, shuffle')
change(basecore.strip(),core.strip())
change('escapeHTML:e, grade, makeRound, normalize','escapeHTML:e, grade, gradeSubmission, makeRound, normalize')
change('function checkAnswer(skipped=false) {','function checkAnswer(skipped=false) {\n  skipped=skipped===true;')
change("if(!session||!isSpellingMode(session.mode)||session.checked)return;","if(!session||view!=='practice'||!isSpellingMode(session.mode)||session.checked)return;")
change("const result=skipped?{status:'skipped'}:grade(expected,typed);","const result=gradeSubmission(expected,typed,skipped);")
change('Try an answer, or tap “I’m not sure — show me.”','Type an answer, or choose “Show answer (skip).”')
change('I’m not sure — show me','Show answer (skip)')
change("input.classList.add(correct?'is-correct':'is-wrong');","input.classList.add(correct?'is-correct':result.status==='skipped'?'is-skipped':'is-wrong');")
change("result.status==='skipped'?'Let’s learn this one.'","result.status==='skipped'?'Answer shown — not graded.'")
change("const helper=correct?'That spelling is correct.':result.status==='accent'?","const helper=correct?'That spelling is correct.':result.status==='skipped'?'No answer was entered. This word is saved for practice, not counted as a spelling mistake.':result.status==='accent'?")
change("class=\"feedback ${correct?'correct':''}\"","class=\"feedback ${correct?'correct':result.status==='skipped'?'skipped':''}\"")
change("const next=document.getElementById('quiz-submit');", """// A separate Next control cannot reinterpret a queued Check click.
  const previous=document.getElementById('quiz-submit');
  const next=previous.cloneNode(false);
  next.dataset.action='quiz-next';
  previous.replaceWith(next);""")
change("case 'quiz-submit':session?.checked?nextCard():checkAnswer();break;","case 'quiz-submit':checkAnswer();break;\n    case 'quiz-next':nextCard();break;")
change("if(!button||button.disabled)return;","if(!button||button.disabled||!button.isConnected)return;")
change("if(session?.checked)nextCard();else checkAnswer();", "// Form Enter checks once; only the explicit Next button advances.\n  if(!session?.checked)checkAnswer();")
change("if(event.target.id==='answer-input'){document.getElementById('answer-error').textContent='';}","if(event.target.id==='answer-input'){document.getElementById('answer-error').textContent='';updateRevealLabel();}")
change('function quizHTML(card) {', """function updateRevealLabel() {
  const input=document.getElementById('answer-input'),button=document.getElementById('quiz-skip');
  if(!input||!button||session?.checked)return;
  button.textContent=normalize(input.value)?'Check & show answer':'Show answer (skip)';
}
function quizHTML(card) {""")
change("document.addEventListener('click',handleAction);", """document.addEventListener('click',handleAction);
// Holding Enter must not check the next word or discard feedback.
document.addEventListener('keydown',event=>{
  if(view==='practice' && event.key==='Enter' && event.repeat)event.preventDefault();
});""")
change("document.getElementById('listen-play').disabled=true;", "document.getElementById('listen-play').disabled=true;document.getElementById('listen-play').innerHTML=icon('sound')+' Answer shown';")
start=h.index('function renderResults() {');end=h.index('function openWordList()',start)
segment=h[start:end]
segment=segment.replace("const quiz=isSpellingMode(session.mode);","const quiz=isSpellingMode(session.mode);\n  const shown=session.responses.filter(r=>r.status==='skipped').length;\n  const incorrect=missed.length-shown;")
needle='    <div class="result-actions">'
assert segment.count(needle)==1
segment=segment.replace(needle,'''    ${quiz?`<p class="result-breakdown" aria-label="Answer breakdown"><span><strong>${correct}</strong> correct</span><span><strong>${incorrect}</strong> incorrect</span><span><strong>${shown}</strong> shown without an answer</span></p>`:''}
'''+needle)
segment=segment.replace("r.status==='skipped'?'Skipped'","r.status==='skipped'?'Shown without an answer (not graded)'")
h=h[:start]+segment+h[end:]
change("class=\"feedback ${correct?'correct':result.status==='skipped'?'skipped':''}\"", "data-result=\"${result.status}\" class=\"feedback ${correct?'correct':result.status==='skipped'?'skipped':''}\"")
change('</style>', '''/* Neutral reveals are not spelling errors. */
.feedback.skipped{background:var(--lavender);border-color:var(--line)}
.feedback.skipped .feedback-heading{color:var(--purple-dark)}
.answer-input.is-skipped{background:var(--paper);border-color:var(--line)}
.result-breakdown{display:flex;gap:10px 18px;flex-wrap:wrap;font-size:12px;line-height:1.6;margin:12px 0 20px;color:var(--muted)}
.quiz-skip .text-button{min-height:44px}
</style>''')
change('name="app-version" content="1.4.1"','name="app-version" content="1.4.2"')
change('<span class="app-version">v1.4.1</span>','<span class="app-version">v1.4.2</span>')
assert re.search(r'<script id="vocabulary-data".*?</script>',h,re.S)[0]==re.search(r'<script id="vocabulary-data".*?</script>',old,re.S)[0]
assert re.findall(r'data:image/webp;base64,[A-Za-z0-9+/=]+',h)==re.findall(r'data:image/webp;base64,[A-Za-z0-9+/=]+',old)
for f in ['index.html','docs/index.html']:(ROOT/f).write_text(h,encoding='utf-8')
(ROOT/'src/core.js').write_text(core,encoding='utf-8')
for f in ['sw.js','docs/sw.js']:
 p=ROOT/f;s=p.read_text(encoding='utf-8');assert "'v1.4.1'" in s;p.write_text(s.replace("'v1.4.1'","'v1.4.2'"),encoding='utf-8')
# Only update assertions of the current version, not historic card-introduction IDs.
for p in (ROOT/'tests').glob('*'):
 if p.suffix not in ['.py','.cjs'] or p.name=='reproduce_martes.py':continue
 s=p.read_text(encoding='utf-8');s=s.replace("to_have_attribute('content','1.4.1')","to_have_attribute('content','1.4.2')").replace("'v1.4.1'","'v1.4.2'")
 p.write_text(s,encoding='utf-8')
print('Patched 1.4.2; all 263 vocabulary objects, artwork and storage key untouched.');print(hashlib.sha256(h.encode()).hexdigest())
