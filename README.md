# Local Reader No GPU

[Italiano](#italiano) · [English](#english) · [Download](https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/releases/latest)

## Italiano

Lettore assistivo local-first per trasformare PDF, immagini e testo in contenuti
modificabili e audio. Interfaccia italiana/inglese con OpenDyslexic, controlli
grandi e flussi separati per OCR, revisione e lettura. Non serve una GPU.

La versione standard usa **Kokoro offline senza account, login o chiavi API**.
Pocket TTS è stato rimosso. Kokoro offre voci predefinite, **non clona la voce**.
Le funzioni cloud e la clonazione opzionale sono distinte dal percorso standard.

### Scarica e apri

I pacchetti sono nella [release](https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/releases/latest).

| Sistema supportato | File | Apertura |
| --- | --- | --- |
| Windows 10/11, Intel/AMD 64 bit | `.exe` | Doppio clic, senza installare Python |
| Linux x86-64, distribuzione desktop recente | `.AppImage` | Consenti l'esecuzione nelle proprietà, poi apri |
| macOS Apple Silicon (M1 o successivo), macOS 14+ | `.dmg` oppure `.app.zip` | Nel DMG trascina l'app in Applicazioni; apri la copia |

Mac Intel, Windows ARM e Linux ARM non hanno pacchetti in questa release.
I pacchetti non hanno firma commerciale e macOS non è notarizzato: SmartScreen
e Gatekeeper possono richiedere una conferma. Verifica origine e checksum;
non disattivare le protezioni di sistema per installare l'app.

Il primo avvio apre una finestra di avanzamento nel terminale, prepara Python
3.12 e gli ambienti isolati e scarica OCR, Kokoro, FFmpeg e il modello testuale
leggero LFM. Richiede Internet e alcuni minuti; non è un pacchetto completamente
offline prima di questa preparazione. Poi apre il browser sull'app locale.
Se il download si interrompe, riapri lo stesso pacchetto: la preparazione
incompleta viene ritentata. Non chiudere il terminale mentre usi l'app.

Come margine pratico, consigliamo 8 GB di RAM e almeno 5 GB liberi per la
versione standard, oltre ai documenti e ai risultati. Sono indicazioni
prudenziali, non requisiti minimi certificati. Modelli opzionali e cache
possono richiedere molto più spazio.

### Installazione con una sola riga

Esegui come utente normale, non come amministratore. Questi comandi eseguono
uno script pubblico della versione indicata: leggilo prima se desideri
verificarne il contenuto. Lo script scarica il pacchetto della release,
verifica SHA-256 e lo avvia; non richiede Git, Python o uv già installati.
I checksum verificano integrità, non sono una firma indipendente da GitHub.

Linux (Terminale):

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/v0.3.3/install-release.sh | bash
```

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/v0.3.3/install-release.ps1 | iex
```

macOS Apple Silicon (Terminale):

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/v0.3.3/install-release.sh | bash
```

Su Windows l'EXE crea o aggiorna un collegamento nel menu Start; macOS installa sotto
`~/Applications/Local Reader No GPU 0.3.3`. Su Linux il percorso del
pacchetto installato è mostrato nel terminale; puoi riaprirlo da quel percorso.
Lo script Linux usa la modalità estrazione dell'AppImage, senza richiedere FUSE.

### Primo utilizzo

1. Apri l'app e attendi che la dashboard mostri i motori pronti. Scegli la
   lingua dell'interfaccia; la lingua del documento e quella della voce sono
   impostazioni separate.
2. Per un PDF o un'immagine, scegli il flusso OCR e carica il documento.
   Per testo già disponibile, incolla il contenuto o carica un file `.txt`
   o `.md`: non è necessario eseguire OCR.
3. Se il testo è riservato, attiva **Modalità offline** prima di avviare lavori.
   Scegli Kokoro per la voce. I servizi online vengono bloccati dal server,
   non soltanto nascosti nell'interfaccia.
4. Apri il risultato, confrontalo con le anteprime e correggi eventuali errori
   nell'editor. Imposta voce, lingua e velocità.
5. Avvia la lettura. Puoi generare l'audio automaticamente dopo l'OCR oppure
   solo dopo la revisione. Salva l'MP3, il testo e l'HTML dai risultati.
6. La cronologia conserva i lavori e il browser salva bozze e posizione
   d'ascolto. Eliminare un lavoro elimina i suoi risultati locali; il file
   originale non viene modificato.

### Come funziona

- **Ingresso:** copie di lavoro private, controlli su dimensioni, numero di
  pagine e pixel; testo diretto e documenti seguono percorsi distinti.
- **OCR:** PaddleOCR plain PP-OCRv6 su CPU riconosce righe e blocchi.
  Non usa PP-Structure, ricostruzione di tabelle o correzione dell'impaginazione
  complessa. Una scansione nitida migliora il risultato.
- **Revisione:** testo, ordine di lettura e ruoli restano da controllare.
  L'HTML usa contenuti testuali escapati, non esegue il testo del documento.
- **Organizzazione facoltativa:** LFM2.5 230M usa llama.cpp locale con
  ragionamento disattivato. L'output è accettato soltanto se preserva i
  caratteri non bianchi; altrimenti si applica una formattazione deterministica.
  Non è una funzione per riassumere o riscrivere liberamente il contenuto.
- **Audio:** il testo viene suddiviso in blocchi, sintetizzato e unito in MP3.
  Kokoro usa ONNX su CPU e FFmpeg incluso nella dipendenza audio.
  Il modello FP32 occupa circa 326 MB, le voci circa 28 MB; LFM Q8 circa 247 MB.
  L'installazione scarica anche Python, dipendenze e modelli OCR.
- **Recupero:** lavori persistenti possono essere ripresi dopo un riavvio.
  Un caricamento mai completato va ripetuto. Le copie temporanee vengono
  ripulite; esportazioni e campioni salvati rimangono dati dell'utente.

Per avere la risposta più rapida usa testo diretto quando possibile, Kokoro e
il modello leggero predefinito. Evita l'organizzazione AI se non serve.
Tempi di OCR e audio dipendono da CPU e lunghezza del documento: non è garantita
una lettura istantanea di file lunghi.

### Online, offline e modelli opzionali

Il toggle offline interrompe i lavori online attivi; una lettura Edge-TTS
può ripartire con Kokoro. Disattivarlo rende nuovamente disponibili i provider
online. Se Edge-TTS fallisce, viene tentato Kokoro quando installato.

| Motore | Rete durante l'uso | Account | Clonazione |
| --- | --- | --- | --- |
| Kokoro | No, dopo il download | No | No |
| Edge-TTS | Sì, testo inviato a Microsoft | Nessuna chiave nell'app | No |
| Voxtral / Mistral | Sì | Chiave API, condizioni del servizio | Sì |
| ElevenLabs | Sì | Chiave API, condizioni del servizio | Sì |
| Fish Audio cloud | Sì | Chiave API e Reference ID | ID creato esternamente |
| Fish Audio locale MLX | No, dopo preparazione | Nessuna chiave cloud nell'app | Solo Mac Apple Silicon |

In **Impostazioni → Impostazioni avanzate** trovi chiavi, provider e download
opzionali. Gemma 4 E4B Q4 occupa circa 5,2 GB. Fish Audio S2 Pro MLX 8-bit circa
6,7 GB, oltre alle dipendenze. Non sono scaricati dal percorso standard.
Fish è soggetto a una licenza di ricerca/non commerciale: verifica i termini
prima di installarlo o utilizzarlo. La riorganizzazione può usare anche un
provider AI cloud configurato; in tal caso il testo viene inviato al provider.

### Registrare e usare una voce clonata

1. Nelle impostazioni avanzate apri **Clonazione della voce**.
2. Scegli un provider compatibile e configurato. Kokoro non compare perché non
   effettua clonazione; Pocket TTS non è più disponibile.
3. Carica un campione oppure premi **Registra** e autorizza il microfono nel
   browser. Usa un ambiente silenzioso e un solo parlante; la registrazione
   si arresta automaticamente dopo circa 29 secondi.
4. Riascolta il campione, indica un nome e, per Fish locale, la trascrizione.
   Conferma di avere il consenso e i diritti necessari, poi avvia la clonazione.
   Un provider cloud riceve il campione: la registrazione non viene inviata
   soltanto perché hai premuto Registra.
5. In **Voci clonate salvate** seleziona **Usa** per impostare una voce.
   **Rimuovi** la nasconde dal menu: non elimina il campione locale né la voce
   sul servizio remoto. Per eliminarla dal cloud usa anche il servizio stesso.

Le vecchie preferenze Pocket TTS vengono migrate a Kokoro. I vecchi campioni
privati sono conservati ma non proposti tra le voci utilizzabili.
Non clonare voci senza consenso né usare la funzione per impersonare persone.

### Dati, privacy e sicurezza

| Sistema | Dati e runtime |
| --- | --- |
| Linux | `~/.local/share/local-reader-no-gpu` (rispetta XDG) |
| Windows | `%LOCALAPPDATA%\Local Reader No GPU` |
| macOS | `~/Library/Application Support/Local Reader No GPU` |

I risultati si trovano in `Documents/Local Reader No GPU - Results`
nella cartella utente; su Linux viene usata `Documenti` se presente al posto
di `Documents`. Cache e stato possono risiedere in cartelle separate.
Chiavi API, token locale e campioni vocali non vanno condivisi: sono dati
locali, non un archivio cifrato. Non pubblicare cartelle runtime o risultati.

Il server ascolta su `127.0.0.1`, usa un token locale e controlla l'origine
delle richieste. OCR, organizzazione locale e Kokoro non richiedono provider
remoti dopo la preparazione. Download e funzioni cloud richiedono rete.
Il browser e altri programmi del sistema non sono isolati dal toggle.

L'app è per **un solo utente locale**: non esporla su LAN o Internet.
Le protezioni di rete sono difese aggiuntive, non una sandbox del sistema
operativo. Consulta [SECURITY.md](SECURITY.md) per limiti e segnalazioni private.
Non esiste garanzia assoluta di sicurezza o conformità WCAG, PDF/UA o GDPR.

### Problemi comuni e aggiornamenti

- **Prima installazione interrotta:** controlla rete e spazio libero, poi
  riapri il pacchetto. Il terminale mostra il passaggio che non è riuscito.
- **Niente voce offline:** attendi il download completo e verifica Kokoro nella
  dashboard. Non basta scaricare il solo launcher per lavorare senza rete.
- **Microfono non disponibile:** consenti l'accesso al sito locale nelle
  impostazioni del browser; in alternativa carica un campione audio.
- **AppImage non si avvia:** da terminale usa
  `APPIMAGE_EXTRACT_AND_RUN=1 ./Local-Reader-No-GPU-0.3.3-linux-x86_64.AppImage`.
- **Aggiornamento:** dalla versione 0.3.3 l'app controlla le release all'avvio
  e ogni 12 ore. Usa **Verifica aggiornamenti** per un controllo manuale; se
  trova una release, scarica il pacchetto indicato, chiudi l'app e aprilo.
  Su Windows basta avviare l'EXE scaricato: si installa nella cartella utente
  e crea o aggiorna il collegamento nel menu Start per le aperture successive.
  Dopo il primo aggiornamento, apri l'app dal menu Start per usare la nuova
  versione. Le versioni precedenti alla 0.3.3 non possono notificare questo
  primo aggiornamento: scarica una volta l'EXE della release e avvialo
  manualmente. Per i successivi aggiornamenti la verifica integrata segnala le
  nuove release. Impostazioni, campioni e risultati restano nella cartella dati
  locale.
- **Avvisi del sistema operativo:** controlla la release ufficiale e
  `SHA256SUMS.txt`. Non vengono forniti certificati commerciali o notarizzazione.

### Sorgenti, build e test

Con Git installato, il sorgente aggiornato è scaricabile con:

```bash
git clone https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU.git
```

Nella cartella del progetto: `./install.sh` e `./start.sh` su Linux/macOS;
`.\install.ps1` e `.\start.ps1` su Windows.
Questi installer preparano uv e Python senza installazione globale.
`--core-only` serve allo sviluppo dell'interfaccia; `--skip-models` evita
download dei modelli e richiede cache già disponibili.

```bash
./scripts/check.sh
.venv/bin/python tests/smoke_local.py --offline
.venv/bin/python tests/smoke_local.py --full
python3 packaging/install_appimage_tools.py
./packaging/build_appimage.sh
```

Su macOS usa `./packaging/build_macos.sh`; su Windows
`.\packaging\build_windows.ps1`. I builder richiedono uv e vengono eseguiti sul
sistema nativo. GitHub Actions verifica il primo avvio del pacchetto, OCR,
audio offline e il flusso completo prima della pubblicazione.
I test usano documenti sintetici, non documenti dell'autore. I test automatici
non sostituiscono una verifica con screen reader e utenti reali.

### Licenze e redistribuzione

Codice originale: [GPL-3.0-only](LICENSE). Font: SIL OFL 1.1, con testi in
[licenses](licenses). Il modello LFM usa la **LFM Open License v1.0**, con una
limitazione per uso commerciale legata a una soglia di fatturato di 10 milioni
di dollari: non è una licenza senza restrizioni. Fish locale ha termini
non commerciali/di ricerca. Le condizioni esatte dei rispettivi editori
prevalgono su questa sintesi.

La release include sorgente dell'app, checksum, avvisi delle dipendenze
installate per piattaforma e sorgenti del runtime distribuibile.
Consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md),
[LICENSE-GUIDE.md](LICENSE-GUIDE.md) e
[istruzioni per ricostruire il runtime](packaging/RUNTIME-SOURCE.md).
Questa documentazione non è un parere legale né una certificazione.

---

## English

Local-first assistive reader for PDFs, images and text, with editable OCR,
speech generation and an Italian/English interface using OpenDyslexic.
The standard workflow runs on CPU: no GPU, account or API key is required.
**Pocket TTS has been removed. Kokoro works offline but does not clone voices.**

### Download and launch

Get the [latest release](https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/releases/latest):
Windows 10/11 x86-64 `.exe`, recent desktop Linux x86-64 `.AppImage`, or
macOS 14+ Apple Silicon `.dmg` / `.app.zip`.
Intel Macs, Windows ARM and Linux ARM are not packaged.

Open the Windows executable; make the AppImage executable before opening;
on macOS drag the app from the DMG into Applications and open that copy.
Packages have no commercial signature and macOS is not notarized.
SmartScreen/Gatekeeper may warn: verify the source and checksum, and do not
disable system-wide security protections.

First launch prepares Python 3.12, isolated environments, OCR, Kokoro, FFmpeg
and the lightweight LFM model, then opens the local app in your browser.
**Internet is required for initial setup**, which may take several minutes.
Keep the progress terminal open while using the app. Reopening after an
interruption retries unfinished setup. As a practical allowance, plan for
8 GB RAM and 5 GB free disk space plus your results; these are recommendations,
not certified minimums. Optional models need substantially more space.

### One-command installation

Run as a normal user. These commands execute a public versioned script;
inspect it first if desired. It downloads the native release, verifies SHA-256
and launches it. Git, Python and uv need not be preinstalled.
Checksums provide integrity, not an independent signature against a compromised
GitHub repository.

Linux or macOS Apple Silicon, in Terminal:

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/v0.3.3/install-release.sh | bash
```

Windows, in PowerShell:

```powershell
irm https://raw.githubusercontent.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/v0.3.3/install-release.ps1 | iex
```

Windows gets a Start menu shortcut. macOS installs under
`~/Applications/Local Reader No GPU 0.3.3`. Linux prints the installed
package path and uses extraction mode, so FUSE is not required.

### Using the application

1. Wait for the engines to become ready. Interface, document and speech
   languages are separate settings.
2. Upload a PDF/image for OCR, or paste text / upload `.txt` or `.md` for
   direct reading.
3. Enable **Offline mode** before processing confidential content and use
   Kokoro. The server blocks online providers, not just the interface.
4. Compare OCR with previews, correct the editable result, then choose voice,
   language and speed. Generate speech automatically after OCR or after review.
5. Download MP3, text and HTML results. History, drafts and playback position
   are stored locally. Deleting a job deletes its local results, not the
   original document.

PaddleOCR plain PP-OCRv6 recognizes lines on CPU; it does not reconstruct
tables or complex layouts. Optional local organization uses LFM2.5 with
llama.cpp, reasoning disabled and a non-whitespace character preservation
check. If the model changes content, deterministic formatting is used instead.
This is not unrestricted summarization or rewriting.

Speech is generated in bounded chunks and combined into MP3. Kokoro FP32 is
about 326 MB, voices 28 MB and LFM Q8 247 MB, in addition to Python, OCR and
dependencies. Use direct text, Kokoro and the small default model for the
simplest workflow. Processing speed depends on CPU and document length.

### Online options and voice cloning

Turning offline mode on interrupts active online work; Edge-TTS speech can
restart with Kokoro. Turning it off allows online providers again.
Edge-TTS also falls back to installed Kokoro after a service failure.

Edge-TTS sends text to Microsoft without an API key configured in the app.
Voxtral/Mistral, ElevenLabs and Fish Audio cloud require your own credentials
and are subject to their service terms. Cloud AI organization likewise sends
text to the configured provider.

Advanced settings offer optional Gemma 4 E4B Q4 (~5.2 GB) and Fish Audio S2 Pro
MLX 8-bit (~6.7 GB plus dependencies, Apple Silicon only). They are not part of
default downloads. Fish's research/non-commercial license must be reviewed.

To clone a voice, open **Settings → Advanced settings → Voice cloning**:

1. Select a supported, configured provider: Voxtral/Mistral, ElevenLabs, or
   local Fish on Apple Silicon. Fish cloud instead uses an externally created
   Reference ID.
2. Upload a sample or record directly in the app after granting microphone
   permission. Recording stops automatically after about 29 seconds.
3. Listen to the sample, name the voice, add a transcript for local Fish, and
   confirm consent before submitting. Cloud cloning uploads the sample;
   recording alone does not send it.
4. Choose **Use** in the saved-clones menu. **Remove** hides a voice from that
   menu but does not delete its local sample or the voice at the cloud provider.

Kokoro has preset voices only. Legacy Pocket preferences migrate to Kokoro;
old private samples remain on disk but are not offered as supported voices.
Only clone voices you have consent and rights to use; do not impersonate people.

### Privacy, storage and troubleshooting

Runtime/settings: Linux `~/.local/share/local-reader-no-gpu` (XDG
overrides supported); Windows `%LOCALAPPDATA%\Local Reader No GPU`;
macOS `~/Library/Application Support/Local Reader No GPU`.
Results are under your user `Documents/Local Reader No GPU - Results`
folder (`Documenti` is used when applicable). Cache and state may be separate.
Credentials, local tokens and voice samples are private local files, not an
encrypted vault. Never publish your runtime or results directory.

The server binds to `127.0.0.1`, requires a local token and checks request
origins. Local OCR, organization and Kokoro do not require remote providers
after setup. The browser and other applications are outside the network
guard. This is a single-user workstation app, not a LAN/public service or an
OS sandbox. See [SECURITY.md](SECURITY.md).

If setup fails, check network/disk space and reopen the package; terminal
output identifies the failed step. If offline speech is missing, finish the
model download. If microphone access fails, check browser permission or upload
a sample. On Linux, try `APPIMAGE_EXTRACT_AND_RUN=1 ./your-package.AppImage`.
From version 0.3.3, the app checks releases on startup and every 12 hours.
Choose **Check for updates** for a manual check, download the offered package,
close the app and open it. On Windows, the downloaded EXE installs under the
user's local app-data folder and creates or refreshes the Start menu shortcut
to launch that installed copy. After this first update, open the app from the
Start menu to use the new version. Earlier versions cannot announce this first
update, so download and open the EXE once manually; later releases can be
checked in-app. Settings, samples and results stay in the local data directory.

### Development, verification and licensing

Clone the public source with
`git clone https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU.git`.
Inside it run `./install.sh` then `./start.sh` on Linux/macOS, or
`.\install.ps1` then `.\start.ps1` on Windows.
`--core-only` is for UI development; `--skip-models` requires existing caches.

Run `./scripts/check.sh`, then `.venv/bin/python tests/smoke_local.py --offline`
and `.venv/bin/python tests/smoke_local.py --full`. The native builders are
`packaging/build_appimage.sh`, `packaging/build_macos.sh` and
`packaging/build_windows.ps1`; Linux first needs
`python3 packaging/install_appimage_tools.py`. Each builder runs on its target
OS. Release automation tests actual first-run installation, OCR and speech.

Original code is [GPL-3.0-only](LICENSE); fonts are SIL OFL 1.1.
LFM uses LFM Open License v1.0 with a commercial-use revenue threshold of
USD 10 million. Local Fish has research/non-commercial restrictions.
These terms are not replaced by the application's GPL license.
See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md),
[LICENSE-GUIDE.md](LICENSE-GUIDE.md), [licenses](licenses) and
[runtime rebuilding instructions](packaging/RUNTIME-SOURCE.md).

Releases include app source, checksums, per-platform installed dependency
notices and runtime source archives. Automated tests use synthetic documents;
they do not replace screen-reader/user testing. No absolute security,
accessibility, WCAG, PDF/UA or GDPR compliance is claimed. This is technical
documentation, not legal advice.
