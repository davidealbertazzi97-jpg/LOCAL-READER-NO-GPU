# Disclaimer and limitations

**English** · [Italiano](#italiano)

Local Accessibility Studio is personal, experimental open-source software. It
is not a managed service and does not provide legal, regulatory,
accessibility-conformance, medical, financial, cybersecurity, or professional
advice.

## No warranty

The software is provided **“as is” and “as available”**, without warranties of
any kind, express or implied. To the extent permitted by applicable law, this
includes warranties of accuracy, completeness, reliability, availability,
security, merchantability, fitness for a particular purpose, and
non-infringement.

Use is at the user's own risk. To the maximum extent permitted by law,
copyright holders and contributors are not liable for loss or damage arising
from use of the software, including data loss, confidentiality breaches,
business interruption, accessibility failures, or decisions based on its
output.

Nothing in this notice excludes or limits liability that applicable law does
not permit to be excluded or limited.

## Functional and accessibility limits

- OCR can omit, invent, merge, split, or misread content.
- Reading order, headings, lists, page-number detection, and exclusions are
  heuristic and can be wrong.
- Kokoro speech can mispronounce words, names, abbreviations, numbers, or switch
  language incorrectly when the selected locale does not match the document.
- Semantic HTML and reading text are review candidates. Their generation does
  not prove conformance with WCAG, PDF/UA, EN 301 549, the European
  Accessibility Act, or another standard or law.
- Meaningful images, tables, formulas, multi-column layouts, footnotes, and
  complex forms require qualified human review that this release does not
  automate.
- The software is not intended for safety-critical systems or for unreviewed
  legal, medical, financial, employment, education-assessment, or
  rights-affecting decisions.

Review the result with the intended user and assistive technology before
relying on it.

## Privacy and local files

Local processing reduces external disclosure but does not by itself establish
GDPR or other regulatory compliance. Users remain responsible for having a
lawful basis to process files and for applying appropriate legal,
organizational, backup, endpoint-security, and access-control measures.

Page previews, reviewed text, HTML, reports, and WAV files are durable results
and can contain confidential information. Deleting history removes the
application's result directory, but it does not erase independent copies,
backups, browser downloads, or the original file.

## Distribution

Original project code and documentation are licensed under
[GNU GPL version 3 only](LICENSE). Distributors must comply with that license
and with the terms of every third-party package, model, native library, and
voice asset they include.

The source installer downloads dependencies and model files on the user's
computer. A future preassembled binary distribution would require a separate,
platform-specific license and corresponding-source audit.

This notice supplements, but does not replace, the warranty disclaimer and
limitation of liability in the GNU GPL. It is not legal advice.

---

<a id="italiano"></a>

# Avvertenze e limiti

[English](#disclaimer-and-limitations) · **Italiano**

Local Accessibility Studio è un software open source personale e sperimentale.
Non è un servizio gestito e non fornisce consulenza legale, normativa, di
conformità dell'accessibilità, medica, finanziaria, cybersecurity o
professionale.

## Nessuna garanzia

Il software è fornito **“così com'è” e “come disponibile”**, senza garanzie
espresse o implicite. Nei limiti consentiti dalla legge applicabile, ciò
include accuratezza, completezza, affidabilità, disponibilità, sicurezza,
commerciabilità, idoneità a uno scopo particolare e non violazione.

L'uso avviene a rischio dell'utente. Nei limiti massimi consentiti dalla legge,
i titolari dei diritti e i contributori non rispondono di perdite o danni
derivanti dall'uso del software, inclusi perdita di dati, violazioni della
riservatezza, interruzioni dell'attività, problemi di accessibilità o decisioni
basate sui risultati.

Nulla in queste avvertenze esclude o limita responsabilità che la legge
applicabile non consente di escludere o limitare.

## Limiti funzionali e di accessibilità

- L'OCR può omettere, inventare, unire, separare o leggere male i contenuti.
- Ordine di lettura, titoli, elenchi, numeri di pagina ed esclusioni sono
  euristiche e possono essere errati.
- Kokoro può pronunciare male parole, nomi, abbreviazioni e numeri oppure usare
  una fonetica inadeguata se la lingua scelta non corrisponde al documento.
- HTML semantico e testo sono bozze da revisionare. La loro generazione non
  dimostra conformità a WCAG, PDF/UA, EN 301 549, European Accessibility Act o
  altri standard e leggi.
- Immagini significative, tabelle, formule, impaginazioni a colonne, note e
  moduli complessi richiedono una revisione umana qualificata che questa
  versione non automatizza.
- Il software non è destinato a sistemi critici o a decisioni legali, mediche,
  finanziarie, lavorative, scolastiche o che incidono sui diritti senza
  controllo.

Prova il risultato con l'utente destinatario e la tecnologia assistiva prevista
prima di farvi affidamento.

## Privacy e file locali

L'elaborazione locale riduce la divulgazione esterna, ma non dimostra da sola
la conformità al GDPR o ad altre norme. L'utente resta responsabile del titolo
per trattare i file e delle misure legali, organizzative, di backup, sicurezza
del dispositivo e controllo degli accessi.

Anteprime, testo revisionato, HTML, rapporti e WAV sono risultati persistenti e
possono contenere informazioni riservate. Cancellare la cronologia elimina la
cartella dei risultati dell'applicazione, ma non copie indipendenti, backup,
download del browser o il file originale.

## Distribuzione

Codice e documentazione originali sono distribuiti sotto
[GNU GPL versione 3 soltanto](LICENSE). Chi distribuisce il progetto deve
rispettare tale licenza e i termini di ogni pacchetto, modello, libreria nativa
e voce inclusi.

L'installer sorgente scarica dipendenze e modelli sul computer dell'utente. Una
futura distribuzione binaria preassemblata richiederebbe un audit separato per
piattaforma delle licenze e del sorgente corrispondente.

Queste avvertenze integrano, ma non sostituiscono, l'esclusione di garanzia e la
limitazione di responsabilità della GNU GPL. Non costituiscono parere legale.
