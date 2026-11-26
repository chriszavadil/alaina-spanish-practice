/* A worksheet-style quiz. The bank stays fixed until the learner starts a new set. */
(() => {
  'use strict';
  const {escapeHTML: esc, shuffle} = HistoryCore;
  const key = 'history-studio-empires-matching-v1';
  const sizes = [5, 10, 20];
  const cards = new Map(HISTORY_TERMS.map(card => [card.term, card]));
  const names = [...cards.keys()];
  const host = document.getElementById('matching-view');
  let counts = {};
  let round;
  let pendingSize;
  let active = 0;

  function save() {
    try {
      localStorage.setItem(key, JSON.stringify({counts, round, active}));
    } catch {
      document.getElementById('storage-note').hidden = false;
    }
  }

  function validRound(r) {
    if (!r || !sizes.includes(r.size) || !Array.isArray(r.bank) || r.bank.length !== r.size ||
        !r.bank.every(name => cards.has(name)) || new Set(r.bank).size !== r.bank.length ||
        !Array.isArray(r.rows) || !r.rows.length || r.rows.length > r.size ||
        !Array.isArray(r.answers) || r.answers.length !== r.rows.length) return false;
    const assigned = r.answers.filter(Boolean);
    return r.rows.every(row => row && r.bank.includes(row.term) && Number.isInteger(row.variant) &&
      row.variant >= 0 && row.variant < 3) && new Set(r.rows.map(row => row.term)).size === r.rows.length &&
      r.answers.every(name => name === '' || r.bank.includes(name)) && new Set(assigned).size === assigned.length &&
      typeof r.graded === 'boolean' && (!r.graded || assigned.length === r.rows.length);
  }

  function restore() {
    try {
      const saved = JSON.parse(localStorage.getItem(key));
      if (!saved) return;
      for (const name of cards.keys()) {
        const count = saved.counts?.[name];
        if (Number.isSafeInteger(count) && count >= 0) counts[name] = count;
      }
      if (validRound(saved.round)) {
        round = saved.round;
        active = Number.isInteger(saved.active) && saved.active >= 0 && saved.active < round.rows.length ? saved.active : 0;
      }
    } catch { /* Missing or outdated data starts a fresh quiz. */ }
  }

  function newSet(size) {
    // Draw the least-practiced words first; shuffle ties and the two display orders.
    const pool = shuffle(names).sort((a,b) => (counts[a] || 0) - (counts[b] || 0));
    const selected = pool.slice(0, size);
    const rows = shuffle(selected).map(term => {
      const n = counts[term] || 0;
      const offset = names.indexOf(term);
      counts[term] = n + 1;
      return {term, variant:(n + offset) % 3};
    });
    const bank = shuffle(selected);
    if (bank.every((name,i) => rows[i].term === name)) bank.push(bank.shift());
    round = {size, bank, rows, answers:rows.map(() => ''), graded:false};
    active = 0;
    pendingSize = undefined;
    save();
  }

  const letter = i => String.fromCharCode(65 + i);
  const filled = () => round.answers.filter(Boolean).length;
  const isRight = i => round.answers[i] === round.rows[i].term;
  const byId = id => host.querySelector('#' + id);
  function rowHTML(row, i) {
    const card = cards.get(row.term);
    const number = i + 1;
    const options = round.bank.map((name, bankIndex) =>
      '<option value="' + esc(name) + '">' + letter(bankIndex) + '. ' + esc(name) + '</option>');
    const feedback = round.graded
      ? '<p class="match-answer"><strong>' + (isRight(i) ? 'Correct' : 'Correct answer: ' + esc(row.term)) +
        '</strong>' + (isRight(i) ? '' : ' · You chose ' + esc(round.answers[i])) + '</p>' : '';
    const gradeClass = round.graded ? (isRight(i) ? ' correct' : ' incorrect') : '';
    return '<li class="match-row' + gradeClass + '" data-index="' + i + '">' +
      '<button class="match-number" type="button" data-activate="' + i + '" aria-label="Select definition ' + number + '"' +
      (round.graded ? ' disabled' : '') + '>' + number + '</button><div class="match-row-body">' +
      '<label class="match-definition" id="match-prompt-' + i + '" for="match-select-' + i + '">' +
      esc(card.quizDefinitions[row.variant]) + '</label><select class="match-select" id="match-select-' + i +
      '" data-row="' + i + '" aria-label="Word for definition ' + number + '" aria-describedby="match-prompt-' + i + '"' +
      (round.graded ? ' disabled' : '') + '><option value="">Choose a word</option>' + options.join('') +
      '</select>' + feedback + '</div></li>';
  }

  function render() {
    const correct = round.rows.filter((_,i) => isRight(i)).length;
    const total = round.rows.length;
    const isRetry = total < round.bank.length;
    const bankButtons = round.bank.map((word,i) => '<button type="button" class="match-word" data-word="' + esc(word) +
      '"' + (round.graded ? ' disabled' : '') + '><span class="match-letter" aria-hidden="true">' + letter(i) +
      '</span><span class="match-word-name">' + esc(word) + '</span></button>').join('');
    host.innerHTML = `
      <header class="match-heading"><div><div class="eyebrow">Empires vocabulary</div><h1 tabindex="-1">Word bank quiz</h1>
        <p>Match each numbered definition to a word in the bank. ${isRetry ? 'Some bank words will be left over.' : 'Use each word once.'}</p></div>
        <div class="match-size"><label for="match-size">Words per set</label><select id="match-size">
        ${sizes.map(n => '<option value="'+n+'"'+(round.size===n?' selected':'')+'>'+n+' words'+(n===20?' · full test':'')+'</option>').join('')}</select></div></header>
      <div id="match-reset" class="match-reset" hidden>
        <p>Start a new set and replace your unfinished answers?</p>
        <button type="button" class="primary" id="match-replace">Start new set</button>
        <button type="button" class="secondary" id="match-keep">Keep working</button></div>
      <div class="match-layout"><aside class="match-bank-panel" aria-labelledby="match-bank-title">
        <h2 id="match-bank-title">Word bank</h2><p id="match-bank-guide"></p>
        <div class="match-bank" id="match-bank">${bankButtons}</div></aside>
        <section class="match-sheet" aria-labelledby="match-sheet-title"><div class="match-sheet-head"><h2 id="match-sheet-title">${isRetry?'Missed definitions':'Definitions'}</h2>
        <span id="match-count"></span></div>
        ${round.graded ? '<div class="match-result" id="match-result" tabindex="-1" role="status"><strong>'+correct+' of '+total+' correct</strong><p>'+(correct===total?'Every definition has the right match.':'Your corrections appear under each missed definition.')+'</p></div>' : ''}
        <ol id="match-questions">${round.rows.map(rowHTML).join('')}</ol>
        <p id="match-message" role="status"></p><div class="match-actions">
        ${!round.graded ? '<button class="primary" type="button" id="match-check">Check answers</button>' :
          correct < total ? '<button class="primary" type="button" id="match-retry">Retry missed</button>' : ''}
        <button class="${round.graded && correct===total?'primary':'secondary'}" type="button" id="match-new">New set</button></div></section></div>`;
    syncControls();
  }

  function syncControls() {
    byId('match-count').textContent = filled() + ' of ' + round.rows.length + ' matched';
    byId('match-bank-guide').textContent = round.graded ? 'Letters match the choices on your sheet.' :
      'Tap a word for definition ' + (active + 1) + ', or use the menu under any definition.';
    for (const row of host.querySelectorAll('.match-row')) {
      const i = Number(row.dataset.index);
      row.classList.toggle('active', !round.graded && i === active);
      row.querySelector('select').value = round.answers[i];
      const number = row.querySelector('.match-number');
      if (!round.graded && i === active) number.setAttribute('aria-current','true');
      else number.removeAttribute('aria-current');
    }
    for (const chip of host.querySelectorAll('[data-word]')) {
      const at = round.answers.indexOf(chip.dataset.word);
      chip.classList.toggle('used', at !== -1);
      chip.title = at === -1 ? 'Available' : 'Used for definition ' + (at + 1);
      chip.setAttribute('aria-label', chip.dataset.word + (at === -1 ? ', available' : ', used for definition ' + (at + 1)));
    }
  }

  function assign(i, word, advance) {
    if (round.graded || (word && !round.bank.includes(word))) return;
    const previous = round.answers[i];
    const other = word ? round.answers.indexOf(word) : -1;
    if (other >= 0 && other !== i) round.answers[other] = previous;
    round.answers[i] = word;
    active = i;
    if (advance) {
      for (let step = 1; step < round.rows.length; step++) {
        const next = (i + step) % round.rows.length;
        if (!round.answers[next]) { active = next; break; }
      }
    }
    save();
    syncControls();
    const moved = other >= 0 && other !== i;
    const message = word ? word + ' matched to definition ' + (i+1) + '.' : 'Definition ' + (i+1) + ' cleared.';
    byId('match-message').textContent = moved ? message + ' Definition ' + (other + 1) +
      (previous ? ' now uses ' + previous + '.' : ' is now empty.') : message;
  }

  function showFresh(size) {
    newSet(size);
    render();
    host.querySelector('h1').focus();
    window.scrollTo(0,0);
  }

  let returnFocus = 'match-new';
  function requestFresh(size, trigger) {
    if (round.graded || !filled()) { showFresh(size); return; }
    returnFocus = trigger;
    pendingSize = size;
    byId('match-size').value = String(round.size);
    byId('match-reset').hidden = false;
    byId('match-keep').focus();
  }

  function grade() {
    if (round.graded) return;
    const empty = round.answers.indexOf('');
    if (empty >= 0) {
      byId('match-select-' + empty).focus();
      byId('match-message').textContent = 'Choose a word for each definition before checking. Definition ' + (empty+1) + ' still needs a match.';
      document.getElementById('status').textContent = byId('match-message').textContent;
      return;
    }
    round.graded = true;
    save();
    round.rows.forEach((row,i) => window.Empires.report(row.term, isRight(i)));
    window.Empires.playFeedback(round.rows.every((_,i) => isRight(i)));
    render();
    byId('match-result').focus();
  }

  function retry() {
    const missed = round.rows.filter((_,i) => !isRight(i));
    if (!round.graded || !missed.length) return;
    round = {...round, rows:shuffle(missed), answers:missed.map(() => ''), graded:false};
    active = 0;
    save();
    render();
    byId('match-select-0').focus();
  }

  host.addEventListener('focusin', event => {
    const control = event.target.closest('[data-row],[data-activate]');
    if (!control || !round || round.graded) return;
    active = Number(control.dataset.row ?? control.dataset.activate);
    syncControls();
  });
  host.addEventListener('change', event => {
    const el = event.target;
    if (el.id === 'match-size') requestFresh(Number(el.value), el.id);
    else if (el.matches('select[data-row]')) assign(Number(el.dataset.row), el.value, false);
  });
  host.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button || button.disabled) return;
    if (button.dataset.word) assign(active, button.dataset.word, true);
    else if (button.dataset.activate !== undefined) {
      active = Number(button.dataset.activate);
      syncControls();
      byId('match-message').textContent = 'Choose a bank word for definition ' + (active + 1) + '.';
    } else if (button.id === 'match-check') grade();
    else if (button.id === 'match-retry') retry();
    else if (button.id === 'match-new') requestFresh(round.size, button.id);
    else if (button.id === 'match-replace' && pendingSize) showFresh(pendingSize);
    else if (button.id === 'match-keep') {
      pendingSize = undefined;
      byId('match-reset').hidden = true;
      byId(returnFocus).focus();
    }
  });

  window.addEventListener('storage', event => {
    if (event.key !== key || !event.newValue) return;
    restore();
    pendingSize = undefined;
    if (!host.hidden && round) render();
  });
  restore();
  window.EmpiresMatching = {open() {
    if (!round) newSet(5);
    pendingSize = undefined;
    render();
  }};
})();
