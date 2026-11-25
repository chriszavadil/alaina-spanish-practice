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
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Horizontal overflow"


def exercise(page, history_url):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(history_url, wait_until="domcontentloaded")
    page.get_by_role("link", name="Empires Vocabulary").click()
    page.wait_for_url("**/history/empires/")
    expect(page.get_by_role("heading", name=re.compile(r"^Empires\s*Vocabulary$"))).to_be_visible()
    check_size(page)

    page.get_by_role("link", name="Open word list").first.click()
    search = page.get_by_role("searchbox")
    search.fill("Caravel")
    expect(page.get_by_role("heading", name="Caravel", exact=True)).to_be_visible()
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
        check_size(page)
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
                        print(f"{engine.name} {width}px passed notebook, five modes, grading and resumed-round checks.", flush=True)
                    finally:
                        context.close()
            finally:
                browser.close()
