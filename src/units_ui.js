/* Unit-scoped views share the tested practice engine and the existing storage key. */
function unitOf(card) { return byCategory.get(card.category)?.unit || 'unit1'; }
function unitCards(id=settings.unit) { return CARDS.filter(c=>unitOf(c)===id); }
function unitCategories(id=settings.unit) { return DATA.categories.filter(c=>(c.unit||'unit1')===id); }
function unitName(id=settings.unit) { return id==='unit2'?'Unit 2':'Unit 1'; }
function defaultTopics(id) { return unitCategories(id).filter(c=>!c.supplemental).map(c=>c.id); }
function unitProgress(id=settings.unit) {
  if(!progress.units || typeof progress.units!=='object' || Array.isArray(progress.units)) {
    progress.units={unit1:{rounds:progress.rounds,perfectRounds:progress.perfectRounds,
      listeningRounds:progress.listeningRounds,lastQuiz:progress.lastQuiz,lastListening:progress.lastListening}};
  }
  if(!progress.units[id] || typeof progress.units[id]!=='object')progress.units[id]={rounds:0,perfectRounds:0,listeningRounds:0,lastQuiz:null,lastListening:null};
  return progress.units[id];
}
function unitSwitcher() {
  return `<section class="unit-picker" aria-label="Choose a study unit"><div class="unit-picker-label">YOUR STUDY UNITS</div><div class="unit-choices">${['unit1','unit2'].map(id=>`<button type="button" class="unit-choice" data-action="unit" data-unit="${id}" aria-pressed="${settings.unit===id}"><strong>${unitName(id)} ${settings.unit===id?icon('check'):''}</strong><small>${id==='unit1'?'Original vocabulary':'New words'} · ${unitCards(id).length} cards</small></button>`).join('')}</div></section>`;
}
function switchUnit(id) {
  if(!['unit1','unit2'].includes(id) || id===settings.unit)return;
  // Unit controls are not rendered in practice. Guard against an accidental extra control.
  if(view==='practice')return;
  stopSpeech();settings.categoriesByUnit[settings.unit]=[...settings.categories];
  settings.unit=id;settings.categories=[...settings.categoriesByUnit[id]];
  onlyReview=false;lastOrder=[];session=null;save();
  if(view==='home')renderHome();else if(view==='words')openWordList();else{view='setup';renderSetup();}
}
function progressPanel() {
  const cards=unitCards(),seen=cards.filter(c=>progress.items[c.id]?.seen>0).length;
  const correct=cards.reduce((n,c)=>n+(Number(progress.items[c.id]?.quizCorrect)||0),0);
  const rounds=Number(unitProgress().rounds)||0;
  return `<section class="progress-card" aria-label="Saved practice progress"><div class="progress-card-top"><h2>${unitName()} progress</h2><button class="text-button" data-action="achievements">Achievements ${achievementCount()}/${achievements().length} →</button></div><div class="progress-meter" role="progressbar" aria-label="${unitName()} cards explored" aria-valuemin="0" aria-valuemax="${cards.length}" aria-valuenow="${seen}"><span style="width:${seen/cards.length*100}%"></span></div><div class="progress-grid"><div class="progress-mini"><strong>${seen} / ${cards.length}</strong><small>cards explored</small></div><div class="progress-mini"><strong>${correct}</strong><small>spelling answers right</small></div><div class="progress-mini"><strong>${needsReviewCards().length}</strong><small>to revisit</small></div><div class="progress-mini"><strong>${rounds}</strong><small>rounds finished</small></div></div><p class="unit-save-note">Each unit keeps its own progress. Your achievements carry across both.</p></section>`;
}
function aboutUnit2() {
  modalShell('Unit 2: the new words',`<p><strong>109 study cards</strong> from the six new photos: <strong>89 main vocabulary cards</strong> plus <strong>20 optional extra cards</strong> for visible date phrases and map labels. The extras start unchecked. Alternative expressions with the same English meaning share a card.</p><table class="coverage-table" aria-label="Unit 2 vocabulary coverage"><tbody>${unitCategories('unit2').map(c=>`<tr><td>${e(c.name)}</td><td>${c.count}</td></tr>`).join('')}<tr><td>Total</td><td>109</td></tr></tbody></table><h3>Careful spellings</h3><p>Numbers are exactly <strong>0–31</strong>. The three printed forms for 21 are veintiuno (counting), veintiuna (before a feminine noun), and veintiún (before a masculine noun). Las tijeras is plural. The page’s marker / highlighter is el marcador.</p><p>Months and weekdays are written lowercase. In Unit 2 punctuation is optional, but accents, ñ, and ü still count. Matching el, la, los, or las may be omitted from vocabulary nouns; they are not removed from complete sentence starters. Listen & Spell still asks for the particular form spoken.</p><h3>What was not guessed</h3><p>No unheard listening answers, unseen pages, missing holiday dates, handwritten information, or invented country lists were added. The photos label the textbook section Unidad 0; Unit 2 is the requested grouping in this app.</p><h3>Progress and pronunciation</h3><p>Unit 1 stays available with its original 147 cards and saved progress. Both units use all three modes, the same voice and speed, and one first listen plus three replays per listening question. Voice quality and sound still depend on the device.</p><p><a class="source-link" href="https://www.rae.es/dpd/uno" target="_blank" rel="noopener noreferrer">RAE: uno, veintiuno and agreement</a><a class="source-link" href="https://www.rae.es/dpd/tijera" target="_blank" rel="noopener noreferrer">RAE: tijera / tijeras</a></p>`);
}
function answerHint(card) {
  const intro=session.mode==='listening'?'Spell the exact word or phrase you heard.':'Write one form from the page.';
  const article=card.articleOptional===false?'Keep all the words, including articles.':'A matching noun article (el, la, los, las) is optional.';
  return intro+' Accents, ñ, and ü count. '+article+(card.punctuationOptional?' Punctuation is optional.':'');
}
