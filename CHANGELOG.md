# Changelog

All notable changes to Local Accessibility Studio are documented here.

## Unreleased

- Added the local-reader workflow for inclusive education with a bilingual UI,
  OpenDyslexic font, paste/text-file input, and long-document reading.
- Enforced browser origin checks on every state-changing API request and added
  a pre-parser upload request limit.
- Added controlled PaddleOCR, llama.cpp, and Edge-TTS process termination,
  stricter private file permissions, bounded chunking, and hardened runtimes.
- Locked all installation dependencies with SHA-256 hashes and disabled source
  distribution builds in the public installer.
- Added plain PaddleOCR model prefetch and an LFM2.5 non-whitespace content
  guard with deterministic fallback formatting.
- Simplified the complete workflow to PaddleOCR → Edge-TTS, keeping LFM only
  in the explicit organization mode.
- Added Kokoro 82M offline speech, provider settings for Mistral/OpenCode/Kilo
  and custom OpenAI-compatible endpoints, plus Fish Audio and ElevenLabs keys.
- Added consent-gated Voxtral/Mistral and ElevenLabs voice cloning controls.
- Hardened CI permissions, checkout credentials, expression handling, and
  concurrency.
- Added native-platform portable launchers, safe payload extraction, local
  first-run dependency/model bootstrap, and a Linux AppImage build.
- Added automatic verified LFM2.5 and CPU llama.cpp setup for the local
  organization workflow.

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
