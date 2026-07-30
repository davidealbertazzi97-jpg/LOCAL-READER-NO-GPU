const COPY = {
  it: {
    language: "Lingua",
    privacyTitle: "Solo sul tuo computer",
    privacyBody: "Il servizio Python ascolta soltanto su 127.0.0.1 e rifiuta le proprie connessioni esterne.",
    newJob: "Nuova elaborazione",
    engine: "Motore",
    file: "Documento locale",
    start: "Elabora in locale",
    jobs: "Elaborazioni",
    refresh: "Aggiorna",
    empty: "Nessuna elaborazione.",
    sending: "Copia locale in preparazione…",
    accepted: "Elaborazione accodata.",
    failed: "Operazione non riuscita.",
    download: "Scarica",
  },
  en: {
    language: "Language",
    privacyTitle: "On your computer only",
    privacyBody: "The Python service listens only on 127.0.0.1 and rejects its own external connections.",
    newJob: "New job",
    engine: "Engine",
    file: "Local document",
    start: "Process locally",
    jobs: "Jobs",
    refresh: "Refresh",
    empty: "No jobs yet.",
    sending: "Preparing the local working copy…",
    accepted: "Job queued.",
    failed: "The operation failed.",
    download: "Download",
  },
};

let language = localStorage.getItem("local-ai-language") || document.documentElement.lang || "it";
let engines = [];
let product = null;

function t(key) {
  return COPY[language]?.[key] || COPY.en[key] || key;
}

async function api(path, options = {}) {
  const response = await fetch(path, {credentials: "same-origin", ...options});
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `${response.status}`);
  }
  return response.json();
}

function renderLanguage() {
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelector("#language-select").value = language;
  for (const option of document.querySelector("#engine").options) {
    const engine = engines.find((item) => item.id === option.value);
    option.textContent = engine?.[`label_${language}`] || option.value;
  }
  if (product) {
    document.querySelector("#product-description").textContent = product[`description_${language}`];
  }
  renderEngineDescription();
  void renderJobs();
}

function renderEngineDescription() {
  const id = document.querySelector("#engine").value;
  const engine = engines.find((item) => item.id === id);
  document.querySelector("#engine-description").textContent = engine?.[`description_${language}`] || "";
}

async function renderJobs() {
  const container = document.querySelector("#jobs");
  try {
    const jobs = await api("/api/jobs");
    if (!jobs.length) {
      container.textContent = t("empty");
      return;
    }
    container.replaceChildren(...jobs.map((job) => {
      const item = document.createElement("article");
      item.className = "job";
      const heading = document.createElement("div");
      heading.className = "job-head";
      const title = document.createElement("strong");
      title.textContent = job.input_name;
      const badge = document.createElement("span");
      badge.className = "badge";
      badge.textContent = job.status;
      heading.append(title, badge);
      const message = document.createElement("p");
      message.className = job.status === "failed" ? "error" : "muted";
      message.textContent = job.error || job.message;
      item.append(heading, message);
      for (const artifact of job.artifacts || []) {
        const link = document.createElement("a");
        link.href = `/api/jobs/${encodeURIComponent(job.id)}/files/${artifact.split("/").map(encodeURIComponent).join("/")}`;
        link.textContent = `${t("download")}: ${artifact}`;
        const row = document.createElement("div");
        row.append(link);
        item.append(row);
      }
      return item;
    }));
  } catch (error) {
    container.textContent = `${t("failed")} ${error.message}`;
  }
}

async function initialize() {
  [product, engines] = await Promise.all([api("/api/product"), api("/api/engines")]);
  document.title = product.name;
  document.querySelector("#product-name").textContent = product.name;
  if (!localStorage.getItem("local-ai-language")) language = product.default_language;
  const select = document.querySelector("#engine");
  select.replaceChildren(...engines.map((engine) => {
    const option = document.createElement("option");
    option.value = engine.id;
    option.textContent = engine[`label_${language}`];
    return option;
  }));
  renderLanguage();
}

document.querySelector("#language-select").addEventListener("change", (event) => {
  language = event.target.value;
  localStorage.setItem("local-ai-language", language);
  renderLanguage();
});
document.querySelector("#engine").addEventListener("change", renderEngineDescription);
document.querySelector("#refresh").addEventListener("click", () => void renderJobs());
document.querySelector("#job-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  const status = document.querySelector("#form-status");
  button.disabled = true;
  status.textContent = t("sending");
  try {
    const data = new FormData(event.currentTarget);
    data.set("options", "{}");
    await api("/api/jobs", {method: "POST", body: data});
    status.textContent = t("accepted");
    event.currentTarget.reset();
    renderEngineDescription();
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
