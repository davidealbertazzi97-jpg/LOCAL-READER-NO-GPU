#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


def request_headers(config: dict[str, object]) -> dict[str, str]:
    provider = str(config.get("provider", ""))
    key = str(config.get("api_key", ""))
    if provider == "claude":
        return {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Accept": "application/json",
        }
    return {"Authorization": f"Bearer {key}", "Accept": "application/json"}


def model_ids(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return []
    candidates = payload.get("data", payload.get("models", []))
    if not isinstance(candidates, list):
        return []
    values: set[str] = set()
    for item in candidates:
        if isinstance(item, str) and item.strip():
            values.add(item.strip())
        elif isinstance(item, dict):
            value = item.get("id", item.get("name", ""))
            if isinstance(value, str) and value.strip():
                values.add(value.strip())
    return sorted(values, key=str.casefold)


def fetch_models(config: dict[str, object]) -> list[str]:
    base_url = str(config.get("base_url", "")).rstrip("/")
    if not base_url:
        raise ValueError("provider endpoint is missing")
    request = urllib.request.Request(
        f"{base_url}/models",
        headers=request_headers(config),
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # nosec B310
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"provider request failed with status {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RuntimeError("provider model list could not be retrieved") from exc
    models = model_ids(payload)
    if not models:
        raise RuntimeError("provider returned no models")
    return models


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("provider configuration is invalid")
        models = fetch_models(config)
        Path(args.output).write_text(
            json.dumps({"models": models}, ensure_ascii=False), encoding="utf-8"
        )
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
