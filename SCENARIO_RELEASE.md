# Scenario Practice — verified History Studio v1.1.0

Live app: https://chriszavadil.github.io/alaina-spanish-practice/history/?v=1.1.0

## Requested section

Thirty original illustrative scenarios cover all 15 Global Tapestry terms, with two situations per term and a matching-term explanation. These are learning examples, not quotations, reports of specific historical events, or a teacher's official answer key.

For study, open the book icon / Word list and expand **Scenario examples** below a word. Each example shows its situation, matching term, and explanation together. These examples also appear on revealed flashcards.

For a quiz, choose **Scenario Practice** on the home screen or practice-mode screen. Read the situation and select one of four terms. Check the answer to see **Why this term fits**. New rounds shuffle terms and alternate the two examples per word. Choose 5, 10, or all eligible terms, with the existing topics and review filters.

The original four modes remain. Existing definitions, aliases, sources, categories, scores, review words, achievements, and unfinished rounds are retained. Scenario success counts toward meaning recall, not spelling. Scenario choices, feedback and variants survive pause/resume and backup/restore. No Spanish application, vocabulary, grading, progress-storage, or service-worker files were changed by this release.

## Release and verification

Release commit: f9d6207ef37806a0da1cd1df536c23cd5cc75023

Tested History HTML SHA-256: 252168f114966f496b55b5854ffbcd3e237e6ae20bfc4a020db7d617d58de7a1

Candidate validation run 41558560290 completed successfully before publishing. It checked all 30 situations and explanations, correct/incorrect/ungraded answers, review, legacy progress and unfinished-round migration, backup/restore, phone layouts and storage failures. The original history modes, both apps offline, and the installed-history 1.0-to-1.1 upgrade also passed in WebKit and Chromium.

Public verification run 41559093878 completed successfully. Downloaded artifact 13196082837 contains the verification and browser reports. The public History HTML exactly matched the tested hash, and Spanish HTML matched its unchanged prior hash. All **44 live browser groups** passed: **12 scenario groups, 18 existing-history groups and 14 Spanish regression groups**, across WebKit and Chromium.

The tests use isolated phone-sized browser contexts, not Alaina's actual browser profile. Automated speech tests simulate API events; physical-iPhone audio has not been tested. Scenario questions themselves do not require audio.

## Offline update fix

History's own service worker now refreshes installation assets and reads offline fallback only from its active release cache. Tests verified the activated 1.1.0 worker, both cached entry-page versions, preservation of old saved rounds, and repeated offline reloads. This does not clear saved study data or affect the Spanish service worker.

## Getting the update

Open the history app online and refresh. The footer shows **History v1.1.0**. Select **Scenario Practice** or browse **Word list → Scenario examples**. Do not clear Safari website data. The website remains hosted by GitHub and does not require a home computer or temporary tunnel.
