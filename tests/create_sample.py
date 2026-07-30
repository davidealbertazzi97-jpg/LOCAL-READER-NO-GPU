#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    args = parser.parse_args()
    image = Image.new("RGB", (1400, 620), "white")
    draw = ImageDraw.Draw(image)
    regular = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        46,
    )
    bold = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        62,
    )
    draw.text((65, 55), "AVVISO IMPORTANTE", font=bold, fill="black")
    draw.text(
        (65, 180),
        "La riunione è fissata per martedì 15 settembre.",
        font=regular,
        fill="black",
    )
    draw.text(
        (65, 275),
        "Portare i documenti entro 30 giorni.",
        font=regular,
        fill="black",
    )
    draw.text((65, 390), "1. Primo punto", font=regular, fill="black")
    draw.text((65, 475), "2. Secondo punto", font=regular, fill="black")
    image.save(Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
