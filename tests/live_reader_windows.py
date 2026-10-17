"""Optional native Windows integration using real Edge/Windows speech events."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    edge = Path(os.environ["PROGRAMFILES(X86)"]) / (
        "Microsoft/Edge/Application/msedge.exe"
    )
    assert edge.is_file(), "Microsoft Edge is required for this integration test"
    with tempfile.TemporaryDirectory(prefix="las-native-live-") as temporary:
        env = os.environ.copy()
        for suffix in ("DATA", "STATE", "OUTPUTS"):
            env[f"LOCAL_ACCESSIBILITY_STUDIO_{suffix}"] = str(
                Path(temporary) / suffix.lower()
            )
        env["LOCAL_AI_APP_TOKEN"] = "live-native-test-" + "x" * 48
        env["LOCAL_AI_APP_PORT"] = "18768"
        with (Path(temporary) / "server.log").open("w") as log:
            server = subprocess.Popen(
                [
                    str(args.runtime / ".venv/Scripts/python.exe"),
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--port",
                    "18768",
                ],
                cwd=args.runtime,
                env=env,
                stdout=log,
                stderr=log,
            )
            try:
                for _ in range(150):
                    try:
                        with urllib.request.urlopen(
                            "http://127.0.0.1:18768/health", timeout=1
                        ):
                            break
                    except (urllib.error.URLError, TimeoutError):
                        time.sleep(0.2)
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(
                        executable_path=str(edge), headless=False
                    )
                    page = browser.new_page(viewport={"width": 1280, "height": 900})
                    page.set_default_timeout(90000)
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.route("https://api.github.com/**", lambda route: route.abort())
                    page.goto(
                        "http://127.0.0.1:18768/?token=" + env["LOCAL_AI_APP_TOKEN"],
                        wait_until="domcontentloaded",
                        timeout=120000,
                    )
                    page.locator("#main-nav [data-view-link=live]").click()
                    page.wait_for_function(
                        "() => document.querySelector('#live-voice')"
                        ".options.length > 0",
                        timeout=30000,
                    )
                    voices = page.evaluate(
                        "() => speechSynthesis.getVoices().map(v => "
                        "({name:v.name, lang:v.lang, local:v.localService}))"
                    )
                    assert any(v["local"] for v in voices), voices
                    page.evaluate(
                        "() => { window.speechEvents = []; "
                        "const nativeSpeak = "
                        "speechSynthesis.speak.bind(speechSynthesis);"
                        "speechSynthesis.speak = utterance => {"
                        "['start','boundary','end','error'].forEach(type => "
                        "utterance.addEventListener(type, event => "
                        "speechEvents.push({type, name:event.name, "
                        "index:event.charIndex, text:utterance.text, "
                        "error:event.error}))); nativeSpeak(utterance); }; }"
                    )
                    page.locator("#live-input").fill(
                        "Questa è una prova di lettura dal vivo con una voce reale "
                        "del sistema Windows, con parole sottolineate mentre vengono "
                        "lette e controlli per mettere in pausa e riprendere.\n\n"
                        "Secondo paragrafo: la voce deve iniziare immediatamente "
                        "da questo punto dopo un clic, senza aspettare il resto "
                        "del primo paragrafo."
                    )
                    page.locator("#live-form button").click()
                    page.locator(".live-paragraph").first.click()
                    page.wait_for_function(
                        "() => speechEvents.filter(e => e.type === 'boundary' "
                        "&& e.name === 'word').length >= 2 "
                        "&& document.querySelectorAll('.live-current').length === 1",
                        timeout=30000,
                    )
                    page.locator("#live-play").click()
                    assert page.locator("#live-play").inner_text() == "Riprendi"
                    page.locator("#live-play").click()
                    assert page.locator("#live-play").inner_text() == "Pausa"
                    page.locator(".live-paragraph").nth(1).click()
                    page.wait_for_function(
                        "() => speechEvents.some(e => e.type === 'start' "
                        "&& e.text.startsWith('Secondo paragrafo')) "
                        "&& document.querySelector('.live-active').textContent"
                        ".startsWith('Secondo paragrafo')",
                        timeout=15000,
                    )
                    page.wait_for_function(
                        "() => speechEvents.some(e => e.type === 'boundary' "
                        "&& e.text.startsWith('Secondo paragrafo') && e.name==='word')"
                        "&& document.querySelectorAll('.live-current').length === 1"
                    )
                    page.screenshot(path=str(args.output.with_suffix(".png")))
                    events = page.evaluate("speechEvents")
                    page.locator("#live-stop").click()
                    assert page.locator(".live-current").count() == 0
                    assert not errors, errors
                    report = {
                        "status": "passed",
                        "browser": browser.version,
                        "voices": voices,
                        "selected_voice": page.locator("#live-voice").input_value(),
                        "events": events,
                        "checks": [
                            "real word boundary highlighting",
                            "pause and resume",
                            "immediate paragraph switch",
                            "stop clears highlighting",
                        ],
                    }
                    args.output.write_text(
                        json.dumps(report, indent=2), encoding="utf8"
                    )
                    browser.close()
                    print("Native Windows live reading passed")
            finally:
                if os.name == "nt":
                    # The venv executable redirects to a child interpreter.
                    # Closing just its parent leaves SQLite and the port open.
                    subprocess.run(
                        ["taskkill.exe", "/PID", str(server.pid), "/T", "/F"],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    server.terminate()
                server.wait(timeout=20)


if __name__ == "__main__":
    main()
