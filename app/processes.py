from __future__ import annotations

import subprocess
import threading
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

from .provider_config import SETTINGS_LOCK, load_settings

_LOCK = threading.Lock()
_ACTIVE: set[subprocess.Popen[str]] = set()
_NETWORK: set[subprocess.Popen[str]] = set()
_STOPPING = False


class WorkerStopping(RuntimeError):
    pass


class OfflineModeEnabled(RuntimeError):
    pass


def network_busy() -> bool:
    with _LOCK:
        return any(process.poll() is None for process in _NETWORK)


def stop_network_workers() -> None:
    """Stop cloud work immediately when the user switches to offline mode."""
    with _LOCK:
        for process in tuple(_NETWORK):
            _terminate(process, force=True)


def allow_worker_processes() -> None:
    global _STOPPING
    with _LOCK:
        _STOPPING = False


def _terminate(process: subprocess.Popen[str], *, force: bool = False) -> None:
    if process.poll() is not None:
        return
    try:
        if force:
            process.kill()
        else:
            process.terminate()
    except (OSError, ProcessLookupError):
        return


def stop_worker_processes(timeout: float = 8.0) -> None:
    global _STOPPING
    with _LOCK:
        _STOPPING = True
        active = tuple(_ACTIVE)
    for process in active:
        _terminate(process)
    deadline = time.monotonic() + timeout
    for process in active:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            break
    for process in active:
        _terminate(process, force=True)


def run_worker(
    command: Sequence[str],
    *,
    cwd: Path,
    timeout: float,
    env: Mapping[str, str] | None = None,
    network: bool = False,
) -> subprocess.CompletedProcess[str]:
    with SETTINGS_LOCK, _LOCK:
        if _STOPPING:
            raise WorkerStopping("application shutdown is in progress")
        if network and load_settings()["tts"].get("offline_mode"):
            raise OfflineModeEnabled(
                "Modalità offline attiva: i servizi online sono disabilitati."
            )
        process = subprocess.Popen(
            list(command),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=dict(env) if env is not None else None,
        )
        _ACTIVE.add(process)
        if network:
            _NETWORK.add(process)
    try:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            _terminate(process)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                _terminate(process, force=True)
                stdout, stderr = process.communicate()
            raise subprocess.TimeoutExpired(
                command,
                timeout,
                output=stdout,
                stderr=stderr,
            ) from exc
        return subprocess.CompletedProcess(
            command,
            process.returncode,
            stdout,
            stderr,
        )
    finally:
        with _LOCK:
            _ACTIVE.discard(process)
            _NETWORK.discard(process)
