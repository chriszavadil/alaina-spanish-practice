/* One resumable practice round. Worksheet and subject-wide progress live in the host app. */
(() => {
  'use strict';

  const key = 'alaina-empires-practice-round-v1';
  const modes = {
    flash: ['Flashcards', 'Say what the term means, then flip the card.'],
    choice: ['Meaning Quiz', 'Match each clue to its term. Later rounds test different details about the same word.'],
    scenario: ['Scenario Practice', 'Read a situation and decide which term best explains it.'],
    type: ['Recall Challenge', 'Type the term that fits the clue. Later rounds test different details about the same word.'],
    listen: ['Listen & Spell', 'Listen to a term and type what you hear.']
  };
  const { escapeHTML: escape, shuffle, normalize } = window.HistoryCore;
  const cards = () => HISTORY_TERMS;
  const findCard = name => cards().find(card => card.term === name);
  const panel = () => document.getElementById('practice-view');
  const host = () => window.Empires;
  let round = null;
  let setup = null;
  let view = '';
  let storageUnavailable = false;
  let mounted = false;
  let audioRequest = 0;

  function load() {
    if (round) return round;
    try {
      const value = JSON.parse(localStorage.getItem(key));
      if (value && Object.hasOwn(modes, value.mode) && Array.isArray(value.questions) &&
          value.questions.length > 0 && value.questions.every(q => q && findCard(q.term) &&
            Array.isArray(q.options) && q.options.every(findCard) && typeof q.prompt === 'string' &&
            typeof q.answer === 'string' && [null, 'correct', 'incorrect', 'shown'].includes(q.result)) &&
          Number.isInteger(value.index) && value.index >= 0 && value.index < value.questions.length) {
        round = value;
      }
    } catch (_) { /* A disabled or cleared store can start a fresh session. */ }
    return round;
  }

  function persist() {
    try {
      if (round) localStorage.setItem(key, JSON.stringify(round));
      else localStorage.removeItem(key);
      storageUnavailable = false;
    } catch (_) { storageUnavailable = true; }
  }

  function button(label, action, kind = 'secondary', attributes = '') {
    return '<button type="button" class="' + kind + '" data-practice="' + action + '" ' +
      attributes + '>' + escape(label) + '</button>';
  }

  function attach() {
    if (mounted) return;
    mounted = true;
    panel().addEventListener('click', onClick);
    panel().addEventListener('submit', event => {
      event.preventDefault();
      if (event.target.id === 'practice-form') check(false);
    });
    panel().addEventListener('input', event => {
      if (event.target.id !== 'practice-answer' || !round || current().result) return;
      current().answer = event.target.value;
      const reveal = panel().querySelector('[data-practice="show"]');
      if (reveal) reveal.textContent = normalize(event.target.value) ? 'Check & show answer' : 'Show answer';
      persist();
    });
  }

  function render(html, selector = '[data-practice-title]') {
    attach();
    panel().innerHTML = html + (storageUnavailable
      ? '<p class="practice-note" role="status">This browser can keep your round open, but cannot save it after you leave.</p>'
      : '');
    const target = selector && panel().querySelector(selector);
    if (target) target.focus({ preventScroll: true });
  }

  function top(title, right = '') {
    return '<div class="practice-top"><h2 tabindex="-1" data-practice-title>' + escape(title) +
      '</h2>' + right + '</div>';
  }

  function open(mode, subset) {
    if (!Object.hasOwn(modes, mode)) return;
    load();
    const requested = Array.isArray(subset) ? new Set(subset) : null;
    const pool = cards().filter(c => !requested || requested.has(c.term)).map(c => c.term);
    setup = { mode, pool, size: Math.min(5, pool.length), review: Boolean(requested) };
    setupView();
  }

  function setupView(focus = '[data-practice-title]') {
    view = 'setup';
    const { mode, pool, size, review } = setup;
    const sizes = [...new Set([5, 10, pool.length].map(n => Math.min(n, pool.length)))].filter(Boolean);
    const selectedSize = sizes.map(n => button(n + (n === 1 ? ' term' : ' terms'), 'size', 'practice-size secondary',
      'data-size="' + n + '" aria-pressed="' + (n === size) + '"')).join('');
    render(top(modes[mode][0], button('Back to studio', 'home')) +
      '<div class="practice-card"><p>' + escape(modes[mode][1]) + '</p>' +
      (review ? '<p class="practice-note">Practicing terms from your review list.</p>' : '') +
      '<h3>Terms per round</h3><div class="practice-controls" role="group" aria-label="Terms per round">' + selectedSize + '</div>' +
      (round && !round.finished ? '<p class="practice-note">Starting a new round replaces your paused round.</p>' : '') +
      '<div class="practice-actions">' + (pool.length ? button('Start round', 'begin', 'primary') : '<p>Your review list is empty.</p>') +
      (round && !round.finished ? button('Resume paused round', 'resume') : '') + '</div></div>', focus);
  }

  function nextVariant(lastSeen, term, count) {
    const last = lastSeen[term];
    const index = Number.isInteger(last) ? (last + 1) % count : Math.floor(Math.random() * count);
    lastSeen[term] = index;
    return index;
  }

  function begin() {
    const { mode, pool, size } = setup;
    if (!pool.length) return;
    const scenarioLast = { ...(round?.scenarioLast || {}) };
    const definitionLast = { ...(round?.definitionLast || {}) };
    const questions = shuffle(pool).slice(0, size).map(term => {
      const card = findCard(term);
      const specified = Array.isArray(card.distractors) ? card.distractors.filter(findCard) : [];
      const candidates = [...new Set([...shuffle(specified), ...shuffle(cards().map(c => c.term))])].filter(t => t !== term);
      let prompt = card.clue || card.simple;
      let definitionIndex = 0;
      if (mode === 'scenario' && card.scenarios?.length) {
        prompt = card.scenarios[nextVariant(scenarioLast, term, card.scenarios.length)];
      }
      if (mode === 'choice' || mode === 'type') {
        const clues = [card.clue, ...(card.extraClues || [])];
        definitionIndex = nextVariant(definitionLast, term, clues.length);
        prompt = clues[definitionIndex];
      }
      return { term, prompt, definitionIndex,
        options: shuffle([term, ...candidates.slice(0,3)]), answer: '', flipped: false, result: null };
    });
    round = { mode, questions, scenarioLast, definitionLast, index: 0, finished: false };
    persist();
    questionView();
    if (mode === 'listen') hear();
  }

  function current() { return round.questions[round.index]; }
  function hear() {
    const question = current();
    const request = ++audioRequest;
    function message(text) {
      if (request !== audioRequest || view !== 'question' || current() !== question) return;
      const status = panel().querySelector('#practice-audio-status');
      if (status) status.textContent = text;
    }
    function finished(ok) {
      message(ok ? 'Playback finished. Choose Hear term to listen again.' :
        'The recording could not play. Try Hear term again, or choose Show answer to leave this word ungraded.');
    }
    message('Playing the term…');
    try {
      if (host().say(question.term, finished) === false) finished(false);
    } catch (_) { finished(false); }
  }

  function choices(q, checked) {
    return '<div class="practice-choices" role="group" aria-label="Answer choices">' + q.options.map((name, index) => {
      let style = 'practice-choice';
      if (q.answer === name) style += ' is-selected';
      if (checked && name === q.term) style += ' is-correct';
      if (checked && name === q.answer && name !== q.term) style += ' is-incorrect';
      return button(name, 'option', style, 'data-option="' + index + '" aria-pressed="' + (name === q.answer) +
        '"' + (checked ? ' disabled' : ''));
    }).join('') + '</div>';
  }

  function flashcard(card, q) {
    const heading = '<h3>' + escape(card.term) + '</h3>';
    if (!q.flipped) return heading + '<p>What does this term mean in your own words?</p>' +
      '<div class="practice-actions">' + button('Flip card', 'flip', 'primary') + '</div>';
    return heading + host().definitionsHTML(card) + '<blockquote>' + escape(card.example) + '</blockquote>' +
      '<div class="practice-sketch">' + host().sketch(card.term) + '<p>' + escape(card.draw) + '</p><p>' + escape(card.why) + '</p></div>' +
      '<div class="practice-actions">' + button('Study again', 'again') + button('I knew it', 'known', 'primary') + '</div>';
  }

  function questionView(focus = '[data-practice-title]') {
    view = 'question';
    const q = current(), mode = round.mode, card = findCard(q.term), checked = Boolean(q.result);
    const choose = mode === 'choice' || mode === 'scenario';
    let body;
    if (mode === 'flash') {
      body = flashcard(card, q);
    } else {
      const prompt = mode === 'listen' ? 'Which term do you hear?' : q.prompt;
      body = '<h3 class="practice-prompt">' + escape(prompt) + '</h3>' +
        (mode === 'listen' ? button('Hear term', 'hear') +
          '<p class="practice-note" id="practice-audio-status" role="status"></p>' : '') +
        '<form id="practice-form">' + (choose ? choices(q, checked) :
          '<label for="practice-answer">Your answer</label><input id="practice-answer" name="answer" type="text" ' +
          'maxlength="150" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" value="' +
          escape(q.answer) + '"' + (checked ? ' readonly' : '') + '>') +
        (!checked ? '<p id="practice-error" role="status"></p><div class="practice-actions"><button class="primary" type="submit">Check answer</button>' +
          button(normalize(q.answer) ? 'Check & show answer' : 'Show answer', 'show') + '</div>' : '') + '</form>';
      if (checked) {
        const feedback = q.result === 'shown' ? 'Answer revealed' : q.result === 'correct' ? 'Correct!' : 'The answer is ' + q.term + '.';
        body += '<div class="practice-feedback ' + (q.result === 'correct' ? 'is-correct' : q.result === 'incorrect' ? 'is-incorrect' : '') +
          '" role="status" tabindex="-1" id="practice-feedback"><strong>' + escape(feedback) + '</strong><p>' +
          escape(q.term + ' — ' + ([card.simple, card.detailed, card.alternate][q.definitionIndex] || card.simple)) + '</p>' +
          (mode === 'scenario' && card.example ? '<p>' + escape(card.example) + '</p>' : '') + '</div>' +
          '<div class="practice-actions">' + button(round.index + 1 === round.questions.length ? 'See results' : 'Next question', 'next', 'primary') + '</div>';
      }
    }
    render(top(modes[mode][0], button('Pause round', 'home')) +
      '<div class="practice-stats"><span>' + (mode === 'flash' ? 'Card ' : 'Question ') + (round.index + 1) + ' of ' +
      round.questions.length + '</span><progress aria-label="Round progress" value="' + round.index + '" max="' +
      round.questions.length + '"></progress></div><article class="practice-card">' + body + '</article>', focus);
  }

  function check(reveal) {
    if (view !== 'question' || current().result || round.mode === 'flash') return;
    const q = current();
    const typed = panel().querySelector('#practice-answer');
    if (typed) q.answer = typed.value;
    if (!normalize(q.answer) && !reveal) {
      panel().querySelector('#practice-error').textContent =
        typed ? 'Type an answer or choose Show answer.' : 'Choose a term or select Show answer.';
      if (typed) typed.focus();
      return;
    }
    const card = findCard(q.term);
    const aliases = round.mode === 'type' && Array.isArray(card.aliases) ? card.aliases : [];
    const correct = [q.term, ...aliases].some(name => normalize(q.answer) === normalize(name));
    q.result = !normalize(q.answer) ? 'shown' : correct ? 'correct' : 'incorrect';
    persist();
    if (q.result !== 'shown') {
      host().report(q.term, correct);
      host().playFeedback(correct);
    }
    questionView('#practice-feedback');
  }

  function advance() {
    if (round.index + 1 < round.questions.length) {
      round.index += 1;
      persist();
      questionView();
      if (round.mode === 'listen') hear();
    } else {
      round.finished = true;
      persist();
      resultsView();
    }
  }

  function resultsView() {
    view = 'results';
    const questions = round.questions;
    const correct = questions.filter(q => q.result === 'correct').length;
    const shown = questions.filter(q => q.result === 'shown').length;
    const missed = questions.filter(q => q.result !== 'correct').map(q => q.term);
    const flash = round.mode === 'flash';
    const summary = flash ? correct + ' of ' + questions.length + ' marked “I knew it.”'
      : correct + ' correct · ' + (questions.length - correct - shown) + ' incorrect · ' + shown + ' revealed';
    render(top('Round complete') + '<article class="practice-card"><h3>' + escape(modes[round.mode][0]) +
      '</h3><p class="practice-summary">' + escape(summary) + '</p>' +
      (missed.length ? '<h3>Words to review</h3><ul class="practice-review">' + missed.map(name =>
        '<li><strong>' + escape(name) + '</strong> · ' + escape(findCard(name).simple) + '</li>').join('') + '</ul>' : '') +
      '<div class="practice-actions">' + (missed.length ? button('Practice these words', 'review', 'primary') : '') +
      button('New round', 'more', missed.length ? 'secondary' : 'primary') + button('Back to studio', 'home') + '</div></article>');
  }

  function onClick(event) {
    const control = event.target.closest('[data-practice]');
    if (!control || !panel().contains(control)) return;
    switch (control.dataset.practice) {
      case 'home': host().home(); break;
      case 'size': setup.size = Number(control.dataset.size); setupView('[data-size="' + setup.size + '"]'); break;
      case 'resume': resume(); break;
      case 'begin': begin(); break;
      case 'flip': current().flipped = true; persist(); questionView(); break;
      case 'known':
      case 'again': {
        if (view !== 'question' || !current().flipped || current().result) return;
        const correct = control.dataset.practice === 'known';
        current().result = correct ? 'correct' : 'incorrect';
        host().report(current().term, correct);
        host().playFeedback(correct);
        advance();
        break;
      }
      case 'option': {
        const q = current();
        if (q.result) return;
        q.answer = q.options[Number(control.dataset.option)];
        persist();
        questionView('[data-option="' + control.dataset.option + '"]');
        break;
      }
      case 'hear': hear(); break;
      case 'show': check(true); break;
      case 'next': if (current().result) advance(); break;
      case 'review': open(round.mode, round.questions.filter(q => q.result !== 'correct').map(q => q.term)); break;
      case 'more': open(round.mode); break;
    }
  }

  function resume() {
    if (!load() || round.finished) return false;
    questionView();
    return true;
  }
  function leave() {
    audioRequest += 1;
    view = '';
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  }

  window.EmpiresPractice = { open, resume, hasSaved: () => Boolean(load() && !round.finished), leave };
})();
