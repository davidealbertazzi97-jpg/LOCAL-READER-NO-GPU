"""Real Kokoro/browser integration with every non-loopback browser request blocked.

Run: uv run --no-project --with playwright==1.55.0 python
tests/live_kokoro_browser.py --chrome /opt/google/chrome/chrome
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.start import stop_process  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chrome", required=True)
    parser.add_argument("--screenshot", default="live-kokoro.png")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="las-live-kokoro-") as temporary:
        env = os.environ.copy()
        for suffix in ("DATA", "STATE", "OUTPUTS"):
            env[f"LOCAL_READER_{suffix}"] = str(Path(temporary) / suffix.lower())
        token = "kokoro-browser-test-" + "x" * 48
        env.update(LOCAL_AI_APP_TOKEN=token, LOCAL_AI_APP_PORT="18768")
        # Apply the same Python network guard as the installed launcher.
        env["PYTHONPATH"] = str(ROOT / "runtime_guard")
        with (Path(temporary) / "server.log").open("w") as log:
            server = subprocess.Popen(
                [
                    str(
                        ROOT
                        / ".venv"
                        / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
                    ),
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "18768",
                    "--no-access-log",
                ],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=log,
                **(
                    {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                    if os.name == "nt"
                    else {"start_new_session": True}
                ),
            )
            try:
                base = "http://127.0.0.1:18768"
                for _ in range(100):
                    try:
                        with urllib.request.urlopen(base + "/health", timeout=1):
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
                        viewport={"width": 1280, "height": 1000}
                    )
                    context.add_init_script("""
window.localAudio = [];
const NativeAudio = window.Audio;
window.Audio = class extends NativeAudio {
  constructor(...args) {super(...args); window.localAudio.push(this);}
};
Object.defineProperty(window, 'speechSynthesis', {value: undefined});
Object.defineProperty(window, 'SpeechSynthesisUtterance', {value: undefined});
""")
                    blocked = []

                    def route_request(route):
                        host = urllib.parse.urlsplit(route.request.url).hostname
                        if host not in {"127.0.0.1", "localhost"}:
                            blocked.append(route.request.url)
                            route.abort()
                        else:
                            route.continue_()

                    context.route("**/*", route_request)
                    page = context.new_page()
                    page.set_default_timeout(120000)
                    errors = []
                    audio_requests = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on(
                        "request",
                        lambda request: (
                            audio_requests.append(request.url)
                            if "/api/live/audio" in request.url
                            else None
                        ),
                    )
                    page.goto(
                        base + "/?token=" + token,
                        timeout=120000,
                        wait_until="domcontentloaded",
                    )
                    page.locator("#main-nav [data-view-link=live]").click()
                    page.wait_for_function(
                        "() => document.querySelector('#live-voice').value "
                        "=== 'kokoro:if_sara'"
                    )
                    response = context.request.put(
                        base + "/api/settings",
                        headers={"Origin": base},
                        data={
                            "tts": {"offline_mode": True, "default_provider": "kokoro"}
                        },
                    )
                    assert response.ok
                    assert response.json()["settings"]["tts"]["offline_mode"]
                    page.reload()
                    page.locator("#main-nav [data-view-link=live]").click()
                    page.wait_for_function(
                        "() => document.querySelector('#live-voice').value "
                        "=== 'kokoro:if_sara'"
                    )
                    page.wait_for_function(
                        "() => document.querySelector('#offline-mode-toggle')"
                        ".getAttribute('aria-pressed') === 'true'"
                    )
                    assert page.locator("#live-voice option").count() == 4
                    text = (
                        "Kokoro legge sul computer senza Internet, "
                        "con la frase sottolineata. "
                        "Questa è la seconda frase da ascoltare.\n\n"
                        "Questo secondo paragrafo parte subito "
                        "quando viene selezionato."
                    )
                    page.locator("#live-input").fill(text)
                    page.locator("#live-form button").click()
                    start = time.monotonic()
                    page.locator("#live-play").click()
                    page.wait_for_function(
                        "() => localAudio.some(a => !a.paused && a.currentTime > .15)",
                        timeout=90000,
                    )
                    first_latency = time.monotonic() - start
                    print(f"First local audio: {first_latency:.2f}s", flush=True)
                    assert page.locator(".live-current").count() > 2
                    page.locator("#live-play").click()
                    assert page.locator("#live-play").inner_text() == "Riprendi"
                    paused_at = page.evaluate("localAudio.at(-1).currentTime")
                    page.wait_for_timeout(400)
                    assert (
                        abs(page.evaluate("localAudio.at(-1).currentTime") - paused_at)
                        < 0.05
                    )
                    page.locator("#live-play").click()
                    page.wait_for_function(
                        f"() => localAudio.at(-1).currentTime > {paused_at + 0.15}"
                    )
                    page.locator(".live-paragraph").nth(1).click()
                    page.wait_for_function(
                        "() => document.querySelector('.live-active')?.textContent"
                        ".startsWith('Questo secondo') && "
                        "localAudio.at(-1).currentTime > .15",
                        timeout=90000,
                    )
                    assert page.locator(".live-current").count() > 2
                    page.locator("#live-rate").select_option("1.5")
                    page.wait_for_function(
                        "() => localAudio.at(-1).currentTime > .15", timeout=90000
                    )
                    assert page.evaluate("localAudio.at(-1).playbackRate") == 1.5
                    page.screenshot(path=args.screenshot, full_page=True)
                    page.locator("#live-stop").click()
                    assert page.locator(".live-current").count() == 0
                    assert page.evaluate("localAudio.every(a => a.paused)")
                    page.locator("#live-voice").select_option("kokoro:im_nicola")
                    page.locator("#live-play").click()
                    page.wait_for_function(
                        "() => localAudio.at(-1).currentTime > .15", timeout=90000
                    )
                    page.locator("#main-nav [data-view-link=history]").click()
                    assert page.evaluate("localAudio.every(a => a.paused)")
                    jobs = context.request.get(base + "/api/jobs").json()
                    assert jobs == [], "live audio must not create History jobs"
                    assert not errors, errors
                    assert len(audio_requests) >= 4
                    print(
                        json.dumps(
                            {
                                "status": "passed",
                                "provider": "kokoro",
                                "offline_mode": True,
                                "native_browser_speech": False,
                                "first_audio_seconds": round(first_latency, 2),
                                "audio_requests": len(audio_requests),
                                "checks": [
                                    "all remote browser traffic blocked",
                                    "real local model and WAV playback",
                                    "actual phrase highlighting",
                                    "exact pause/resume",
                                    "paragraph jump",
                                    "speed",
                                    "Sara and Nicola",
                                    "stop",
                                    "navigation",
                                    "no History jobs",
                                ],
                                "blocked_remote_requests": len(blocked),
                            },
                            indent=2,
                        )
                    )
                    browser.close()
            finally:
                stop_process(server)


if __name__ == "__main__":
    main()
