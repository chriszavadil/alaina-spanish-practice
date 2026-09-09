# Alaina's Spanish Quiz Practice — v1.4.1

Live app: https://chriszavadil.github.io/alaina-spanish-practice/?v=1.4.1

Phone-friendly Flashcards, Spelling Quiz, and Listen & Spell. No account, timer, advertising, or analytics. Study progress is browser-local; worksheet photographs and private handwriting are not published.

## Study units

Unit 1 retains all 147 original cards. Unit 2 contains 116 cards from the six textbook photos plus the Places / Origin worksheet: 96 main vocabulary cards, plus 20 optional date/phrase and map-label cards. The two Extra topics start unchecked. Expressions with the same meaning share a card. See `VOCABULARY_AUDIT.md` and `UNIT2_AUDIT.md` for complete lists and scope notes.

Choose Unit 1 or Unit 2 on the welcome or topic screen. Both units support all three modes. Topic selections, completed-card progress, and tricky-word review are kept separately by unit; achievements span the app. The existing `alaina-spanish-practice-v1` storage key and original card IDs are retained. Do not clear site data to update.

Listen & Spell plays the Spanish form once initially and permits three replays per question. It grades the exact form spoken. Failed/interrupted playback does not spend a listen. The same device voice and speed settings are used.

## Hosting and updates

The complete self-contained application is in both `index.html` and `docs/index.html`; their contents match. GitHub Pages hosts the app directly and does not depend on a PC or temporary tunnel. The app's X returns home, not out of Safari. Refresh the existing GitHub Pages address to update; v1.4.1 appears in the footer.

## Verification of the preceding v1.4.0 release

CI run 34400597946 passed vocabulary/grading tests, touchscreen/mouse/keyboard accent tests, Unit 2 complete rounds, saved-progress migration, Unit 1 regression checks, speech-interruption recovery, and offline-cache fallback in Chromium and WebKit. The live public site was subsequently verified to serve the identical tested HTML, and 10 Unit 2 browser groups plus 14 Unit 1 regression groups passed against that public address. The live iPhone-size layouts were also inspected.

Validated HTML SHA-256 after LF normalization: `a5b35bcf8fcac3512165a51b672ed0923416969542c49b6b5face2b5b96b7e0f`.

```sh
node --test tests/core.test.cjs tests/unit2.test.cjs
python tests/accent_input.py
python tests/unit2_tests.py
python tests/listening_browser.py
python tests/listening_recovery.py
python tests/listening_offline.py
```

Python browser tests require Playwright with Chromium and WebKit installed. Speech events are simulated in automated tests; these checks do not certify audible output on a physical iPhone. No student browser data is touched by the isolated test contexts.

## Places / Origin update (v1.4.1)

The latest worksheet adds exactly seven printed entries under Places and Origin. Existing card objects, artwork, voice settings, replay rules, storage key and hosting address are retained. Previously earned achievements remain unlocked when the unit expands. The new topics are selected automatically once for learners who had all original core topics selected; intentional topic filters and optional extras remain unchanged.

Run the existing regression suites plus `node --test tests/places.test.cjs` and `python tests/places_addendum.py` to verify this update. `tools/extend_unit2_places.py` records the assertion-checked update from the materialized v1.4.0 app; `tools/apply_unit2.py` and `tools/unit2_data.py` retain the original six-page migration history. The current canonical Unit 2 vocabulary is in `src/unit2.json`.
