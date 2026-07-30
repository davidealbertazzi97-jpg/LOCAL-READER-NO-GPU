from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_TEST_ROOT = tempfile.TemporaryDirectory(prefix="local-ai-starter-unit-")
os.environ["LOCAL_AI_APP_STARTER_DATA"] = str(Path(_TEST_ROOT.name) / "data")
os.environ["LOCAL_AI_APP_STARTER_STATE"] = str(Path(_TEST_ROOT.name) / "state")
os.environ["LOCAL_AI_APP_STARTER_OUTPUTS"] = str(Path(_TEST_ROOT.name) / "outputs")

from app.engines.example import TextStatisticsEngine  # noqa: E402
from app.product import load_product  # noqa: E402
from app.security import TOKEN_COOKIE  # noqa: E402
from app.store import JobStore  # noqa: E402
from app.utils import resolve_artifact, safe_name  # noqa: E402
from scripts.start import guarded_environment  # noqa: E402


class ProductTests(unittest.TestCase):
    def test_product_file_is_valid(self) -> None:
        product = load_product()
        self.assertEqual(product.slug, "local-ai-app-starter")
        self.assertIn(product.default_language, {"it", "en"})
        self.assertEqual(TOKEN_COOKIE, "local_ai_app_starter_token")

    def test_launcher_removes_inherited_injection_paths(self) -> None:
        hostile = {
            "LD_PRELOAD": "/tmp/not-a-real-library.so",
            "PYTHONHOME": "/tmp/not-a-python-home",
            "PYTHONPATH": "/tmp/not-a-python-path",
        }
        with mock.patch.dict(os.environ, hostile, clear=False):
            environment = guarded_environment("x" * 48, 54321)
        self.assertNotIn("PYTHONHOME", environment)
        self.assertNotEqual(environment.get("LD_PRELOAD"), hostile["LD_PRELOAD"])
        self.assertTrue(environment["PYTHONPATH"].endswith("runtime_guard"))
        self.assertEqual(environment["LOCAL_AI_APP_PORT"], "54321")


class PathTests(unittest.TestCase):
    def test_upload_name_is_reduced_to_a_safe_basename(self) -> None:
        self.assertEqual(safe_name("../../private report.txt"), "private report.txt")
        self.assertEqual(safe_name(r"..\..\private.txt"), "private.txt")
        self.assertEqual(safe_name("CON.txt"), "_CON.txt")
        self.assertEqual(safe_name(".."), "document")

    def test_artifact_path_cannot_escape_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ok.txt").write_text("ok", encoding="utf-8")
            self.assertEqual(resolve_artifact(root, "ok.txt"), root / "ok.txt")
            with self.assertRaises(ValueError):
                resolve_artifact(root, "../secret.txt")


class EngineTests(unittest.TestCase):
    def test_example_engine_writes_only_declared_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "input.txt"
            output = root / "output"
            source.write_text("Hello world  \nSecond line\n", encoding="utf-8")
            result = TextStatisticsEngine().process(source, output, {})
            self.assertEqual(result.summary["words"], 4)
            self.assertEqual(
                {path.name for path in result.artifacts},
                {"normalized.txt", "report.json"},
            )
            report = json.loads((output / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["lines"], 2)


class StoreTests(unittest.TestCase):
    def test_options_survive_the_persistent_queue(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = JobStore(Path(temporary) / "jobs.sqlite3")
            created = store.create(
                "job-id",
                "text-statistics",
                "input.txt",
                {"language": "it"},
            )
            self.assertEqual(created["options"], {"language": "it"})
            self.assertEqual(store.get("job-id")["status"], "uploading")
            queued = store.mark_queued("job-id")
            self.assertEqual(queued["status"], "queued")
            self.assertEqual(store.pending_ids(), ["job-id"])

    def test_interrupted_uploads_and_running_jobs_are_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = JobStore(Path(temporary) / "jobs.sqlite3")
            store.create("upload", "text-statistics", "one.txt", {})
            store.create("running", "text-statistics", "two.txt", {})
            store.mark_queued("running")
            store.update("running", status="running", message="Running")
            self.assertEqual(
                set(store.interrupt_incomplete()),
                {"upload", "running"},
            )
            self.assertEqual(store.get("upload")["status"], "failed")
            self.assertEqual(store.get("running")["status"], "failed")


if __name__ == "__main__":
    unittest.main()
