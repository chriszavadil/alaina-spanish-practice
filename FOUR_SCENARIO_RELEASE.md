# Four scenarios per term — verified History Studio v1.1.2

Live app: https://chriszavadil.github.io/alaina-spanish-practice/history/?v=1.1.2

The corrected request is complete: two additional scenarios per term compared with the original two-example release, making **four scenarios for each of 15 terms and 60 total**. Every scenario has the associated vocabulary term and an explanation. All 30 original examples remain unchanged. The intermediate three-example release was reconciled without replacing any of its 45 published examples, protecting saved third-example questions too.

## Using the update

Open the history app online and refresh. The footer shows **History v1.1.2**. Choose **Scenario Practice** to answer situation-based questions. Later rounds cycle through all four examples per term. Open **Word list → Scenario examples** to study all four situations, matching terms and explanations together. Rounds still contain 5, 10, or all eligible terms; “All” is not a single 60-question round.

Do not clear Safari website data. Existing scores, review words, achievements, filters, unfinished rounds and backups are preserved. The existing history storage key, grading and rotation logic are unchanged. No Spanish runtime, vocabulary, grading, progress or service-worker files changed.

## Verification

Candidate run **41752198250** passed all stages: content and original-example preservation, grading, all 60 scenarios through four rounds in both WebKit and Chromium, fourth-example pause/resume and backup restoration, existing history modes, and the installed 1.1.1-to-1.1.2 upgrade. The upgrade test preserved a selected third-example question, its answer choices, progress and earned achievements, then verified repeated offline reloads.

Release commit: `38003ca5ef33282ec7ed61f8797565e733b97733`.

Verified History HTML SHA-256: `ca731bcde77b6a103c6f949c322ab710942ee0666ca6d61bdad8746adc2767be`.

Public verification run **41752915366** completed successfully. Artifact **13286918647** was downloaded and inspected. The live history HTML exactly matched the tested file; Spanish HTML remained unchanged. All **44 live browser groups** passed: **12 scenario groups, 18 existing-history groups, and 14 Spanish regression groups**, across WebKit and Chromium. The report records `live_verified: true` and `history_version: 1.1.2`.

Browser tests used isolated phone-sized touch contexts, not Alaina’s actual iPhone profile. Existing speech tests simulate browser audio events; physical-iPhone audio was not tested. Scenario questions do not require audio. The scenarios are illustrative learning situations, not quotations or the teacher’s official answer key.
