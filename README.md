<p align="center">
  <img src="static/icon.svg" width="88" height="88" alt="Local Accessibility Studio">
</p>

<h1 align="center">LOCAL READER (NO GPU)</h1>

<p align="center">
  <strong>Inclusive reading with high-quality local AI speech on ordinary CPUs.</strong><br>
  Documents and generated voice stay on the device. No account, cloud
  inference, telemetry, or GPU is required.
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#italiano">Italiano</a>
</p>

---

<a id="english"></a>

## English

**Local Reader** is the source repository for the application installed as
**Local Accessibility Studio**. It was born as an inclusive-education project:
give teachers, students, support educators, families, and professionals a
simple way to turn scanned or difficult documents into reviewable text and
high-quality AI speech directly on their own device.

The entire OCR-to-reading workflow runs locally, so classroom material,
assessment documents, accommodations, and other confidential content do not
need to reach an external server. It is designed for low- to mid-range
consumer hardware without a GPU and remains useful outside education wherever
private, accessible reading is needed.

### Current distribution

Version **0.2.0** is currently distributed as source. Prebuilt `.exe`,
`.AppImage`, and `.dmg` packages are not published yet; this README does not
link to installers that have not been built and verified.

| Platform | Current verification | Architecture |
| --- | --- | --- |
| Linux | Full OCR, review, export, and Kokoro pipeline | x86-64 |
| Windows 10/11 | Installer and live core server verified in CI; native engines pending | x86-64 |
| macOS 13+ | Installer and live core server verified in CI; native engines pending | Apple Silicon |

The complete model pipeline is exercised automatically on Linux. Windows and
macOS users should treat the current source release as an early test profile
until full native engine testing is added for those platforms.

### Install from source

Download or clone the repository, open a terminal in its root, then run:

```bash
./install.sh
./start.sh
```

On Windows, use PowerShell:

```powershell
.\install.ps1
.\start.ps1
```

Linux installation also adds **Local Accessibility Studio** to the desktop
application menu without requiring `sudo`.

The first installation needs internet access to download Python packages locked
with SHA-256 hashes and verified model files. The installer accepts prebuilt
wheels only and does not build source distributions. Normal document processing
runs locally and does not require internet access.

### Plug-and-play setup with an AI agent

If an AI coding agent can use a terminal on the computer, copy the ready-made
prompt from [`AI-AGENT-INSTALL-PROMPT.md`](AI-AGENT-INSTALL-PROMPT.md). It
instructs the agent to:

- verify the operating system and supported architecture;
- download this repository without sending any user document elsewhere;
- run the official installer with the most suitable CPU speech profile;
- start the application and verify its local health endpoint;
- explain where private data and durable results are stored;
- stop and report clearly instead of bypassing security controls.

No document is required for setup. A real confidential file must never be
uploaded to an AI agent, issue, chat, or external diagnostic service.

#### Compact and fast speech profiles

The default installer downloads the compact Kokoro INT8 model. On many modern
x86 CPUs, the larger FP32 model can synthesize speech substantially faster:

```bash
./install.sh --fast-tts
```

| Kokoro profile | Download size | Purpose |
| --- | ---: | --- |
| INT8 compact | 92,361,271 bytes | Smaller installation |
| FP32 fast | 325,532,387 bytes | Faster synthesis on compatible CPUs |
| Voice bundle | 28,214,398 bytes | Italian and English voices |

All Kokoro files are checked against the SHA-256 values pinned in
[`scripts/install_kokoro.py`](scripts/install_kokoro.py). RapidOCR's wheel
contains the PP-OCRv6 small ONNX models. Models, environments, user documents,
and generated audio are excluded from Git.

### What it does

- Italian or English interface with a saved local preference.
- OCR for PDF, PNG, JPEG, WebP, TIFF, and BMP files using RapidOCR,
  PP-OCRv6 small, and ONNX Runtime on CPU.
- Side-by-side page previews, editable OCR blocks, and confidence indicators.
- Reviewable roles for headings, paragraphs, list items, page numbers, and
  content excluded from reading.
- Regenerated semantic HTML and clean reading text after every saved revision.
- Automatic Kokoro audio draft after OCR, with an option to disable it.
- Male and female voices for Italian, American English, and British English.
- Adjustable speech speed and a fast FP32 CPU profile.
- Individual or bulk deletion of completed history and its local result files.
- Persistent local jobs with private working-copy cleanup after success,
  failure, or interrupted restart.

Piper is not installed or used.

### Voices

| Language | Male | Female |
| --- | --- | --- |
| Italian | Nicola (`im_nicola`) | Sara (`if_sara`) |
| English — United States | Michael (`am_michael`) | Heart (`af_heart`) |
| English — United Kingdom | George (`bm_george`) | Emma (`bf_emma`) |

Switching the interface to English selects American English for the next
document by default. Document language, speech language, and voice remain
editable during review. The selected locale is passed to Kokoro's phonemizer;
the change is not only a translated label.

### Workflow

1. Select the document/speech language and a male or female voice.
2. Upload a supported PDF or image.
3. Wait for local OCR and, by default, the automatic audio draft.
4. Open **Review text and order**.
5. Correct the title, text, language, reading order, and semantic roles.
6. Save the revision, download HTML/text, or regenerate audio.
7. Test the result with the intended reader, screen reader, and user.

The original file is never modified. Page previews, reviewed text, semantic
HTML, OCR reports, and WAV files are durable results and may still contain
confidential information.

### Accessibility boundary

OCR, reading-order inference, heading detection, and speech synthesis can be
wrong. Generated files are **review candidates**, not proof that a document
conforms to WCAG, PDF/UA, the European Accessibility Act, or any other
accessibility requirement.

Low confidence is shown explicitly, all inferred roles remain editable, and
the interface does not label an unreviewed result compliant. The current
release exports semantic HTML and plain reading text. Tagged PDF, EPUB, and
DOCX remain deferred until they can be tested with real assistive technologies
and users.

See [`DISCLAIMER.md`](DISCLAIMER.md) for the complete limitations.

### Privacy and security model

- The service binds only to numeric loopback `127.0.0.1`.
- API requests require a random per-installation token.
- State-changing requests enforce the exact local browser origin.
- Oversized upload requests are rejected before multipart parsing.
- Python runtime processes reject non-loopback network connections.
- Linux adds a native outbound-network guard when a C compiler is available.
- The interface contains no telemetry, CDN assets, account, or remote inference.
- Upload, edit, page, pixel, frame, artifact-path, and speech-size limits are
  enforced.
- Kokoro model and voice files must match approved SHA-256 values.
- OCR and speech run in isolated Python environments.
- User/OCR text is escaped into a fixed HTML template and is never interpreted
  as markup.
- Private working copies are removed after completion, failure, and interrupted
  restart.
- Active OCR and speech process groups are terminated during an orderly
  application shutdown.

Installation needs network access for third-party packages and models. The
default browser is outside the application's network guard and may perform its
own background traffic. The runtime guards are defense in depth, not an
operating-system sandbox and not protection against malicious native code or
another process already running as the same user.

Local processing does not by itself establish GDPR, accessibility, or other
regulatory compliance. Review every output before using or sharing it.

### Local data

| Platform | Private application data | Durable results |
| --- | --- | --- |
| Linux | `~/.local/share/local-accessibility-studio` | `~/Documents/Local Accessibility Studio - Results` |
| macOS | `~/Library/Application Support/Local Accessibility Studio` | `~/Documents/Local Accessibility Studio - Results` |
| Windows | `%LOCALAPPDATA%\Local Accessibility Studio` | `%USERPROFILE%\Documents\Local Accessibility Studio - Results` |

Deleting a history item also removes its result directory. It does not modify
the original source document.

### Repository control files

`.gitignore` is intentionally tracked: it prevents virtual environments,
models, tokens, databases, logs, native build products, user documents, page
previews, and audio from entering Git. `.github/` contains only read-only CI
and dependency-update configuration.

The `.git` directory is repository metadata on the local computer. It is never
tracked, included in GitHub source archives, or copied by the installer.

### License

Original project code and documentation are licensed under
[GNU GPL version 3 only](LICENSE) (`GPL-3.0-only`). Distributed modified
versions must preserve the GPL terms and corresponding-source obligations.

Third-party packages, OCR models, Kokoro weights, and voice data retain their
own licenses. See
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and
[`LICENSE-GUIDE.md`](LICENSE-GUIDE.md).

This licensing summary is technical information, not legal advice. It assumes
that the publisher owns or is authorized to license the original project code.

### Development and verification

```bash
./scripts/check.sh
.venv/bin/python tests/smoke_local.py
.venv/bin/python tests/smoke_local.py --full
```

The full test performs OCR, automatic British English speech, document review,
export regeneration, American English speech, and secure history cleanup
through the real authenticated local API. Test fixtures contain synthetic text
only.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Report
security problems as described in [`SECURITY.md`](SECURITY.md), never by
attaching a confidential document to a public issue.

---

<a id="italiano"></a>

## Italiano

**Local Reader** è il repository sorgente dell'applicazione installata con il
nome **Local Accessibility Studio**. Nasce come progetto per la didattica
inclusiva: offrire a insegnanti, studenti, educatori di sostegno, famiglie e
professionisti un modo semplice per trasformare documenti scansionati o
difficili in testo revisionabile e sintesi vocale IA di alta qualità
direttamente sul proprio dispositivo.

L'intero percorso da OCR a lettura resta locale: materiale didattico, verifiche,
documenti relativi agli adattamenti e altri contenuti riservati non devono
raggiungere server esterni. È pensato per hardware consumer di fascia
medio-bassa senza GPU e rimane utile anche fuori dalla scuola quando serve una
lettura accessibile e privata.

### Distribuzione attuale

La versione **0.2.0** viene attualmente distribuita come sorgente. I pacchetti
`.exe`, `.AppImage` e `.dmg` non sono ancora pubblicati: questo README non
promette installer che non sono stati costruiti e verificati.

| Sistema | Verifica attuale | Architettura |
| --- | --- | --- |
| Linux | Pipeline completa OCR, revisione, export e Kokoro | x86-64 |
| Windows 10/11 | Installer e server core reale verificati in CI; motori nativi da provare | x86-64 |
| macOS 13+ | Installer e server core reale verificati in CI; motori nativi da provare | Apple Silicon |

La pipeline completa dei modelli viene provata automaticamente su Linux. Su
Windows e macOS il profilo sorgente va considerato ancora preliminare finché
non verranno aggiunti test completi dei motori sulle rispettive piattaforme.

### Installazione dal sorgente

Scarica o clona il repository, apri un terminale nella cartella principale ed
esegui:

```bash
./install.sh
./start.sh
```

Su Windows usa PowerShell:

```powershell
.\install.ps1
.\start.ps1
```

Su Linux viene aggiunta anche **Local Accessibility Studio** al menu delle
applicazioni, senza richiedere `sudo`.

La prima installazione usa internet per scaricare pacchetti Python bloccati con
hash SHA-256 e modelli verificati. L'installer accetta soltanto wheel
precompilate e non costruisce distribuzioni sorgente. La normale elaborazione
dei documenti resta locale e non richiede la rete.

### Installazione plug-and-play con un agente IA

Se un agente IA per lo sviluppo può usare il terminale del computer, copia il
prompt pronto da
[`AI-AGENT-INSTALL-PROMPT.md`](AI-AGENT-INSTALL-PROMPT.md). Il prompt chiede
all'agente di:

- verificare sistema operativo e architettura supportata;
- scaricare questo repository senza inviare altrove documenti dell'utente;
- eseguire l'installer ufficiale con il profilo voce CPU più adatto;
- avviare l'applicazione e controllare il suo endpoint locale;
- spiegare dove restano dati privati e risultati persistenti;
- fermarsi e descrivere chiaramente l'errore senza aggirare le protezioni.

Per l'installazione non serve alcun documento. Un file realmente riservato non
deve mai essere caricato in un agente IA, una issue, una chat o un servizio
esterno di diagnostica.

#### Profili voce compatto e rapido

L'installazione predefinita scarica Kokoro INT8. Su molti processori x86
moderni, il modello FP32 più grande può generare la voce molto più rapidamente:

```bash
./install.sh --fast-tts
```

| Profilo Kokoro | Dimensione | Scopo |
| --- | ---: | --- |
| INT8 compatto | 92.361.271 byte | Installazione più piccola |
| FP32 rapido | 325.532.387 byte | Sintesi più veloce sulle CPU compatibili |
| Pacchetto voci | 28.214.398 byte | Voci italiane e inglesi |

Tutti i file Kokoro vengono confrontati con gli SHA-256 fissati in
[`scripts/install_kokoro.py`](scripts/install_kokoro.py). La wheel RapidOCR
contiene i modelli ONNX PP-OCRv6 small. Modelli, ambienti, documenti e audio
generati restano esclusi da Git.

### Funzioni

- Interfaccia italiana o inglese con preferenza locale.
- OCR di PDF, PNG, JPEG, WebP, TIFF e BMP con RapidOCR, PP-OCRv6 small e ONNX
  Runtime su CPU.
- Anteprima pagina affiancata ai blocchi modificabili e alla confidenza OCR.
- Ruoli revisionabili per titoli, paragrafi, elenchi, numeri di pagina ed
  elementi esclusi dalla lettura.
- Rigenerazione di HTML semantico e testo pulito dopo ogni salvataggio.
- Bozza audio Kokoro automatica dopo l'OCR, disattivabile.
- Voci maschili e femminili italiane, inglesi americane e britanniche.
- Velocità regolabile e profilo FP32 rapido per CPU.
- Cancellazione singola o completa della cronologia e dei relativi risultati.
- Coda persistente con eliminazione delle copie di lavoro dopo successo,
  errore o riavvio interrotto.

Piper non viene installato né utilizzato.

### Voci

| Lingua | Maschile | Femminile |
| --- | --- | --- |
| Italiano | Nicola (`im_nicola`) | Sara (`if_sara`) |
| English — Stati Uniti | Michael (`am_michael`) | Heart (`af_heart`) |
| English — Regno Unito | George (`bm_george`) | Emma (`bf_emma`) |

Passando l'interfaccia a English, il documento successivo usa per impostazione
predefinita l'inglese americano. Lingua del documento, pronuncia e voce restano
modificabili durante la revisione. Il codice passa la lingua selezionata al
fonemizzatore di Kokoro: non cambia soltanto l'etichetta.

### Flusso di lavoro

1. Seleziona lingua e voce maschile o femminile.
2. Carica un PDF o un'immagine supportata.
3. Attendi OCR locale e, normalmente, la bozza audio automatica.
4. Apri **Rivedi testo e ordine**.
5. Correggi titolo, testo, lingua, ordine di lettura e ruoli semantici.
6. Salva, scarica HTML/testo oppure rigenera l'audio.
7. Prova il risultato con il lettore, lo screen reader e l'utente destinatario.

L'originale non viene mai modificato. Anteprime, testo revisionato, HTML,
rapporti OCR e WAV sono risultati persistenti e possono ancora contenere
informazioni riservate.

### Limite di accessibilità

OCR, ordine di lettura, riconoscimento dei titoli e sintesi vocale possono
sbagliare. I file generati sono **bozze da revisionare**, non la prova che un
documento rispetti WCAG, PDF/UA, European Accessibility Act o altri requisiti.

La confidenza bassa è mostrata, ogni ruolo rimane modificabile e l'interfaccia
non definisce conforme un risultato non revisionato. La versione attuale
esporta HTML semantico e testo semplice. PDF con tag, EPUB e DOCX restano in
roadmap finché non potranno essere provati con tecnologie assistive e utenti
reali.

Consulta [`DISCLAIMER.md`](DISCLAIMER.md) per tutti i limiti.

### Modello di privacy e sicurezza

- Il servizio ascolta soltanto sul loopback numerico `127.0.0.1`.
- Le API richiedono un token casuale dell'installazione.
- Le richieste che modificano dati verificano l'origine esatta del browser.
- Gli upload troppo grandi vengono rifiutati prima del parser multipart.
- I processi Python rifiutano connessioni non loopback.
- Su Linux viene aggiunto un guard nativo quando è disponibile un compilatore C.
- L'interfaccia non contiene telemetria, CDN, account o inferenza remota.
- Sono applicati limiti a upload, modifiche, pagine, pixel, frame, percorsi degli
  artefatti e dimensione del testo parlato.
- Modelli e voci Kokoro devono corrispondere agli SHA-256 approvati.
- OCR e sintesi usano ambienti Python separati.
- Il testo dell'utente e dell'OCR viene inserito con escaping in un modello HTML
  fisso e non è mai interpretato come markup.
- Le copie di lavoro vengono eliminate dopo completamento, errore e riavvio
  interrotto.
- I gruppi di processi OCR e sintesi attivi vengono terminati durante la chiusura
  ordinata dell'applicazione.

La rete serve durante l'installazione. Il browser predefinito è esterno al
guard dell'applicazione e può generare traffico proprio in background. I guard
sono una difesa aggiuntiva, non una sandbox del sistema operativo e non
proteggono da codice nativo malevolo o da un altro processo già attivo con lo
stesso utente.

L'elaborazione locale non dimostra da sola conformità GDPR, accessibilità o
altri adempimenti. Controlla ogni risultato prima di usarlo o condividerlo.

### Dati locali

| Sistema | Dati applicativi privati | Risultati persistenti |
| --- | --- | --- |
| Linux | `~/.local/share/local-accessibility-studio` | `~/Documents/Local Accessibility Studio - Results` |
| macOS | `~/Library/Application Support/Local Accessibility Studio` | `~/Documents/Local Accessibility Studio - Results` |
| Windows | `%LOCALAPPDATA%\Local Accessibility Studio` | `%USERPROFILE%\Documents\Local Accessibility Studio - Results` |

Cancellando un elemento dalla cronologia viene eliminata anche la sua cartella
dei risultati. L'originale non viene modificato.

### File di controllo del repository

`.gitignore` è incluso intenzionalmente: impedisce di aggiungere ambienti,
modelli, token, database, log, prodotti nativi, documenti, anteprime e audio.
`.github/` contiene soltanto CI in sola lettura e configurazione degli
aggiornamenti delle dipendenze.

La directory `.git` contiene metadati locali del repository. Non è tracciata,
non entra negli archivi sorgente di GitHub e non viene copiata
dall'installazione.

### Licenza

Codice e documentazione originali sono distribuiti sotto
[GNU GPL versione 3 soltanto](LICENSE) (`GPL-3.0-only`). Le versioni modificate
distribuite devono rispettare la GPL e gli obblighi sul sorgente corrispondente.

Pacchetti, modelli OCR, pesi Kokoro e voci conservano le licenze originali.
Consulta [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) e
[`LICENSE-GUIDE.md`](LICENSE-GUIDE.md).

Questo riepilogo è informazione tecnica, non un parere legale. Presuppone che
chi pubblica possieda o sia autorizzato a licenziare il codice originale.

### Sviluppo e verifica

```bash
./scripts/check.sh
.venv/bin/python tests/smoke_local.py
.venv/bin/python tests/smoke_local.py --full
```

Il test completo esegue OCR, bozza automatica con voce britannica, revisione,
rigenerazione degli export, voce americana e cancellazione sicura della
cronologia attraverso le API locali autenticate. Usa soltanto testi sintetici.

Leggi [`CONTRIBUTING.md`](CONTRIBUTING.md) prima di una pull request. Segnala i
problemi di sicurezza come indicato in [`SECURITY.md`](SECURITY.md), senza
allegare documenti riservati a una issue pubblica.
