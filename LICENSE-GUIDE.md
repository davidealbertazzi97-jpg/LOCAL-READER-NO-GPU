# License guide

## English

The original Local Reader No GPU code, tests, scripts, interface, and
documentation are distributed under **GNU GPL version 3 only**
(`GPL-3.0-only`). The authoritative terms are in [LICENSE](LICENSE).

The project licence does not replace the terms of third-party packages,
fonts, model files, or services. The current runtime uses PaddlePaddle and
PaddleOCR, Pillow, pypdfium2, Edge-TTS, kokoro-onnx, OpenDyslexic, llama.cpp,
the local LFM2.5 model, and optional remote voice providers. Keep the notices listed in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) when distributing a modified
version or a preassembled environment.

In particular:

- PaddleOCR and PaddlePaddle retain their upstream Apache-2.0 notices;
- OpenDyslexic retains its upstream font licence and attribution;
- llama.cpp retains its upstream MIT notice;
- the LFM2.5 model retains the terms of its model publisher;
- Edge-TTS retains its package and service terms and sends selected text to
  Microsoft’s remote speech endpoint.
- Kokoro-onnx and its model/voice assets retain their upstream terms and are
  used as the offline speech option.

A distributor must also preserve GPLv3 source and attribution obligations for
the covered modified work, and must repeat the dependency inventory for each
platform or bundled binary. This guide is technical information, not legal
advice.

## Italiano

Il codice, i test, gli script, l’interfaccia e la documentazione originali di
Local Reader No GPU sono distribuiti sotto **GNU General Public
License versione 3 soltanto** (`GPL-3.0-only`). I termini autorevoli sono in
[LICENSE](LICENSE).

La licenza del progetto non sostituisce i termini di pacchetti, font, modelli
o servizi di terze parti. Il runtime attuale usa PaddlePaddle e PaddleOCR,
Pillow, pypdfium2, Edge-TTS, kokoro-onnx, OpenDyslexic, llama.cpp, il modello
locale LFM2.5 e provider vocali remoti opzionali. In caso di distribuzione vanno conservati gli avvisi indicati in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

In particolare:

- PaddleOCR e PaddlePaddle mantengono gli avvisi Apache-2.0 upstream;
- OpenDyslexic mantiene la propria licenza e attribuzione;
- llama.cpp mantiene l’avviso MIT upstream;
- il modello LFM2.5 mantiene i termini del suo distributore;
- Edge-TTS mantiene i termini del pacchetto e del servizio e invia il testo
  selezionato all’endpoint vocale remoto Microsoft.
- kokoro-onnx e i suoi modelli/voci mantengono i termini upstream e sono usati
  come opzione vocale offline.

Chi distribuisce una versione modificata deve rispettare gli obblighi GPLv3
sul sorgente e sulle attribuzioni, oltre a ripetere l’inventario per ogni
piattaforma o binario incluso. Questo documento è informazione tecnica, non
un parere legale.
