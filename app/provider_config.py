from __future__ import annotations

import copy
import json
import os
import tempfile
import threading
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .config import PATHS

SETTINGS_LOCK = threading.RLock()

AI_PROVIDER_PRESETS: dict[str, dict[str, str]] = {
    "local": {"label": "Solo locale", "base_url": "", "model": "LFM2.5-230M"},
    "mistral": {
        "label": "Mistral",
        "base_url": "https://api.mistral.ai/v1",
        "model": "mistral-small-latest",
    },
    "opencode": {
        "label": "OpenCode Zen",
        "base_url": "https://opencode.ai/zen/v1",
        "model": "big-pickle",
    },
    "gemini": {
        "label": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-3.8-flash",
    },
    "claude": {
        "label": "Anthropic Claude",
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-sonnet-4-6",
    },
    "nvidia-nim": {
        "label": "NVIDIA NIM",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "model": "meta/llama-3.3-70b-instruct",
    },
    "kilo": {
        "label": "Kilo Gateway",
        "base_url": "https://api.kilo.ai/api/gateway",
        "model": "auto",
    },
    "custom": {
        "label": "OpenAI-compatible personalizzato",
        "base_url": "",
        "model": "",
    },
}

TTS_PROVIDER_INFO: dict[str, dict[str, Any]] = {
    "edge-tts": {"label": "Edge-TTS", "network": True, "key": None},
    "kokoro": {"label": "Kokoro 82M", "network": False, "key": None},
    "voxtral": {"label": "Voxtral TTS (Mistral)", "network": True, "key": "mistral"},
    "fish": {"label": "Fish Audio", "network": True, "key": "fish"},
    "fish-local": {
        "label": "Fish Audio locale (Apple Silicon)",
        "network": False,
        "key": None,
    },
    "elevenlabs": {"label": "ElevenLabs", "network": True, "key": "elevenlabs"},
}


def _defaults() -> dict[str, Any]:
    return {
        "ai": {
            "provider": "local",
            "base_url": "",
            "model": "LFM2.5-230M",
            "local_model": "lfm",
            "api_key": "",
        },
        "ai_keys": {},
        "tts": {
            "default_provider": "edge-tts",
            "offline_mode": False,
            "offline_provider": "kokoro",
            "mistral": {
                "api_key": "",
                "model": "voxtral-mini-tts-2603",
                "voice_id": "",
            },
            "fish": {
                "api_key": "",
                "model": "s2.1",
                "voice_id": "",
            },
            "fish-local": {"model": "mlx-community/fish-audio-s2-pro-8bit"},
            "elevenlabs": {
                "api_key": "",
                "model": "eleven_multilingual_v2",
                "voice_id": "",
            },
            "kokoro": {"voice_it": "if_sara", "voice_en": "af_heart"},
        },
        "clones": [],
    }


def _settings_path() -> Path:
    return PATHS.data / "providers.json"


def _merge(default: dict[str, Any], saved: Any) -> dict[str, Any]:
    result = copy.deepcopy(default)
    if not isinstance(saved, dict):
        return result
    for key, value in saved.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key].update(value)
        elif key in result:
            result[key] = value
    return result


def load_settings() -> dict[str, Any]:
    path = _settings_path()
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, ValueError):
        return _defaults()
    result = _merge(_defaults(), saved)
    # Retired provider: keep private clone records and files, but use Kokoro.
    if result["tts"].get("default_provider") == "pocket-tts":
        result["tts"]["default_provider"] = "kokoro"
    result["tts"]["offline_provider"] = "kokoro"
    # Older builds called this provider OpenCode Go and stored its old
    # endpoint. Keep the provider id stable, but move existing installations
    # to the current OpenCode Zen endpoint automatically.
    if (
        result["ai"].get("provider") == "opencode"
        and result["ai"].get("base_url") == "https://opencode.ai/zen/go/v1"
    ):
        result["ai"]["base_url"] = AI_PROVIDER_PRESETS["opencode"]["base_url"]
    legacy_key = result["ai"].get("api_key", "")
    selected = result["ai"].get("provider", "local")
    if legacy_key and selected not in result["ai_keys"]:
        result["ai_keys"][selected] = legacy_key
    return result


def _write_settings(settings: dict[str, Any]) -> None:
    path = _settings_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=".providers-", suffix=".json", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        if os.name != "nt":
            os.chmod(temporary, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _string(value: Any, *, maximum: int = 512) -> str:
    if value is None:
        return ""
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError("provider setting is invalid")
    return value.strip()


def valid_url(value: str, *, allow_empty: bool = False) -> bool:
    if not value and allow_empty:
        return True
    parsed = urlparse(value)
    if parsed.scheme == "https" and parsed.netloc:
        return True
    return parsed.scheme == "http" and parsed.hostname in {
        "127.0.0.1",
        "localhost",
        "::1",
    }


def save_settings(payload: dict[str, Any]) -> dict[str, Any]:
    with SETTINGS_LOCK:
        return _save_settings(payload)


def _save_settings(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("settings must be an object")
    current = load_settings()
    ai = payload.get("ai", {})
    if ai:
        if not isinstance(ai, dict):
            raise ValueError("AI settings are invalid")
        provider = _string(ai.get("provider", current["ai"]["provider"]), maximum=32)
        if provider not in AI_PROVIDER_PRESETS:
            raise ValueError("unknown AI provider")
        base_url = _string(ai.get("base_url", current["ai"]["base_url"]))
        if provider not in {"local", "custom"}:
            base_url = AI_PROVIDER_PRESETS[provider]["base_url"]
        if not valid_url(base_url, allow_empty=provider in {"local"}):
            raise ValueError("the provider URL must use HTTPS, or local HTTP")
        current["ai"].update(
            {
                "provider": provider,
                "base_url": base_url,
                "model": _string(ai.get("model", current["ai"]["model"]), maximum=160),
                "local_model": _string(
                    ai.get("local_model", current["ai"].get("local_model", "lfm")),
                    maximum=32,
                ),
            }
        )
        if current["ai"]["local_model"] not in {"lfm", "gemma4"}:
            raise ValueError("unknown local text model")
        api_key = _string(ai.get("api_key"), maximum=1024)
        if api_key:
            current["ai_keys"][provider] = api_key
        current["ai"]["api_key"] = ""

    tts = payload.get("tts", {})
    if tts:
        if not isinstance(tts, dict):
            raise ValueError("TTS settings are invalid")
        selected = _string(
            tts.get("default_provider", current["tts"]["default_provider"]), maximum=32
        )
        if selected not in TTS_PROVIDER_INFO:
            raise ValueError("unknown speech provider")
        current["tts"]["default_provider"] = selected
        offline_mode = tts.get(
            "offline_mode", current["tts"].get("offline_mode", False)
        )
        if not isinstance(offline_mode, bool):
            raise ValueError("offline mode must be true or false")
        current["tts"]["offline_mode"] = offline_mode
        current["tts"]["offline_provider"] = "kokoro"
        if offline_mode and TTS_PROVIDER_INFO[selected]["network"]:
            current["tts"]["default_provider"] = current["tts"]["offline_provider"]
        elif (
            "offline_mode" in tts and "default_provider" not in tts and not offline_mode
        ):
            current["tts"]["default_provider"] = "edge-tts"
        for name in ("mistral", "fish", "elevenlabs"):
            section = tts.get(name, {})
            if not isinstance(section, dict):
                raise ValueError("TTS provider settings are invalid")
            target = current["tts"][name]
            key = _string(section.get("api_key"), maximum=1024)
            if key:
                target["api_key"] = key
            for field, maximum in (("model", 160), ("voice_id", 240)):
                if field in section:
                    target[field] = _string(section[field], maximum=maximum)
        for field, maximum in (("voice_it", 80), ("voice_en", 80)):
            if field in tts.get("kokoro", {}):
                current["tts"]["kokoro"][field] = _string(
                    tts["kokoro"][field], maximum=maximum
                )

    _write_settings(current)
    if current["tts"].get("offline_mode"):
        from .processes import stop_network_workers

        stop_network_workers()
    return public_settings()


def _configured(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def public_settings() -> dict[str, Any]:
    settings = load_settings()
    ai_provider_status = {
        provider: {
            "configured": provider == "local"
            or _configured(settings["ai_keys"].get(provider, ""))
        }
        for provider in AI_PROVIDER_PRESETS
    }
    return {
        "ai": {
            "provider": settings["ai"]["provider"],
            "base_url": settings["ai"]["base_url"],
            "model": settings["ai"]["model"],
            "local_model": settings["ai"].get("local_model", "lfm"),
            "configured": ai_provider_status[settings["ai"]["provider"]]["configured"],
            "providers": ai_provider_status,
        },
        "tts": {
            "default_provider": settings["tts"]["default_provider"],
            "offline_mode": bool(settings["tts"].get("offline_mode", False)),
            "offline_provider": settings["tts"].get("offline_provider", "kokoro"),
            "mistral": {
                "model": settings["tts"]["mistral"]["model"],
                "voice_id": settings["tts"]["mistral"]["voice_id"],
                "configured": _configured(settings["tts"]["mistral"].get("api_key")),
            },
            "fish": {
                "model": settings["tts"]["fish"]["model"],
                "voice_id": settings["tts"]["fish"]["voice_id"],
                "configured": _configured(settings["tts"]["fish"].get("api_key")),
            },
            "fish-local": copy.deepcopy(settings["tts"]["fish-local"]),
            "elevenlabs": {
                "model": settings["tts"]["elevenlabs"]["model"],
                "voice_id": settings["tts"]["elevenlabs"]["voice_id"],
                "configured": _configured(settings["tts"]["elevenlabs"].get("api_key")),
            },
            "kokoro": copy.deepcopy(settings["tts"]["kokoro"]),
        },
        "clones": [
            {
                **{
                    key: clone[key]
                    for key in ("id", "name", "provider", "voice_id")
                    if key in clone
                },
                "ready": (
                    private_voice_file(str(clone.get("reference_audio", "")))
                    is not None
                )
                if clone.get("provider") == "fish-local"
                else True,
            }
            for clone in settings.get("clones", [])
            if isinstance(clone, dict) and clone.get("provider") in TTS_PROVIDER_INFO
        ],
    }


def ai_runtime_config() -> dict[str, Any]:
    settings = load_settings()
    section = settings["ai"]
    provider = section["provider"]
    preset = AI_PROVIDER_PRESETS[provider]
    return {
        "provider": provider,
        "base_url": section["base_url"] or preset["base_url"],
        "model": section["model"] or preset["model"],
        "api_key": section.get("api_key", ""),
    }


def ai_config_for(provider: str) -> dict[str, Any]:
    settings = load_settings()
    if provider not in AI_PROVIDER_PRESETS:
        raise ValueError("unknown AI provider")
    if provider == "local":
        return {"provider": "local"}
    if provider == settings["ai"]["provider"]:
        result = dict(settings["ai"])
        result["api_key"] = settings["ai_keys"].get(provider, "")
    else:
        preset = AI_PROVIDER_PRESETS[provider]
        result = {
            "provider": provider,
            **preset,
            "api_key": settings["ai_keys"].get(provider, ""),
        }
    if not result.get("base_url") or not result.get("api_key"):
        raise ValueError("this provider is not configured")
    return result


def speech_runtime_config(provider: str) -> dict[str, Any]:
    settings = load_settings()
    if provider not in TTS_PROVIDER_INFO:
        raise ValueError("unknown speech provider")
    if provider in {"edge-tts", "kokoro", "fish-local"}:
        return {"provider": provider, **settings["tts"].get(provider, {})}
    section_name = "mistral" if provider == "voxtral" else provider
    section = settings["tts"][section_name]
    if not section.get("api_key"):
        raise ValueError("this speech provider has no API key configured")
    return {"provider": provider, **section}


def private_voice_file(value: str) -> Path | None:
    if not value:
        return None
    path = Path(value).resolve()
    root = (PATHS.data / "voice-clones").resolve()
    return path if root in path.parents and path.is_file() else None


def add_clone(
    *,
    provider: str,
    name: str,
    voice_id: str,
    reference_audio: str = "",
    reference_text: str = "",
) -> dict[str, Any]:
    clone_id = f"{provider}-{uuid.uuid4().hex}"
    clone = {"id": clone_id, "name": name, "provider": provider, "voice_id": voice_id}
    if reference_audio:
        clone["reference_audio"] = reference_audio
    if reference_text:
        clone["reference_text"] = reference_text
    with SETTINGS_LOCK:
        settings = load_settings()
        settings.setdefault("clones", []).append(clone)
        _write_settings(settings)
    return clone


def remove_clone(clone_id: str) -> bool:
    """Remove from the menu, retaining local samples for recovery."""
    with SETTINGS_LOCK:
        settings = load_settings()
        clone = next((c for c in settings["clones"] if c.get("id") == clone_id), None)
        if clone is None:
            return False
        settings["clones"].remove(clone)
        section = "mistral" if clone["provider"] == "voxtral" else clone["provider"]
        config = settings["tts"].get(section, {})
        if config.get("voice_id") == clone["voice_id"]:
            config["voice_id"] = ""
        _write_settings(settings)
        return True
