#!/usr/bin/env python3
"""Export installed package versions and license/notice texts, without user data."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    inventory = []
    for dist in sorted(
        importlib.metadata.distributions(), key=lambda d: d.metadata["Name"]
    ):
        name = dist.metadata["Name"]
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", name)
        notices = []
        for entry in dist.files or []:
            path = Path(str(entry))
            if not any(
                word in path.name.lower()
                for word in ("license", "copying", "notice", "copyright")
            ):
                continue
            source = Path(dist.locate_file(entry))
            if not source.is_file() or source.suffix.lower() in (
                ".py",
                ".pyc",
                ".so",
                ".dll",
            ):
                continue
            relative = Path(safe_name) / f"{len(notices):03d}-{path.name}"
            target = args.output / relative
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(source.read_bytes())
            notices.append(relative.as_posix())
        inventory.append(
            {
                "name": name,
                "version": dist.version,
                "purl": f"pkg:pypi/{name.lower().replace('_', '-')}@{dist.version}",
                "license_expression": dist.metadata.get("License-Expression"),
                "license_classifiers": [
                    c
                    for c in dist.metadata.get_all("Classifier", [])
                    if c.startswith("License ::")
                ],
                "notices": notices,
            }
        )
    (args.output / "inventory.json").write_text(
        json.dumps({"packages": inventory}, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Exported {len(inventory)} package records and their installed notices.")


if __name__ == "__main__":
    main()
