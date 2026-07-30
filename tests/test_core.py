from __future__ import annotations

import json
import math
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_TEST_ROOT = tempfile.TemporaryDirectory(prefix="local-accessibility-unit-")
os.environ["LOCAL_ACCESSIBILITY_STUDIO_DATA"] = str(Path(_TEST_ROOT.name) / "data")
os.environ["LOCAL_ACCESSIBILITY_STUDIO_STATE"] = str(Path(_TEST_ROOT.name) / "state")
os.environ["LOCAL_ACCESSIBILITY_STUDIO_OUTPUTS"] = str(
    Path(_TEST_ROOT.name) / "outputs"
)

from app.documents import (  # noqa: E402
    accessible_html,
    reading_text,
    validate_document,
    write_exports,
)
from app.engines import ENGINES  # noqa: E402
from app.product import load_product  # noqa: E402
from app.security import TOKEN_COOKIE  # noqa: E402
from app.store import JobStore  # noqa: E402
from app.utils import resolve_artifact, safe_name  # noqa: E402
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
            self.assertTrue(store.delete_finished("upload"))
            self.assertIsNone(store.get("upload"))


if __name__ == "__main__":
    unittest.main()
