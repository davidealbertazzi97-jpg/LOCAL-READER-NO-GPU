# Product blueprints

These are implementation briefs, not four half-built applications. Each product
should begin as a fresh copy of the starter and receive its own dependency,
model, licence, privacy, and acceptance-test review.

| Product | Main promise | First technical core | Main risk |
| --- | --- | --- | --- |
| [Local Document Radar](local-document-radar.md) | Find evidence and versions across private folders | text extraction + exact/semantic index | confidential index and false matches |
| [Photo Privacy Studio](photo-privacy-studio.md) | Review and redact photo privacy risks before sharing | safe image decode + detectors + full re-encode | missed visual identifiers |
| [Deadline Radar](deadline-radar.md) | Propose calendar actions with source evidence | constrained date extraction + deterministic calculator | invented or miscalculated deadlines |
| [Local Accessibility Studio](accessibility-studio.md) | OCR, restructure, and read documents naturally | OCR + reading-order editor + Kokoro TTS | incorrect structure presented as accessible |

Recommended build order:

1. **Local Accessibility Studio, phase 1:** it creates the reviewed OCR and
   document-structure component needed by two other products.
2. **Deadline Radar:** it can consume that reviewed text and has a narrow,
   testable output (`.ics` proposals).
3. **Local Document Radar:** it reuses extraction knowledge but adds a
   confidential long-lived index and therefore needs a separate security review.
4. **Photo Privacy Studio:** build independently because its image redaction
   pipeline and failure modes are different.

If the priority is instead the fastest visible standalone release, start with
Photo Privacy Studio using manual redaction plus metadata removal, then add
detectors gradually.
