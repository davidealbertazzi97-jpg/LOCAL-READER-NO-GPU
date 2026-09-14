# Third-party notices

Local Reader No GPU’s original code and documentation are licensed
under GNU GPL version 3 only. Dependencies, fonts, runtimes, model files, and
remote services retain their own licences and terms.

## Runtime components

| Component | Pinned version / source | Notes |
| --- | --- | --- |
| FastAPI, Uvicorn, python-multipart | See `requirements-core.lock` | Web runtime; their upstream licences apply |
| PaddlePaddle | 3.3.1 | Apache-2.0 upstream |
| PaddleOCR | 3.7.0 with `doc-parser` extra | Apache-2.0 upstream; plain OCR pipeline used here |
| Pillow | 12.3.0 | MIT-CMU upstream |
| pypdfium2 | 5.12.1 | BSD-3-Clause / Apache-2.0 and bundled PDFium notices |
| Edge-TTS | 7.2.8 | Upstream package terms apply; its Microsoft speech endpoint is remote |
| kokoro-onnx | 0.6.1 | ONNX runtime adapter; package and Kokoro model terms apply |
| imageio-ffmpeg | 0.6.0 | Bundled platform FFmpeg binary for self-contained offline audio; BSD-2-Clause wrapper and FFmpeg notices apply |
| Kokoro 82M ONNX / voices | Local model assets | Used offline; preserve the model and voice asset terms |
| llama.cpp | CPU build `b10886`, downloaded with SHA-256 pin | MIT upstream; the portable launcher downloads the target build when missing |
| OpenDyslexic | Vendored WOFF2 font | Upstream font licence applies; keep its licence with distributions |
| LFM2.5 230M GGUF | Liquid AI Q8 model, downloaded with SHA-256 pin | Do not redistribute without observing the model’s own terms |
| Gemma 4 E4B Q4_0 GGUF | Google model, optional download with SHA-256 pin | Apache-2.0; optional 5.2 GB local text model |
| Fish Audio S2 Pro MLX 8-bit | `mlx-community/fish-audio-s2-pro-8bit`, optional macOS download at a fixed revision | Fish Audio Research License; non-commercial/research use only unless separately licensed |

Exact transitive versions and approved wheel hashes are recorded in
`requirements-core.lock`, `requirements-ocr.lock`, `requirements-tts.lock`,
and `requirements-dev.lock`. The installer accepts wheels only.

## OCR models

The installer prefetches the plain PaddleOCR models used by the worker into the
PaddleX local cache. The application disables document orientation,
unwarping, text-line orientation, and PP-Structure for this flow. It therefore
reads text lines without attempting table reconstruction. PaddleOCR and its
model assets retain the notices and terms published by PaddlePaddle:

- <https://github.com/PaddlePaddle/PaddleOCR>
- <https://github.com/PaddlePaddle/Paddle>

## Speech service

Edge-TTS is used by the simple complete workflow. The worker sends bounded
text chunks to Microsoft’s Edge speech endpoint and writes the returned audio
as MP3. Kokoro 82M is the offline alternative. Voxtral/Mistral, Fish Audio,
and ElevenLabs are optional remote services and retain their own package,
model, account, and voice-consent terms.

## Font and local model

OpenDyslexic is vendored only as a browser font asset. The LFM2.5 GGUF file is
resolved from the user’s local LM Studio directory, the app runtime, or an
explicit environment variable and is not copied into this repository. The
portable launcher may download both the model and the CPU llama.cpp build into
the user’s private runtime directory; preserve their upstream notices when
packaging either component.

This inventory is technical information, not legal advice.
