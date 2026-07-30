from __future__ import annotations

import subprocess
import threading
import time
from collections.abc import Sequence
from pathlib import Path

_LOCK = threading.Lock()
_ACTIVE: set[subprocess.Popen[str]] = set()
_STOPPING = False


class WorkerStopping(RuntimeError):
    pass


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
) -> subprocess.CompletedProcess[str]:
    with _LOCK:
        if _STOPPING:
            raise WorkerStopping("application shutdown is in progress")
        process = subprocess.Popen(
            list(command),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _ACTIVE.add(process)
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
