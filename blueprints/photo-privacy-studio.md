# Photo Privacy Studio

## One-sentence product

A local pre-sharing workstation that finds privacy risks in photos, lets the
user review every redaction, removes metadata, and exports a safe copy while
preserving the original.

## Risks it should reveal

- faces and vehicle plates;
- screens, papers, badges, labels, addresses, and QR codes;
- readable text found by local OCR;
- GPS, device, timestamp, author, and other EXIF/XMP metadata;
- reflections and background regions that deserve manual review.

Detection is assistance, not automatic proof. The export button remains a
human decision and the preview must make missed areas easy to mark manually.

## First useful release

1. Import JPEG, PNG, WebP, HEIC where the platform decoder is available.
2. Show metadata before removal.
3. Local face, plate, QR, and text-region detection.
4. Click-to-toggle detections plus freehand rectangle and polygon selection.
5. Blur, pixelate, or opaque-fill with a warning that weak blur may be
   reversible or still recognizable.
6. Export a newly encoded copy with metadata removed by default.
7. Before/after comparison and a machine-readable redaction receipt that
   contains coordinates and settings but no image pixels.

## Security choices

- Never overwrite the original.
- Decode with resource limits and reject malformed or decompression-bomb input.
- Flatten orientation before redaction so coordinates cannot shift.
- Re-encode the full image; do not copy unreviewed thumbnails or metadata blocks.
- Warn that visible context can identify a person even after faces are hidden.
- Keep exported file names neutral and avoid logging OCR text.

## Model boundary

Prefer narrowly scoped CPU detectors over a general vision-language model for
the first release. Each detector must be independently removable, benchmarked
on synthetic Italian examples, and documented with its exact licence and
training-data caveats.
