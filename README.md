# Local Accessibility Studio

Private, local OCR, accessible-document preparation, and natural Italian speech
for ordinary CPU computers. Documents are processed on the user's workstation;
the application has no cloud mode, telemetry, account, or GPU requirement.

The current MVP can:

- recognize PDF and image pages with RapidOCR, PP-OCRv6 small, and ONNX Runtime;
- show every page beside editable text blocks and OCR confidence;
- let the user correct text and mark headings, paragraphs, lists, page numbers,
  or content that must be excluded from reading;
- regenerate clean reading text and semantic HTML after every review;
- automatically queue a Kokoro audio draft after OCR, unless the user disables
  that option;
- create long-form Italian WAV audio with Kokoro ONNX using `im_nicola` or
  `if_sara`, adjustable speed, and streaming CPU synthesis;
- keep durable results in the user's Documents folder while deleting private
  working copies after success, failure, or interrupted restart.

Piper is not a dependency and is not used.

## Important accessibility boundary

OCR, reading-order inference, and heading detection can be wrong. A generated
file is a **review candidate**, not proof that a document is accessible. Low
confidence is shown explicitly, all inferred roles remain editable, and the
interface never silently calls an unreviewed result compliant.

The first release exports semantic HTML and plain reading text. Tagged PDF,
EPUB, and DOCX are deliberately deferred until they can be tested with real
assistive technologies and users.

## Install and start

Supported release profiles are Linux x86-64, macOS Apple Silicon, and Windows
x86-64 with Python 3.12 managed by the installer.

```bash
./install.sh
./start.sh
```

On Windows:

```powershell
.\install.ps1
.\start.ps1
```

On Linux the installer also adds **Local Accessibility Studio** to the desktop
application menu without requiring `sudo`.

Installation needs internet access to obtain pinned Python packages and the
verified Kokoro files. Runtime binds only to numeric loopback and guarded Python
processes deny non-loopback connections. The installer downloads:

- Kokoro v1.0 INT8 CPU model: 92,361,271 bytes;
- Kokoro v1.0 voice bundle: 28,214,398 bytes;
- RapidOCR's wheel, which contains the PP-OCRv6 small ONNX models.

The exact Kokoro SHA-256 values are pinned in
`scripts/install_kokoro.py`. Model files and virtual environments are excluded
from Git.

## Workflow

1. Upload a PDF, PNG, JPEG, WebP, TIFF, or BMP from the local interface.
2. Wait for local OCR and, by default, the automatic Kokoro audio draft.
3. Open **Review text and order**.
4. Correct the title, language, block text, and semantic roles.
5. Save corrections, then download accessible HTML/text or regenerate the audio.
6. Review the final output with the intended screen reader and user.

The original file is never modified. Page previews and exported results are
durable copies and may still contain confidential information.

## Verification

```bash
python -m unittest discover -s tests -p "test_*.py"
python tests/smoke_local.py
python tests/smoke_local.py --full
ruff check .
ruff format --check .
bandit -q -c pyproject.toml -r app runtime_guard scripts workers
```

The full smoke test performs OCR, verifies the automatic Kokoro draft, edits the
recognized structure through the real authenticated API, regenerates exports,
synthesizes a second reviewed audio file, and checks work-copy deletion.

## Licence

Original code and documentation are GNU GPL version 3 only. This choice is also
compatible with the GPL speech-processing dependencies used by Kokoro's
phonemization path. Models and third-party components retain their own terms;
see `THIRD_PARTY_NOTICES.md`.

---

# Local Accessibility Studio — Italiano

OCR privato in locale, preparazione di documenti accessibili e sintesi vocale
italiana naturale per normali computer con CPU. Non esistono modalità cloud,
telemetria, account o requisiti GPU.

L’MVP attuale:

- riconosce PDF e immagini con RapidOCR, PP-OCRv6 small e ONNX Runtime;
- mostra ogni pagina accanto ai blocchi di testo modificabili e alla confidenza;
- permette di correggere testo, titoli, paragrafi, elenchi, numeri di pagina ed
  elementi da non leggere;
- rigenera testo pulito e HTML semantico dopo ogni revisione;
- accoda automaticamente una bozza audio Kokoro dopo l’OCR, salvo disattivazione;
- crea audio WAV italiano con Kokoro e le voci `im_nicola` e `if_sara`;
- elimina le copie private di lavoro anche dopo errori o riavvii interrotti.

Piper non viene installato né utilizzato.

OCR, ordine di lettura e riconoscimento dei titoli possono sbagliare. Il
risultato è una **bozza da revisionare**, non la prova che il documento sia
accessibile. Per questo ogni ruolo rimane modificabile e le parole a bassa
confidenza vengono evidenziate.

Installazione e avvio su Linux/macOS:

```bash
./install.sh
./start.sh
```

Su Windows usa `.\install.ps1` e `.\start.ps1`. L’installazione scarica pacchetti
versionati e i file Kokoro verificati; l’esecuzione dell’applicazione resta
locale. Gli originali non vengono mai modificati, ma anteprime e risultati
persistenti possono ancora contenere informazioni riservate.
