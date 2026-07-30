from __future__ import annotations

import json
import math
import os
import re
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

_TEST_ROOT = tempfile.TemporaryDirectory(prefix="local-accessibility-unit-")
os.environ["LOCAL_ACCESSIBILITY_STUDIO_DATA"] = str(Path(_TEST_ROOT.name) / "data")
os.environ["LOCAL_ACCESSIBILITY_STUDIO_STATE"] = str(Path(_TEST_ROOT.name) / "state")
os.environ["LOCAL_ACCESSIBILITY_STUDIO_OUTPUTS"] = str(
    Path(_TEST_ROOT.name) / "outputs"
)

from app.config import PATHS  # noqa: E402
from app.documents import (  # noqa: E402
    accessible_html,
    reading_text,
    validate_document,
    write_exports,
)
from app.engines import ENGINES  # noqa: E402
from app.product import load_product  # noqa: E402
from app.security import TOKEN_COOKIE  # noqa: E402
from app.speech_jobs import normalized_options, queue_speech_job  # noqa: E402
from app.store import JobStore  # noqa: E402
from app.utils import remove_work_tree, resolve_artifact, safe_name  # noqa: E402
from scripts.start import guarded_environment  # noqa: E402


def example_document() -> dict:
    return {
        "schema": 1,
        "revision": 1,
        "title": "Documento di prova",
        "language": "it",
        "pages": [
            {
                "number": 1,
                "preview": "pages/page-0001.webp",
                "blocks": [
                    {
                        "id": "p1-b1",
                        "role": "heading1",
                        "text": "Titolo",
                        "confidence": 0.99,
                        "bbox": [0, 0, 100, 30],
                    },
                    {
                        "id": "p1-b2",
                        "role": "paragraph",
                        "text": "Testo <privato> & controllato.",
                        "confidence": 0.78,
                        "bbox": [0, 40, 300, 80],
                    },
                    {
                        "id": "p1-b3",
                        "role": "page_number",
                        "text": "1",
                        "confidence": 1.0,
                        "bbox": [150, 700, 160, 720],
                    },
                ],
            }
        ],
    }


class ProductTests(unittest.TestCase):
    def test_product_and_engine_registry(self) -> None:
        product = load_product()
        self.assertEqual(product.slug, "local-accessibility-studio")
        self.assertEqual(product.version, "0.2.0")
        self.assertEqual(TOKEN_COOKIE, "local_accessibility_studio_token")
        self.assertEqual(
            set(ENGINES),
            {"accessible-document", "kokoro-italian"},
        )
        self.assertTrue(ENGINES["accessible-document"].user_upload)
        self.assertFalse(ENGINES["kokoro-italian"].user_upload)

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


class PublicUiTests(unittest.TestCase):
    def test_every_static_label_has_italian_and_english_copy(self) -> None:
        root = Path(__file__).resolve().parents[1]
        html = (root / "static" / "index.html").read_text(encoding="utf-8")
        javascript = (root / "static" / "app.js").read_text(encoding="utf-8")
        keys = set(re.findall(r'data-i18n="([^"]+)"', html))
        self.assertTrue(keys)
        for key in keys:
            occurrences = re.findall(
                rf"^    {re.escape(key)}:",
                javascript,
                flags=re.MULTILINE,
            )
            self.assertEqual(
                len(occurrences),
                2,
                f"{key!r} must have one Italian and one English value",
            )

    def test_static_page_does_not_load_remote_assets(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for name in ("index.html", "legal.html"):
            html = (root / "static" / name).read_text(encoding="utf-8")
            asset_urls = re.findall(r'(?:href|src)="([^"]+)"', html)
            self.assertTrue(asset_urls)
            for url in asset_urls:
                self.assertFalse(
                    url.startswith(("http://", "https://", "//")),
                    f"remote asset is not allowed in {name}: {url}",
                )


class DocumentTests(unittest.TestCase):
    def test_accessible_export_escapes_text_and_omits_page_number(self) -> None:
        document = validate_document(example_document())
        rendered = accessible_html(document)
        spoken = reading_text(document)
        self.assertIn("Testo &lt;privato&gt; &amp; controllato.", rendered)
        self.assertNotIn("<privato>", rendered)
        self.assertNotIn(">1<", rendered)
        self.assertIn("Testo <privato> & controllato.", spoken)

    def test_exports_are_regenerated_from_reviewed_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            document = write_exports(output, example_document())
            self.assertEqual(document["revision"], 1)
            self.assertTrue((output / "accessible.html").is_file())
            stored = json.loads((output / "document.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["pages"][0]["blocks"][1]["confidence"], 0.78)

    def test_duplicate_block_identifiers_are_rejected(self) -> None:
        value = example_document()
        value["pages"][0]["blocks"][1]["id"] = "p1-b1"
        with self.assertRaises(ValueError):
            validate_document(value)

    def test_non_finite_geometry_is_rejected(self) -> None:
        value = example_document()
        value["pages"][0]["blocks"][0]["bbox"][2] = math.nan
        with self.assertRaises(ValueError):
            validate_document(value)

    def test_english_document_defaults_to_american_speech(self) -> None:
        value = example_document()
        value["language"] = "en"
        document = validate_document(value)
        self.assertEqual(document["speech_language"], "en-us")

        value = example_document()
        value["pages"][0]["blocks"][0]["confidence"] = math.inf
        with self.assertRaises(ValueError):
            validate_document(value)


class PathTests(unittest.TestCase):
    def test_upload_name_and_artifact_boundary(self) -> None:
        self.assertEqual(safe_name(r"..\..\documento.pdf"), "documento.pdf")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ok.txt").write_text("ok", encoding="utf-8")
            self.assertEqual(resolve_artifact(root, "ok.txt"), root / "ok.txt")
            with self.assertRaises(ValueError):
                resolve_artifact(root, "../secret.txt")


class StoreTests(unittest.TestCase):
    def test_options_and_interruption_states(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = JobStore(Path(temporary) / "jobs.sqlite3")
            created = store.create(
                "upload",
                "accessible-document",
                "input.pdf",
                {"language": "it"},
            )
            self.assertEqual(created["options"], {"language": "it"})
            store.create("running", "accessible-document", "two.pdf", {})
            store.mark_queued("running")
            store.update("running", status="running", message="Running")
            self.assertEqual(
                set(store.interrupt_incomplete()),
                {"upload", "running"},
            )
            self.assertEqual(store.get("upload")["status"], "failed")
            self.assertEqual(
                set(store.finished_ids()),
                {"upload", "running"},
            )
            self.assertTrue(store.delete_finished("upload"))
            self.assertIsNone(store.get("upload"))


class SpeechQueueTests(unittest.TestCase):
    def test_reviewed_text_is_copied_and_queued_privately(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "reading.txt"
            source.write_text("Testo italiano revisionato.", encoding="utf-8")
            store = JobStore(root / "jobs.sqlite3")

            class Runner:
                def __init__(self) -> None:
                    self.queued: list[str] = []

                def submit(
                    self,
                    engine: str,
                    input_name: str,
                    options: dict,
                ) -> dict:
                    return store.create(
                        uuid.uuid4().hex,
                        engine,
                        input_name,
                        options,
                    )

                def enqueue(self, job_id: str) -> None:
                    self.queued.append(job_id)

            runner = Runner()
            child = queue_speech_job(
                runner,
                store,
                source,
                source_job="parent",
                voice="im_nicola",
                speed=1.0,
            )
            work_dir = PATHS.work / child["id"]
            try:
                self.assertEqual(child["status"], "queued")
                self.assertEqual(runner.queued, [child["id"]])
                self.assertEqual(child["options"]["language"], "it")
                self.assertEqual(
                    (work_dir / "reading.txt").read_text(encoding="utf-8"),
                    "Testo italiano revisionato.",
                )
            finally:
                remove_work_tree(work_dir)

    def test_invalid_speech_numbers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            normalized_options("im_nicola", math.nan)
        with self.assertRaises(ValueError):
            normalized_options("im_nicola", True)
        with self.assertRaises(ValueError):
            normalized_options("im_nicola", 1.0, "en-us")
        voice, speed, language = normalized_options("bf_emma", 1.0, "en-gb")
        self.assertEqual((voice, speed, language), ("bf_emma", 1.0, "en-gb"))


if __name__ == "__main__":
    unittest.main()
