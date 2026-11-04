# Three scenarios per term — verified History Studio v1.1.1

Live app: https://chriszavadil.github.io/alaina-spanish-practice/history/?v=1.1.1

## Requested expansion

All 15 Global Tapestry terms now have exactly three distinct illustrative scenarios, for 45 scenarios total. The original 30 scenarios and explanations are retained unchanged. Each of the 15 additions has its own situation and a matching-term explanation. These are learning examples, not claims about specific historical events or a teacher's official answer key.

Choose Scenario Practice for a quiz. A round still contains 5, 10, or all eligible terms, with one situation per term; subsequent rounds cycle through all three variants. Open Word list and expand Scenario examples to study all three situations with their matching word and explanation together. Revealed flashcards also show all three examples.

Existing definitions, aliases, source links, categories, term IDs, grading rules, progress, achievements, review words, settings, and unfinished rounds are preserved. The history storage key remains alaina-history-studio-v1. No Spanish app HTML, vocabulary, grading, progress storage, or service-worker files were changed.

## Verification

Release commit: 36dec311f5240cc8efbb95251064cdf49f793dcf.
Validated history HTML SHA-256: f6030cbdc5251f43383f3e121b9e3efbd067c0329a03c9e154cc50ab6ffe64df.

Candidate validation run 41750837163 completed successfully. It covered all 45 examples across three rounds in WebKit and Chromium; old saved scenario variants; third-example pause/resume and backup/restore; review; existing modes; progress and storage isolation; and installed offline upgrades from History 1.0.0 and 1.1.0 to 1.1.1. Tests confirmed the original 30 scenarios and all original term data remained unchanged.

GitHub Pages deployment run 41751383558 completed successfully. Public verification run 41751383946 then confirmed the exact tested History HTML at the public address and unchanged Spanish HTML. All 44 live browser groups passed: 12 scenario groups, 18 existing-history groups, and 14 Spanish regression groups, across WebKit and Chromium. Evidence is in workflow artifact 13287016056 (history-live-verification); verification.json reports history_version 1.1.1, live_verified true, and the hash above. The three-example study layout was visually inspected at iPhone dimensions.

Tests use isolated browser contexts, not Alaina's actual profile. Existing listening tests simulate speech API events; audible playback on a physical iPhone was not retested. Scenario questions do not require audio.

## Updating

Open the app online and refresh or reopen it. The footer should show History v1.1.1. Use Scenario Practice or Word list → Scenario examples. Do not clear Safari website data or reset progress to obtain the update. The existing permanent address is unchanged and does not require the home computer to remain on.
