# Changelog

All notable changes to Local Accessibility Studio are documented here.

## Unreleased

- Presented the source repository as Local Reader, with an inclusive-education
  focus and a bilingual plug-and-play prompt for terminal-capable AI agents.

## 0.2.0 - 2026-07-30

- Automatic Kokoro audio draft after OCR.
- Fast FP32 Kokoro profile for compatible CPUs, with compact INT8 fallback.
- Male and female Italian voices.
- Male and female American and British English voices.
- Document and speech locale validation through the complete pipeline.
- Individual and bulk deletion of completed history and local result files.
- Bilingual user interface and English-default voice selection.
- Browser-level regression tests for upload, audio, voices, and history.

## 0.1.0 - 2026-07-30

- Local PDF and image OCR with RapidOCR PP-OCRv6 small on CPU.
- Editable text blocks, confidence values, and semantic roles.
- Semantic HTML and clean reading-text exports.
- Italian Kokoro speech on CPU without Piper.
- Loopback-only API, per-installation token, exact-origin checks, and outbound
  network guards.
- Isolated web, OCR, and speech Python environments.
- Private working-copy cleanup and durable local results.
- GPL-3.0-only licensing and third-party inventory.
