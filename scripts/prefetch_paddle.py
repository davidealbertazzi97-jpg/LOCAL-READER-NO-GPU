#!/usr/bin/env python3
"""Download the plain PaddleOCR models during installation."""

from __future__ import annotations

import os

os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")


def main() -> int:
    from paddleocr import PaddleOCR

    print("Preparing the plain PaddleOCR models...")
    try:
        PaddleOCR(
            lang="it",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device="cpu",
            enable_mkldnn=False,
        )
    except TypeError:
        PaddleOCR(lang="it", use_angle_cls=False)
    print("PaddleOCR models ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
