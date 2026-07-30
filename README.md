# Local AI App Starter

A small, security-minded foundation for local-only AI desktop utilities that
run on ordinary CPU hardware. It is a **starter**, not a finished product and
not a copy of AI Privacy Studio.

The reusable core provides:

- a FastAPI service bound to numeric loopback (`127.0.0.1`) only;
- a per-installation secret token and strict browser-origin checks;
- a Python runtime guard and an optional Linux-native guard that deny external
  connections from guarded processes;
- bounded uploads, private working directories, and automatic work-copy cleanup;
- a persistent SQLite job queue and a narrow plug-in contract for local engines;
- a dependency-free, bilingual Italian/English interface;
- pinned installers for Linux x86-64, macOS Apple Silicon, and Windows x86-64.

It intentionally contains no OCR stack, language model, cloud SDK, telemetry,
document corpus, AI Privacy Studio branding, or generated binary.

## Start a new product

Copy this directory outside any existing repository, then set its identity:

```bash
python3 scripts/configure.py \
  --name "My Local App" \
  --slug "my-local-app" \
  --description-en "A precise English description." \
  --description-it "Una descrizione precisa in italiano."
```

Replace the example engine in `app/engines/`, register the replacement in
`app/engines/__init__.py`, and add only the dependencies and model notices that
the new product really needs. The [engine contract](docs/ENGINE-CONTRACT.md)
defines the trust boundary.

Install and start:

```bash
./install.sh
./start.sh
```

On Windows use `.\install.ps1` and `.\start.ps1`. Installation needs internet
access to obtain pinned tools and packages. Application runtime is local-only.

## Verification

After installing development tools:

```bash
python -m unittest discover -s tests -p "test_*.py"
python tests/smoke_local.py
ruff check .
ruff format --check .
bandit -q -c pyproject.toml -r app runtime_guard scripts
```

This starter reduces accidental network and file exposure; it does not prove
that a future engine is correct, anonymous, legally compliant, or safe for every
threat model. Audit each model, binary, license, parser, and output format added
to a derived product.

## Licence

Original code and documentation are licensed under GNU GPL version 3 only.
Dependencies keep their own licences. See `THIRD_PARTY_NOTICES.md`.

---

# Local AI App Starter — Italiano

Una base piccola e orientata alla sicurezza per applicazioni desktop con IA che
funzionano soltanto in locale, anche su normali computer senza GPU. È uno
**starter**, non un prodotto finito e non una copia di AI Privacy Studio.

Il nucleo riutilizzabile offre:

- servizio FastAPI limitato al loopback numerico (`127.0.0.1`);
- token segreto diverso per ogni installazione e controllo dell’origine browser;
- blocco delle connessioni esterne in Python e, su Linux, anche a livello nativo;
- caricamenti con limite, cartelle di lavoro private e cancellazione automatica;
- coda persistente SQLite e contratto ristretto per i motori locali;
- interfaccia senza dipendenze esterne in italiano e inglese;
- installer versionati per Linux x86-64, macOS Apple Silicon e Windows x86-64.

Non contiene volutamente OCR, modelli linguistici, SDK cloud, telemetria,
documenti, marchio di AI Privacy Studio o file binari generati.

## Creare un nuovo prodotto

Copia questa cartella fuori da repository esistenti, poi assegna la nuova
identità:

```bash
python3 scripts/configure.py \
  --name "La mia app locale" \
  --slug "la-mia-app-locale" \
  --description-en "A precise English description." \
  --description-it "Una descrizione precisa in italiano."
```

Sostituisci il motore di esempio in `app/engines/`, registralo in
`app/engines/__init__.py` e aggiungi esclusivamente dipendenze, modelli e
licenze realmente necessari. Il [contratto dei motori](docs/ENGINE-CONTRACT.md)
definisce il confine di fiducia.

Per installare e avviare:

```bash
./install.sh
./start.sh
```

Su Windows usa `.\install.ps1` e `.\start.ps1`. L’installazione richiede
internet per scaricare strumenti e pacchetti versionati. L’esecuzione
dell’applicazione è soltanto locale.

Questa base riduce il rischio di esposizioni accidentali, ma non dimostra che un
nuovo motore sia corretto, anonimo, conforme alla legge o adatto a ogni modello
di minaccia. Ogni modello, binario, licenza, parser e formato aggiunto deve
essere verificato nel prodotto derivato.
