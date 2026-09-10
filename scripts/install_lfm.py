#!/usr/bin/env python3
"""Install the approved local LFM model and a CPU llama.cpp executable."""

from __future__ import annotations

import hashlib
import os
import platform
import posixpath
import shutil
import stat
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PureWindowsPath

APP_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = APP_DIR / "models" / "lfm"
BIN_DIR = APP_DIR / "bin"
MODEL = (
    "LFM2.5-230M-Q8_0.gguf",
    246_598_496,
    "855be85429300602eda72958547614703541b7d6dd965a8f8f6052b85a7aa935",
)
MODEL_URL = "https://huggingface.co/LiquidAI/LFM2.5-230M-GGUF/resolve/main/"
LLAMA_RELEASE = "b10886"
LLAMA_BUILDS = {
    ("Linux", "x86_64"): (
        f"llama-{LLAMA_RELEASE}-bin-ubuntu-x64.tar.gz",
        16_814_289,
        "3026e7653fbc74d54aa74f9bd495a4725ec6603e56a86f621fe2e412b4243f48",
    ),
    ("Darwin", "arm64"): (
        f"llama-{LLAMA_RELEASE}-bin-macos-arm64.tar.gz",
        11_141_049,
        "7c91c1c307a0eb13f921310a965a064f4549b810f3a93ba869ea4d8d1c25bc98",
    ),
    ("Windows", "AMD64"): (
        f"llama-{LLAMA_RELEASE}-bin-win-cpu-x64.zip",
        18_425_336,
        "44067316062506f5900e9afe0b48080d58d33018a937deb8fffb31b713b1afc7",
    ),
}
LLAMA_URL = f"https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_RELEASE}/"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verified(path: Path, expected_size: int, expected_hash: str) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == expected_size
        and digest(path) == expected_hash
    )


def download(
    url: str, destination: Path, expected_size: int, expected_hash: str
) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in {
        "github.com",
        "huggingface.co",
    }:
        raise RuntimeError("unexpected model or runtime download URL")
    temporary = destination.with_suffix(destination.suffix + ".download")
    temporary.unlink(missing_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Local-Accessibility-Studio/0.3"},
    )
    try:
        # The URL is fixed above and the payload is checked before replacement.
        # nosemgrep
        response = urllib.request.urlopen(request, timeout=120)  # nosec B310
        received = 0
        with response, temporary.open("xb") as output:
            while chunk := response.read(1024 * 1024):
                received += len(chunk)
                if received > expected_size:
                    raise RuntimeError("download exceeds the approved size")
                output.write(chunk)
        if received != expected_size or not verified(
            temporary, expected_size, expected_hash
        ):
            raise RuntimeError("download checksum verification failed")
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def local_llama_candidates() -> list[Path]:
    suffix = ".exe" if os.name == "nt" else ""
    candidates = [
        BIN_DIR / f"llama-cli{suffix}",
        BIN_DIR / f"llama-completion{suffix}",
    ]
    configured = os.environ.get("LOCAL_ACCESSIBILITY_STUDIO_LLAMA_CLI")
    if configured:
        candidates.insert(0, Path(configured).expanduser())
    for name in ("llama-cli", "llama-completion"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    candidates.extend(
        Path.home() / "llama.cpp" / build / "bin" / f"{name}{suffix}"
        for build in ("build", "build-local-reader", "build-cuda")
        for name in ("llama-cli", "llama-completion")
    )
    return candidates


def safe_members(archive: tarfile.TarFile | zipfile.ZipFile) -> list[object]:
    if isinstance(archive, tarfile.TarFile):
        members = archive.getmembers()
    else:
        members = archive.infolist()
    for member in members:
        raw_name = (
            member.name if isinstance(member, tarfile.TarInfo) else member.filename
        )
        name = raw_name.replace("\\", "/")
        path = Path(name)
        if path.is_absolute() or PureWindowsPath(name).drive or ".." in path.parts:
            raise RuntimeError("runtime archive contains an unsafe path")
        if isinstance(member, tarfile.TarInfo):
            if member.issym() or member.islnk():
                target = member.linkname.replace("\\", "/")
                resolved = posixpath.normpath(
                    posixpath.join(
                        posixpath.dirname(name) if member.issym() else "", target
                    )
                )
                if (
                    target.startswith("/")
                    or PureWindowsPath(target).drive
                    or resolved == ".."
                    or resolved.startswith("../")
                ):
                    raise RuntimeError("runtime archive contains an unsafe link")
            elif not (member.isfile() or member.isdir()):
                raise RuntimeError("runtime archive contains a special file")
        elif stat.S_ISLNK(member.external_attr >> 16):
            raise RuntimeError("runtime ZIP contains a link")
    return members


def install_llama() -> None:
    if any(candidate.is_file() for candidate in local_llama_candidates()):
        print("Using an existing llama.cpp executable")
        return
    build = LLAMA_BUILDS.get((platform.system(), platform.machine()))
    if build is None:
        raise RuntimeError(
            f"No approved llama.cpp build for {platform.system()}/{platform.machine()}"
        )
    archive_name, archive_size, archive_hash = build
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="llama-runtime-", dir=BIN_DIR) as temp_dir:
        archive_path = Path(temp_dir) / archive_name
        print(f"Downloading verified llama.cpp {LLAMA_RELEASE}...")
        download(
            urllib.parse.urljoin(LLAMA_URL, archive_name),
            archive_path,
            archive_size,
            archive_hash,
        )
        extract_dir = Path(temp_dir) / "extracted"
        extract_dir.mkdir()
        if archive_name.endswith(".zip"):
            with zipfile.ZipFile(archive_path) as archive:
                safe_members(archive)
                archive.extractall(extract_dir)  # nosec B202
        else:
            with tarfile.open(archive_path) as archive:
                safe_members(archive)
                archive.extractall(extract_dir, filter="data")  # nosec B202
        suffix = ".exe" if os.name == "nt" else ""
        executable = next(
            (
                path
                for path in extract_dir.rglob(f"llama-cli{suffix}")
                if path.is_file()
            ),
            None,
        )
        if executable is None:
            raise RuntimeError("llama.cpp archive did not contain llama-cli")
        for source in executable.parent.iterdir():
            if source.is_file():
                destination = BIN_DIR / source.name
                if destination.exists():
                    destination.unlink()
                shutil.copy2(source, destination)
        installed = BIN_DIR / executable.name
        if not installed.is_file():
            raise RuntimeError("llama.cpp executable was not installed")
        if os.name != "nt":
            installed.chmod(0o755)
    print(f"Installed llama.cpp {LLAMA_RELEASE}.")


def install_model() -> None:
    name, size, expected_hash = MODEL
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    destination = MODEL_DIR / name
    if verified(destination, size, expected_hash):
        print(f"Verified existing {name}")
        return
    for candidate in (
        Path.home() / ".lmstudio" / "models" / "LiquidAI" / "LFM2.5-230M-GGUF" / name,
    ):
        if verified(candidate, size, expected_hash):
            print(f"Using the verified existing local model {candidate}")
            return
    if destination.exists():
        raise RuntimeError(f"{destination} exists but is not the approved model")
    print("Downloading the verified local LFM2.5 model...")
    download(
        urllib.parse.urljoin(MODEL_URL, name) + "?download=true",
        destination,
        size,
        expected_hash,
    )
    print(f"Installed and verified {name}.")


def main() -> int:
    install_model()
    install_llama()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
