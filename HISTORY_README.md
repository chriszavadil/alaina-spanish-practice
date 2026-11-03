# Alaina’s History Studio — v1.1.0

Live app: https://chriszavadil.github.io/alaina-spanish-practice/history/?v=1.1.0

A separate English-language app for Alaina’s 15 Global Tapestry terms. No worksheet photos, handwriting, surname or grades are published.

## Scenario Practice

Choose **Scenario Practice** on the home screen or practice-mode screen. Read a situation and choose the associated term from four options. After checking, read **Why this term fits**. There are 30 original illustrative situations: two for each term. Rounds shuffle terms and alternate the example used for a term on later rounds.

For studying rather than quizzing, open **Word list** and expand **Scenario examples**. The situation, matching term and explanation appear together. These examples also appear on revealed flashcards. Situations are learning examples, not historical quotations or a teacher’s official answer key.

## Five practice modes

- Flashcards: term, definition, example, memory cue, pronunciation, scenarios, sketch idea and sources.
- Meaning Quiz: the original mix of definitions and brief situations.
- Scenario Practice: dedicated 30-scenario collection with explanations.
- Recall Challenge: type the term matching a definition; documented aliases are accepted.
- Listen & Spell: hear an English term and spell the actual term spoken; one initial playback plus three replays.

Choose 5, 10 or all eligible terms, topic filters, or a review round. Correct submitted answers receive credit through Check or Show. Empty reveals are ungraded. Meaning, scenario and recall questions count toward meaning-recall goals; spelling and flashcard self-assessment do not.

## Saved progress and privacy

The existing `alaina-history-studio-v1` key is retained. Existing scores, review words, six achievements, filters and unfinished rounds are preserved. Scenario variants, selected choices and feedback survive pause/resume and backup/restore. Progress remains local to the browser and does not automatically sync between devices. Reset affects history only.

No Spanish application, vocabulary, grading, storage or service-worker files are changed by the scenario update. History’s own offline cache now refreshes versioned assets and uses only its active release, preventing old cached pages from reopening after an update.

## Build and test

`python tools/build_history.py` builds current source into matching `history/` and `docs/history/` output. The assertion-checked one-time migration from 1.0.0 is recorded in `tools/add_history_scenarios.py`.

```sh
node --test tests/history.test.cjs tests/history_scenarios.test.cjs
python tests/history_scenarios.py
python tests/history_browser.py
python tests/history_backup.py
python tests/history_scenario_upgrade.py
python tests/history_offline.py
```

Candidate validation run 41558560290 passed all stages before release. The public-release workflow separately verifies the exact deployed HTML and runs history, scenario and Spanish browser suites.

Tests use Playwright WebKit and Chromium at phone-sized touch viewports. Offline tests use real service workers. Speech events in the existing listening tests are simulated; these checks are not a sound test on Alaina’s physical iPhone. Tests use isolated browser contexts, not the learner’s profile.

## Updating

Open the history app online, refresh and look for **History v1.1.0** in the footer. Do not clear Safari website data. Offline access needs a successful online update; device speech voices may still require internet. The X pauses and returns home rather than closing Safari.
