/* Speech events are the clock: never estimate word positions with a timer. */
(function (root) {
  "use strict";
  const MAX_TEXT = 512 * 1024;
  function paragraphs(text) {
    return text.replace(/\r\n?/g, "\n").split(/\n\s*\n/u).map(p => p.trim()).filter(Boolean);
  }
  function words(text) {
    return Array.from(text.matchAll(/\S+/gu), match => ({text: match[0], start: match.index, end: match.index + match[0].length}));
  }
  function chunks(text, start = 0, locale = "it") {
    const tail = text.slice(start);
    const sentences = typeof Intl.Segmenter === "function"
      ? Array.from(new Intl.Segmenter(locale, {granularity: "sentence"}).segment(tail), s => ({text: s.segment, start: start + s.index}))
      : [{text: tail, start}];
    const result = [];
    for (const sentence of sentences) {
      // Short utterances also work around browser limits on long synthesis.
      let offset = 0;
      while (offset < sentence.text.length) {
        let end = Math.min(offset + 240, sentence.text.length);
        if (end < sentence.text.length) {
          const space = sentence.text.lastIndexOf(" ", end);
          if (space > offset) end = space + 1;
          // Do not cut a UTF-16 surrogate pair in two.
          if (/[\uD800-\uDBFF]/u.test(sentence.text[end - 1])) end--;
        }
        const raw = sentence.text.slice(offset, end);
        const leading = raw.length - raw.trimStart().length;
        if (raw.trim()) result.push({text: raw.trim(), start: sentence.start + offset + leading});
        offset = end;
      }
    }
    return result;
  }
  class Reader {
    constructor(synth, Utterance, update = () => {}) {
      this.synth = synth;
      this.Utterance = Utterance;
      this.update = update;
      this.texts = [];
      this.paragraph = 0;
      this.offset = 0;
      this.state = "idle";
      this.generation = 0;
      this.continuous = true;
      this.rate = 1;
      this.voice = null;
      this.restartOnResume = false;
    }
    emit(extra = {}) { this.update({state: this.state, paragraph: this.paragraph, offset: this.offset, ...extra}); }
    stop() {
      this.generation++;
      this.synth?.cancel();
      this.state = "idle";
      this.restartOnResume = false;
      this.emit();
    }
    load(text) {
      this.stop();
      this.texts = paragraphs(text);
      this.paragraph = 0;
      this.offset = 0;
      this.emit();
    }
    play(paragraph = this.paragraph, offset = this.offset) {
      if (!this.texts.length || !this.voice || !this.synth || !this.Utterance) return false;
      this.stop();
      this.paragraph = Math.max(0, Math.min(paragraph, this.texts.length - 1));
      this.offset = Math.max(0, Math.min(offset, this.texts[this.paragraph].length));
      this.synth.resume();
      const generation = this.generation;
      this.state = "loading";
      this.emit();
      this.speakParagraph(generation);
      return true;
    }
    speakParagraph(generation) {
      const queue = chunks(this.texts[this.paragraph], this.offset, this.voice.lang);
      const next = () => {
        if (generation !== this.generation) return;
        const chunk = queue.shift();
        if (!chunk) {
          if (this.continuous && this.paragraph + 1 < this.texts.length) {
            this.paragraph++;
            this.offset = 0;
            this.speakParagraph(generation);
          } else {
            this.state = "finished";
            this.offset = 0;
            this.emit();
          }
          return;
        }
        const utterance = new this.Utterance(chunk.text);
        // Hold a reference until completion (some browsers otherwise lose events).
        this.utterance = utterance;
        utterance.voice = this.voice;
        utterance.lang = this.voice.lang;
        utterance.rate = this.rate;
        utterance.onstart = () => {
          if (generation !== this.generation) return;
          if (this.state !== "paused") this.state = "speaking";
          this.offset = chunk.start;
          this.emit({chunk, word: null});
        };
        utterance.onboundary = event => {
          if (generation !== this.generation || event.name !== "word") return;
          const index = Math.max(0, Math.min(event.charIndex, chunk.text.length));
          this.offset = chunk.start + index;
          this.emit({chunk, word: this.offset});
        };
        utterance.onend = next;
        utterance.onerror = event => {
          if (generation !== this.generation) return;
          this.state = "error";
          this.emit({error: event.error});
        };
        try { this.synth.speak(utterance); }
        catch { this.state = "error"; this.emit({error: "synthesis-failed"}); }
      };
      next();
    }
    toggle() {
      if (this.state === "speaking" || this.state === "loading") {
        // Firefox's Speech Dispatcher backend does not implement native pause.
        // Cancel its utterance, then resume from the last real text position.
        if (this.voice?.voiceURI?.startsWith("urn:moz-tts:speechd:")) {
          this.generation++;
          this.synth.cancel();
          this.restartOnResume = true;
        } else this.synth.pause();
        this.state = "paused";
        this.emit({keepHighlight: true});
      } else if (this.state === "paused") {
        if (this.restartOnResume) this.play();
        else {
          this.synth.resume();
          this.state = "speaking";
          this.emit({keepHighlight: true});
        }
      } else this.play(this.state === "finished" && this.continuous ? 0 : this.paragraph, this.state === "finished" ? 0 : this.offset);
    }
  }
  const exports = {Reader, paragraphs, words, chunks, MAX_TEXT};
  if (typeof module !== "undefined" && module.exports) module.exports = exports;
  else { root.LiveReader = exports; mount(); }

  function mount() {
    const $ = id => document.getElementById(id);
    const view = $("view-live");
    if (!view) return;
    const copy = {
      it: {
        liveTitle: "Lettura live", liveHelp: "Ascolta e segui il testo. Fai clic su un paragrafo per leggerlo subito, oppure raggiungilo con Tab e premi Invio. Le frecce spostano il fuoco tra i paragrafi.",
        liveInput: "Incolla il testo da leggere", liveFile: "Oppure apri un file di testo (.txt, .md)", liveLoad: "Apri il testo", liveEdit: "Modifica testo", liveVoice: "Voce del dispositivo", liveRate: "Velocità", liveSize: "Dimensione testo", liveFollow: "Segui la lettura", liveContinue: "Continua nei paragrafi successivi",
        livePlay: "Leggi", livePause: "Pausa", liveResume: "Riprendi", liveResumeSentence: "Riprendi la frase", liveStop: "Interrompi", livePrevious: "Paragrafo precedente", liveNext: "Paragrafo successivo", liveEmpty: "Apri un testo per iniziare. Puoi anche aprire i risultati OCR e i testi dalla Cronologia.",
        livePrivacy: "Questa pagina usa le voci del dispositivo. Le voci non confermate come locali possono inviare il testo al servizio vocale; in Modalità offline sono escluse. Per creare un MP3 con Kokoro o altre voci usa Solo voce.",
        liveSync: "La sottolineatura segue le parole quando la voce le segnala; altrimenti segue la frase in lettura.",
        liveNoVoices: "Nessuna voce disponibile. Su Windows aggiungi una voce in Impostazioni → Data/ora e lingua → Funzionalità vocali, quindi riapri il browser. Su Linux usa Firefox con Speech Dispatcher e una voce installata. Puoi creare un audio anche dalla pagina Solo voce.",
        liveReady: "Pronto. Scegli un paragrafo oppure premi Leggi.", liveLoading: "Avvio della voce…", liveSpeaking: "Lettura in corso", livePaused: "In pausa", liveFinished: "Lettura completata", liveError: "La voce non è partita. Seleziona un’altra voce e premi Leggi.", liveTooLong: "Usa un testo o un file fino a 512 KB.", liveMissing: "Incolla o apri un testo prima di continuare.", liveStorage: "Il browser non consente di salvare il punto di lettura. Il testo rimane disponibile in questa pagina.", liveParagraph: "Paragrafo", liveLocal: "locale", liveOnline: "locale non confermato", liveFileError: "Non riesco ad aprire questo file di testo."
      },
      en: {
        liveTitle: "Live reading", liveHelp: "Listen and follow the text. Click a paragraph to read it immediately, or reach it with Tab and press Enter. Arrow keys move focus between paragraphs.",
        liveInput: "Paste the text to read", liveFile: "Or open a text file (.txt, .md)", liveLoad: "Open text", liveEdit: "Edit text", liveVoice: "Device voice", liveRate: "Speed", liveSize: "Text size", liveFollow: "Follow reading", liveContinue: "Continue through the next paragraphs",
        livePlay: "Read", livePause: "Pause", liveResume: "Resume", liveResumeSentence: "Resume sentence", liveStop: "Stop", livePrevious: "Previous paragraph", liveNext: "Next paragraph", liveEmpty: "Open text to begin. You can also open OCR results and texts from History.",
        livePrivacy: "This page uses device voices. Voices not confirmed as local may send text to the speech service; Offline mode excludes them. To create an MP3 with Kokoro or other voices, use Voice only.",
        liveSync: "Underlining follows words when reported by the voice; otherwise it follows the sentence being read.",
        liveNoVoices: "No voices available. On Windows add a voice in Settings → Time & language → Speech, then reopen the browser. On Linux use Firefox with Speech Dispatcher and an installed voice. You can also create audio from Voice only.",
        liveReady: "Ready. Choose a paragraph or press Read.", liveLoading: "Starting voice…", liveSpeaking: "Reading", livePaused: "Paused", liveFinished: "Reading completed", liveError: "The voice could not start. Choose another voice and press Read.", liveTooLong: "Use text or a file up to 512 KB.", liveMissing: "Paste or open some text first.", liveStorage: "The browser cannot save your reading position. Your text remains available on this page.", liveParagraph: "Paragraph", liveLocal: "local", liveOnline: "locality unconfirmed", liveFileError: "I could not open this text file."
      }
    };
    const tr = key => (copy[document.documentElement.lang] || copy.it)[key] || key;
    const storageKey = "local-accessibility-studio-live-v1";
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(storageKey)) || {}; } catch { /* A damaged checkpoint must not block reading. */ }
    const reader = new Reader(root.speechSynthesis, root.SpeechSynthesisUtterance, update);
    let nodes = [];
    let highlighted = [];
    let activeNode = null;
    let lastSave = 0;
    let storageFailed = false;
    let statusKey = "liveReady";
    let availableVoices = [];
    $("live-rate").value = String(Math.max(.5, Math.min(2, Number(saved.rate) || 1)));
    $("live-size").value = String(Math.max(18, Math.min(36, Number(saved.size) || 24)));
    $("live-follow").checked = saved.follow !== false;
    $("live-continue").checked = saved.continuous !== false;
    function persist(force = false) {
      if (!force && Date.now() - lastSave < 600) return;
      lastSave = Date.now();
      saved = {text: $("live-input").value.slice(0, MAX_TEXT), paragraph: reader.paragraph, offset: reader.offset, rate: Number($("live-rate").value), size: Number($("live-size").value), voice: $("live-voice").value, follow: $("live-follow").checked, continuous: $("live-continue").checked};
      try { localStorage.setItem(storageKey, JSON.stringify(saved)); storageFailed = false; }
      catch { storageFailed = true; }
      $("live-storage-status").textContent = storageFailed ? tr("liveStorage") : "";
    }
    function clearHighlight() {
      highlighted.forEach(node => node.classList.remove("live-current"));
      highlighted = [];
    }
    function update(event) {
      if (!nodes) return;
      const current = nodes[event.paragraph];
      if (activeNode !== current?.node) {
        activeNode?.classList.remove("live-active");
        activeNode?.removeAttribute("aria-current");
        activeNode = current?.node;
        activeNode?.classList.add("live-active");
        activeNode?.setAttribute("aria-current", "true");
      }
      if (!event.keepHighlight) {
        clearHighlight();
        if (current && event.chunk) {
          const hit = event.word == null
            ? current.words.filter(word => word.start >= event.chunk.start && word.start < event.chunk.start + event.chunk.text.length)
            : current.words.filter(word => event.word >= word.start && event.word < word.end);
          highlighted = hit.map(word => word.node);
          highlighted.forEach(node => node.classList.add("live-current"));
          if ($("live-follow").checked && !view.hidden) {
            const target = highlighted[0] || current.node;
            const rect = target.getBoundingClientRect();
            const toolbarBottom = $("live-toolbar").getBoundingClientRect().bottom;
            if (rect.top < toolbarBottom + 16 || rect.bottom > innerHeight - 40) target.scrollIntoView({block: "center", behavior: "instant"});
          }
        }
      }
      statusKey = ({idle: "liveReady", loading: "liveLoading", speaking: "liveSpeaking", paused: "livePaused", finished: "liveFinished", error: "liveError"})[event.state];
      renderControls();
      persist();
    }
    function renderControls() {
      const ready = !!reader.voice && reader.texts.length > 0;
      $("live-play").disabled = !ready;
      $("live-stop").disabled = !["speaking", "loading", "paused"].includes(reader.state);
      $("live-previous").disabled = !ready || reader.paragraph <= 0;
      $("live-next").disabled = !ready || reader.paragraph >= reader.texts.length - 1;
      $("live-play").textContent = tr(reader.state === "paused" ? (reader.restartOnResume ? "liveResumeSentence" : "liveResume") : ["speaking", "loading"].includes(reader.state) ? "livePause" : "livePlay");
      $("live-play").setAttribute("aria-pressed", String(["speaking", "loading"].includes(reader.state)));
      const message = tr(!reader.voice ? "liveNoVoices" : statusKey);
      if ($("live-status").textContent !== message) $("live-status").textContent = message;
      $("live-status").classList.toggle("error", reader.state === "error");
      $("live-position").textContent = reader.texts.length ? `${tr("liveParagraph")} ${reader.paragraph + 1} / ${reader.texts.length}` : "";
      $("live-progress").max = Math.max(1, reader.texts.length);
      $("live-progress").value = reader.state === "finished" ? reader.paragraph + 1 : reader.paragraph;
      $("live-progress").setAttribute("aria-label", tr("liveParagraph"));
    }
    function voices() {
      const preferred = $("live-voice").value || saved.voice;
      const offline = document.querySelector("#offline-mode-toggle")?.getAttribute("aria-pressed") === "true";
      availableVoices = (root.speechSynthesis?.getVoices() || []).filter(v => !offline || v.localService).sort((a, b) => Number(b.localService) - Number(a.localService) || a.name.localeCompare(b.name));
      $("live-voice").replaceChildren(...availableVoices.map(v => {
        const option = document.createElement("option");
        option.value = v.voiceURI;
        option.textContent = `${v.name} · ${v.lang} · ${tr(v.localService ? "liveLocal" : "liveOnline")}`;
        return option;
      }));
      const selected = availableVoices.find(v => v.voiceURI === preferred) || availableVoices.find(v => v.lang.toLowerCase().startsWith(document.documentElement.lang)) || availableVoices[0];
      $("live-voice").value = selected?.voiceURI || "";
      if (reader.voice && reader.voice.voiceURI !== selected?.voiceURI) reader.stop();
      reader.voice = selected || null;
      renderControls();
    }
    function renderText() {
      nodes = reader.texts.map((text, index) => {
        const node = document.createElement("p");
        node.className = "live-paragraph";
        node.tabIndex = 0;
        node.setAttribute("role", "button");
        node.setAttribute("aria-label", `${tr("liveParagraph")} ${index + 1}. ${text}`);
        const tokens = words(text);
        let offset = 0;
        tokens.forEach(word => {
          node.append(document.createTextNode(text.slice(offset, word.start)));
          word.node = document.createElement("span");
          word.node.textContent = word.text;
          node.append(word.node);
          offset = word.end;
        });
        node.append(document.createTextNode(text.slice(offset)));
        node.addEventListener("click", () => {
          if (!root.getSelection()?.isCollapsed) return;
          reader.play(index, 0);
        });
        node.addEventListener("keydown", event => {
          if (["Enter", " "].includes(event.key)) { event.preventDefault(); reader.play(index, 0); }
          if (["ArrowDown", "ArrowUp"].includes(event.key)) {
            event.preventDefault();
            nodes[Math.max(0, Math.min(nodes.length - 1, index + (event.key === "ArrowDown" ? 1 : -1)))].node.focus();
          }
        });
        return {node, words: tokens};
      });
      $("live-paper").replaceChildren(...nodes.map(item => item.node));
      $("live-empty").hidden = nodes.length > 0;
      $("live-edit").hidden = nodes.length === 0;
      update({state: reader.state, paragraph: reader.paragraph, offset: reader.offset});
    }
    function load(text, restore = false) {
      if (!text.trim()) { $("live-input-status").textContent = tr("liveMissing"); return false; }
      if (text.length > MAX_TEXT) { $("live-input-status").textContent = tr("liveTooLong"); return false; }
      const checkpoint = {...saved};
      $("live-input").value = text;
      reader.load(text);
      if (restore) {
        reader.paragraph = Math.max(0, Math.min(reader.texts.length - 1, Number(checkpoint.paragraph) || 0));
        reader.offset = Math.max(0, Math.min(reader.texts[reader.paragraph].length, Number(checkpoint.offset) || 0));
      }
      renderText();
      $("live-source").open = false;
      $("live-input-status").textContent = "";
      persist(true);
      return true;
    }
    function preferences() {
      reader.rate = Number($("live-rate").value);
      reader.continuous = $("live-continue").checked;
      $("live-rate-value").textContent = `${reader.rate.toFixed(2)}×`;
      $("live-paper").style.fontSize = `${$("live-size").value}px`;
      $("live-size-value").textContent = `${$("live-size").value} px`;
    }
    function translate() {
      document.querySelectorAll("[data-live-i18n]").forEach(node => { node.textContent = tr(node.dataset.liveI18n); });
      nodes.forEach((item, index) => item.node.setAttribute("aria-label", `${tr("liveParagraph")} ${index + 1}. ${reader.texts[index]}`));
      voices();
      renderControls();
    }
    $("live-form").addEventListener("submit", event => { event.preventDefault(); if (load($("live-input").value)) nodes[0]?.node.focus(); });
    $("live-edit").addEventListener("click", () => { reader.stop(); $("live-source").open = true; $("live-input").focus(); });
    $("live-file").addEventListener("change", async event => {
      const file = event.target.files[0];
      if (!file) return;
      if (file.size > MAX_TEXT) { $("live-input-status").textContent = tr("liveTooLong"); return; }
      try { load(await file.text()); } catch { $("live-input-status").textContent = tr("liveFileError"); }
      event.target.value = "";
    });
    $("live-play").addEventListener("click", () => reader.toggle());
    $("live-stop").addEventListener("click", () => { reader.stop(); persist(true); });
    $("live-previous").addEventListener("click", () => reader.play(reader.paragraph - 1, 0));
    $("live-next").addEventListener("click", () => reader.play(reader.paragraph + 1, 0));
    $("live-voice").addEventListener("change", () => {
      const speaking = ["speaking", "loading"].includes(reader.state);
      reader.stop();
      reader.voice = availableVoices.find(v => v.voiceURI === $("live-voice").value) || null;
      if (speaking) reader.play();
      persist(true);
      renderControls();
    });
    ["live-rate", "live-size", "live-follow", "live-continue"].forEach(id => $(id).addEventListener("change", () => {
      const speaking = id === "live-rate" && ["speaking", "loading"].includes(reader.state);
      const paused = id === "live-rate" && reader.state === "paused";
      if (speaking || paused) reader.stop();
      preferences();
      if (speaking) reader.play();
      persist(true);
    }));
    root.speechSynthesis?.addEventListener("voiceschanged", voices);
    document.addEventListener("studio-language", translate);
    document.addEventListener("studio-offline", voices);
    document.addEventListener("studio-view", event => { if (event.detail !== "live") { reader.stop(); persist(true); } });
    root.addEventListener("pagehide", () => { reader.stop(); persist(true); });
    root.openLiveReader = text => {
      if (!load(text)) { $("live-source").open = true; }
      closeReview();
      showView("live");
    };
    preferences();
    translate();
    if (typeof saved.text === "string" && saved.text.trim()) load(saved.text, true);
  }
})(typeof window !== "undefined" ? window : globalThis);
