"""Exercise the Empires unit from the real History Studio entry in isolated profiles."""
import argparse
import hashlib
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import expect, sync_playwright


def verify_files(history_url):
    """Wait briefly for Pages to serve the same unit that the workflow checked out."""
    public_dir = Path(__file__).resolve().parents[1] / "docs" / "history" / "empires"
    files = {p.name: p.read_bytes() for p in public_dir.iterdir() if p.is_file()}
    assert "index.html" in files and "terms.js" in files
    for attempt in range(24):
        try:
            for name, local in files.items():
                version = hashlib.sha256(local).hexdigest()[:12]
                url = history_url + "empires/" + name + "?verify=" + version
                request = Request(url, headers={"Cache-Control": "no-cache"})
                with urlopen(request, timeout=15) as response:
                    assert response.status == 200 and response.read() == local, name
            print(f"Verified {len(files)} published Empires assets.", flush=True)
            return
        except (AssertionError, OSError) as error:
            if attempt == 23:
                raise
            print(f"Waiting for Pages ({type(error).__name__})", flush=True)
            time.sleep(5)


def check_size(page):
    layout = page.evaluate("""() => ({
      width: innerWidth,
      content: document.documentElement.scrollWidth,
      route: location.hash,
      outside: Array.from(document.querySelectorAll('main *, header *, footer *'))
        .filter(el => el.getBoundingClientRect().right > innerWidth + 0.5)
        .slice(0, 8).map(el => el.id || el.className?.baseVal || el.className || el.tagName)
    })""")
    assert layout["content"] <= layout["width"], f"Horizontal overflow: {layout}"


def check_word_bank(page):
    """Match a five-word sheet and its retry, then inspect three full worksheets."""
    expect(page.get_by_role("heading", name="Word bank quiz", exact=True)).to_be_visible()
    size = page.locator("#match-size")
    expect(size).to_have_value("5")
    bank = page.locator("#match-bank button[data-word]")
    prompts = page.locator("#match-questions .match-definition")
    selects = page.locator("#match-questions select[data-row]")
    words = bank.evaluate_all("(buttons) => buttons.map(b => b.dataset.word)")
    cards = page.evaluate("HISTORY_TERMS.map(c => [c.term, c.quizDefinitions])")
    assert len(cards) == 20 and all(len(set(defs)) == 3 for _, defs in cards)
    answers = {definition: term for term, definitions in cards for definition in definitions}
    assert len(answers) == 60

    initial = prompts.all_text_contents()
    assert len(initial) == len(set(words)) == len(words) == 5
    correct = [answers[p] for p in initial]
    assert set(correct) == set(words)
    dropdowns = selects.evaluate_all("(rows) => rows.map(s => Array.from(s.options, o => o.value))")
    assert all(options == ["", *words] for options in dropdowns)
    expect(selects).to_have_count(5)

    # Two chip taps fill successive rows. Reusing a word swaps the existing matches.
    bank.nth(words.index(correct[0])).click()
    bank.nth(words.index(correct[1])).click()
    expect(selects.nth(0)).to_have_value(correct[0])
    expect(selects.nth(1)).to_have_value(correct[1])
    selects.nth(0).select_option(correct[1])
    expect(selects.nth(1)).to_have_value(correct[0])
    page.locator("#match-check").click()
    expect(page.locator("#match-result")).to_have_count(0)
    expect(page.locator("#match-message")).to_contain_text("still needs a match")

    # A half-filled worksheet must survive a reload with both the bank and rows in order.
    page.reload()
    expect(prompts).to_have_text(initial)
    assert bank.evaluate_all("(buttons) => buttons.map(b => b.dataset.word)") == words
    expect(selects.nth(0)).to_have_value(correct[1])
    expect(selects.nth(1)).to_have_value(correct[0])
    for i in range(2, 5):
        selects.nth(i).select_option(correct[i])
    page.locator("#match-check").click()
    expect(page.locator("#match-result")).to_contain_text("3 of 5 correct")
    expect(page.locator("#match-questions .incorrect")).to_have_count(2)
    page.reload()
    expect(page.locator("#match-result")).to_contain_text("3 of 5 correct")
    page.locator("#match-retry").click()
    retry = prompts.all_text_contents()
    assert len(retry) == 2 and set(retry) == set(initial[:2])
    assert bank.evaluate_all("(buttons) => buttons.map(b => b.dataset.word)") == words
    for i, definition in enumerate(retry):
        selects.nth(i).select_option(answers[definition])
    page.locator("#match-check").click()
    expect(page.locator("#match-result")).to_contain_text("2 of 2 correct")

    size.select_option("10")
    expect(prompts).to_have_count(10)
    expect(bank).to_have_count(10)
    size.select_option("20")
    seen = set()
    for sheet in range(3):
        if sheet:
            page.locator("#match-new").click()
        definitions = prompts.all_text_contents()
        choices = bank.evaluate_all("(buttons) => buttons.map(b => b.dataset.word)")
        assert len(definitions) == len(set(choices)) == len(choices) == 20
        assert {answers[text] for text in definitions} == set(choices)
        assert seen.isdisjoint(definitions), "Repeated a definition before all three variants appeared"
        seen.update(definitions)
    assert seen == set(answers)
    check_size(page)


def check_definition_rotation(page):
    """All 20 words cycle through three different clues across meaning and recall rounds."""
    cards = {card["term"]: card for card in page.evaluate("HISTORY_TERMS")}
    assert len(cards) == 20
    seen = {name: set() for name in cards}
    for mode in ("choice", "type", "choice"):
        page.locator(f'a[href="#practice/{mode}"]:visible').first.click()
        page.get_by_role("button", name="20 terms", exact=True).click()
        page.get_by_role("button", name="Start round").click()
        questions = page.evaluate("JSON.parse(localStorage.getItem('alaina-empires-practice-round-v1')).questions")
        assert {q["term"] for q in questions} == set(cards)
        for q in questions:
            card = cards[q["term"]]
            assert q["prompt"] == [card["clue"], *card["extraClues"]][q["definitionIndex"]]
            seen[q["term"]].add(q["prompt"])
        first = questions[0]
        expect(page.locator(".practice-prompt")).to_have_text(first["prompt"])
        page.get_by_role("button", name="Show answer", exact=True).click()
        card = cards[first["term"]]
        definition = [card["simple"], card["detailed"], card["alternate"]][first["definitionIndex"]]
        expect(page.locator("#practice-feedback")).to_contain_text(definition)
        page.get_by_role("button", name="Pause round").click()
        page.reload()
    assert all(len(prompts) == 3 for prompts in seen.values())


def exercise(page, history_url):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(history_url, wait_until="domcontentloaded")
    page.get_by_role("link", name="Empires Vocabulary").click()
    page.wait_for_url("**/history/empires/")
    check_word_bank(page)
    page.get_by_role("link", name="Overview", exact=True).click()
    expect(page.get_by_role("heading", name=re.compile(r"^Empires\s*Vocabulary$"))).to_be_visible()
    expect(page.get_by_role("link", name="Start word bank quiz", exact=True)).to_have_attribute("href", "#matching")
    check_size(page)

    page.get_by_role("link", name="Open word list").first.click()
    search = page.get_by_role("searchbox")
    search.fill("Caravel")
    expect(page.get_by_role("heading", name="Caravel", exact=True)).to_be_visible()
    expect(page.locator(".entry .definition-list b")).to_have_text(
        ["Hull and shallow water", "How the sails worked", "The 1492 Atlantic crossing"]
    )
    search.fill("zznothing")
    expect(page.get_by_role("heading", name="No matching terms")).to_be_visible()
    page.get_by_role("link", name="Overview", exact=True).click()

    for mode in ("flash", "choice", "scenario", "type", "listen"):
        page.locator(f'a[href="#practice/{mode}"]:visible').first.click()
        expect(page.get_by_role("button", name="5 terms", exact=True)).to_have_attribute("aria-pressed", "true")
        page.get_by_role("button", name="Start round").click()
        saved = page.evaluate("JSON.parse(localStorage.getItem('alaina-empires-practice-round-v1'))")
        question = saved["questions"][0]
        if mode == "flash":
            page.get_by_role("button", name="Flip card").click()
            card = page.evaluate("term => HISTORY_TERMS.find(card => card.term === term)", question["term"])
            expect(page.locator(".practice-card .definition-list b")).to_have_text(card["definitionLabels"])
            expect(page.locator(".practice-card .definition-list p")).to_have_text([card["simple"], card["detailed"], card["alternate"]])
            expect(page.locator(".practice-sketch .sketch")).to_be_visible()
            page.get_by_role("button", name="Study again").click()
        else:
            if mode in ("choice", "scenario"):
                page.get_by_role("button", name=question["term"], exact=True).click()
            else:
                page.get_by_role("textbox", name="Your answer").fill(question["term"])
            page.get_by_role("button", name="Check answer", exact=True).click()
            expect(page.locator("#practice-feedback")).to_contain_text("Correct!")
            page.get_by_role("button", name="Next question").click()
        page.get_by_role("button", name="Pause round").click()
        page.reload()
        page.get_by_role("link", name="Resume round").click()
        expect(page.locator(".practice-stats")).to_contain_text("2 of 5")
        page.get_by_role("button", name="Pause round").click()
        expect(page.locator("#overview-view")).to_be_visible()
        check_size(page)
    check_definition_rotation(page)
    assert not errors, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Global Tapestry landing URL, the parent of empires/")
    parser.add_argument("--verify-assets", action="store_true")
    args = parser.parse_args()
    url = args.url.rstrip("/") + "/"
    if args.verify_assets:
        verify_files(url)
    with sync_playwright() as playwright:
        for engine in (playwright.chromium, playwright.webkit):
            browser = engine.launch()
            try:
                for width, height in [(390, 844), (1366, 768)]:
                    context = browser.new_context(viewport={"width": width, "height": height}, has_touch=width < 500)
                    try:
                        exercise(context.new_page(), url)
                        print(f"{engine.name} {width}px passed the shared word bank, 60 definitions, notebook, five modes, grading and resumed-round checks.", flush=True)
                    finally:
                        context.close()
            finally:
                browser.close()
