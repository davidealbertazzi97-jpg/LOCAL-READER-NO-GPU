"""Generate the native Explorer product identity from product.toml."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    product = tomllib.loads((root / "product.toml").read_text())["product"]
    version = tuple(int(p) for p in product["version"].split(".")) + (0,)
    fields = {
        "CompanyName": "Ai Swarm Solutions",
        "FileDescription": product["name"],
        "FileVersion": product["version"],
        "InternalName": product["slug"],
        "OriginalFilename": product["slug"] + ".exe",
        "ProductName": product["name"],
        "ProductVersion": product["version"],
        "LegalCopyright": "Copyright 2026 Davide Albertazzi; GPL-3.0-only",
    }
    strings = ",\n".join(f"StringStruct({k!r}, {v!r})" for k, v in fields.items())
    content = (
        "VSVersionInfo(ffi=FixedFileInfo("
        f"filevers={version!r}, prodvers={version!r}, "
        "mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0,0)), "
        "kids=[StringFileInfo([StringTable('040904B0', [" + strings + "])]), "
        "VarFileInfo([VarStruct('Translation', [1033,1200])])])\n"
    )
    Path(sys.argv[1]).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
