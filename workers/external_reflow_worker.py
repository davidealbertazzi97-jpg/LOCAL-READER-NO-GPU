#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.reflow import (
    MAX_REFLOW_BYTES,
    format_for_speech,
    reflow_chunks,
    validated_model_output,
)


def _prompt(source: str) -> str:
    return (
        "Riorganizza SOLO spazi e ritorni a capo del testo fornito. "
        "Non cambiare nessuna parola, lettera, numero o segno di punteggiatura. "
        "Non riassumere, correggere, spiegare o aggiungere testo. "
        "Rispondi solo con il testo.\n\n"
        f"TESTO:\n<<<\n{source}\n>>>"
    )


def call_provider(config: dict[str, object], source: str) -> str:
    base_url = str(config.get("base_url", "")).rstrip("/")
    provider = str(config.get("provider", ""))
    prompt = _prompt(source)
    if provider == "claude":
        return _call_claude(config, base_url, prompt)
    return _call_openai_compatible(config, base_url, prompt)


def _call_openai_compatible(
    config: dict[str, object], base_url: str, prompt: str
) -> str:
    url = f"{base_url}/chat/completions"
    request = urllib.request.Request(
        url,
        data=json.dumps(
            {
                "model": str(config.get("model", "")),
                "temperature": 0,
                "messages": [
                    {
                        "role": "system",
                        "content": "Sei un impaginatore per la sintesi vocale.",
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            ensure_ascii=False,
        ).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.get('api_key', '')}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15 * 60) as response:  # nosec B310
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"provider request failed with status {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RuntimeError("provider request could not be completed") from exc
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("provider returned no text") from exc
    if not isinstance(content, str):
        raise RuntimeError("provider returned invalid text")
    return content


def _call_claude(config: dict[str, object], base_url: str, prompt: str) -> str:
    """Call Anthropic's Messages API, which is not OpenAI-compatible."""
    request = urllib.request.Request(
        f"{base_url}/messages",
        data=json.dumps(
            {
                "model": str(config.get("model", "")),
                "max_tokens": 8192,
                "temperature": 0,
                "system": "Sei un impaginatore per la sintesi vocale.",
                "messages": [{"role": "user", "content": prompt}],
            },
            ensure_ascii=False,
        ).encode("utf-8"),
        headers={
            "x-api-key": str(config.get("api_key", "")),
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15 * 60) as response:  # nosec B310
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"provider request failed with status {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RuntimeError("provider request could not be completed") from exc
    try:
        blocks = payload["content"]
        content = "".join(
            block["text"]
            for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        )
    except (KeyError, TypeError) as exc:
        raise RuntimeError("provider returned no text") from exc
    if not content:
        raise RuntimeError("provider returned no text")
    return content


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    try:
        source = Path(args.input)
        output = Path(args.output)
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        text = source.read_text(encoding="utf-8", errors="strict")
        if not text.strip():
            raise ValueError("reading text is empty")
        if len(text.encode("utf-8")) > MAX_REFLOW_BYTES:
            raise ValueError("reading text exceeds the local limit")
        result: list[str] = []
        fallback = 0
        for chunk in reflow_chunks(text):
            try:
                candidate = validated_model_output(chunk, call_provider(config, chunk))
            except (RuntimeError, OSError, urllib.error.URLError):
                candidate = None
            if candidate is None:
                fallback += 1
                result.append(format_for_speech(chunk))
            else:
                result.append(candidate)
        output.mkdir(parents=True, exist_ok=True)
        (output / "reading.txt").write_text(
            "\n\n".join(result).strip() + "\n", encoding="utf-8"
        )
        (output / "reflow-report.json").write_text(
            json.dumps(
                {
                    "engine": "OpenAI-compatible",
                    "provider": config.get("provider", "custom"),
                    "model": config.get("model", ""),
                    "chunks": len(result),
                    "fallback_chunks": fallback,
                    "content_guard": "non-whitespace characters preserved",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
