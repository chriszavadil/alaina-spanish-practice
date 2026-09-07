/* Inlined inside the app closure. One initial play plus three replays. */
const LISTEN_LIMIT = 4;
let cancelListeningAttempt = null;
const isSpellingMode = mode => mode === 'quiz' || mode === 'listening';
const modeTitle = mode => mode === 'listening' ? 'Listen & Spell' : mode === 'quiz' ? 'Spelling quiz' : 'Flashcards';
function prepareListeningQuestion() {
  if (session.mode !== 'listening') return;
  const card = session.cards[session.index];
  const formIndex = Math.floor(Math.random() * card.forms.length);
  session.listening = {formIndex, form:card.forms[formIndex], plays:0, busy:false, message:''};
}
function listeningPromptHTML() {
  return `<div class="listen-prompt"><span class="card-language">LISTEN IN SPANISH</span>
    <div class="listen-emblem" aria-hidden="true">${icon('sound')}</div>
    <h2>Listen, then spell.</h2><p>No written clues. Take your time.</p>
    <button type="button" class="secondary listen-play" id="listen-play" data-action="listen-play" aria-describedby="listen-status">${icon('sound')} Play Spanish</button>
    <p id="listen-status" class="listen-status" role="status" aria-live="polite">One first listen + 3 replays.</p>
    <p id="listen-error" class="listen-error" role="status" hidden></p></div>`;
}
function updateListeningControls() {
  const q=session?.listening, play=document.getElementById('listen-play');
  if (!q || !play || view !== 'practice' || session.checked) return;
  const remaining=Math.max(0,LISTEN_LIMIT-q.plays);
  play.disabled=q.busy || remaining===0;
  play.innerHTML=icon('sound')+' '+(q.busy?'Playing Spanish…':!q.plays?'Play Spanish':remaining?`Play again (${remaining} left)`:'No replays left');
  document.getElementById('listen-status').textContent=q.busy?'Listen carefully.':!q.plays?'One first listen + 3 replays.':remaining?`${remaining} ${remaining===1?'replay':'replays'} left for this question.`:'All 4 listens used. Now spell what you heard.';
  const message=document.getElementById('listen-error'); message.textContent=q.message; message.hidden=!q.message;
  document.getElementById('quiz-submit').disabled=q.busy || !q.plays;
}
function playListeningQuestion() {
  const q=session?.listening;
  if (view!=='practice' || session?.mode!=='listening' || session.checked || !q || q.busy || q.plays>=LISTEN_LIMIT) return;
  q.busy=true; q.message=''; updateListeningControls();
  let settled=false, startTimer=null, endTimer=null;
  const finish=(success,message='')=>{
    if (settled) return; settled=true;
    clearTimeout(startTimer); clearTimeout(endTimer);
    if (cancelListeningAttempt===cancel) cancelListeningAttempt=null;
    q.busy=false;
    if (session?.listening!==q || session.checked || view!=='practice') return;
    if (success) q.plays++;
    q.message=message; updateListeningControls();
  };
  const cancel=()=>finish(false,'Audio paused. Tap Play Spanish to try again. This listen was not used.');
  const failed=()=>finish(false,'Audio did not finish. Check your volume or Spanish voice in Settings, then tap Play Spanish. This listen was not used.');
  const timedOut=()=>{failed(); stopSpeech();};
  startTimer=setTimeout(timedOut,6000);
  speak(q.form,{
    onStart:()=>{if(settled)return;clearTimeout(startTimer);endTimer=setTimeout(timedOut,30000);},
    onEnd:()=>finish(true),
    onFailure:failed
  });
  if (!settled) cancelListeningAttempt=cancel;
}
function heardAudioHTML(card) {
  const q=session.listening;
  return `<div class="audio-group"><button class="audio-button" type="button" data-action="speak" data-card="${e(card.id)}" data-form="${q.formIndex}" aria-label="Listen to the answer again">${icon('sound')} Listen to the answer</button></div>`;
}
