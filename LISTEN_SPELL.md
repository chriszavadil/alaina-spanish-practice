# Listen & Spell — version 1.3.0

Adds a third mode to the existing application; does not replace the flashcard or written-prompt quizzes.

## Learner experience
- Choose topics and a 10-question, 20-question, or full round as before.
- The first playback is requested directly from the Start / Next button interaction.
- One initial playback plus three replays is allowed per question (four complete listens total).
- The same Spanish form is used on every replay of a question.
- English, digits, and written Spanish are absent from the question prompt. The topic remains visible.
- If playback fails or is interrupted, that incomplete listen is not counted. A Play Spanish button allows recovery.
- The replay button is locked while speech is pending/playing. A watchdog recovers from missing speech events.
- Spell the form actually spoken, not another gender form or synonym. Initial el/la remains optional; accents, ñ, and ü still count.
- Checking or revealing the answer ends the replay restriction for that question. Answer audio is then available for learning.
- Correct answers contribute to saved spelling totals and the existing achievements. Tricky-word review is retained.

## Compatibility and data
The existing `alaina-spanish-practice-v1` storage key is retained. Existing items, totals, achievements, and settings are preserved. Additional listening counters are additive. No account, microphone, analytics, or new speech service was introduced. The existing voice and speed settings are used.

The root and `docs/` HTML files are identical. Both service-worker versions are 1.3.0. Production JavaScript remains inline; `src/listening-ui.js` is the readable source of the new listening helpers, inserted inside the application closure.

## Verification
Run `node --test tests/core.test.cjs` and `python tests/listening_browser.py` with Playwright Chromium and WebKit installed. The browser suite starts an isolated loopback server, or accepts `--url` for a deployed copy. `--quick` skips exhaustive vocabulary and timeout checks.

`tests/speech_stub.js` is a test-only API double and is never loaded by the app. It exercises success, failure, cancellation, replay limits, exact-form grading, keyboard/touch navigation, persistence, and old-mode regressions. These tests do not certify audible output on a physical iPhone.

Speech event reference: https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance
