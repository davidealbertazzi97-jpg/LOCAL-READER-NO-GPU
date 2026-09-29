# Sorgenti dei runtime / Runtime source

## Italiano

La release contiene `Local-Reader-No-GPU-source.zip` (sorgente GPLv3
dell'app, test, script e documentazione) e `Third-party-runtime-sources.zip`.
Quest'ultimo conserva senza modifiche gli archivi upstream elencati in
`third_party_sources.json`, verificati con SHA-256.

- CPython 3.12.13: sorgente e licenza PSF, comprese le notice upstream.
- PyInstaller 6.19.0: sorgente del bootloader e licenza GPL con eccezione
  speciale per i programmi distribuiti. I suoi avvisi sono inclusi anche nel
  payload del launcher, sotto `licenses/launcher`.
- AppImage type2-runtime 20251108: sorgente, Makefile, script di build,
  Dockerfile e patch libfuse originali.
- libfuse 3.15.0: sorgente completo LGPL e relativi avvisi. La patch applicata
  dal runtime è in `patches/libfuse/mount.c.diff` nell'archivio del runtime.
- squashfuse 0.5.2: sorgente e licenza.

Per ricostruire il runtime Linux segui `BUILD.md` nell'archivio type2-runtime,
usando gli script sotto `scripts/docker` in un ambiente Docker isolato.
Il Dockerfile descrive gli ulteriori strumenti/dipendenze Alpine. Non eseguire
lo script chroot su un sistema personale. Le versioni e i checksum di libfuse
e squashfuse sono fissati negli script upstream e negli archivi qui inclusi.

È consentito modificare/ricollegare libfuse e sostituire il runtime; non imponiamo
restrizioni al reverse engineering necessario a correggere tali modifiche.
Il contenuto SquashFS dell'app è separato dal runtime. Per mantenerlo usando
un runtime ricostruito:

```bash
offset="$(./original.AppImage --appimage-offset)"
dd if=original.AppImage of=payload.squashfs bs=1 skip="$offset"
cat runtime-x86_64 payload.squashfs > rebuilt.AppImage
chmod +x rebuilt.AppImage
```

Sono comandi per sviluppatori: usa copie in una cartella di lavoro.
In alternativa ricostruisci l'AppImage da sorgente con il builder dell'app e
il tuo runtime. Non viene promessa identità bit-per-bit con i binari upstream.

Le dipendenze Python operative e i modelli non sono incorporati negli eseguibili:
il primo avvio li installa da upstream. I file
`Installed-dependency-notices-*.zip` conservano versioni e licenze effettivamente
installate dai test di release per ogni piattaforma. Il codice dei fornitori,
gli avvisi originali e le loro licenze restano separati dalla licenza dell'app.
Se redistribuisci anche ambienti/modelli già installati, devi verificare anche
i loro obblighi: i soli avvisi di questa release non sono un'offerta completa
dei sorgenti per una distribuzione ampliata.

## English

`Local-Reader-No-GPU-source.zip` contains the app's GPLv3 source,
tests, build scripts and documentation. `Third-party-runtime-sources.zip`
contains unchanged, SHA-256-verified upstream CPython 3.12.13, PyInstaller
6.19.0, type2-runtime 20251108, libfuse 3.15.0 and squashfuse 0.5.2 sources.

The runtime archive includes build scripts, a Dockerfile and the actual
libfuse patch. Follow its `BUILD.md` and `scripts/docker` instructions in an
isolated Docker environment; do not run its chroot builder on a personal host.
You may modify/relink libfuse, reverse engineer for debugging those changes,
and replace the AppImage runtime. The commands above preserve the independent
SquashFS payload and concatenate it with a rebuilt runtime. Use working copies.
Alternatively rebuild the application with its packaging scripts.
Bit-for-bit reproducibility against upstream binaries is not claimed.

Python runtime dependencies and models are downloaded on first launch, not
embedded in these executables. Per-platform
`Installed-dependency-notices-*.zip` files record the packages and license
texts actually installed by release tests. Redistributing preinstalled
environments/models requires a separate check of their source/notice and other
license obligations; this release is not a blanket source offer for them.
