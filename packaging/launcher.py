#!/usr/bin/env python3
"""First-run launcher for the portable Local Reader No GPU packages."""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

APP_NAME = "Local Reader No GPU"
APP_SLUG = "local-reader-no-gpu"
PYTHON_VERSION = "3.12"
UV_VERSION = "0.11.16"
UV_BUILDS = {
    ("Linux", "x86_64"): (
        "uv-x86_64-unknown-linux-gnu.tar.gz",
        "74947fe2c03315cf07e82ab3acc703eddef01aba4d5232a98e4c6825ec116131",
    ),
    ("Darwin", "arm64"): (
        "uv-aarch64-apple-darwin.tar.gz",
        "2b25be1af546be330b340b0a76b99f989daa6d92678fdffb87438e661e9d88fb",
    ),
    ("Windows", "AMD64"): (
        "uv-x86_64-pc-windows-msvc.zip",
        "dd9d6d6554bfab265bfa98aa8e8a406c5c3a7b97582f93de1f4d48d9154a0395",
    ),
}
UV_URL = f"https://github.com/astral-sh/uv/releases/download/{UV_VERSION}/"


def platform_root() -> Path:
    home = Path.home()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        return base / APP_NAME
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_NAME
    base = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share")).expanduser()
    return base / APP_SLUG


def payload_path() -> Path:
    if getattr(sys, "frozen", False):
        bundle_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return bundle_root / "payload.zip"
    return Path(__file__).resolve().with_name("payload.zip")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    print(f"\n-> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def safe_zip_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    for member in archive.infolist():
        name = member.filename.replace("\\", "/")
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("application payload contains an unsafe path")
        mode = member.external_attr >> 16
        if mode and (mode & 0o170000) == 0o120000:
            raise RuntimeError("application payload contains a link")
    archive.extractall(destination)  # nosec B202


def install_payload(payload: Path, root: Path) -> Path:
    if not payload.is_file():
        raise RuntimeError("the portable package is missing its application payload")
    digest = sha256(payload)
    runtime_root = root / "runtime"
    target = runtime_root / digest[:16]
    marker = target / ".payload-sha256"
    if marker.is_file() and marker.read_text(encoding="ascii").strip() == digest:
        return target
    runtime_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="payload-", dir=runtime_root) as temp_dir:
        temporary = Path(temp_dir)
        with zipfile.ZipFile(payload) as archive:
            safe_zip_extract(archive, temporary)
        (temporary / ".payload-sha256").write_text(digest + "\n", encoding="ascii")
        temporary.replace(target)
    return target


def download_uv(root: Path) -> Path:
    asset = UV_BUILDS.get((platform.system(), platform.machine()))
    if asset is None:
        raise RuntimeError(
            f"Unsupported portable package platform: "
            f"{platform.system()}/{platform.machine()}"
        )
    asset_name, expected_hash = asset
    tools = root / ".tools"
    tools.mkdir(parents=True, exist_ok=True)
    executable = tools / ("uv.exe" if os.name == "nt" else "uv")
    if executable.is_file():
        return executable
    archive_path = tools / asset_name
    archive_path.unlink(missing_ok=True)
    print("Downloading the verified Python runtime manager (uv)...", flush=True)
    request = urllib.request.Request(
        urllib.parse.urljoin(UV_URL, asset_name),
        headers={"User-Agent": "Local-Reader-No-GPU/0.3"},
    )
    with (
        urllib.request.urlopen(  # nosec B310
            request, timeout=120
        ) as response,
        archive_path.open("xb") as output,
    ):
        shutil.copyfileobj(response, output)
    if sha256(archive_path) != expected_hash:
        archive_path.unlink(missing_ok=True)
        raise RuntimeError("uv archive checksum verification failed")
    extract = tools / "uv-extracted"
    extract.mkdir()
    try:
        if asset_name.endswith(".zip"):
            with zipfile.ZipFile(archive_path) as archive:
                safe_zip_extract(archive, extract)
        else:
            with tarfile.open(archive_path) as archive:
                for member in archive.getmembers():
                    relative = Path(member.name)
                    if relative.is_absolute() or ".." in relative.parts:
                        raise RuntimeError("uv archive contains an unsafe path")
                    if member.issym() or member.islnk():
                        raise RuntimeError("uv archive contains a link")
            archive.extractall(extract)  # nosec B202
        candidate = next(extract.rglob("uv.exe" if os.name == "nt" else "uv"), None)
        if candidate is None or not candidate.is_file():
            raise RuntimeError("uv archive did not contain its executable")
        shutil.copy2(candidate, executable)
        if os.name != "nt":
            executable.chmod(0o755)
    finally:
        archive_path.unlink(missing_ok=True)
        shutil.rmtree(extract, ignore_errors=True)
    return executable


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Install local models and start Local Reader No GPU."
    )
    root.add_argument("--no-browser", action="store_true")
    root.add_argument("--version", action="store_true")
    root.add_argument("--verify-payload", action="store_true", help=argparse.SUPPRESS)
    return root


def main() -> int:
    args = parser().parse_args()
    if args.version:
        print(f"{APP_NAME} portable launcher")
        return 0
    if args.verify_payload:
        with zipfile.ZipFile(payload_path()) as archive:
            names = archive.namelist()
        if "app/main.py" not in names or "static/index.html" not in names:
            raise RuntimeError("the application payload is incomplete")
        print(f"Embedded application payload verified ({len(names)} files).")
        return 0
    root = platform_root()
    root.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        root.chmod(0o700)
    install = install_payload(payload_path(), root)
    uv = download_uv(root)
    environment = os.environ.copy()
    for variable in tuple(environment):
        if variable.startswith(("DYLD_", "LD_", "PIP_", "PYTHON", "UV_")):
            environment.pop(variable, None)
    environment["LOCAL_AI_APP_UV"] = str(uv)
    bootstrap = [
        str(uv),
        "run",
        "--no-project",
        "--python",
        PYTHON_VERSION,
        str(install / "scripts" / "bootstrap.py"),
        "--skip-desktop",
    ]
    core_python = (
        install / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    if not core_python.is_file():
        print(
            "Prima esecuzione: preparo Python, OCR, voci e modelli locali. "
            "Può richiedere qualche minuto e spazio su disco.",
            flush=True,
        )
        run(bootstrap, install, environment)
    if not core_python.is_file():
        raise RuntimeError("the core environment was not created")
    command = [str(core_python), str(install / "scripts" / "start.py")]
    if args.no_browser:
        command.append("--no-browser")
    run(command, install, environment)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"{APP_NAME}: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
