"""Optional integration test: isolated Chromium, deterministic speech events.

Run with uv run --no-project --with playwright==1.55.0 python
tests/live_reader_browser.py --chrome /opt/google/chrome/chrome
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MOCK = """
const local = {name: 'Italian test voice', voiceURI: 'test:it',
  lang: 'it-IT', localService: true};
const online = {name: 'Online test voice', voiceURI: 'test:online',
  lang: 'it-IT', localService: false};
window.testSpeech = {utterances: [], paused: false, cancelled: 0,
  voices: [local, online], getVoices() {return this.voices;},
  addEventListener() {}, cancel() {this.cancelled++;},
  pause() {this.paused = true;}, resume() {this.paused = false;},
  speak(u) {this.utterances.push(u); u.onstart();}
};
Object.defineProperty(window, 'speechSynthesis', {value: window.testSpeech});
Object.defineProperty(window, 'SpeechSynthesisUtterance', {
  value: class {constructor(text) {this.text = text;}}});
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chrome", required=True)
    parser.add_argument("--python", default=str(ROOT / ".venv/bin/python"))
    parser.add_argument("--screenshot", default="/tmp/las-live-reader.png")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="las-live-browser-") as temporary:
        env = os.environ.copy()
        for suffix in ("DATA", "STATE", "OUTPUTS"):
            env[f"LOCAL_ACCESSIBILITY_STUDIO_{suffix}"] = str(
                Path(temporary) / suffix.lower()
            )
        env["LOCAL_AI_APP_TOKEN"] = "live-browser-test-" + "x" * 48
        env["LOCAL_AI_APP_PORT"] = "18767"
        with (Path(temporary) / "server.log").open("w") as log:
            server = subprocess.Popen(
                [args.python, "-m", "uvicorn", "app.main:app", "--port", "18767"],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=log,
            )
            try:
                for _ in range(100):
                    try:
                        with urllib.request.urlopen(
                            "http://127.0.0.1:18767/health", timeout=1
                        ):
                            break
                    except (urllib.error.URLError, TimeoutError):
                        time.sleep(0.1)
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(
                        executable_path=args.chrome,
                        headless=True,
                        args=["--no-sandbox"],
                    )
                    context = browser.new_context(
                        viewport={"width": 1440, "height": 1100}
                    )
                    context.add_init_script(MOCK)
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.route("https://api.github.com/**", lambda route: route.abort())
                    page.goto(
                        "http://127.0.0.1:18767/?token=" + env["LOCAL_AI_APP_TOKEN"]
                    )
                    page.locator("#main-nav [data-view-link=live]").click()
                    page.locator("#live-input").fill(
                        "Lettura 🌍, città e parole. Una seconda frase.\n\n"
                        "Questo paragrafo parte subito.\n\n"
                        "<img src=x onerror=alert(1)> è solo testo."
                    )
                    page.locator("#live-form button").click()
                    assert page.locator(".live-paragraph").count() == 3
                    assert page.locator("#live-paper img").count() == 0
                    page.locator(".live-paragraph").nth(0).click()
                    assert page.locator(".live-current").count() > 1
                    page.evaluate(
                        "testSpeech.utterances.at(-1).onboundary({name:'word',charIndex:12})"
                    )
                    assert page.locator(".live-current").inner_text() == "città"
                    page.locator("#live-play").click()
                    assert page.locator("#live-play").inner_text() == "Riprendi"
                    assert page.evaluate("testSpeech.paused")
                    page.locator("#live-play").click()
                    assert not page.evaluate("testSpeech.paused")
                    page.locator(".live-paragraph").nth(1).click()
                    assert page.evaluate(
                        "testSpeech.utterances.at(-1).text"
                    ).startswith("Questo paragrafo")
                    page.locator("#live-stop").click()
                    assert page.locator(".live-current").count() == 0
                    page.locator(".live-paragraph").nth(0).focus()
                    page.keyboard.press("ArrowDown")
                    page.keyboard.press("Enter")
                    assert (
                        page.locator(".live-active").inner_text().startswith("Questo")
                    )
                    page.locator("#live-rate").select_option("1.5")
                    assert page.evaluate("testSpeech.utterances.at(-1).rate") == 1.5
                    page.locator("#live-voice").select_option("test:online")
                    page.evaluate(
                        "document.querySelector('#offline-mode-toggle').setAttribute('aria-pressed','true');"
                        "document.dispatchEvent(new Event('studio-offline'))"
                    )
                    assert page.locator("#live-voice option").count() == 1
                    assert page.locator("#live-voice").input_value() == "test:it"
                    page.locator("#language-select").select_option("en")
                    assert page.locator("#live-title").inner_text() == "Live reading"
                    page.locator("#language-select").select_option("it")
                    page.locator(".live-paragraph").nth(1).click()
                    page.screenshot(path=args.screenshot, full_page=True)
                    page.locator("#main-nav [data-view-link=history]").click()
                    count = page.evaluate("testSpeech.utterances.length")
                    page.evaluate("testSpeech.utterances.at(-1).onend()")
                    assert page.evaluate("testSpeech.utterances.length") == count
                    page.locator("#main-nav [data-view-link=live]").click()
                    page.reload()
                    page.locator("#main-nav [data-view-link=live]").click()
                    assert page.locator(".live-paragraph").count() == 3
                    assert "2 / 3" in page.locator("#live-position").inner_text()
                    assert page.evaluate("testSpeech.utterances.length") == 0
                    page.set_viewport_size({"width": 390, "height": 844})
                    assert page.evaluate(
                        "document.documentElement.scrollWidth <= innerWidth"
                    )
                    page.evaluate(
                        "testSpeech.voices = []; "
                        "document.dispatchEvent(new Event('studio-offline'))"
                    )
                    assert page.locator("#live-play").is_disabled()
                    assert "Nessuna voce" in page.locator("#live-status").inner_text()
                    page.reload()
                    page.evaluate(
                        "documentValue = {pages: [{blocks: ["
                        "{role:'paragraph', text:'Correzione non ancora salvata.'},"
                        "{role:'exclude', text:'ESCLUSO'},"
                        "{role:'page_number', text:'99'}]}]};"
                        "document.querySelector('#document-live').click()"
                    )
                    assert page.locator("#live-paper").inner_text() == (
                        "Correzione non ancora salvata."
                    )
                    page.evaluate(
                        "document.querySelector('#text-workspace').value = "
                        "'Bozza del testo corretta.';"
                        "document.querySelector('#text-live').click()"
                    )
                    assert "Bozza del testo" in page.locator("#live-paper").inner_text()
                    page.locator("#live-edit").click()
                    page.locator("#live-file").set_input_files(
                        {
                            "name": "lettura.txt",
                            "mimeType": "text/plain",
                            "buffer": "File città.\n\nAltro paragrafo.".encode(),
                        }
                    )
                    page.wait_for_function(
                        "() => document.querySelector('#live-paper').textContent"
                        ".includes('File città.')"
                    )
                    assert page.locator(".live-paragraph").count() == 2
                    page.evaluate(
                        "async () => { const job = await submitText("
                        "'Live history test',"
                        "'Testo dalla cronologia.', "
                        "{auto_speech:false, preserve_text:true});"
                        "await waitForJob(job.id, () => {}); await renderJobs(); }"
                    )
                    page.locator("#main-nav [data-view-link=history]").click()
                    page.locator(".job").filter(
                        has_text="Live history test"
                    ).get_by_role("button", name="Lettura live", exact=True).click()
                    page.wait_for_function(
                        "() => document.querySelector('#live-paper').textContent"
                        ".includes('Testo dalla cronologia.')"
                    )
                    assert not errors, errors
                    browser.close()
                    print(
                        "Live reader browser integration passed; screenshot:",
                        args.screenshot,
                    )
            finally:
                server.terminate()
                server.wait(timeout=15)


if __name__ == "__main__":
    main()
