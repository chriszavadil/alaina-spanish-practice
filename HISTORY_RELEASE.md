# Alaina’s History Studio — verified release 1.0.0

Live app: https://chriszavadil.github.io/alaina-spanish-practice/history/?v=1.0.0

This is a separate English-language history app, not a unit in Spanish practice. It uses the existing GitHub Pages host, so the home computer and temporary tunnels are not required. Its title, icon, manifest, saved progress, and study collection are its own.

## What Alaina can use

All 15 unique Global Tapestry terms from the four distinct worksheet pages are included. The repeated photo was not duplicated. The uploaded photos, handwriting, surname, and grades are not published.

- Flashcards: flip from term to clarified definition, with examples, memory cues, English pronunciation, sketch ideas, and source links.
- Meaning Quiz: identify terms from definitions and short illustrative situations.
- Recall Challenge: type the term matching a definition. Documented alternate names such as Taoism and Black Death are accepted.
- Listen & Spell: hear the English term, then spell the actual term spoken; one initial playback plus three replays per question.

Rounds are shuffled and can contain 5, 10, or all eligible terms. Topic filters, a review pile, six achievements, resumable unfinished rounds, and progress backup/restore are available. Progress is saved only in the same browser, not automatically synced across devices. Correct typed answers receive credit through either Check or Show; an empty reveal is explicitly ungraded.

## Verified release evidence

Release commit: `7c8da24112876ab5e6a3237cbae62da2296d70be`.

History HTML SHA-256: `78e18df2f4001332e2bb388c1b1d1fa526d3869927ef06d1947a609b173bdc8f`.

Candidate validation run `41550023111` passed all stages: content/grading/syntax, original Spanish-file preservation, all four modes, progress/resume/reset isolation, backup/restore, English-audio control flow, and upgrading from the old Spanish offline cache. Both apps were verified offline in Chromium and WebKit with independent caches and preserved progress.

Public verification run `41550568177` completed successfully. It verified the exact tested History HTML at the public URL and the unchanged Spanish HTML. All 18 History browser groups and 14 Spanish regression groups passed against the public websites, for 32 live browser groups in total. iPhone-sized screenshots were captured and reviewed.

Automated audio checks use simulated speech events; sound playback has not been tested on Alaina’s physical iPhone. Device voice availability can affect pronunciation and offline audio.

## Separation from Spanish practice

The Spanish HTML, vocabulary, grading core, and progress storage are unchanged. A narrowly scoped parent service-worker routing fix prevents history navigation from being cached as the Spanish homepage. History uses `alaina-history-studio-v1`; it never clears Spanish local storage. No learner browser profile was accessed during testing.

## Opening the app

Open the live link in Safari and tap **Start exploring**. The footer shows **History v1.0.0**. To install a separate Home Screen icon, use Safari’s Share menu, choose **Add to Home Screen**, enable **Open as Web App** when offered, and tap **Add**. Offline study requires a successful online visit first; device speech voices may still require internet. The X pauses and returns home rather than forcibly closing Safari. Do not clear browser data to update.
