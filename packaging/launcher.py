#!/usr/bin/env python3
"""First-run launcher for the portable Local Reader No GPU packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PureWindowsPath

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
VC_REDIST_URL = "https://aka.ms/vc14/vc_redist.x64.exe"


def platform_root() -> Path:
    home = Path.home()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        return base / APP_NAME
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_NAME
    base = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share")).expanduser()
    return base / APP_SLUG


def refresh_windows_start_menu_shortcut(executable: Path, version: str) -> None:
    """Create a Start menu link using the Windows Shell COM interfaces."""
    if os.name != "nt":
        return

    import ctypes

    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", ctypes.c_ulong),
            ("Data2", ctypes.c_ushort),
            ("Data3", ctypes.c_ushort),
            ("Data4", ctypes.c_ubyte * 8),
        ]

    hresult = ctypes.c_long
    ole32 = ctypes.OleDLL("ole32")
    ole32.CLSIDFromString.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(GUID)]
    ole32.CLSIDFromString.restype = hresult
    ole32.CoInitialize.argtypes = [ctypes.c_void_p]
    ole32.CoInitialize.restype = hresult
    ole32.CoCreateInstance.argtypes = [
        ctypes.POINTER(GUID),
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(GUID),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    ole32.CoCreateInstance.restype = hresult
    ole32.CoUninitialize.argtypes = []
    ole32.CoUninitialize.restype = None

    def parse_guid(value: str) -> GUID:
        result = GUID()
        status = ole32.CLSIDFromString(value, ctypes.byref(result))
        if status < 0:
            raise OSError(
                f"Could not parse Windows Shell identifier: 0x{status & 0xFFFFFFFF:08x}"
            )
        return result

    def method(pointer, index: int, *arguments):
        vtable = ctypes.cast(
            pointer, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
        ).contents
        return ctypes.WINFUNCTYPE(hresult, ctypes.c_void_p, *arguments)(vtable[index])

    initialized = ole32.CoInitialize(None)
    if initialized < 0 and (initialized & 0xFFFFFFFF) != 0x80010106:
        raise OSError(
            f"Could not initialize Windows Shell COM: 0x{initialized & 0xFFFFFFFF:08x}"
        )

    shell_link = ctypes.c_void_p()
    persist_file = ctypes.c_void_p()
    try:
        status = ole32.CoCreateInstance(
            ctypes.byref(parse_guid("{00021401-0000-0000-C000-000000000046}")),
            None,
            1,  # CLSCTX_INPROC_SERVER
            ctypes.byref(parse_guid("{000214F9-0000-0000-C000-000000000046}")),
            ctypes.byref(shell_link),
        )
        if status < 0:
            raise OSError(
                f"Could not create Windows Shell link: 0x{status & 0xFFFFFFFF:08x}"
            )

        status = method(shell_link, 20, ctypes.c_wchar_p)(shell_link, str(executable))
        if status < 0:
            raise OSError(
                f"Could not set Windows Shell link target: 0x{status & 0xFFFFFFFF:08x}"
            )
        label = f"{APP_NAME} {version}"
        status = method(shell_link, 7, ctypes.c_wchar_p)(shell_link, label)
        if status < 0:
            raise OSError(
                f"Could not set Windows Shell link description: 0x{status & 0xFFFFFFFF:08x}"
            )

        status = method(
            shell_link,
            0,
            ctypes.POINTER(GUID),
            ctypes.POINTER(ctypes.c_void_p),
        )(
            shell_link,
            ctypes.byref(parse_guid("{0000010b-0000-0000-C000-000000000046}")),
            ctypes.byref(persist_file),
        )
        if status < 0:
            raise OSError(
                f"Could not save Windows Shell link: 0x{status & 0xFFFFFFFF:08x}"
            )

        app_data = Path(
            os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
        )
        menu = app_data / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        menu.mkdir(parents=True, exist_ok=True)
        shortcut = menu / f"{label}.lnk"
        temporary = shortcut.with_suffix(".lnk.tmp")
        try:
            status = method(
                persist_file, 6, ctypes.c_wchar_p, ctypes.c_int
            )(persist_file, str(temporary), True)
            if status < 0:
                raise OSError(
                    f"Could not write Windows Shell link: 0x{status & 0xFFFFFFFF:08x}"
                )
            temporary.replace(shortcut)
        finally:
            temporary.unlink(missing_ok=True)
    finally:
        if persist_file:
            method(persist_file, 2)(persist_file)
        if shell_link:
            method(shell_link, 2)(shell_link)
        if initialized >= 0:
            ole32.CoUninitialize()


def register_windows_package(root: Path, version: str) -> None:
    """Install this version without replacing another version's package or link."""
    if os.name != "nt" or not getattr(sys, "frozen", False):
        return
    version_match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z.-]+)?", version)
    if not version_match:
        return

    source = Path(sys.executable).resolve()
    packages_dir = root / "packages"
    package_dir = packages_dir / version
    installed_executable = package_dir / (
        f"Local-Reader-No-GPU-{version}-windows-x86_64.exe"
    )
    try:
        package_dir.mkdir(parents=True, exist_ok=True)
        if source != installed_executable.resolve():
            temporary = installed_executable.with_suffix(".exe.tmp")
            try:
                shutil.copy2(source, temporary)
                temporary.replace(installed_executable)
            finally:
                temporary.unlink(missing_ok=True)
    except OSError:
        return

    try:
        refresh_windows_start_menu_shortcut(installed_executable, version)
    except OSError:
        # The app remains usable if Windows cannot create its Start menu link.
        pass


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
        if (
            relative.is_absolute()
            or PureWindowsPath(name).drive
            or ".." in relative.parts
        ):
            raise RuntimeError("application payload contains an unsafe path")
        mode = member.external_attr >> 16
        if mode and (mode & 0o170000) not in (0, 0o040000, 0o100000):
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
    is_windows = platform.system() == "Windows"
    executable = tools / ("uv.exe" if is_windows else "uv")
    if executable.is_file():
        return executable
    archive_path = tools / asset_name
    archive_path.unlink(missing_ok=True)
    print("Downloading the verified Python runtime manager (uv)...", flush=True)
    download_url = urllib.parse.urljoin(UV_URL, asset_name)
    if is_windows:
        # The frozen launcher has no Python CA bundle. Use Windows' Schannel
        # trust store for HTTPS, then verify the pinned archive before use.
        download_env = os.environ.copy()
        download_env["LOCAL_READER_UV_URL"] = download_url
        download_env["LOCAL_READER_UV_ARCHIVE"] = str(archive_path)
        powershell = (
            "$ErrorActionPreference = 'Stop'; "
            "[Net.ServicePointManager]::SecurityProtocol = "
            "[Net.SecurityProtocolType]::Tls12; "
            "Invoke-WebRequest -UseBasicParsing -Uri $env:LOCAL_READER_UV_URL "
            "-OutFile $env:LOCAL_READER_UV_ARCHIVE"
        )
        try:
            subprocess.run(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    powershell,
                ],
                check=True,
                env=download_env,
            )
        except Exception:
            archive_path.unlink(missing_ok=True)
            raise
    else:
        request = urllib.request.Request(
            download_url,
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
    extract = Path(tempfile.mkdtemp(prefix="uv-extracted-", dir=tools))
    try:
        if asset_name.endswith(".zip"):
            with zipfile.ZipFile(archive_path) as archive:
                safe_zip_extract(archive, extract)
        else:
            with tarfile.open(archive_path) as archive:
                for member in archive.getmembers():
                    relative = Path(member.name.replace("\\", "/"))
                    if (
                        relative.is_absolute()
                        or PureWindowsPath(member.name).drive
                        or ".." in relative.parts
                    ):
                        raise RuntimeError("uv archive contains an unsafe path")
                    if not (member.isfile() or member.isdir()):
                        raise RuntimeError("uv archive contains a special file")
                archive.extractall(extract, filter="data")  # nosec B202
        candidate = next(extract.rglob("uv.exe" if is_windows else "uv"), None)
        if candidate is None or not candidate.is_file():
            raise RuntimeError("uv archive did not contain its executable")
        shutil.copy2(candidate, executable)
        if not is_windows:
            executable.chmod(0o755)
    finally:
        archive_path.unlink(missing_ok=True)
        shutil.rmtree(extract, ignore_errors=True)
    return executable


def windows_vc_runtime_installed() -> bool:
    """Return whether the machine-wide x64 Visual C++ 14 runtime is installed."""
    if platform.system() != "Windows":
        return True
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
        ) as key:
            installed, _ = winreg.QueryValueEx(key, "Installed")
    except OSError:
        return False
    return installed == 1


def ensure_windows_vc_runtime(root: Path) -> None:
    """Install Microsoft's signed x64 runtime when PaddleOCR needs it."""
    if platform.system() != "Windows" or windows_vc_runtime_installed():
        return

    tools = root / ".tools"
    tools.mkdir(parents=True, exist_ok=True)
    installer = tools / "vc_redist.x64.exe"
    environment = os.environ.copy()
    environment["LOCAL_READER_VC_URL"] = VC_REDIST_URL
    environment["LOCAL_READER_VC_INSTALLER"] = str(installer)
    powershell = (
        "$ErrorActionPreference = 'Stop'; "
        "Invoke-WebRequest -UseBasicParsing -TimeoutSec 240 "
        "-Uri $env:LOCAL_READER_VC_URL -OutFile $env:LOCAL_READER_VC_INSTALLER; "
        "$signature = Get-AuthenticodeSignature -LiteralPath "
        "$env:LOCAL_READER_VC_INSTALLER; "
        "if ($signature.Status -ne 'Valid' -or "
        "$signature.SignerCertificate.Subject -notlike '*Microsoft Corporation*') "
        "{ throw 'Microsoft Visual C++ installer signature is invalid.' }; "
        "$process = Start-Process -FilePath $env:LOCAL_READER_VC_INSTALLER "
        "-ArgumentList @('/install', '/quiet', '/norestart') "
        "-PassThru -Wait -Verb RunAs; "
        "if ($process.ExitCode -notin @(0, 1638, 3010)) "
        "{ throw \"Visual C++ Redistributable returned exit code $($process.ExitCode).\" }"
    )
    print(
        "Installing the Microsoft Visual C++ x64 runtime required by Windows OCR...",
        flush=True,
    )
    try:
        subprocess.run(
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell,
            ],
            check=True,
            env=environment,
        )
    finally:
        installer.unlink(missing_ok=True)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Install local models and start Local Reader No GPU."
    )
    root.add_argument("--no-browser", action="store_true")
    root.add_argument("--console", action="store_true", help=argparse.SUPPRESS)
    root.add_argument("--install-only", action="store_true", help=argparse.SUPPRESS)
    root.add_argument("--version", action="store_true")
    root.add_argument("--verify-payload", action="store_true", help=argparse.SUPPRESS)
    return root


def terminal_command(arguments: list[str]) -> list[str] | None:
    """Show first-run progress on double-click without interpolating shell input."""
    if not getattr(sys, "frozen", False):
        return None
    command = [os.environ.get("APPIMAGE") or sys.executable, "--console", *arguments]
    if sys.platform == "darwin":
        script = 'tell application "Terminal" to do script ' + json.dumps(
            shlex.join(["env", "PYINSTALLER_RESET_ENVIRONMENT=1", *command]),
            ensure_ascii=False,
        )
        return ["/usr/bin/osascript", "-e", script]
    if sys.platform.startswith("linux") and os.environ.get("DISPLAY"):
        for name in ("x-terminal-emulator", "gnome-terminal", "konsole", "xterm"):
            terminal = shutil.which(name)
            if terminal:
                separator = "--" if name == "gnome-terminal" else "-e"
                return [terminal, separator, *command]
    return None


def verify_payload(payload: Path) -> str:
    with zipfile.ZipFile(payload) as archive:
        names = set(archive.namelist())
        required = {
            "app/main.py",
            "static/index.html",
            "product.toml",
            "LICENSE",
            "THIRD_PARTY_NOTICES.md",
            "licenses/Inter-OFL.txt",
            "licenses/OpenDyslexic-LICENSE.txt",
        }
        if not required.issubset(names) or any("pocket" in n.lower() for n in names):
            raise RuntimeError(
                "the application payload is incomplete or contains Pocket TTS"
            )
        if archive.testzip() is not None:
            raise RuntimeError("the application payload is corrupt")
        version = tomllib.loads(archive.read("product.toml").decode())["product"][
            "version"
        ]
    return version


def main() -> int:
    args = parser().parse_args()
    if args.version:
        print(f"{APP_NAME} {verify_payload(payload_path())}")
        return 0
    if args.verify_payload:
        version = verify_payload(payload_path())
        print(f"Embedded application payload verified: {version}; no Pocket TTS.")
        return 0
    if (
        not args.console
        and not args.no_browser
        and not args.install_only
        and (sys.stdout is None or not sys.stdout.isatty())
    ):
        terminal = terminal_command(sys.argv[1:])
        if terminal:
            subprocess.Popen(terminal, start_new_session=True)
            return 0
    version = verify_payload(payload_path())
    root = platform_root()
    root.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        root.chmod(0o700)
    register_windows_package(root, version)
    install = install_payload(payload_path(), root)
    uv = download_uv(root)
    ensure_windows_vc_runtime(root)
    environment = os.environ.copy()
    for variable in tuple(environment):
        if variable.startswith(
            ("DYLD_", "LD_", "PIP_", "PYTHON", "UV_")
        ) or variable in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"):
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
    ready = install / ".bootstrap-complete"
    if not core_python.is_file() or not ready.is_file():
        print(
            "Prima esecuzione: preparo Python, OCR, voci e modelli locali. "
            "Può richiedere qualche minuto e spazio su disco.",
            flush=True,
        )
        run(bootstrap, install, environment)
        ready.write_text("complete\n", encoding="ascii")
    if not core_python.is_file():
        raise RuntimeError("the core environment was not created")
    if args.install_only:
        return 0
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
