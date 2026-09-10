from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from .config import PATHS
from .store import JobStore
from .utils import remove_work_tree

MAX_REFLOW_SOURCE_BYTES = 20 * 1024 * 1024
COPY_CHUNK = 1024 * 1024


class ReflowQueue(Protocol):
    def submit(
        self,
        engine: str,
        input_name: str,
        options: dict[str, Any],
    ) -> dict[str, Any]: ...

    def enqueue(self, job_id: str) -> None: ...


def queue_reflow_job(
    runner: ReflowQueue,
    store: JobStore,
    source: Path,
    *,
    source_job: str,
    device: str = "auto",
    provider: str = "local",
) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError("reading text is missing")
    if source.stat().st_size > MAX_REFLOW_SOURCE_BYTES:
        raise ValueError("reading text exceeds the reflow limit")
    child = runner.submit(
        "lfm-reflow",
        "reading.txt",
        {"source_job": source_job, "device": device, "provider": provider},
    )
    child_id = str(child["id"])
    work_dir = PATHS.work / child_id
    try:
        work_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
        received = 0
        with (
            source.open("rb") as input_handle,
            (work_dir / "reading.txt").open("xb") as output_handle,
        ):
            while chunk := input_handle.read(COPY_CHUNK):
                received += len(chunk)
                if received > MAX_REFLOW_SOURCE_BYTES:
                    raise ValueError("reading text exceeds the reflow limit")
                output_handle.write(chunk)
        child = store.mark_queued(child_id)
        runner.enqueue(child_id)
        return child
    except Exception:
        remove_work_tree(work_dir)
        store.update(
            child_id,
            status="failed",
            message="Reflow preparation failed",
            error="The text could not be copied into the private job.",
        )
        raise
