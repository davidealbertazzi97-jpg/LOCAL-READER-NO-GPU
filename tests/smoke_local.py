#!/usr/bin/env python3
"""Exercise the real loopback server, token boundary, queue, and cleanup."""

from __future__ import annotations

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
TOKEN = "smoke-test-" + "x" * 48


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
) -> tuple[int, object]:
    headers = {}
    if token:
        headers["X-Local-AI-Token"] = TOKEN
    if data is not None:
        parsed = urllib.parse.urlsplit(url)
        headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST" if data is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


def multipart() -> tuple[bytes, str]:
    boundary = "----local-ai-" + uuid.uuid4().hex
    parts = [
        (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="engine"\r\n\r\n'
            "text-statistics\r\n"
        ).encode(),
        (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="options"\r\n\r\n'
            '{"language":"it"}\r\n'
        ).encode(),
        (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="sample.txt"\r\n'
            "Content-Type: text/plain\r\n\r\n"
            "uno due tre\r\n"
        ).encode(),
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def main() -> int:
    port = free_port()
    with tempfile.TemporaryDirectory(prefix="local-ai-starter-smoke-") as temporary:
        root = Path(temporary)
        environment = os.environ.copy()
        environment.update(
            {
                "LOCAL_AI_APP_TOKEN": TOKEN,
                "LOCAL_AI_APP_PORT": str(port),
                "LOCAL_AI_APP_STARTER_DATA": str(root / "data"),
                "LOCAL_AI_APP_STARTER_STATE": str(root / "state"),
                "LOCAL_AI_APP_STARTER_OUTPUTS": str(root / "outputs"),
                "PYTHONPATH": str(APP_DIR / "runtime_guard"),
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
            }
        )
        environment.pop("LD_PRELOAD", None)
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
        )
        base = f"http://127.0.0.1:{port}"
        try:
            for _ in range(100):
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
            assert status == 200 and product["slug"] == "local-ai-app-starter"

            body, content_type = multipart()
            status, job = request_json(
                f"{base}/api/jobs",
                token=True,
                data=body,
                content_type=content_type,
            )
            assert status == 202, (status, job)
            job_id = job["id"]
            for _ in range(100):
                status, job = request_json(
                    f"{base}/api/jobs/{job_id}",
                    token=True,
                )
                assert status == 200
                if job["status"] in {"completed", "failed"}:
                    break
                time.sleep(0.05)
            assert job["status"] == "completed", job
            assert "options" not in job
            assert not (root / "data" / "work" / job_id).exists()
            assert (root / "outputs" / job_id / "report.json").is_file()
            print("Local server smoke test passed.")
        finally:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
