#!/usr/bin/env python3
"""Exercise the real local server; optionally run OCR, text input, and speech."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
TOKEN = "accessibility-smoke-" + "x" * 48
sys.path.insert(0, str(APP_DIR))
from scripts.start import stop_process  # noqa: E402


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def request_json(
    url: str,
    *,
    token: bool = False,
    data: bytes | None = None,
    content_type: str | None = None,
    method: str | None = None,
    origin: bool = True,
) -> tuple[int, object]:
    headers = {}
    if token:
        headers["X-Local-AI-Token"] = TOKEN
    if data is not None and origin:
        parsed = urllib.parse.urlsplit(url)
        headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method or ("POST" if data is not None else "GET"),
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


def multipart(path: Path, options: dict | None = None) -> tuple[bytes, str]:
    boundary = "----accessibility-" + uuid.uuid4().hex
    content_type = "application/pdf" if path.suffix == ".pdf" else "image/png"
    encoded_options = json.dumps(options or {})
    parts = [
        (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="engine"\r\n\r\n'
            "accessible-document\r\n"
        ).encode(),
        (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="options"\r\n\r\n'
            f"{encoded_options}\r\n"
        ).encode(),
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode()
        + path.read_bytes()
        + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def wait_for_job(base: str, job_id: str, timeout: float = 180.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status, value = request_json(f"{base}/api/jobs/{job_id}", token=True)
        assert status == 200
        job = dict(value)
        if job["status"] in {"completed", "failed"}:
            return job
        time.sleep(0.2)
    raise RuntimeError("job timeout")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    root.add_argument("--full", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    port = free_port()
    with tempfile.TemporaryDirectory(prefix="local-accessibility-smoke-") as temporary:
        root = Path(temporary)
        environment = os.environ.copy()
        environment.update(
            {
                "LOCAL_AI_APP_TOKEN": TOKEN,
                "LOCAL_AI_APP_PORT": str(port),
                "LOCAL_ACCESSIBILITY_STUDIO_DATA": str(root / "data"),
                "LOCAL_ACCESSIBILITY_STUDIO_STATE": str(root / "state"),
                "LOCAL_ACCESSIBILITY_STUDIO_OUTPUTS": str(root / "outputs"),
                "PYTHONPATH": str(APP_DIR / "runtime_guard"),
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
            }
        )
        environment.pop("LD_PRELOAD", None)
        process_group: dict[str, object]
        if os.name == "nt":
            process_group = {
                "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP,
            }
        else:
            process_group = {"start_new_session": True}
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--no-access-log",
            ],
            cwd=APP_DIR,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            **process_group,
        )
        base = f"http://127.0.0.1:{port}"
        try:
            for _ in range(160):
                if process.poll() is not None:
                    raise RuntimeError(process.stdout.read() if process.stdout else "")
                try:
                    status, health = request_json(f"{base}/health")
                    if status == 200 and health["status"] == "ok":
                        break
                except (OSError, KeyError):
                    time.sleep(0.05)
            else:
                raise RuntimeError("server startup timeout")

            status, _ = request_json(f"{base}/api/product")
            assert status == 401
            status, product = request_json(f"{base}/api/product", token=True)
            assert status == 200
            assert product["slug"] == "local-accessibility-studio"
            header_request = urllib.request.Request(
                f"{base}/api/product",
                headers={"X-Local-AI-Token": TOKEN},
            )
            with urllib.request.urlopen(header_request, timeout=5) as response:
                headers = response.headers
                assert headers["Cache-Control"] == "no-store"
                assert headers["Cross-Origin-Opener-Policy"] == "same-origin"
                assert headers["Cross-Origin-Resource-Policy"] == "same-origin"
                assert "default-src 'self'" in headers["Content-Security-Policy"]
            status, engines = request_json(f"{base}/api/engines", token=True)
            assert status == 200 and len(engines) == 4
            status, _ = request_json(
                f"{base}/api/jobs",
                token=True,
                data=b"",
                method="DELETE",
                origin=False,
            )
            assert status == 403
            if not args.full:
                status, cleared = request_json(
                    f"{base}/api/jobs",
                    token=True,
                    data=b"",
                    method="DELETE",
                )
                assert status == 200 and cleared["deleted"] == 0

            if args.full:
                sample = root / "sample.pdf"
                subprocess.run(
                    [
                        str(APP_DIR / ".venv-ocr" / "bin" / "python"),
                        str(APP_DIR / "tests" / "create_sample.py"),
                        str(sample),
                    ],
                    check=True,
                    cwd=APP_DIR,
                )
                body, content_type = multipart(
                    sample,
                    {
                        "auto_speech": True,
                        "document_language": "en",
                        "speech_language": "en-gb",
                        "voice": "en-GB-SoniaNeural",
                        "speed": 1.0,
                    },
                )
                status, queued = request_json(
                    f"{base}/api/jobs",
                    token=True,
                    data=body,
                    content_type=content_type,
                )
                assert status == 202, (status, queued)
                ocr_job = wait_for_job(base, queued["id"], timeout=900)
                assert ocr_job["status"] == "completed", ocr_job
                assert ocr_job["summary"]["audio"] == "Edge-TTS queued automatically"
                assert not (root / "data" / "work" / ocr_job["id"]).exists()

                status, jobs = request_json(f"{base}/api/jobs", token=True)
                assert status == 200
                automatic = next(job for job in jobs if job["engine"] == "edge-tts")
                automatic = wait_for_job(base, automatic["id"], timeout=300)
                assert automatic["status"] == "completed", automatic
                assert automatic["summary"]["voice"] == "en-GB-SoniaNeural"
                assert automatic["summary"]["language"] == "en-gb"
                automatic_audio = root / "outputs" / automatic["id"] / "speech.mp3"
                assert automatic_audio.stat().st_size > 10_000

                status, text_job = request_json(
                    f"{base}/api/text",
                    token=True,
                    data=json.dumps(
                        {
                            "title": "testo-incollato.txt",
                            "text": "Prima riga.\nSeconda riga.",
                            "options": {
                                "auto_speech": False,
                                "document_language": "it",
                                "speech_language": "it",
                                "voice": "it-IT-GiuseppeMultilingualNeural",
                                "speed": 1.0,
                            },
                        }
                    ).encode(),
                    content_type="application/json",
                )
                assert status == 202, (status, text_job)
                text_job = wait_for_job(base, text_job["id"])
                assert text_job["status"] == "completed", text_job
                status, text_payload = request_json(
                    f"{base}/api/jobs/{text_job['id']}/text",
                    token=True,
                )
                assert status == 200 and "Prima riga." in text_payload["text"]
                status, reflow_job = request_json(
                    f"{base}/api/jobs/{text_job['id']}/reflow",
                    token=True,
                    data=json.dumps({"device": "cpu"}).encode(),
                    content_type="application/json",
                )
                assert status == 202, (status, reflow_job)
                reflow_job = wait_for_job(base, reflow_job["id"])
                assert reflow_job["status"] == "completed", reflow_job
                assert reflow_job["summary"]["reasoning"] == "off"
                status, reflow_text = request_json(
                    f"{base}/api/jobs/{reflow_job['id']}/text",
                    token=True,
                )
                assert status == 200
                assert "Prima riga." in reflow_text["text"]

                status, document = request_json(
                    f"{base}/api/jobs/{ocr_job['id']}/document",
                    token=True,
                )
                assert status == 200 and document["pages"][0]["blocks"]
                assert document["language"] == "en"
                assert document["speech_language"] == "en-gb"
                document["title"] = "Documento corretto"
                document["pages"][0]["blocks"][0]["text"] = "Testo revisionato."
                status, document = request_json(
                    f"{base}/api/jobs/{ocr_job['id']}/document",
                    token=True,
                    data=json.dumps(document).encode(),
                    content_type="application/json",
                    method="PUT",
                )
                assert status == 200 and document["revision"] == 2
                stored_text = (
                    root / "outputs" / ocr_job["id"] / "reading.txt"
                ).read_text(encoding="utf-8")
                assert "Testo revisionato." in stored_text

                status, queued_speech = request_json(
                    f"{base}/api/jobs/{ocr_job['id']}/speech",
                    token=True,
                    data=json.dumps(
                        {
                            "voice": "en-US-AndrewMultilingualNeural",
                            "speed": 1.0,
                            "language": "en-us",
                        }
                    ).encode(),
                    content_type="application/json",
                )
                assert status == 202, (status, queued_speech)
                speech_job = wait_for_job(base, queued_speech["id"], timeout=300)
                assert speech_job["status"] == "completed", speech_job
                assert (
                    speech_job["summary"]["voice"] == "en-US-AndrewMultilingualNeural"
                )
                assert speech_job["summary"]["language"] == "en-us"
                audio = root / "outputs" / speech_job["id"] / "speech.mp3"
                assert audio.stat().st_size > 10_000
                status, deleted = request_json(
                    f"{base}/api/jobs/{automatic['id']}",
                    token=True,
                    data=b"",
                    method="DELETE",
                )
                assert status == 200 and deleted["deleted"]
                assert not (root / "outputs" / automatic["id"]).exists()
                status, cleared = request_json(
                    f"{base}/api/jobs",
                    token=True,
                    data=b"",
                    method="DELETE",
                )
                assert status == 200 and cleared["deleted"] == 4
                assert not (root / "outputs" / speech_job["id"]).exists()
                assert not (root / "outputs" / ocr_job["id"]).exists()
                status, jobs = request_json(f"{base}/api/jobs", token=True)
                assert status == 200 and jobs == []
                print("Full OCR, text, review, and Edge-TTS smoke test passed.")
            else:
                print("Local server core smoke test passed.")
        finally:
            stop_process(process)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
