/* Pure, testable grading and round logic. No network and no dependencies. */
(function (root) {
  'use strict';
  function normalize(value) {
    return String(value ?? '').normalize('NFC').toLocaleLowerCase('es')
      .trim().replace(/\s+/gu, ' ').replace(/^[¿¡]+|[.!?¡¿,]+$/gu, '').trim();
  }
  // Remove only vowel stress marks / diaeresis for feedback. NEVER turn ñ into n.
  function withoutVowelMarks(value) {
    return normalize(value).normalize('NFD').replace(/[\u0301\u0308]/gu, '').normalize('NFC');
  }
  function acceptedAnswers(card) {
    const full = [...card.forms, ...(card.alternatives || [])].map(normalize);
    return [...new Set(full.flatMap(text => /^(el|la) /u.test(text)
      ? [text, text.replace(/^(el|la) /u, '')] : [text]))];
  }
  function grade(card, input) {
    const value = normalize(input), answers = acceptedAnswers(card);
    if (!value) return {status:'empty', expected:card.forms[0]};
    if (answers.includes(value)) return {status:'correct', expected:card.forms[0]};
    const close = answers.find(answer => withoutVowelMarks(answer) === withoutVowelMarks(value));
    return {status:close ? 'accent' : 'incorrect', expected:close || card.forms[0]};
  }
  function shuffle(items, random = Math.random) {
    const copy = [...items];
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }
  function makeRound(pool, length, previous = [], random = Math.random) {
    const count = length === 'all' ? pool.length : Math.min(pool.length, Math.max(1, Number(length) || 10));
    let shuffled = shuffle(pool, random);
    const same = shuffled.slice(0, count).every((card, i) => card.id === previous[i]);
    if (pool.length > 1 && previous.length === count && same) {
      shuffled.push(shuffled.shift());
    }
    return shuffled.slice(0, count);
  }
  function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>"']/gu, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  const api = {normalize, withoutVowelMarks, acceptedAnswers, grade, shuffle, makeRound, escapeHTML};
  root.SpanishCore = Object.freeze(api);
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
