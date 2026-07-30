# Architecture

```text
browser on 127.0.0.1
        |
        | token + exact origin
        v
 FastAPI boundary ──> SQLite job metadata
        |
        | private bounded work copy
        v
 serialized job runner
        |
        +── isolated OCR Python ──> reviewed document.json
        |                           + accessible.html
        |                           + reading.txt
        |                           + page previews
        |
        └── isolated Kokoro Python ──> speech.wav

work copy removed ────────────────> durable results remain
```

The web core, OCR stack, and speech stack use separate virtual environments.
This keeps the web boundary small and releases model memory when a worker exits.
The launcher supplies the network guard to every Python child.

RapidOCR uses the PP-OCRv6 small ONNX detection and recognition models on CPU.
PDF pages are rendered with PDFium; image dimensions, pixel count, frame count,
and PDF page count are bounded. Each OCR block carries text, a bounding box,
confidence, and an inferred semantic role.

`document.json` is the editable source of truth. The server validates every
revision and regenerates HTML and reading text by escaping text into a fixed
template; user text is never interpreted as HTML. A revision number prevents a
stale browser tab from silently overwriting a newer edit.

Speech is created only from a saved `reading.txt` artifact. The server makes a
private child-job copy either automatically after OCR or after a reviewed
manual request, verifies Kokoro model and voice hashes, and starts a separate
worker. The document records `it`, `en-us`, or `en-gb`; the server only permits
voices belonging to that language. The worker synthesizes bounded chunks and
streams PCM samples to WAV, avoiding a full-document audio array in memory.
