# Local Accessibility Studio

Local Accessibility Studio è un lettore assistivo local-first, pensato anche
per studenti con dislessia e difficoltà grafiche. L’interfaccia usa
OpenDyslexic, ha testi grandi e contrastati, e mantiene modificabile ogni
risultato OCR.

## Flussi disponibili

- OCR di PDF e immagini multipagina con PaddleOCR plain `PP-OCRv6` su CPU.
  Non usa PP-Structure: tabelle e impaginazioni complesse non vengono
  ricostruite, così il risultato è un testo lineare adatto alla lettura.
- Inserimento di testo copiato/incollato o allegato (`.txt`, `.md`).
- Revisione del testo OCR, esportazione in HTML accessibile e `reading.txt`.
- Sintesi vocale con Edge-TTS a blocchi, adatta anche a documenti molto lunghi.
  Le voci preimpostate sono `it-IT-GiuseppeMultilingualNeural` e
  `it-IT-ElsaNeural`, oltre alle coppie inglesi USA/UK.
- Riorganizzazione facoltativa con LFM2.5 230M tramite llama.cpp, in CPU o
  GPU quando il binario è stato costruito con il backend adatto. Il guard
  confronta i caratteri non bianchi prima di accettare l’output del modello;
  se il modello modifica il contenuto, viene usata una formattazione
  deterministica solo-spazi.
- In “Impostazioni avanzate” si può scegliere Gemma 4 E4B Q4_0 per una
  riorganizzazione locale più potente e scaricarlo con un pulsante. Sono circa
  5,2 GB e il download è facoltativo.
- Studio completo semplificato: PaddleOCR → modello audio scelto. Nel workflow
  principale puoi scegliere direttamente Edge-TTS o Kokoro 82M.
- Kokoro 82M ONNX per una voce offline, anche con la rete disattivata.
- Il pulsante globale “Modalità offline” passa in un clic da Edge-TTS a Kokoro
  e impedisce al server di inviare il testo online.
- Provider vocali opzionali Voxtral/Mistral, Fish Audio ed ElevenLabs. Le
  chiavi e gli ID voce si configurano dalla pagina Impostazioni; Fish Audio usa
  un Reference ID già creato.
- Su macOS Apple Silicon si può preparare Fish Audio S2 Pro MLX a 8 bit (circa
  6,7 GB) e salvare un campione con trascrizione per la clonazione locale. Il
  modello è soggetto alla Fish Audio Research License e non è incluso nel repo.
- Clonazione disponibile tramite Voxtral/Mistral ed ElevenLabs, con conferma
  del consenso. Il campione temporaneo viene eliminato dopo l’invio.

Il flusso può essere usato separatamente: solo OCR, solo audio su testo già
disponibile, oppure OCR → revisione → audio. La modalità “Solo organizza” è
separata e usa LFM locale per impostazione predefinita; può anche usare un
provider configurato tra Mistral, OpenCode Zen, Google Gemini, Anthropic
Claude, NVIDIA NIM, Kilo Gateway o un endpoint personalizzato. La pagina
Impostazioni mette in alto solo la scelta audio essenziale. Provider cloud,
modelli, chiavi API, guide e clonazione sono raccolti sotto “Impostazioni
avanzate”.

La sessione viene salvata localmente nel browser: vista attiva, moduli di
testo, bozze dell’editor e lavori in corso possono essere ripristinati dopo
uno spegnimento. I job locali che avevano già ricevuto la copia privata del
file vengono rimessi automaticamente in coda al riavvio; un caricamento
interrotto prima del completamento viene invece segnalato come non riuscito.
Anche la posizione di ascolto degli audio generati viene salvata e ripristinata
alla riapertura.

## Installazione

Richiede Python 3.12 e `uv` (l’installer può scaricarlo):

```bash
./install.sh
./start.sh
```

Su macOS Apple Silicon si può fare tutto con una sola riga nel Terminale:

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/main/install-macos.sh | bash
```

La riga scarica il codice pubblico, prepara Python, OCR, sintesi vocale,
Kokoro, LFM e FFmpeg, scarica i modelli necessari e crea `Local Accessibility
Studio.app` sul Desktop. Il doppio clic avvia il server locale e apre la web
app nel browser. Gemma 4 e Fish Audio, molto più pesanti, restano opzionali:
si possono scaricare dalle Impostazioni avanzate oppure includere durante
l’installazione impostando `LAS_INSTALL_OPTIONAL_MODELS=1`.

Su Windows:

```powershell
.\install.ps1
.\start.ps1
```

L’installazione prepara ambienti separati per web core, PaddleOCR, Edge-TTS e
Kokoro, pre-carica i modelli PaddleOCR e installa il modello LFM locale e il
binario CPU di `llama.cpp` quando non sono già presenti. Include anche FFmpeg
nel pacchetto Python per rendere l’audio offline indipendente dal sistema.
`--skip-models` evita
il prefetch completo e lascia disponibili soltanto i componenti già in cache.

## Pacchetti plug-and-play

I pacchetti portabili usano un piccolo launcher compilato: al primo avvio
creano una copia privata dell’app nella cartella dati dell’utente, scaricano
`uv` con checksum, preparano Python 3.12 e installano automaticamente i
modelli e le dipendenze necessarie. Non richiedono Python o `uv` già installati
e non copiano documenti personali nel pacchetto.

Per costruire localmente il pacchetto del sistema in uso:

```bash
./packaging/build_appimage.sh   # Linux x86-64 → dist/*.AppImage
./packaging/build_macos.sh      # macOS Apple Silicon → dist/*.app
```

Su Windows PowerShell:

```powershell
.\packaging\build_windows.ps1  # Windows x86-64 → dist\*.exe
```

PyInstaller produce binari nativi: ogni script va eseguito sul sistema
operativo di destinazione. La build Linux viene verificata in locale; macOS e
Windows richiedono una macchina nativa corrispondente.

Il modello LFM2.5 Q8 viene cercato prima nel runtime dell’app e poi, per
riusare un’installazione già presente, in:

```text
~/.lmstudio/models/LiquidAI/LFM2.5-230M-GGUF/LFM2.5-230M-Q8_0.gguf
```

Per un binario llama.cpp in un’altra posizione usare
`LOCAL_ACCESSIBILITY_STUDIO_LLAMA_CLI` e, se necessario,
`LOCAL_ACCESSIBILITY_STUDIO_LFM_MODEL`. La dashboard mostra separatamente se
OCR, Edge-TTS, Kokoro e il modello locale selezionato sono disponibili.

## Privacy

Il server web ascolta solo su `127.0.0.1`, richiede un token locale e salva le
copie di lavoro con permessi privati. OCR e LFM restano locali. Edge-TTS,
Voxtral, Fish Audio ed ElevenLabs inviano il testo al rispettivo servizio solo
quando vengono scelti. Kokoro non richiede rete. Se il testo non deve uscire
dal computer, usare Kokoro in “Solo voce”.

Installazione, cache modelli e ambienti Python richiedono rete; l’elaborazione
locale successiva non usa provider esterni quando è attiva la modalità offline.
Il launcher portabile
mostra i passaggi nel terminale e registra gli errori nella cartella dati locale
se la prima preparazione non riesce.

## Dati

| Sistema | Dati applicativi | Risultati persistenti |
| --- | --- | --- |
| Linux | `~/.local/share/local-accessibility-studio` | `~/Documents/Local Accessibility Studio - Results` |
| macOS | `~/Library/Application Support/Local Accessibility Studio` | `~/Documents/Local Accessibility Studio - Results` |
| Windows | `%LOCALAPPDATA%\\Local Accessibility Studio` | `%USERPROFILE%\\Documents\\Local Accessibility Studio - Results` |

La cancellazione dalla cronologia rimuove anche i risultati locali. L’originale
non viene modificato.

## Verifica

```bash
./scripts/check.sh
.venv/bin/python tests/smoke_local.py
.venv/bin/python tests/smoke_local.py --full
```

Il test completo usa solo una fixture sintetica e verifica PaddleOCR, testo
incollato, LFM2.5 con ragionamento disattivato, revisione, due generazioni
Edge-TTS e pulizia dei file. Kokoro viene verificato durante l’installazione
con il controllo della libreria e può essere provato dalla modalità “Solo voce”.

I risultati sono bozze da controllare con l’utente, uno screen reader e il
lettore audio previsto. Non costituiscono da soli conformità WCAG, PDF/UA,
GDPR o altri requisiti normativi.

## Licenza

Codice e documentazione originali: [GPL-3.0-only](LICENSE). PaddleOCR,
PaddlePaddle, Edge-TTS, OpenDyslexic, llama.cpp, il modello LFM e ogni altra
dipendenza mantengono le proprie licenze e condizioni. Vedere
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) e
[`LICENSE-GUIDE.md`](LICENSE-GUIDE.md).
