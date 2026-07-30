# Local Accessibility Studio

## One-sentence product

Turn scanned or poorly structured documents into readable, navigable text and
natural Italian speech entirely on the user's computer.

## User flow

1. Import a PDF or image.
2. Run local OCR and show page images beside recognized text.
3. Reconstruct reading order, headings, lists, tables, footnotes, page numbers,
   and language changes.
4. Let the user correct text and structure.
5. Export accessible HTML and tagged text first; evaluate EPUB and accessible
   DOCX only after validation with real screen readers.
6. Read the selected section or full document with local Kokoro speech.
7. Export chaptered WAV, with optional MP3 only when the exact encoder and
   licence are documented.

The TTS input is not raw OCR. A preparation stage expands or marks
abbreviations, removes repeated headers, describes page transitions, preserves
punctuation, and splits long documents at structural boundaries.

## Kokoro decision — no Piper

Piper is outside this product plan. The intended engine is `kokoro-onnx` with
Italian voices such as `if_sara` and `im_nicola`, selectable speed, sentence
preview, pause/resume, and CPU-only inference.

The workstation already contains a HyperFrames Kokoro cache:

- `~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx` — 325,532,387 bytes;
- `~/.cache/hyperframes/tts/voices/voices-v1.0.bin` — 28,214,398 bytes;
- the voice bundle includes `if_sara` and `im_nicola`;
- an isolated prior environment used `kokoro-onnx 0.5.0`,
  `onnxruntime 1.27.0`, and `soundfile 0.14.0`.

Current local SHA-256 values are
`7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5`
for the model and
`bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d`
for the voice bundle. These identify the discovered development copies; they
are not a substitute for an upstream release manifest.

That model is the full float model, not a 50 MB model. The official v1.0 ONNX
release describes the CPU-oriented INT8 model as about 88 MB, plus the roughly
28 MB voice bundle. The “50 MB” recollection should therefore not be encoded as
a false requirement.

Implementation policy:

1. never copy or commit the existing cache or prior virtual environment;
2. during development, allow an explicit user-selected cache path;
3. for releases, download the exact INT8 model and voices from their upstream
   release, pin hashes, and show download size before installation;
4. benchmark full and INT8 models on the same Italian passages for speed,
   pronunciation, punctuation, RAM, and long-form stability;
5. retain the full model as an optional quality profile only if the difference
   is meaningful;
6. inventory the exact wrapper, model, voice, phonemizer, ONNX Runtime, audio
   library, and encoder licences before distribution.

Upstream references:

- <https://github.com/thewh1teagle/kokoro-onnx>
- <https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0>

## OCR and accessibility boundary

OCR confidence must remain visible. Low-confidence words, uncertain reading
order, merged table cells, formulas, handwriting, and decorative images require
review rather than silent invention.

The first release should support:

- searchable text with page anchors;
- heading and list navigation;
- image alternative-text fields written or approved by the user;
- table linearization preview;
- keyboard-only operation, visible focus, scalable text, and screen-reader
  labels;
- phrase-level TTS highlighting and resume position stored locally.

“Accessible” is a test result, not a marketing assumption. Validate exports
with NVDA on Windows, VoiceOver on macOS, and at least one Linux screen reader,
plus keyboard-only tests and human review by users who rely on assistive
technology.

## Phased build

1. OCR + correction + clean HTML/text export.
2. Reading-order editor and structural accessibility checks.
3. Kokoro Italian preview and section playback.
4. Long-document chaptered audio export and resume.
5. Additional formats only after interoperability tests.
