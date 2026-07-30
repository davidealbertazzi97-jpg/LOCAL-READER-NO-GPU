const COPY = {
  it: {
    skip: "Vai al contenuto",
    language: "Lingua",
    privacyTitle: "Documenti e voce restano locali",
    privacyBody: "OCR e sintesi vocale funzionano sul computer. I risultati vanno comunque controllati prima dell’uso.",
    newJob: "Riconosci un documento",
    newJobHelp: "Carica un PDF o un’immagine. Verranno create copie revisionabili; l’originale non viene modificato.",
    file: "Documento locale",
    autoSpeech: "Crea anche una bozza audio Kokoro dopo l’OCR",
    autoVoice: "Voce della bozza automatica",
    speechLanguage: "Lingua della voce",
    languageItalian: "Italiano",
    languageEnglishUs: "English — Stati Uniti",
    languageEnglishUk: "English — Regno Unito",
    voiceItalianMale: "Maschile — Nicola",
    voiceItalianFemale: "Femminile — Sara",
    voiceAmericanMale: "Maschile — Michael",
    voiceAmericanFemale: "Femminile — Heart",
    voiceBritishMale: "Maschile — George",
    voiceBritishFemale: "Femminile — Emma",
    autoSpeechHelp: "Puoi correggere il testo e rigenerare l’audio con un’altra voce in seguito.",
    start: "Avvia OCR locale",
    jobs: "Lavori locali",
    refresh: "Aggiorna",
    clearHistory: "Cancella cronologia conclusa",
    confirmClearHistory: "Cancellare dalla cronologia tutti i lavori conclusi e i relativi file locali?",
    historyCleared: "Elementi cancellati: {count}.",
    empty: "Nessun lavoro.",
    sending: "Preparazione della copia locale…",
    accepted: "OCR inserito in coda. L’audio Kokoro partirà automaticamente.",
    acceptedOcr: "OCR inserito in coda.",
    failed: "Operazione non riuscita.",
    ready: "Pronto e offline",
    unavailable: "Non installato",
    review: "Rivedi testo e ordine",
    reviewTitle: "Revisione accessibile",
    reviewHelp: "Controlla testo, ordine e ruolo di ogni blocco. La confidenza bassa richiede particolare attenzione.",
    close: "Chiudi",
    documentTitle: "Titolo del documento",
    documentLanguage: "Lingua del documento",
    save: "Salva correzioni",
    saved: "Correzioni salvate.",
    saving: "Salvataggio…",
    downloadHtml: "Scarica HTML accessibile",
    downloadText: "Scarica testo per lettura",
    speechTitle: "Sintesi vocale",
    voice: "Voce",
    speed: "Velocità",
    createSpeech: "Crea audio con Kokoro",
    speechQueued: "Audio Kokoro inserito in coda.",
    page: "Pagina",
    confidence: "Confidenza",
    low: "bassa",
    download: "Scarica",
    delete: "Cancella dalla cronologia",
    confirmDelete: "Cancellare questo lavoro dalla cronologia e rimuovere tutti i relativi file locali?",
    play: "Ascolta l’audio generato",
    roles: {
      heading1: "Titolo principale",
      heading2: "Titolo di sezione",
      heading3: "Sottotitolo",
      paragraph: "Paragrafo",
      list_item: "Elemento elenco",
      page_number: "Numero di pagina (non letto)",
      exclude: "Escludi dalla lettura",
    },
    statuses: {uploading: "caricamento", queued: "in coda", running: "in elaborazione", completed: "completato", failed: "non riuscito"},
  },
  en: {
    skip: "Skip to content",
    language: "Language",
    privacyTitle: "Documents and speech stay local",
    privacyBody: "OCR and speech synthesis run on this computer. Results still require human review before use.",
    newJob: "Recognize a document",
    newJobHelp: "Upload a PDF or image. The app creates reviewable copies and never changes the original.",
    file: "Local document",
    autoSpeech: "Also create a Kokoro audio draft after OCR",
    autoVoice: "Automatic draft voice",
    speechLanguage: "Speech language",
    languageItalian: "Italian",
    languageEnglishUs: "English — United States",
    languageEnglishUk: "English — United Kingdom",
    voiceItalianMale: "Male — Nicola",
    voiceItalianFemale: "Female — Sara",
    voiceAmericanMale: "Male — Michael",
    voiceAmericanFemale: "Female — Heart",
    voiceBritishMale: "Male — George",
    voiceBritishFemale: "Female — Emma",
    autoSpeechHelp: "You can correct the text and regenerate audio with another voice later.",
    start: "Start local OCR",
    jobs: "Local jobs",
    refresh: "Refresh",
    clearHistory: "Clear finished history",
    confirmClearHistory: "Clear every finished job from history and remove its local files?",
    historyCleared: "Items cleared: {count}.",
    empty: "No jobs yet.",
    sending: "Preparing the local working copy…",
    accepted: "OCR queued. Kokoro audio will start automatically.",
    acceptedOcr: "OCR job queued.",
    failed: "The operation failed.",
    ready: "Ready and offline",
    unavailable: "Not installed",
    review: "Review text and order",
    reviewTitle: "Accessibility review",
    reviewHelp: "Check every block’s text, order, and role. Low confidence needs particular attention.",
    close: "Close",
    documentTitle: "Document title",
    documentLanguage: "Document language",
    save: "Save corrections",
    saved: "Corrections saved.",
    saving: "Saving…",
    downloadHtml: "Download accessible HTML",
    downloadText: "Download reading text",
    speechTitle: "Speech synthesis",
    voice: "Voice",
    speed: "Speed",
    createSpeech: "Create audio with Kokoro",
    speechQueued: "Kokoro audio job queued.",
    page: "Page",
    confidence: "Confidence",
    low: "low",
    download: "Download",
    delete: "Remove from history",
    confirmDelete: "Remove this job from history and delete all its local files?",
    play: "Play generated audio",
    roles: {
      heading1: "Main heading",
      heading2: "Section heading",
      heading3: "Subheading",
      paragraph: "Paragraph",
      list_item: "List item",
      page_number: "Page number (not read)",
      exclude: "Exclude from reading",
    },
    statuses: {uploading: "uploading", queued: "queued", running: "processing", completed: "completed", failed: "failed"},
  },
};

const VOICE_PROFILES = {
  it: [
    ["im_nicola", "voiceItalianMale"],
    ["if_sara", "voiceItalianFemale"],
  ],
  "en-us": [
    ["am_michael", "voiceAmericanMale"],
    ["af_heart", "voiceAmericanFemale"],
  ],
  "en-gb": [
    ["bm_george", "voiceBritishMale"],
    ["bf_emma", "voiceBritishFemale"],
  ],
};

let language = localStorage.getItem("accessibility-language") || "it";
let product = null;
let engines = [];
let editingJob = null;
let documentValue = null;
let pollTimer = null;
let speechReady = false;

function t(key) {
  return COPY[language]?.[key] ?? COPY.en[key] ?? key;
}

async function api(path, options = {}) {
  const response = await fetch(path, {credentials: "same-origin", ...options});
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `${response.status}`);
  }
  return response.json();
}

function artifactUrl(jobId, artifact) {
  const encoded = artifact.split("/").map(encodeURIComponent).join("/");
  return `/api/jobs/${encodeURIComponent(jobId)}/files/${encoded}`;
}

function fillVoiceSelect(select, speechLanguage, preferred = select.value) {
  const profile = VOICE_PROFILES[speechLanguage] || VOICE_PROFILES.it;
  select.replaceChildren(...profile.map(([value, label]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = t(label);
    return option;
  }));
  if (profile.some(([value]) => value === preferred)) select.value = preferred;
}

function syncAutomaticSpeechControls() {
  const enabled =
    speechReady && document.querySelector("#auto-speech").checked;
  document.querySelector("#auto-speech-language").disabled = false;
  document.querySelector("#auto-voice").disabled = !enabled;
}

function renderLanguage() {
  document.documentElement.lang = language;
  document.querySelector("#language-select").value = language;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  if (product) {
    document.querySelector("#product-description").textContent = product[`description_${language}`];
  }
  fillVoiceSelect(
    document.querySelector("#auto-voice"),
    document.querySelector("#auto-speech-language").value,
  );
  fillVoiceSelect(
    document.querySelector("#voice"),
    document.querySelector("#speech-language").value,
  );
  if (documentValue) renderDocument();
  void renderJobs();
}

async function renderStatus() {
  const status = await api("/api/status");
  speechReady = status.speech.ready;
  for (const name of ["ocr", "speech"]) {
    const ready = status[name].ready;
    document.querySelector(`#${name}-dot`).classList.toggle("ready", ready);
    document.querySelector(`#${name}-status`).textContent = t(ready ? "ready" : "unavailable");
  }
  document.querySelector("#job-form button[type=submit]").disabled = !status.ocr.ready;
  const automaticSpeech = document.querySelector("#auto-speech");
  automaticSpeech.disabled = !status.speech.ready;
  if (!status.speech.ready) automaticSpeech.checked = false;
  syncAutomaticSpeechControls();
  document.querySelector("#create-speech").disabled = !status.speech.ready;
}

function addArtifactLinks(container, job) {
  const visible = (job.artifacts || []).filter((name) =>
    !name.startsWith("pages/") && name !== "document.json" && name !== "speech.wav"
  );
  for (const artifact of visible) {
    const link = document.createElement("a");
    link.href = artifactUrl(job.id, artifact);
    link.textContent = `${t("download")}: ${artifact}`;
    container.append(link);
  }
}

function jobCard(job) {
  const card = document.createElement("article");
  card.className = "job";
  const head = document.createElement("div");
  head.className = "job-head";
  const title = document.createElement("strong");
  title.textContent = job.input_name;
  const badge = document.createElement("span");
  badge.className = "badge";
  badge.textContent = COPY[language].statuses[job.status] || job.status;
  head.append(title, badge);
  card.append(head);

  const message = document.createElement("p");
  message.className = job.status === "failed" ? "error" : "muted";
  message.textContent = job.error || job.message;
  card.append(message);
  if (job.summary && Object.keys(job.summary).length) {
    const summary = document.createElement("div");
    summary.className = "summary";
    for (const [key, value] of Object.entries(job.summary)) {
      const item = document.createElement("span");
      item.textContent = `${key}: ${value}`;
      summary.append(item);
    }
    card.append(summary);
  }
  const actions = document.createElement("div");
  actions.className = "job-actions";
  if (job.status === "completed" && job.engine === "accessible-document") {
    const review = document.createElement("button");
    review.type = "button";
    review.textContent = t("review");
    review.addEventListener("click", () => void openDocument(job));
    actions.append(review);
  }
  if (job.status === "completed" && job.engine === "kokoro-italian") {
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.preload = "metadata";
    audio.src = artifactUrl(job.id, "speech.wav");
    audio.setAttribute("aria-label", t("play"));
    card.append(audio);
    const download = document.createElement("a");
    download.href = artifactUrl(job.id, "speech.wav");
    download.download = "speech.wav";
    download.className = "button-link secondary";
    download.textContent = `${t("download")}: speech.wav`;
    actions.append(download);
  }
  addArtifactLinks(actions, job);
  if (["completed", "failed"].includes(job.status)) {
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "secondary";
    remove.textContent = t("delete");
    remove.addEventListener("click", async () => {
      if (!window.confirm(t("confirmDelete"))) return;
      try {
        await api(`/api/jobs/${encodeURIComponent(job.id)}`, {method: "DELETE"});
        if (editingJob?.id === job.id) {
          document.querySelector("#editor").hidden = true;
          editingJob = null;
          documentValue = null;
        }
        await renderJobs();
      } catch (error) {
        window.alert(`${t("failed")} ${error.message}`);
      }
    });
    actions.append(remove);
  }
  if (actions.childNodes.length) card.append(actions);
  return card;
}

async function renderJobs() {
  const container = document.querySelector("#jobs");
  try {
    const jobs = await api("/api/jobs");
    container.replaceChildren(...(jobs.length ? jobs.map(jobCard) : [document.createTextNode(t("empty"))]));
    const active = jobs.some((job) => ["uploading", "queued", "running"].includes(job.status));
    document.querySelector("#clear-history").disabled =
      !jobs.some((job) => ["completed", "failed"].includes(job.status));
    clearTimeout(pollTimer);
    if (active) pollTimer = setTimeout(() => void renderJobs(), 1500);
  } catch (error) {
    container.textContent = `${t("failed")} ${error.message}`;
  }
}

function roleOptions(selected) {
  return Object.keys(COPY[language].roles).map((role) => {
    const option = document.createElement("option");
    option.value = role;
    option.textContent = COPY[language].roles[role];
    option.selected = role === selected;
    return option;
  });
}

function blockEditor(block) {
  const item = document.createElement("div");
  item.className = "block-editor";
  const meta = document.createElement("div");
  meta.className = "block-meta";
  const select = document.createElement("select");
  select.setAttribute("aria-label", t("reviewTitle"));
  select.replaceChildren(...roleOptions(block.role));
  select.addEventListener("change", () => { block.role = select.value; });
  const confidence = document.createElement("span");
  confidence.className = `confidence ${block.confidence < 0.82 ? "low-confidence" : ""}`;
  confidence.textContent = `${t("confidence")}: ${Math.round(block.confidence * 100)}%${block.confidence < 0.82 ? ` (${t("low")})` : ""}`;
  meta.append(select, confidence);
  const textarea = document.createElement("textarea");
  textarea.value = block.text;
  textarea.setAttribute("aria-label", `${t("page")} ${block.id}`);
  textarea.addEventListener("input", () => { block.text = textarea.value; });
  item.append(meta, textarea);
  return item;
}

function renderDocument() {
  if (!documentValue || !editingJob) return;
  document.querySelector("#document-title").value = documentValue.title;
  document.querySelector("#document-language").value = documentValue.language;
  const speechLanguage = document.querySelector("#speech-language");
  speechLanguage.value =
    documentValue.speech_language || (documentValue.language === "en" ? "en-us" : "it");
  fillVoiceSelect(document.querySelector("#voice"), speechLanguage.value);
  document.querySelector("#download-html").href = artifactUrl(editingJob.id, "accessible.html");
  document.querySelector("#download-text").href = artifactUrl(editingJob.id, "reading.txt");
  const pages = document.querySelector("#pages");
  pages.replaceChildren(...documentValue.pages.map((page) => {
    const section = document.createElement("article");
    section.className = "page-editor";
    const heading = document.createElement("h3");
    heading.textContent = `${t("page")} ${page.number}`;
    const layout = document.createElement("div");
    layout.className = "page-layout";
    const image = document.createElement("img");
    image.className = "page-preview";
    image.loading = "lazy";
    image.src = artifactUrl(editingJob.id, page.preview);
    image.alt = `${t("page")} ${page.number}`;
    const blocks = document.createElement("div");
    blocks.className = "blocks";
    blocks.replaceChildren(...page.blocks.map(blockEditor));
    layout.append(image, blocks);
    section.append(heading, layout);
    return section;
  }));
}

async function openDocument(job) {
  editingJob = job;
  documentValue = await api(`/api/jobs/${encodeURIComponent(job.id)}/document`);
  renderDocument();
  const editor = document.querySelector("#editor");
  editor.hidden = false;
  editor.scrollIntoView({behavior: "smooth", block: "start"});
  document.querySelector("#document-title").focus();
}

async function saveDocument() {
  if (!editingJob || !documentValue) throw new Error("No document");
  documentValue.title = document.querySelector("#document-title").value;
  documentValue.language = document.querySelector("#document-language").value;
  documentValue.speech_language =
    document.querySelector("#speech-language").value;
  const status = document.querySelector("#save-status");
  status.textContent = t("saving");
  documentValue = await api(`/api/jobs/${encodeURIComponent(editingJob.id)}/document`, {
    method: "PUT",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(documentValue),
  });
  status.textContent = t("saved");
  return documentValue;
}

async function initialize() {
  [product, engines] = await Promise.all([api("/api/product"), api("/api/engines")]);
  document.title = product.name;
  document.querySelector("#product-name").textContent = product.name;
  if (!localStorage.getItem("accessibility-language")) language = product.default_language;
  document.querySelector("#auto-speech-language").value =
    language === "en" ? "en-us" : "it";
  renderLanguage();
  await Promise.all([renderStatus(), renderJobs()]);
}

document.querySelector("#language-select").addEventListener("change", (event) => {
  language = event.target.value;
  localStorage.setItem("accessibility-language", language);
  document.querySelector("#auto-speech-language").value =
    language === "en" ? "en-us" : "it";
  renderLanguage();
});
document.querySelector("#refresh").addEventListener("click", () => void renderJobs());
document.querySelector("#auto-speech").addEventListener("change", (event) => {
  syncAutomaticSpeechControls();
});
document.querySelector("#auto-speech-language").addEventListener("change", (event) => {
  fillVoiceSelect(document.querySelector("#auto-voice"), event.currentTarget.value);
});
document.querySelector("#clear-history").addEventListener("click", async (event) => {
  if (!window.confirm(t("confirmClearHistory"))) return;
  const button = event.currentTarget;
  const status = document.querySelector("#history-status");
  button.disabled = true;
  try {
    const result = await api("/api/jobs", {method: "DELETE"});
    if (editingJob) {
      document.querySelector("#editor").hidden = true;
      editingJob = null;
      documentValue = null;
    }
    status.textContent = t("historyCleared").replace("{count}", result.deleted);
    await renderJobs();
  } catch (error) {
    status.textContent = `${t("failed")} ${error.message}`;
    button.disabled = false;
  }
});
document.querySelector("#job-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type=submit]");
  const status = document.querySelector("#form-status");
  const engine = engines.find((item) => item.user_upload);
  button.disabled = true;
  status.textContent = t("sending");
  try {
    const automaticSpeech = document.querySelector("#auto-speech");
    const createAutomaticSpeech = automaticSpeech.checked;
    const speechLanguage = document.querySelector("#auto-speech-language").value;
    const automaticVoice = document.querySelector("#auto-voice").value;
    const data = new FormData(form);
    data.set("engine", engine.id);
    data.set("options", JSON.stringify({
      auto_speech: createAutomaticSpeech,
      document_language: speechLanguage === "it" ? "it" : "en",
      speech_language: speechLanguage,
      voice: automaticVoice,
      speed: 1.0,
    }));
    await api("/api/jobs", {method: "POST", body: data});
    status.textContent = t(createAutomaticSpeech ? "accepted" : "acceptedOcr");
    form.reset();
    document.querySelector("#auto-speech-language").value = speechLanguage;
    fillVoiceSelect(
      document.querySelector("#auto-voice"),
      speechLanguage,
      automaticVoice,
    );
    if (automaticSpeech.disabled) automaticSpeech.checked = false;
    syncAutomaticSpeechControls();
    await renderJobs();
  } catch (error) {
    status.textContent = `${t("failed")} ${error.message}`;
  } finally {
    button.disabled = false;
  }
});
document.querySelector("#close-editor").addEventListener("click", () => {
  document.querySelector("#editor").hidden = true;
  editingJob = null;
  documentValue = null;
});
document.querySelector("#save-document").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    await saveDocument();
  } catch (error) {
    document.querySelector("#save-status").textContent = `${t("failed")} ${error.message}`;
  } finally {
    button.disabled = false;
  }
});
document.querySelector("#speed").addEventListener("input", (event) => {
  document.querySelector("#speed-value").textContent = `${Number(event.target.value).toFixed(2)}×`;
});
document.querySelector("#document-language").addEventListener("change", (event) => {
  const speechLanguage = document.querySelector("#speech-language");
  speechLanguage.value = event.currentTarget.value === "en" ? "en-us" : "it";
  fillVoiceSelect(document.querySelector("#voice"), speechLanguage.value);
});
document.querySelector("#speech-language").addEventListener("change", (event) => {
  document.querySelector("#document-language").value =
    event.currentTarget.value === "it" ? "it" : "en";
  fillVoiceSelect(document.querySelector("#voice"), event.currentTarget.value);
});
document.querySelector("#create-speech").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  const status = document.querySelector("#save-status");
  try {
    await saveDocument();
    await api(`/api/jobs/${encodeURIComponent(editingJob.id)}/speech`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        voice: document.querySelector("#voice").value,
        speed: Number(document.querySelector("#speed").value),
        language: document.querySelector("#speech-language").value,
      }),
    });
    status.textContent = t("speechQueued");
    await renderJobs();
  } catch (error) {
    status.textContent = `${t("failed")} ${error.message}`;
  } finally {
    button.disabled = false;
  }
});

void initialize().catch((error) => {
  document.querySelector("#form-status").textContent = `${t("failed")} ${error.message}`;
});
