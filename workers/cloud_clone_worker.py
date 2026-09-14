#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import urllib.error
import urllib.request
from pathlib import Path


def request_json(request: urllib.request.Request) -> dict[str, object]:
    try:
        with urllib.request.urlopen(request, timeout=15 * 60) as response:  # nosec B310
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"voice cloning request failed with status {exc.code}"
        ) from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RuntimeError("voice cloning request could not be completed") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("voice cloning returned an invalid response")
    return payload


def multipart(fields: dict[str, str], file_path: Path) -> tuple[bytes, str]:
    boundary = "----LocalReaderNoGPUVoiceClone"
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            (
                f"--{boundary}\r\nContent-Disposition: form-data; "
                f'name="{name}"\r\n\r\n{value}\r\n'
            ).encode()
        )
    filename = file_path.name.replace('"', "_")
    content_type = mimetypes.guess_type(filename)[0] or "audio/wav"
    parts.append(
        (
            f"--{boundary}\r\nContent-Disposition: form-data; "
            f'name="files[]"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode()
        + file_path.read_bytes()
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("voxtral", "elevenlabs"), required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        key = str(config.get("api_key", ""))
        name = str(args.name)
        sample = Path(args.sample)
        if args.provider == "elevenlabs":
            body, content_type = multipart({"name": name}, sample)
            request = urllib.request.Request(
                "https://api.elevenlabs.io/v1/voices/add",
                data=body,
                headers={"xi-api-key": key, "Content-Type": content_type},
                method="POST",
            )
        else:
            payload = {
                "name": name,
                "sample_audio": base64.b64encode(sample.read_bytes()).decode("ascii"),
                "sample_filename": sample.name,
                "languages": ["it"],
            }
            request = urllib.request.Request(
                "https://api.mistral.ai/v1/audio/voices",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
        result = request_json(request)
        voice_id = result.get("voice_id") or result.get("id")
        if not isinstance(voice_id, str) or not voice_id:
            raise RuntimeError("voice cloning returned no voice ID")
        Path(args.output).write_text(
            json.dumps({"voice_id": voice_id}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
