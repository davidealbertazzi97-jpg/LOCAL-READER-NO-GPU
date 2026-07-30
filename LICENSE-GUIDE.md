# License guide

## English

### Project license

The original Local Accessibility Studio code and documentation are distributed
under the **GNU General Public License version 3 only** (`GPL-3.0-only`). The
authoritative terms are in [LICENSE](LICENSE).

GPLv3 is a strong copyleft license compatible with the Apache-2.0, MIT, BSD,
HPND, and other permissive components used by the project. It is also
compatible with selecting version 3 for the `GPL-3.0-or-later` phonemization
components used in the Kokoro speech environment.

### What the project license covers

GPL-3.0-only covers original source code, scripts, interface code, tests,
workflow files, and original documentation in this repository. It does not
replace the licenses of third-party packages, models, runtimes, or voice data.

- RapidOCR remains Apache-2.0; OCR model copyright remains with
  Baidu/PaddleOCR as documented upstream.
- Kokoro ONNX's wrapper remains MIT and the Kokoro model remains under its
  upstream Apache-2.0 terms.
- Kokoro voice data retains the terms supplied by its upstream release.
- PDFium, eSpeak NG, NumPy, ONNX Runtime, Pillow, uv, and all other dependencies
  retain the terms listed in
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

### Main distributor duties

A person distributing the project or a modified version should, at minimum:

1. provide the complete corresponding source required by GPLv3;
2. keep the GPL license and copyright notices;
3. license the covered modified work under GPLv3 only;
4. identify significant modifications;
5. preserve every applicable third-party license and attribution;
6. repeat the dependency and license inventory for each target platform;
7. meet corresponding-source duties for bundled GPL native libraries.

The current source installer downloads Python packages and models on the
user's computer rather than committing them to this repository. In particular,
`espeakng-loader` can install an eSpeak NG shared library and data under
GPL-3.0-or-later. Anyone distributing a preassembled environment or executable
must preserve its notices and provide the corresponding source required by the
selected GPL version.

This guide is a technical licensing analysis, not legal advice. Relicensing is
valid only if the publisher owns or is authorized to license all original
contributions. Obtain qualified legal review before commercial or binary
distribution when ownership or obligations are uncertain.

---

## Italiano

### Licenza del progetto

Il codice e la documentazione originali di Local Accessibility Studio sono
distribuiti sotto **GNU General Public License versione 3 soltanto**
(`GPL-3.0-only`). I termini giuridicamente rilevanti sono in
[LICENSE](LICENSE).

GPLv3 è una licenza copyleft forte compatibile con i componenti Apache-2.0,
MIT, BSD, HPND e permissivi utilizzati dal progetto. È inoltre compatibile con
la scelta della versione 3 per i componenti di fonemizzazione
`GPL-3.0-or-later` usati nell'ambiente Kokoro.

### Ambito della licenza

GPL-3.0-only copre il codice originale, gli script, l'interfaccia, i test, i
workflow e la documentazione originale del repository. Non sostituisce le
licenze di pacchetti, modelli, runtime o voci di terze parti.

- RapidOCR resta Apache-2.0; il copyright dei modelli OCR resta di
  Baidu/PaddleOCR secondo la documentazione upstream.
- Il wrapper Kokoro ONNX resta MIT e il modello Kokoro conserva i termini
  Apache-2.0 upstream.
- I dati delle voci Kokoro conservano i termini della release upstream.
- PDFium, eSpeak NG, NumPy, ONNX Runtime, Pillow, uv e le altre dipendenze
  mantengono i termini elencati in
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

### Principali obblighi del distributore

Chi distribuisce il progetto o una versione modificata dovrebbe almeno:

1. fornire il sorgente corrispondente completo richiesto dalla GPLv3;
2. conservare licenza GPL e avvisi di copyright;
3. applicare GPLv3 soltanto all'opera modificata coperta;
4. indicare le modifiche rilevanti;
5. conservare licenze e attribuzioni di terze parti;
6. ripetere l'inventario di dipendenze e licenze per ogni piattaforma;
7. rispettare gli obblighi sul sorgente delle librerie native GPL incluse.

L'installer sorgente attuale scarica pacchetti Python e modelli sul computer
dell'utente invece di inserirli nel repository. In particolare,
`espeakng-loader` può installare libreria condivisa e dati eSpeak NG sotto
GPL-3.0-or-later. Chi distribuisce un ambiente o eseguibile preassemblato deve
conservarne gli avvisi e fornire il sorgente corrispondente richiesto dalla
versione GPL selezionata.

Questa guida è un'analisi tecnica delle licenze, non un parere legale. Un cambio
di licenza è valido soltanto se chi pubblica possiede o è autorizzato a
licenziare tutti i contributi originali. Prima di una distribuzione commerciale
o binaria, in caso di dubbi, serve una verifica legale qualificata.
