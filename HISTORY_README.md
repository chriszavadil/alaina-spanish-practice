# Alaina’s History Studio

A separate English-language history app for the 15 unique Global Tapestry worksheet terms. The source photos, handwriting, surname and grade are not included. The duplicate photo is not a duplicate study card.

## Study modes

- Flashcards: term first, tap to reveal a clarified definition, example, memory cue and optional sketch idea/sources. Pronunciation can read both term and definition.
- Meaning Quiz: identify terms from definitions and short illustrative situations.
- Recall Challenge: type the term matching a definition. Case, whitespace and hyphen variants are normalized. Listed aliases (including Taoism and Black Death) are accepted; spelling mistakes are not silently accepted.
- Listen & Spell: English pronunciation of a term, one initial playback plus three replays per question; exact spoken term required. Failed/incomplete playback does not use a listen. The written answer is hidden until checked or revealed.

All new rounds are randomized. Choose 5, 10 or all eligible terms, topic filters, or the review pile. Check and Show both grade existing typed answers; an empty reveal is not an incorrect answer. Correct, incorrect and ungraded counts are separate. Quizzes do not auto-advance after checking. Flashcard self-assessment and spelling scores do not count as meaning mastery.

## Progress and privacy

Six achievements, completed rounds, per-term review and meaning-recall goals are browser-local. An unfinished round can be paused and resumed. Progress can be exported and restored with a validated JSON backup. Reset affects history only. There is no account, microphone, analytics, remote student-data service or timed-test pressure.

The standalone app is `history/index.html`; a matching copy is in `docs/history/index.html` for the existing GitHub Pages publishing folder. Its link is `/alaina-spanish-practice/history/`, but it is a separate application, not a Spanish unit. The original Spanish HTML, vocabulary, grading code and browser-storage key are untouched.

History uses its own storage key (`alaina-history-studio-v1`), scoped manifest and service worker. The only parent-hosting change restricts the Spanish service worker to its own page routes, preventing one app from being cached as the other. A cache-version refresh repairs the old overly broad navigation behavior. Tests cover upgrading from the old installed Spanish worker and using both apps offline.

## Content

15 terms: Caliphate, Christianity, City-state, Caravan, Feudalism, Silk Road, Black Plague, Daoism, Islam, Luxury Goods, Jihad, Dynasty, Confucianism, Meritocracy, Buddhism.

Definitions are original student-friendly summaries, not verbatim teacher answer keys. Examples/scenarios and sketch prompts are learning aids. Source links on each card point to Oxford/Cambridge dictionaries, UNESCO, Smithsonian, CDC, Gettysburg College, UC San Diego and National Geographic. Clarifications: plague is bacterial; jihad has spiritual and armed-struggle meanings depending on context; the Silk Road is a network; feudalism is a simplified model whose scope historians debate. Follow the teacher’s wording requirements for graded assignments.

## Build and verification

`python tools/build_history.py`
`node --test tests/history.test.cjs`
`python tests/history_browser.py`
`python tests/history_offline.py`

Python browser checks use Playwright Chromium and WebKit with an iPhone-sized touch viewport. Simulated speech events test control flow, not audible output on a physical iPhone. The offline/cache test uses real service workers. No learner’s live browser profile is accessed by tests.

Use Safari’s Share > Add to Home Screen to install the history app separately. Offline study needs a successful online visit first. Device speech voices may still need internet. X pauses and returns home; it cannot close Safari.
