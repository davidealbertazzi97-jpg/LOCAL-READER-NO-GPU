from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from app import jobs, utils


class JobCompletionTests(unittest.TestCase):
    def test_completed_status_is_published_after_private_input_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = SimpleNamespace(work=root / "work", outputs=root / "outputs")
            work = paths.work / "test-job"
            work.mkdir(parents=True)
            (work / "input.txt").write_text("Synthetic private input")
            job = {"input_name": "input.txt", "engine": "plain-text", "options": {}}
            engine = mock.Mock(engine_id="plain-text")
            engine.process.return_value = SimpleNamespace(artifacts=[], summary={})
            completed = []

            def update(job_id, **values):
                if values.get("status") == "completed":
                    self.assertFalse(work.exists())
                    completed.append(job_id)

            with (
                mock.patch.object(jobs, "PATHS", paths),
                mock.patch.object(utils, "PATHS", paths),
                mock.patch.object(jobs, "STORE") as store,
                mock.patch.dict(jobs.ENGINES, {"plain-text": engine}),
            ):
                store.get.return_value = job
                store.update.side_effect = update
                jobs.JobRunner()._process("test-job")
            self.assertEqual(completed, ["test-job"])
