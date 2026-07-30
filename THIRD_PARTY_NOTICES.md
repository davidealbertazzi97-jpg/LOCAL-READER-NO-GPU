# Third-party notices

Local Accessibility Studio's original code and documentation are licensed under
GNU GPL version 3 only. Dependencies, models, runtimes, and voice data retain
their own licences.

The source repository does not commit model weights, virtual environments,
generated native libraries, user documents, page previews, or audio output.
The installer obtains dependencies from their upstream distribution channels.

## Direct runtime components

| Component | Pinned version | Licence |
| --- | ---: | --- |
| FastAPI | 0.140.13 | MIT |
| Uvicorn | 0.51.0 | BSD-3-Clause |
| python-multipart | 0.0.32 | Apache-2.0 |
| RapidOCR | 3.9.2 | Apache-2.0; OCR model copyright remains with Baidu/PaddleOCR |
| ONNX Runtime, OCR environment | 1.23.2 | MIT |
| Pillow | 12.3.0 | HPND |
| pypdfium2 | 5.12.1 | BSD-3-Clause / Apache-2.0 plus bundled PDFium notices |
| Kokoro ONNX wrapper | 0.5.0 | MIT |
| ONNX Runtime, speech environment | 1.27.0 | MIT |
| python-soundfile | 0.14.0 | BSD-3-Clause |
| uv installer tool | 0.11.16 | Apache-2.0 OR MIT |

Notable installed transitive components include OpenCV (Apache-2.0), NumPy
(BSD-3-Clause plus bundled notices), Shapely (BSD-3-Clause plus GEOS notices),
`phonemizer-fork` (GPL-3.0-or-later), and eSpeak NG code/data loaded by
`espeakng-loader` (GPL-3.0-or-later upstream). The GPL-3.0-only licence of this
application is compatible with selecting GPL version 3 for GPL-3.0-or-later
components.

Before distributing a preassembled executable or environment, copy the exact
licence files and corresponding-source obligations from every wheel and native
library included for that platform. In particular, the `espeakng-loader` wheel
contains an eSpeak NG shared library and data; a binary distributor must
provide the notices and corresponding source required by eSpeak NG's GPL.

## OCR models

RapidOCR 3.9.2's wheel contains the PP-OCRv6 small detection, recognition, and
orientation ONNX models used by this application. RapidOCR states that its
project is Apache-2.0 and that OCR model copyright belongs to Baidu. The models
are converted from PaddleOCR assets. Record the exact wheel and its notices in
every binary release.

Sources:

- <https://github.com/RapidAI/RapidOCR>
- <https://github.com/PaddlePaddle/PaddleOCR>

## Kokoro model and voices

The installer downloads these unmodified release assets and verifies SHA-256:

| Asset | Size | SHA-256 |
| --- | ---: | --- |
| `kokoro-v1.0.int8.onnx` | 92,361,271 bytes | `6e742170d309016e5891a994e1ce1559c702a2ccd0075e67ef7157974f6406cb` |
| `kokoro-v1.0.onnx` (optional fast profile) | 325,532,387 bytes | `7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5` |
| `voices-v1.0.bin` | 28,214,398 bytes | `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d` |

The Kokoro ONNX project identifies its wrapper as MIT and the Kokoro model as
Apache-2.0. The application exposes the upstream voices `im_nicola`, `if_sara`,
`am_michael`, `af_heart`, `bm_george`, and `bf_emma`.

Source: <https://github.com/thewh1teagle/kokoro-onnx>

This inventory supports release preparation; it is not legal advice.
