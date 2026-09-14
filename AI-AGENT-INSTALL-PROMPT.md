# AI-agent installation prompt

Copy only the section matching your language into an AI coding agent that has
permission to use a terminal on the computer where Local Reader will run.

Never attach a personal, school, medical, assessment, or confidential document
to the agent. Installation and verification do not require one.

## English prompt

```text
Install and start Local Reader No GPU from this official repository:

https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU

Work only on this computer and follow these rules:

1. First inspect the operating system, CPU architecture, free disk space, and
   existing checkout. Do not use sudo or administrator privileges unless the
   official installer explicitly requires them and you explain why first.
2. Supported source-installation targets are Linux x86-64, Windows 10/11
   x86-64, and macOS 13+ Apple Silicon. If the target is different, stop and
   report it. Do not force an unsupported installation.
3. Download with Git into a new folder, or safely update an existing clean
   checkout. Use the main branch. Never overwrite unrelated user changes.
4. Read README.md, SECURITY.md, DISCLAIMER.md, and the installer before
   executing it. Use only scripts contained in this repository.
5. On Linux or macOS run:
      ./install.sh
   On Windows PowerShell run:
      .\install.ps1
   Do not install unrelated system packages, telemetry, browser extensions, or
   API keys. Edge-TTS is an explicit optional remote speech service; explain
   that it sends selected text to Microsoft. LFM2.5 and llama.cpp are optional.
6. Let the verified installer obtain its pinned Python environments, PaddleOCR,
   Edge-TTS, cached OCR models, LFM2.5, and the matching CPU llama.cpp runtime.
   Do not bypass dependency or model hashes.
7. Start with ./start.sh on Linux/macOS or .\start.ps1 on Windows. Confirm that
   the application binds only to 127.0.0.1 and that /health reports status ok.
   Do not expose it to the LAN, a public address, a reverse proxy, or a tunnel.
8. Run ./scripts/check.sh where supported and the core smoke test:
      .venv/bin/python tests/smoke_local.py
   On Windows use the equivalent .venv\Scripts\python.exe path.
9. Do not request, open, copy, upload, or inspect a real user document. If a
   functional example is needed, use only the synthetic fixture produced by
   tests/create_sample.py.
10. At the end, report the installed version, OCR/Edge-TTS/Kokoro/LFM availability,
    local start command, local data/results directories, checks completed, and
    any limitation. If any step fails, stop and provide the
    exact non-sensitive error; never disable authentication, origin checks,
    network guards, checksum validation, or cleanup.
```

## Prompt italiano

```text
Installa e avvia Local Reader No GPU da questo repository ufficiale:

https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU

Lavora soltanto su questo computer e rispetta queste regole:

1. Prima controlla sistema operativo, architettura CPU, spazio libero e
   l'eventuale checkout esistente. Non usare sudo o privilegi amministrativi,
   salvo richiesta esplicita dell'installer ufficiale e dopo averne spiegato il
   motivo.
2. I sistemi previsti per l'installazione dal sorgente sono Linux x86-64,
   Windows 10/11 x86-64 e macOS 13+ Apple Silicon. Se il sistema è diverso,
   fermati e segnalalo. Non forzare un'installazione non supportata.
3. Scarica con Git in una nuova cartella oppure aggiorna in sicurezza un
   checkout esistente e pulito. Usa il ramo main. Non sovrascrivere modifiche
   dell'utente non collegate.
4. Leggi README.md, SECURITY.md, DISCLAIMER.md e l'installer prima di eseguirlo.
   Usa soltanto script contenuti nel repository.
5. Su Linux o macOS esegui:
      ./install.sh
   Su Windows PowerShell esegui:
      .\install.ps1
   Non installare pacchetti di sistema non collegati, telemetria o estensioni
   del browser. Edge-TTS è un servizio vocale remoto opzionale: spiega che
   invia il testo selezionato a Microsoft. LFM2.5 e llama.cpp sono opzionali.
6. Lascia che l'installer verificato scarichi gli ambienti Python versionati,
   PaddleOCR, Edge-TTS, i modelli OCR, LFM2.5 e il runtime CPU di llama.cpp.
   Non aggirare gli hash di dipendenze o modelli.
7. Avvia con ./start.sh su Linux/macOS o .\start.ps1 su Windows. Verifica che
   l'applicazione ascolti soltanto su 127.0.0.1 e che /health riporti status ok.
   Non esporla alla LAN, a indirizzi pubblici, reverse proxy o tunnel.
8. Dove supportato, esegui ./scripts/check.sh e lo smoke test del nucleo:
      .venv/bin/python tests/smoke_local.py
   Su Windows usa il percorso equivalente .venv\Scripts\python.exe.
9. Non chiedere, aprire, copiare, caricare o ispezionare documenti reali
   dell'utente. Se serve un esempio funzionale, usa soltanto il documento
   sintetico prodotto da tests/create_sample.py.
10. Alla fine indica versione installata, disponibilità di OCR, Edge-TTS,
    Kokoro e LFM,
    comando locale di avvio, cartelle locali di dati/risultati, controlli
    completati ed eventuali limiti. Se un passaggio fallisce, fermati e riporta
    l'errore esatto ma non sensibile; non disattivare autenticazione, controlli
    dell'origine, guard di rete, checksum o pulizia.
```
