# Correct-answer / reveal-path repair — v1.4.2

## Reproduced defect
The reported screenshot shows a typed `el martes`, the same displayed answer, and the heading “Let's learn this one.” In v1.4.1 that heading belongs to the reveal/skip path, not the ordinary incorrect-spelling path. A read-only, isolated WebKit and Chromium reproduction against the public v1.4.1 app confirmed that normal checking credits `el martes`, but using the reveal path with the same typed answer discards it, records zero credit, and adds the word to review. The screenshot does not prove which physical button was tapped; the reproduced code path explains the displayed state.

## Repair
- Every submitted nonempty answer is graded, whether sent with Check my answer, Enter, or the reveal control.
- The reveal control reads “Check & show answer” when text is present and “Show answer (skip)” when empty.
- Only an empty reveal is ungraded. Its neutral feedback explicitly says “Answer shown — not graded”; it is not styled as an incorrect answer.
- Results distinguish correct, incorrect, and shown-without-answer counts. Revealed words remain available to practice.
- Check and Next have separate actions, and the Next button is a new DOM control. Queued clicks on removed controls are ignored. A duplicate form submission cannot advance a checked question; held Enter is ignored until released.
- The top listening button changes to “Answer shown” after checking rather than displaying unused replays next to a disabled control.
- Existing accent requirements, matching optional articles, and exact-spoken-form listening grading remain intact.

## Preserved
All 263 vocabulary card objects, both units, artwork, card IDs, replay limits, voices, and the `alaina-spanish-practice-v1` storage key remain unchanged. No student's browser data was accessed or reset. Old incorrect/skipped history cannot reliably be regraded: previous versions did not store enough submitted-answer history. A later correct attempt removes that word from the review pile as before; past totals are not silently rewritten.

## Verification
See `GRADING_FIX_VERIFICATION.json` for the tested HTML hash, completed suites, and public deployment status. Browser tests use simulated speech API events, not sound playback on a physical iPhone. Tests run in isolated contexts, not the learner's browser.

References consulted for event handling:
- https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/submit_event
- https://developer.mozilla.org/en-US/docs/Web/API/SubmitEvent/submitter
- https://developer.mozilla.org/en-US/docs/Web/API/Element/click_event

## Published and verified

The permanent GitHub Pages site serves the exact tested v1.4.2 application. All 32 live browser check groups passed (18 grading-path groups and 14 existing-mode groups) in WebKit and Chromium. This includes the reported el martes case via Check, reveal and Enter, all 263 words through the reveal path, saved progress, exact-form listening, and replay limits. The update uses the same address; refresh and look for v1.4.2 in the footer. Do not clear browser data.

Live address: https://chriszavadil.github.io/alaina-spanish-practice/?v=1.4.2
