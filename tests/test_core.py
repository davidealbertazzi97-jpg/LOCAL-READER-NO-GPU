from __future__ import annotations

import json
import math
import os
import re
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import uuid
from pathlib import Path
from unittest import mock

_TEST_ROOT = tempfile.TemporaryDirectory(prefix="local-reader-no-gpu-unit-")
os.environ["LOCAL_READER_NO_GPU_DATA"] = str(Path(_TEST_ROOT.name) / "data")
os.environ["LOCAL_READER_NO_GPU_STATE"] = str(Path(_TEST_ROOT.name) / "state")
os.environ["LOCAL_READER_NO_GPU_OUTPUTS"] = str(Path(_TEST_ROOT.name) / "outputs")

from starlette.requests import Request  # noqa: E402

from app.body_limit import RequestBodyLimitMiddleware  # noqa: E402
from app.config import PATHS, PORT, _private_directory  # noqa: E402
from app.documents import (  # noqa: E402
    accessible_html,
    document_from_text_pages,
    reading_text,
    validate_document,
    write_exports,
)
from app.engines import ENGINES  # noqa: E402
from app.engines.speech import EdgeSpeechEngine  # noqa: E402
from app.processes import (  # noqa: E402
    allow_worker_processes,
    run_worker,
    stop_worker_processes,
)
from app.product import load_product  # noqa: E402
from app.provider_config import (  # noqa: E402
    AI_PROVIDER_PRESETS,
    public_settings,
    save_settings,
)
from app.reflow import format_for_speech, validated_model_output  # noqa: E402
from app.security import TOKEN_COOKIE, origin_is_allowed  # noqa: E402
from app.speech_jobs import normalized_options, queue_speech_job  # noqa: E402
from app.store import JobStore  # noqa: E402
from app.utils import remove_work_tree, resolve_artifact, safe_name  # noqa: E402
from scripts.start import guarded_environment  # noqa: E402
from workers.audio_utils import text_chunks  # noqa: E402
from workers.provider_models_worker import model_ids, request_headers  # noqa: E402


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
        self.assertEqual(product.slug, "local-reader-no-gpu")
        self.assertEqual(product.version, "0.3.2")
        self.assertEqual(TOKEN_COOKIE, "local_reader_no_gpu_token")
        self.assertEqual(
            set(ENGINES),
            {"accessible-document", "plain-text", "edge-tts", "lfm-reflow"},
        )
        self.assertTrue(ENGINES["accessible-document"].user_upload)
        self.assertFalse(ENGINES["edge-tts"].user_upload)
        self.assertFalse(ENGINES["lfm-reflow"].user_upload)


class FrontendAccessibilityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.html = (root / "static" / "index.html").read_text(encoding="utf-8")
        cls.javascript = (root / "static" / "app.js").read_text(encoding="utf-8")

    def test_primary_landmarks_and_live_regions_are_present(self) -> None:
        self.assertIn('data-i18n-aria-label="mainNavLabel"', self.html)
        self.assertRegex(
            self.html,
            r'id="complete-progress"[\s\S]*class="progress-card"[\s\S]*role="status"',
        )
        self.assertRegex(
            self.html,
            r'id="review-live-status"[\s\S]*class="visually-hidden"[\s\S]*role="status"',
        )
        self.assertRegex(
            self.html,
            r'id="model-list"[\s\S]*class="model-list"[\s\S]*role="listbox"',
        )
        self.assertIn('id="offline-mode-toggle"', self.html)
        self.assertIn('id="complete-provider"', self.html)
        self.assertIn('id="advanced-settings" class="settings-advanced"', self.html)

    def test_dynamic_navigation_and_keyboard_review_contract_is_present(self) -> None:
        self.assertIn('link.setAttribute("aria-current", "page")', self.javascript)
        self.assertIn("heading.tabIndex = -1", self.javascript)
        self.assertIn('event.key === "ArrowDown"', self.javascript)
        self.assertIn('option.setAttribute("aria-posinset"', self.javascript)
        self.assertIn('t("blockMoved")', self.javascript)

    def test_offline_mode_is_persisted_as_kokoro_choice(self) -> None:
        value = save_settings(
            {"tts": {"default_provider": "kokoro", "offline_mode": True}}
        )
        self.assertTrue(value["tts"]["offline_mode"])
        self.assertEqual(public_settings()["tts"]["default_provider"], "kokoro")
        save_settings({"tts": {"default_provider": "edge-tts", "offline_mode": False}})

    def test_launcher_removes_inherited_injection_paths(self) -> None:
        hostile = {
            "GCONV_PATH": "/tmp/not-a-real-gconv",
            "LD_AUDIT": "/tmp/not-a-real-audit-library.so",
            "LD_PRELOAD": "/tmp/not-a-real-library.so",
            "OPENSSL_CONF": "/tmp/not-a-real-openssl-config",
            "PYTHONHOME": "/tmp/not-a-python-home",
            "PYTHONPATH": "/tmp/not-a-python-path",
        }
        with mock.patch.dict(os.environ, hostile, clear=False):
            environment = guarded_environment("x" * 48, 54321)
        self.assertNotIn("PYTHONHOME", environment)
        self.assertNotIn("GCONV_PATH", environment)
        self.assertNotIn("LD_AUDIT", environment)
        self.assertNotIn("OPENSSL_CONF", environment)
        self.assertNotEqual(environment.get("LD_PRELOAD"), hostile["LD_PRELOAD"])
        self.assertEqual(environment["PYTHONNOUSERSITE"], "1")
        self.assertTrue(environment["PYTHONPATH"].endswith("runtime_guard"))

    def test_dependency_locks_contain_every_direct_pin(self) -> None:
        root = Path(__file__).resolve().parents[1]
        profiles = {
            "requirements-core.lock": ("requirements-core.txt",),
            "requirements-dev.lock": (
                "requirements-core.txt",
                "requirements-dev.txt",
            ),
            "requirements-ocr.lock": ("requirements-ocr.txt",),
            "requirements-tts.lock": ("requirements-tts.txt",),
        }
        for lock_name, inputs in profiles.items():
            locked = (root / lock_name).read_text(encoding="utf-8").casefold()
            for input_name in inputs:
                direct_requirements = (root / input_name).read_text(encoding="utf-8")
                for line in direct_requirements.splitlines():
                    match = re.match(
                        r"([a-z0-9_.-]+)==([^;\s]+)",
                        line.casefold(),
                    )
                    if match:
                        direct_pin = f"{match.group(1)}=={match.group(2)}"
                        self.assertRegex(
                            locked,
                            rf"(?m)^{re.escape(direct_pin)}(?:\s|\\)",
                            f"{direct_pin} is missing from {lock_name}",
                        )

    @unittest.skipIf(os.name == "nt", "POSIX permission bits are not portable")
    def test_existing_private_directory_permissions_are_repaired(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "private"
            directory.mkdir(mode=0o755)
            directory.chmod(0o755)
            _private_directory(directory)
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)


class OriginTests(unittest.TestCase):
    @staticmethod
    def request(origin: str | None) -> Request:
        headers = []
        if origin is not None:
            headers.append((b"origin", origin.encode()))
        return Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/api/jobs",
                "headers": headers,
                "client": ("127.0.0.1", 12345),
                "scheme": "http",
                "server": ("127.0.0.1", PORT),
            }
        )

    def test_only_exact_numeric_loopback_origin_is_allowed(self) -> None:
        self.assertTrue(origin_is_allowed(self.request(f"http://127.0.0.1:{PORT}")))
        for origin in (
            None,
            "null",
            f"http://localhost:{PORT}",
            f"http://127.0.0.1:{PORT}/extra",
            "http://127.0.0.1:not-a-port",
            f"http://user@127.0.0.1:{PORT}",
        ):
            with self.subTest(origin=origin):
                self.assertFalse(origin_is_allowed(self.request(origin)))
        duplicate = self.request(f"http://127.0.0.1:{PORT}")
        duplicate.scope["headers"].append(
            (b"origin", f"http://127.0.0.1:{PORT}".encode())
        )
        self.assertFalse(origin_is_allowed(duplicate))


class RequestBodyLimitTests(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    async def consuming_app(scope, receive, send) -> None:
        del scope
        while True:
            message = await receive()
            if not message.get("more_body", False):
                break
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    @staticmethod
    def scope(headers: list[tuple[bytes, bytes]] | None = None) -> dict:
        return {
            "type": "http",
            "method": "POST",
            "path": "/api/jobs",
            "headers": headers or [],
        }

    async def invoke(
        self,
        messages: list[dict],
        *,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> list[dict]:
        queued = iter(messages)
        sent: list[dict] = []

        async def receive() -> dict:
            return next(queued)

        async def send(message: dict) -> None:
            sent.append(message)

        middleware = RequestBodyLimitMiddleware(
            self.consuming_app,
            path="/api/jobs",
            maximum=4,
        )
        await middleware(self.scope(headers), receive, send)
        return sent

    async def test_chunked_body_is_stopped_before_parser(self) -> None:
        sent = await self.invoke(
            [
                {"type": "http.request", "body": b"abc", "more_body": True},
                {"type": "http.request", "body": b"de", "more_body": False},
            ]
        )
        self.assertEqual(sent[0]["status"], 413)

    async def test_declared_oversize_and_ambiguous_lengths_are_rejected(self) -> None:
        oversize = await self.invoke(
            [],
            headers=[(b"content-length", b"5")],
        )
        self.assertEqual(oversize[0]["status"], 413)
        ambiguous = await self.invoke(
            [],
            headers=[
                (b"content-length", b"1"),
                (b"content-length", b"1"),
            ],
        )
        self.assertEqual(ambiguous[0]["status"], 400)


class WorkerProcessTests(unittest.TestCase):
    def test_offline_switch_stops_online_work_and_rejects_new_network_work(
        self,
    ) -> None:
        allow_worker_processes()
        save_settings({"tts": {"offline_mode": False}})
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ready = root / "ready"
            result = []

            def target():
                result.append(
                    run_worker(
                        [
                            sys.executable,
                            "-c",
                            "from pathlib import Path; import time; "
                            f"Path({str(ready)!r}).touch(); time.sleep(60)",
                        ],
                        cwd=root,
                        timeout=60,
                        network=True,
                    )
                )

            thread = threading.Thread(target=target)
            thread.start()
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(ready.exists())
                started = time.monotonic()
                value = save_settings({"tts": {"offline_mode": True}})
                self.assertTrue(value["tts"]["offline_mode"])
                self.assertLess(time.monotonic() - started, 2)
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive())
                self.assertNotEqual(result[0].returncode, 0)
                with self.assertRaises(RuntimeError):
                    run_worker(
                        [sys.executable, "-c", "pass"],
                        cwd=root,
                        timeout=5,
                        network=True,
                    )
                local = run_worker([sys.executable, "-c", "pass"], cwd=root, timeout=5)
                self.assertEqual(local.returncode, 0)
            finally:
                stop_worker_processes(timeout=2)
                thread.join(timeout=5)
                allow_worker_processes()
                save_settings({"tts": {"offline_mode": False}})

    def test_active_worker_is_terminated_during_shutdown(self) -> None:
        allow_worker_processes()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ready = root / "ready"
            result: list[subprocess.CompletedProcess[str] | Exception] = []

            def target() -> None:
                try:
                    result.append(
                        run_worker(
                            [
                                sys.executable,
                                "-c",
                                (
                                    "from pathlib import Path; import time; "
                                    f"Path({str(ready)!r}).write_text('ready'); "
                                    "time.sleep(60)"
                                ),
                            ],
                            cwd=root,
                            timeout=60,
                        )
                    )
                except Exception as exc:
                    result.append(exc)

            thread = threading.Thread(target=target)
            thread.start()
            deadline = time.monotonic() + 5
            while not ready.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(ready.exists())
            stop_worker_processes(timeout=2)
            thread.join(timeout=5)
            allow_worker_processes()
            self.assertFalse(thread.is_alive())
            self.assertTrue(result)


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
            asset_urls = re.findall(
                r'<(?:link|script|img)\b[^>]*(?:href|src)="([^"]+)"', html
            )
            self.assertTrue(asset_urls)
            for url in asset_urls:
                self.assertFalse(
                    url.startswith(("http://", "https://", "//")),
                    f"remote asset is not allowed in {name}: {url}",
                )


class ProviderTests(unittest.TestCase):
    def test_nvidia_nim_preset_uses_hosted_openai_endpoint(self) -> None:
        self.assertEqual(
            AI_PROVIDER_PRESETS["nvidia-nim"]["base_url"],
            "https://integrate.api.nvidia.com/v1",
        )
        self.assertEqual(
            AI_PROVIDER_PRESETS["nvidia-nim"]["model"],
            "meta/llama-3.3-70b-instruct",
        )

    def test_provider_model_response_is_normalized(self) -> None:
        payload = {"data": [{"id": "b"}, {"id": "A"}, {"id": "b"}, "c"]}
        self.assertEqual(model_ids(payload), ["A", "b", "c"])
        self.assertEqual(
            request_headers({"provider": "claude", "api_key": "secret"}),
            {
                "x-api-key": "secret",
                "anthropic-version": "2023-06-01",
                "Accept": "application/json",
            },
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

    def test_plain_text_pages_create_reviewable_blocks_without_previews(self) -> None:
        document = document_from_text_pages(
            "Testo",
            ["Prima riga.\nSeconda riga."],
            language="it",
            speech_language="it",
        )
        self.assertEqual(document["pages"][0]["preview"], "")
        self.assertEqual(len(document["pages"][0]["blocks"]), 2)


class ReflowTests(unittest.TestCase):
    def test_reflow_guard_preserves_non_whitespace_characters(self) -> None:
        source = "Una riga OCR.\nUn’altra riga."
        accepted = validated_model_output(source, "Una riga OCR. Un’altra riga.")
        self.assertEqual(accepted, "Una riga OCR. Un’altra riga.\n")
        self.assertIsNone(validated_model_output(source, "Testo modificato."))
        self.assertEqual(
            format_for_speech(source),
            "Una riga OCR. Un’altra riga.\n",
        )


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

    def test_running_job_with_private_source_is_requeued_after_restart(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            store = JobStore(root / "jobs.sqlite3")
            store.create("recover", "plain-text", "reading.txt", {})
            store.mark_queued("recover")
            store.update("recover", status="running", message="Running")
            source = root / "work" / "recover" / "reading.txt"
            source.parent.mkdir(parents=True)
            source.write_text("Testo da riprendere.", encoding="utf-8")

            recovered, failed = store.recover_incomplete(root / "work")

            self.assertEqual(recovered, ["recover"])
            self.assertEqual(failed, [])
            self.assertEqual(store.get("recover")["status"], "queued")


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
                voice="it-IT-GiuseppeMultilingualNeural",
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
            normalized_options("it-IT-GiuseppeMultilingualNeural", math.nan)
        with self.assertRaises(ValueError):
            normalized_options("it-IT-GiuseppeMultilingualNeural", True)
        with self.assertRaises(ValueError):
            normalized_options("it-IT-GiuseppeMultilingualNeural", 1.0, "en-us")
        voice, speed, language = normalized_options("en-GB-SoniaNeural", 1.0, "en-gb")
        self.assertEqual((voice, speed, language), ("en-GB-SoniaNeural", 1.0, "en-gb"))


class SpeechEngineTests(unittest.TestCase):
    def test_short_ocr_paragraphs_are_grouped_into_bounded_audio_chunks(self) -> None:
        text = "\n\n".join(
            f"Paragrafo {number}. Frase breve di prova." for number in range(1, 181)
        )
        chunks = list(text_chunks(text, maximum=500))

        self.assertLess(len(chunks), 20)
        self.assertTrue(all(len(chunk) <= 500 for chunk in chunks))
        self.assertEqual(" ".join(chunks).split(), text.split())

    def test_edge_failure_uses_local_kokoro_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "reading.txt"
            output = root / "output"
            source.write_text("Testo da leggere.", encoding="utf-8")

            calls = 0

            def run(command, **_kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return subprocess.CompletedProcess(command, 1, "", "offline")
                output.mkdir(parents=True, exist_ok=True)
                (output / "speech.mp3").write_bytes(b"local-audio")
                (output / "speech.json").write_text(
                    json.dumps(
                        {
                            "provider": "kokoro",
                            "voice": "if_sara",
                            "language": "it",
                        }
                    ),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, "", "")

            with (
                mock.patch(
                    "app.engines.speech.PATHS",
                    tts_python=Path(sys.executable),
                    app=root,
                ),
                mock.patch("app.engines.speech.run_worker", side_effect=run),
                mock.patch(
                    "app.engines.speech.verified_kokoro",
                    return_value=(root / "model.onnx", root / "voices.bin"),
                ),
            ):
                result = EdgeSpeechEngine().process(
                    source,
                    output,
                    {
                        "provider": "edge-tts",
                        "voice": "it-IT-GiuseppeMultilingualNeural",
                        "speed": 1.0,
                        "language": "it",
                    },
                )

            self.assertEqual(calls, 2)
            self.assertEqual(result.summary["provider"], "kokoro")
            self.assertEqual(result.summary["fallback_from"], "edge-tts")
            self.assertTrue((output / "speech.mp3").is_file())


if __name__ == "__main__":
    unittest.main()
