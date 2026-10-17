# Changelog

## 0.4.1 — 2026-10-17

- Publish job completion after private input cleanup to avoid a Windows race
  during native OCR verification.

## 0.4.0 — 2026-10-17

- Ship Local Reader as a separate app, alongside legacy Local Accessibility
  Studio and Local Reader No GPU: separate runtime, settings, history, results,
  authentication cookie, browser checkpoints, Start menu links and port 8766.
- Add an original purple book/play/highlight logo to the interface, Windows
  executable and shortcuts, Linux launcher and macOS bundle.
- Add native Windows product/version metadata and a dedicated application ID.
- Include offline Kokoro Live reading and the settings fix from 0.3.9.

## 0.3.9 — 2026-10-17

- Add local Kokoro audio directly to Live reading, including browsers with no
  device voices: Italian Sara/Nicola and English Heart/Michael.
- Keep the isolated CPU model warm, prefetch one phrase, and keep temporary
  speech/audio in memory without creating History jobs or using Internet.
- Underline the phrase on actual audio playback; support exact audio pause and
  resume, speed controls, paragraph jumps, and cancellation of stale requests.
- Fix a mismatched provider status element that interrupted loading settings
  and prevented the offline indicator from reflecting the saved mode.

## 0.3.8 — 2026-10-17

- Make pause work with Firefox Speech Dispatcher voices on Linux: cancel the
  current utterance and resume from the current sentence instead of relying
  on the backend's unimplemented native pause operation.
- Label this action Resume sentence and ignore late events from canceled
  utterances so a paused reader cannot advance to the next paragraph.

## 0.3.7 — 2026-10-17

- Add Live reading with instant paragraph playback using device voices, actual
  speech boundary events for word underlining and sentence highlighting when
  a voice does not report word timing.
- Add keyboard paragraph navigation, pause/resume, speed, font size, automatic
  scrolling, single-paragraph/continuous reading and a local reading checkpoint.
- Open text files, OCR results, edited documents and history texts in the reader.
- Exclude online device voices in Offline mode; keep MP3 generation with Kokoro
  and optional providers in the existing Voice only page.

## 0.3.6 — 2026-10-16

- Rebrand the public application as Local Accessibility Studio with a new
  reading and speech logo and versioned native packages.
- Keep the Windows one-file launcher, verified first-run setup, per-version
  Start menu shortcuts and isolated launcher settings for side-by-side installs.
- Build the Windows executable with the new application icon.
- Keep bundled eSpeak data usable when an installation path exceeds the native
  path buffer, including the default macOS Application Support location.
- Validate the installed Linux and Windows packages with offline speech and
  complete OCR, text, review, reflow and audio smoke tests; verify simultaneous
  Windows startup alongside the public 0.3.5 package.

## 0.3.5 — 2026-10-01

- Carry forward the Windows setup, parallel version installs, shared history
  and automatic update fixes prepared for 0.3.4.
- Use Windows Schannel for bounded, checksum-verified Windows model downloads,
  including the Hugging Face LFM files that fail under Python's CA validation.
- Make the native package smoke-test PDF use Pillow's bundled font instead of
  a runner-specific system font.

## 0.3.4 — 2026-10-01

- Fix Windows launches alongside an older version: each version uses its own
  launcher token, port setting and Start menu shortcut.
- Use Windows' certificate store for the checksum-pinned first-run runtime
  download, and install Microsoft's signed x64 Visual C++ runtime only when
  missing so PaddleOCR can load on a clean Windows machine.
- Allow the release checker to connect to the official GitHub Releases API.
- Preserve older versioned executables instead of replacing them during install.
- Keep job history and user settings available across versions.
- Update the Windows release installer so the app creates its own versioned
  shortcut after checksum verification.
- Fix history behavior when another version's server is already running.

## 0.3.3 — 2026-09-11

- Remove Pocket TTS, its worker and heavyweight dependencies; migrate legacy
  offline preferences to Kokoro without deleting private samples.
- Keep direct recording, consent and a saved cloned-voice menu for supported
  optional providers.
- Fix first-run uv extraction and retry incomplete portable installations.
- Add checksum-verified one-command native installers and native first-run
  release tests for Windows, Linux and Apple Silicon macOS.
- Pin AppImage build tooling/runtime; include font/runtime licenses,
  dependency inventories and corresponding source archives.
- Rewrite the usage manual in Italian first, followed by English.
- Add GitHub release checks at startup and every 12 hours, with a manual check
  button and a platform-specific download link on Windows, Linux and macOS.
- Put a prominent MP3 download action beside each generated track and give each
  file a distinct name.


All notable changes to Local Accessibility Studio are documented here.

## 0.3.2 - 2026-09-10

- Fixed first-run installation on fresh Linux/macOS machines by accepting
  contained library symlinks in the verified llama.cpp archive with Python's
  safe extraction filter. Escaping links and special files remain blocked.
- Fixed Windows runtime ZIP handling (`ZipInfo.filename`).
- Prefer the faster FP32 Kokoro model; new installations download it by default.
- Keep active long Edge-TTS streams alive while timing out stalled responses.

## 0.3.1 - 2026-09-10

- Offline mode immediately stops online workers and routes speech to Kokoro.
- Edge-TTS retries partial or empty responses, with bounded timeouts and an
  automatic Kokoro fallback when the online service is unavailable.
- Long speech uses two concurrent requests, ordered audio assembly, and fewer
  requests for documents with many short paragraphs.
- Kokoro uses at most four CPU threads and disables idle thread spinning.
- Clear OCR/speech progress and localized failure messages.
- Native Linux AppImage, Windows EXE, and macOS Apple Silicon DMG/APP ZIP
  packages published together with SHA-256 checksums.

## 0.3.0

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
