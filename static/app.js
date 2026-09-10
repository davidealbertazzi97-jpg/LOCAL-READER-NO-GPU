const COPY = {
  it: {
    skip: "Vai al contenuto",
    language: "Lingua",
    offlineMode: "Modalità offline",
    offlineModeLabel: "Attiva o disattiva la modalità offline",
    offlineOn: "ON",
    offlineOff: "OFF",
    onlineMode: "Online · Edge-TTS",
    offlineModeStatus: "Offline · Kokoro 82M",
    privacyTitle: "I tuoi documenti restano sul computer",
    privacyBody: "OCR e percorso completo sono locali. I provider vocali online ricevono il testo solo quando li scegli.",
    resumeTitle: "Sessione ripristinata",
    resumeBody: "Ho recuperato l’ultimo punto di lavoro salvato su questo computer.",
    resumeDismiss: "Chiudi",
    resumeNeedsFile: "Il lavoro era in corso. Per un nuovo caricamento, scegli di nuovo il file originale.",
    resumeJob: "Riprendo il lavoro interrotto…",
    resumeAudio: "Riprendo l’audio dall’ultima posizione salvata…",
    services: "Servizi pronti",
    ready: "pronto",
    unavailable: "non disponibile",
    navComplete: "Studio completo",
    navOcr: "Solo OCR",
    navOrganize: "Solo organizza",
    navTts: "Solo voce",
    navHistory: "Cronologia",
    navSettings: "Impostazioni",
    infoCompleteLabel: "Informazioni sullo studio completo",
    infoOcrLabel: "Informazioni su Solo OCR",
    infoOrganizeLabel: "Informazioni su Solo organizza",
    infoTtsLabel: "Informazioni su Solo voce",
    infoHistoryLabel: "Informazioni sulla cronologia",
    infoSettingsLabel: "Informazioni sulle impostazioni",
    infoApiGuideLabel: "Informazioni sulla guida API",
    infoTtsSettingsLabel: "Informazioni sui provider vocali",
    infoCloneSettingsLabel: "Informazioni sulla clonazione della voce",
    infoLocalLabel: "Guida Solo locale",
    infoMistralLabel: "Guida Mistral",
    infoOpenCodeLabel: "Guida OpenCode Zen",
    infoGeminiLabel: "Guida Google Gemini",
    infoClaudeLabel: "Guida Anthropic Claude",
    infoNvidiaLabel: "Guida NVIDIA NIM",
    infoKiloLabel: "Guida Kilo Gateway",
    infoCustomLabel: "Guida provider personalizzato",
    mainNavLabel: "Menu principale",
    modelsListLabel: "Modelli disponibili",
    closeInfoLabel: "Chiudi informazioni",
    understood: "Ho capito",
    browseModels: "Browse Models",
    browseModelsTitle: "Modelli disponibili",
    searchModels: "Cerca un modello",
    useModel: "Usa questo modello",
    loadingModels: "Carico i modelli…",
    noModels: "Nessun modello trovato.",
    modelsNeedKey: "Inserisci prima la chiave API e salvala, oppure incollala nel campo.",
    modelsLoaded: "{count} modelli disponibili.",
    modelsLoadFailed: "Non riesco a recuperare i modelli. Controlla la chiave API.",
    modelSelected: "Modello selezionato.",
    completeEyebrow: "IL PERCORSO PIÙ SEMPLICE",
    completeTitle: "Carica un documento. Al resto pensiamo noi.",
    completeHelp: "PaddleOCR estrae il testo e la voce scelta lo trasforma direttamente in audio.",
    stepOcr: "Leggiamo",
    stepOcrHelp: "PaddleOCR estrae il testo",
    stepListen: "Ascolti",
    stepListenHelp: "La voce scelta crea l’audio",
    chooseDocument: "Scegli il documento",
    chooseDocumentHelp: "PDF o immagine. Anche molte pagine.",
    dropTitle: "Trascina qui il file",
    dropHelp: "oppure fai clic per sceglierlo dal computer",
    noFile: "Nessun file scelto",
    voiceSettings: "Scegli voce e velocità",
    speechLanguage: "Lingua",
    voice: "Voce",
    speed: "Velocità",
    device: "Computer per LFM",
    deviceAuto: "Automatico",
    deviceCpu: "Solo CPU",
    deviceGpu: "GPU, se disponibile",
    startComplete: "Avvia il percorso completo",
    workingTitle: "Sto lavorando sul documento",
    progressOcr: "Lettura del documento",
    progressSpeech: "Creazione dell’audio",
    progressLabel: "Avanzamento",
    completeStart: "Comincio con la lettura del documento…",
    ocrRunning: "Sto leggendo il documento. Se ha molte pagine, attendi qualche minuto…",
    completeOcr: "Il testo è stato estratto. Ora creo l’audio…",
    speechRunning: "Sto creando l’audio. Puoi lasciare aperta questa pagina…",
    completeDone: "Fatto: il tuo audio è pronto.",
    completeDoneFallback: "Audio pronto. Edge-TTS non rispondeva, quindi ho usato Kokoro offline.",
    audioReady: "Audio pronto",
    audioReadyHelp: "Puoi ascoltarlo qui oppure scaricarlo.",
    downloadAudio: "Scarica audio",
    howItWorks: "COME FUNZIONA",
    completeSideTitle: "Due passaggi, uno solo per te",
    guideOne: "Leggiamo",
    guideOneHelp: "Il testo viene estratto dal PDF o dall’immagine.",
    guideThree: "Facciamo ascoltare",
    guideThreeHelp: "Scegli una voce e ascolta il risultato.",
    tipTitle: "Non puoi sbagliare",
    tipHelp: "Se vuoi fare solo un passaggio, usa una delle modalità nel menu in alto.",
    ocrEyebrow: "UN SOLO PASSAGGIO",
    ocrTitle: "Solo OCR: ottieni il testo",
    ocrHelp: "Carica un documento e ricevi il testo estratto. Nessun audio e nessuna organizzazione automatica.",
    ocrChooseHelp: "Il file originale non viene modificato.",
    startOcr: "Estrai il testo",
    ocrReady: "Testo estratto",
    ocrReadyHelp: "Aprilo dalla cronologia per controllarlo o scaricarlo.",
    openResult: "Apri il risultato",
    bestFor: "QUANDO USARLO",
    ocrSideTitle: "Quando ti serve solo il testo",
    ocrSideHelp: "È utile se vuoi copiare il testo in un’altra applicazione o correggerlo con un’altra intelligenza artificiale.",
    localEngine: "funziona sul computer",
    organizeEyebrow: "UN SOLO PASSAGGIO",
    organizeTitle: "Solo organizza: prepara il testo per la voce",
    organizeHelp: "Incolla o carica un testo. LFM conserva le parole e sistema solo pause e paragrafi.",
    giveText: "Dai il testo a LFM",
    giveTextHelp: "Puoi incollarlo oppure allegare un file .txt o .md.",
    textTitle: "Titolo",
    textPaste: "Testo",
    textFile: "Oppure scegli un file di testo",
    modelSettings: "Impostazioni del modello",
    startOrganize: "Organizza il testo",
    organizeReady: "Testo organizzato",
    organizeReadyHelp: "Ora puoi copiarlo o passare alla modalità Solo voce.",
    important: "IMPORTANTE",
    organizeSideTitle: "LFM resta separato",
    organizeSideHelp: "Questa è l’unica modalità che organizza il testo. Il percorso completo non usa LFM e non modifica le parole.",
    ttsEyebrow: "UN SOLO PASSAGGIO",
    ttsTitle: "Solo voce: leggi un testo già pronto",
    ttsHelp: "Incolla o carica il testo già corretto e organizzato da te o da un’altra IA. Qui non usiamo OCR né LFM.",
    ttsGiveHelp: "Il testo verrà letto come lo inserisci, senza OCR e senza LFM.",
    ttsProvider: "Motore vocale",
    providerHelp: "Per usare un provider online inserisci prima la chiave in Impostazioni. Kokoro funziona anche senza rete.",
    startTts: "Crea l’audio",
    ttsSideTitle: "Quando il testo è già a posto",
    ttsSideHelp: "È il modo più rapido per ascoltare appunti, riassunti o testi preparati altrove.",
    networkVoice: "scegli online oppure offline",
    historyEyebrow: "TUTTO IN ORDINE",
    historyTitle: "Cronologia",
    historyHelp: "Qui trovi i documenti, i testi organizzati e gli audio creati su questo computer.",
    recentWork: "Lavori recenti",
    historyLocal: "La cronologia è locale.",
    refresh: "Aggiorna",
    clearHistory: "Cancella conclusi",
    confirmClearHistory: "Cancellare dalla cronologia tutti i lavori conclusi e i relativi file locali?",
    historyCleared: "Elementi cancellati: {count}.",
    empty: "Ancora nessun lavoro. Quando inizi, lo troverai qui.",
    reviewEyebrow: "CONTROLLO FACOLTATIVO",
    reviewTitle: "Controlla il testo OCR",
    reviewHelp: "Controlla le parole prima di creare l’audio. Le parti con confidenza bassa meritano più attenzione.",
    columnWarning: "Possibile impaginazione a colonne: controlla l’ordine dei blocchi prima di salvare.",
    moveBlockUp: "Sposta il blocco prima",
    moveBlockDown: "Sposta il blocco dopo",
    blockRoleLabel: "Tipo del blocco {number}",
    blockTextLabel: "Testo del blocco {number}",
    blockMoved: "Blocco {number} spostato alla posizione {position}.",
    close: "Chiudi",
    documentTitle: "Titolo del documento",
    documentLanguage: "Lingua",
    save: "Salva correzioni",
    saved: "Correzioni salvate.",
    saving: "Salvataggio…",
    downloadHtml: "Scarica HTML",
    downloadText: "Scarica testo",
    moreActions: "Altre azioni",
    textEditorTitle: "Controlla il testo",
    textEditorHelp: "Puoi correggerlo, organizzarlo con LFM oppure mandarlo direttamente alla voce.",
    saveText: "Salva testo",
    createSpeech: "Crea audio",
    reflow: "Organizza con LFM",
    download: "Scarica",
    delete: "Cancella",
    confirmDelete: "Cancellare questo lavoro dalla cronologia e rimuovere tutti i relativi file locali?",
    play: "Ascolta l’audio generato",
    processing: "in lavorazione",
    statuses: {uploading: "caricamento", queued: "in coda", running: "in lavorazione", completed: "completato", failed: "non riuscito"},
    jobTypes: {"accessible-document": "OCR documento", "plain-text": "Testo", "lfm-reflow": "Organizzazione LFM", "edge-tts": "Audio"},
    jobCompleted: "Operazione completata.",
    jobRunning: "Sto lavorando…",
    jobFailed: "Operazione non riuscita.",
    ocrFailed: "Non sono riuscito a leggere il documento. Prova con un PDF o un’immagine più nitida.",
    speechFailed: "Non sono riuscito a creare l’audio. Attiva Modalità offline e riprova con Kokoro.",
    organizationFailed: "Non sono riuscito a organizzare il testo. Il testo originale è ancora disponibile.",
    textFailed: "Non sono riuscito a preparare il testo. Riprova.",
    textRequired: "incolla un testo o scegli un file",
    sending: "Preparazione…",
    ocrQueued: "Documento in coda. Ti avviso quando il testo è pronto.",
    organizeQueued: "Testo in coda. Ora lo organizzo con LFM…",
    ttsQueued: "Testo in coda. Ora creo l’audio…",
    reflowQueued: "Organizzazione LFM in coda.",
    speechQueued: "Audio in coda.",
    failed: "Operazione non riuscita.",
    legal: "Note legali",
    settingsEyebrow: "UNA VOLTA SOLA",
    settingsTitle: "Impostazioni",
    settingsHelp: "Le scelte semplici sono qui. Provider, modelli e chiavi API sono dentro Impostazioni avanzate.",
    basicAudioTitle: "Audio: scegli e parti",
    basicAudioHelp: "Edge-TTS usa internet. Kokoro 82M funziona sul computer e non invia il testo.",
    basicAudioHint: "Usa il pulsante “Modalità offline” in alto per passare a Kokoro in un clic.",
    audioModel: "Modello audio",
    connectionMode: "Modalità",
    advancedSettings: "Impostazioni avanzate",
    aiSettingsTitle: "Intelligenza per “Solo organizza”",
    aiSettingsHelp: "Scegli un provider, apri la guida con il pulsante “i” e inserisci la chiave solo se vuoi usare un servizio online.",
    apiMenuEyebrow: "PROVIDER DISPONIBILI",
    apiMenuTitle: "Scegli l’intelligenza che vuoi usare",
    apiMenuHint: "Le chiavi restano locali",
    selectedProvider: "PROVIDER SELEZIONATO",
    apiGuideEyebrow: "GUIDA PASSO PASSO",
    apiGuideTitle: "Come ottenere e usare una chiave API",
    apiGuideHelp: "Scegli un provider qui sopra per configurarlo. Ogni guida apre il sito ufficiale in una nuova scheda.",
    configuredShort: "configurato",
    notConfiguredShort: "da configurare",
    offlineBadge: "OFFLINE",
    openProviderPage: "Apri la pagina ufficiale ↗",
    guideCustomLink: "Esempio: chiavi OpenAI ↗",
    guideLocalIntro: "Non serve nessuna chiave: LFM lavora sul computer.",
    guideLocalStep1: "Seleziona “Solo locale” nel menu degli AI.",
    guideLocalStep2: "Salva le impostazioni e usa “Solo organizza”.",
    guideMistralIntro: "Per usare i modelli Mistral con una chiave personale.",
    guideMistralStep1: "Apri Mistral Studio e accedi o crea un account.",
    guideMistralStep2: "Apri “API Keys”, scegli “Create new key” e assegna un nome.",
    guideMistralStep3: "Copia subito la chiave: il valore completo viene mostrato una sola volta.",
    guideMistralStep4: "Torna qui, seleziona Mistral, incolla la chiave e salva.",
    guideOpenCodeIntro: "Gateway OpenCode con modelli verificati e pagamento a consumo.",
    guideOpenCodeStep1: "Apri OpenCode Zen e accedi con il tuo account.",
    guideOpenCodeStep2: "Aggiungi un metodo di pagamento o eventuali crediti.",
    guideOpenCodeStep3: "Crea o copia la tua API key dalla pagina Zen.",
    guideOpenCodeStep4: "Seleziona OpenCode Zen qui, lascia l’indirizzo proposto, incolla la chiave e salva.",
    guideGeminiIntro: "Gemini tramite Google AI Studio e la sua API compatibile OpenAI.",
    guideGeminiStep1: "Apri Google AI Studio e accedi con il tuo account Google.",
    guideGeminiStep2: "Nella pagina API keys scegli “Create API key” e collega un progetto.",
    guideGeminiStep3: "Copia la chiave e controlla i limiti o la fatturazione del progetto.",
    guideGeminiStep4: "Torna qui, seleziona Google Gemini, incolla la chiave e salva.",
    guideClaudeIntro: "Claude usa l’API Messages ufficiale di Anthropic.",
    guideClaudeStep1: "Apri Claude Console e accedi o crea un account.",
    guideClaudeStep2: "Vai in “Settings → API keys” e scegli “Create key”.",
    guideClaudeStep3: "Dai un nome, scegli la scadenza e copia la chiave.",
    guideClaudeStep4: "Torna qui, seleziona Anthropic Claude, incolla la chiave e salva.",
    guideNvidiaIntro: "Endpoint NVIDIA compatibile OpenAI con modelli ospitati e lista modelli automatica.",
    guideNvidiaStep1: "Apri NVIDIA Build e accedi o crea un account NVIDIA.",
    guideNvidiaStep2: "Scegli un modello, apri la sezione API e crea una API key.",
    guideNvidiaStep3: "Copia la chiave e torna qui: l’endpoint NVIDIA NIM è già compilato.",
    guideNvidiaStep4: "Seleziona NVIDIA NIM, premi “Browse Models”, scegli il modello e salva.",
    openNvidiaPage: "Apri NVIDIA Build ↗",
    guideKiloIntro: "Un endpoint compatibile OpenAI per molti modelli con una sola chiave.",
    guideKiloStep1: "Apri Kilo e accedi o crea un account.",
    guideKiloStep2: "Apri il profilo personale e raggiungi la sezione della chiave API.",
    guideKiloStep3: "Copia la chiave e aggiungi crediti se il modello lo richiede.",
    guideKiloStep4: "Torna qui, seleziona Kilo Gateway, incolla la chiave e salva.",
    guideCustomIntro: "Per un endpoint OpenAI-compatible che conosci già.",
    guideCustomStep1: "Scegli “Provider personalizzato”.",
    guideCustomStep2: "Inserisci l’indirizzo base HTTPS senza aggiungere “/chat/completions”.",
    guideCustomStep3: "Inserisci il nome esatto del modello e la chiave API.",
    guideCustomStep4: "Salva e prova “Solo organizza”.",
    helpCompleteTitle: "Studio completo",
    helpCompleteBody: "Carica un PDF o un’immagine. Local Accessibility Studio estrae il testo con OCR e crea un audio. Tu devi solo scegliere il file e, se vuoi, la voce.",
    helpOcrTitle: "Solo OCR",
    helpOcrBody: "Usa questa modalità quando vuoi soltanto estrarre il testo. Il documento originale non viene modificato e il risultato resta nella cronologia locale.",
    helpOrganizeTitle: "Solo organizza",
    helpOrganizeBody: "Incolla un testo e l’app migliora spazi e paragrafi per la lettura vocale. LFM locale non cambia le parole; i provider online vengono usati solo se li selezioni.",
    helpTtsTitle: "Solo voce",
    helpTtsBody: "Incolla o carica un testo già pronto, scegli la voce e avvia. Kokoro funziona senza rete; i provider online inviano il testo al servizio scelto.",
    helpHistoryTitle: "Cronologia",
    helpHistoryBody: "Qui trovi i risultati creati su questo computer. Puoi aprire un testo per correggerlo, ascoltare un audio o cancellare i lavori conclusi.",
    helpSettingsTitle: "Impostazioni",
    helpSettingsBody: "Configura una volta sola le chiavi API e i motori vocali. Le chiavi vengono salvate nella cartella privata dell’app e non vengono mostrate dopo il salvataggio.",
    helpApiGuideTitle: "Guida alle API",
    helpApiGuideBody: "Scegli un provider nella griglia, usa il pulsante “i” per saltare alla sua guida e apri il link ufficiale. Poi incolla la chiave nel modulo e salva.",
    helpTtsSettingsTitle: "Voci e audio",
    helpTtsSettingsBody: "Scegli il motore vocale. Edge-TTS e i provider premium funzionano online; Kokoro resta sul computer e non richiede una chiave.",
    helpCloneSettingsTitle: "Clonazione della voce",
    helpCloneSettingsBody: "Carica un breve campione solo se hai il consenso della persona. Il file temporaneo viene eliminato dopo l’invio al servizio scelto.",
    organizationProvider: "Provider",
    model: "Modello",
    baseUrl: "Indirizzo del provider",
    apiKey: "Chiave API",
    saveSettings: "Salva impostazioni",
    voiceProvidersTitle: "Voci e audio premium",
    voiceProvidersHelp: "Le chiavi restano in una cartella privata e non vengono mostrate dopo il salvataggio.",
    defaultVoiceProvider: "Provider vocale predefinito",
    voiceId: "ID voce",
    kokoroItalianVoice: "Voce Kokoro italiana",
    kokoroEnglishVoice: "Voce Kokoro inglese",
    cloneTitle: "Clonazione della voce",
    cloneHelp: "Usa un campione solo con il consenso della persona. Il campione viene eliminato dal computer dopo l’invio.",
    cloneProvider: "Servizio",
    cloneName: "Nome della voce",
    cloneSample: "Campione audio",
    cloneConsent: "Confermo di avere il permesso di usare questa voce.",
    createClone: "Crea voce clonata",
    keyConfigured: "Chiave configurata",
    keyMissing: "Chiave non configurata",
    savedSettings: "Impostazioni salvate.",
    cloneCreated: "Voce creata e pronta da scegliere.",
  },
  en: {
    skip: "Skip to content",
    language: "Language",
    offlineMode: "Offline mode",
    offlineModeLabel: "Turn offline mode on or off",
    offlineOn: "ON",
    offlineOff: "OFF",
    onlineMode: "Online · Edge-TTS",
    offlineModeStatus: "Offline · Kokoro 82M",
    privacyTitle: "Your documents stay on this computer",
    privacyBody: "OCR and the full path are local. Online voice providers receive text only when you choose them.",
    resumeTitle: "Session restored",
    resumeBody: "I recovered the last working point saved on this computer.",
    resumeDismiss: "Close",
    resumeNeedsFile: "The work was in progress. For a new upload, choose the original file again.",
    resumeJob: "Resuming the interrupted work…",
    resumeAudio: "Resuming audio from the last saved position…",
    services: "Services ready",
    ready: "ready",
    unavailable: "unavailable",
    navComplete: "Full studio",
    navOcr: "OCR only",
    navOrganize: "Organize only",
    navTts: "Voice only",
    navHistory: "History",
    navSettings: "Settings",
    infoCompleteLabel: "Information about the full studio",
    infoOcrLabel: "Information about OCR only",
    infoOrganizeLabel: "Information about Organize only",
    infoTtsLabel: "Information about Voice only",
    infoHistoryLabel: "Information about history",
    infoSettingsLabel: "Information about settings",
    infoApiGuideLabel: "Information about the API guide",
    infoTtsSettingsLabel: "Information about voice providers",
    infoCloneSettingsLabel: "Information about voice cloning",
    infoLocalLabel: "Solo locale guide",
    infoMistralLabel: "Mistral guide",
    infoOpenCodeLabel: "OpenCode Zen guide",
    infoGeminiLabel: "Google Gemini guide",
    infoClaudeLabel: "Anthropic Claude guide",
    infoNvidiaLabel: "NVIDIA NIM guide",
    infoKiloLabel: "Kilo Gateway guide",
    infoCustomLabel: "Custom provider guide",
    mainNavLabel: "Main navigation",
    modelsListLabel: "Available models",
    closeInfoLabel: "Close information",
    understood: "Got it",
    browseModels: "Browse Models",
    browseModelsTitle: "Available models",
    searchModels: "Search for a model",
    useModel: "Use this model",
    loadingModels: "Loading models…",
    noModels: "No models found.",
    modelsNeedKey: "Enter and save the API key first, or paste it into the field.",
    modelsLoaded: "{count} models available.",
    modelsLoadFailed: "I could not retrieve the models. Check the API key.",
    modelSelected: "Model selected.",
    completeEyebrow: "THE SIMPLEST PATH",
    completeTitle: "Upload a document. We take care of the rest.",
    completeHelp: "PaddleOCR extracts the text and the selected voice turns it directly into audio.",
    stepOcr: "Read",
    stepOcrHelp: "PaddleOCR extracts text",
    stepListen: "Listen",
    stepListenHelp: "The selected voice creates audio",
    chooseDocument: "Choose the document",
    chooseDocumentHelp: "PDF or image. Many pages are fine.",
    dropTitle: "Drop the file here",
    dropHelp: "or click to choose it from the computer",
    noFile: "No file chosen",
    voiceSettings: "Choose voice and speed",
    speechLanguage: "Language",
    voice: "Voice",
    speed: "Speed",
    device: "Computer for LFM",
    deviceAuto: "Automatic",
    deviceCpu: "CPU only",
    deviceGpu: "GPU, if available",
    startComplete: "Start the full path",
    workingTitle: "Working on your document",
    progressOcr: "Reading the document",
    progressSpeech: "Creating the audio",
    progressLabel: "Progress",
    completeStart: "Starting with the document reading…",
    ocrRunning: "Reading the document. A document with many pages may take a few minutes…",
    completeOcr: "The text is ready. Now I create the audio…",
    speechRunning: "Creating the audio. You can leave this page open…",
    completeDone: "Done: your audio is ready.",
    completeDoneFallback: "Audio ready. Edge-TTS was unavailable, so I used offline Kokoro.",
    audioReady: "Audio ready",
    audioReadyHelp: "Listen here or download it.",
    downloadAudio: "Download audio",
    howItWorks: "HOW IT WORKS",
    completeSideTitle: "Two steps, one action for you",
    guideOne: "Read",
    guideOneHelp: "Text is extracted from the PDF or image.",
    guideThree: "Listen",
    guideThreeHelp: "Choose a voice and listen to the result.",
    tipTitle: "You cannot get lost",
    tipHelp: "For one step only, choose a mode from the menu above.",
    ocrEyebrow: "ONE STEP",
    ocrTitle: "OCR only: get the text",
    ocrHelp: "Upload a document and receive its extracted text. No audio and no automatic organization.",
    ocrChooseHelp: "The original file is never changed.",
    startOcr: "Extract the text",
    ocrReady: "Text extracted",
    ocrReadyHelp: "Open it from history to check or download it.",
    openResult: "Open result",
    bestFor: "WHEN TO USE IT",
    ocrSideTitle: "When you only need the text",
    ocrSideHelp: "Useful when you want to copy the text into another app or correct it with another AI.",
    localEngine: "runs on this computer",
    organizeEyebrow: "ONE STEP",
    organizeTitle: "Organize only: prepare text for speech",
    organizeHelp: "Paste or upload text. LFM preserves words and only fixes pauses and paragraphs.",
    giveText: "Give text to LFM",
    giveTextHelp: "Paste it or attach a .txt or .md file.",
    textTitle: "Title",
    textPaste: "Text",
    textFile: "Or choose a text file",
    modelSettings: "Model settings",
    startOrganize: "Organize the text",
    organizeReady: "Text organized",
    organizeReadyHelp: "Now copy it or switch to Voice only.",
    important: "IMPORTANT",
    organizeSideTitle: "LFM stays separate",
    organizeSideHelp: "This is the only mode that organizes text. The full path does not use LFM or change words.",
    ttsEyebrow: "ONE STEP",
    ttsTitle: "Voice only: read text that is ready",
    ttsHelp: "Paste or upload text already corrected and organized by you or another AI. OCR and LFM are not used here.",
    ttsGiveHelp: "The text is read as you provide it, without OCR or LFM.",
    ttsProvider: "Voice engine",
    providerHelp: "For an online provider, add its key in Settings first. Kokoro also works without a network.",
    startTts: "Create the audio",
    ttsSideTitle: "When the text is already ready",
    ttsSideHelp: "The quickest way to listen to notes, summaries, or text prepared elsewhere.",
    networkVoice: "choose online or offline",
    historyEyebrow: "EVERYTHING IN ORDER",
    historyTitle: "History",
    historyHelp: "Find documents, organized text, and audio created on this computer.",
    recentWork: "Recent work",
    historyLocal: "History is local.",
    refresh: "Refresh",
    clearHistory: "Clear finished",
    confirmClearHistory: "Clear all finished work and its local files from history?",
    historyCleared: "Items cleared: {count}.",
    empty: "No work yet. It will appear here when you start.",
    reviewEyebrow: "OPTIONAL CHECK",
    reviewTitle: "Check the OCR text",
    reviewHelp: "Check the words before creating audio. Low-confidence parts need extra attention.",
    columnWarning: "Possible multi-column layout: check the block order before saving.",
    moveBlockUp: "Move block earlier",
    moveBlockDown: "Move block later",
    blockRoleLabel: "Block {number} type",
    blockTextLabel: "Block {number} text",
    blockMoved: "Block {number} moved to position {position}.",
    close: "Close",
    documentTitle: "Document title",
    documentLanguage: "Language",
    save: "Save corrections",
    saved: "Corrections saved.",
    saving: "Saving…",
    downloadHtml: "Download HTML",
    downloadText: "Download text",
    moreActions: "More actions",
    textEditorTitle: "Check the text",
    textEditorHelp: "Correct it, organize it with LFM, or send it straight to speech.",
    saveText: "Save text",
    createSpeech: "Create audio",
    reflow: "Organize with LFM",
    download: "Download",
    delete: "Delete",
    confirmDelete: "Delete this work and all its local files from history?",
    play: "Play generated audio",
    processing: "processing",
    statuses: {uploading: "uploading", queued: "queued", running: "processing", completed: "completed", failed: "failed"},
    jobTypes: {"accessible-document": "Document OCR", "plain-text": "Text", "lfm-reflow": "LFM organization", "edge-tts": "Audio"},
    jobCompleted: "Operation completed.",
    jobRunning: "Working…",
    jobFailed: "Operation failed.",
    ocrFailed: "I could not read the document. Try a clearer PDF or image.",
    speechFailed: "I could not create the audio. Turn on Offline mode and retry with Kokoro.",
    organizationFailed: "I could not organize the text. The original text is still available.",
    textFailed: "I could not prepare the text. Please retry.",
    textRequired: "paste text or choose a file",
    sending: "Preparing…",
    ocrQueued: "Document queued. I will let you know when the text is ready.",
    organizeQueued: "Text queued. Now I organize it with LFM…",
    ttsQueued: "Text queued. Now I create the audio…",
    reflowQueued: "LFM organization queued.",
    speechQueued: "Audio queued.",
    failed: "Operation failed.",
    legal: "Legal notices",
    settingsEyebrow: "SET UP ONCE",
    settingsTitle: "Settings",
    settingsHelp: "Simple choices are here. Providers, models, and API keys are inside Advanced settings.",
    basicAudioTitle: "Audio: choose and start",
    basicAudioHelp: "Edge-TTS uses the internet. Kokoro 82M stays on this computer and does not send the text.",
    basicAudioHint: "Use the “Offline mode” button at the top to switch to Kokoro with one click.",
    audioModel: "Audio model",
    connectionMode: "Mode",
    advancedSettings: "Advanced settings",
    aiSettingsTitle: "Intelligence for “Organize only”",
    aiSettingsHelp: "Choose a provider, use the “i” button for its guide, and add a key only if you want an online service.",
    apiMenuEyebrow: "AVAILABLE PROVIDERS",
    apiMenuTitle: "Choose the intelligence you want to use",
    apiMenuHint: "Keys stay local",
    selectedProvider: "SELECTED PROVIDER",
    apiGuideEyebrow: "STEP-BY-STEP GUIDE",
    apiGuideTitle: "How to get and use an API key",
    apiGuideHelp: "Choose a provider above to configure it. Each guide opens the official website in a new tab.",
    configuredShort: "configured",
    notConfiguredShort: "needs setup",
    offlineBadge: "OFFLINE",
    openProviderPage: "Open official page ↗",
    guideCustomLink: "Example: OpenAI keys ↗",
    guideLocalIntro: "No key is needed: LFM runs on this computer.",
    guideLocalStep1: "Select “Solo locale” in the AI menu.",
    guideLocalStep2: "Save the settings and use “Organize only”.",
    guideMistralIntro: "Use Mistral models with your own API key.",
    guideMistralStep1: "Open Mistral Studio and sign in or create an account.",
    guideMistralStep2: "Open “API Keys”, choose “Create new key”, and name it.",
    guideMistralStep3: "Copy the key immediately: the full value is shown only once.",
    guideMistralStep4: "Return here, select Mistral, paste the key, and save.",
    guideOpenCodeIntro: "OpenCode gateway with tested models and pay-as-you-go billing.",
    guideOpenCodeStep1: "Open OpenCode Zen and sign in.",
    guideOpenCodeStep2: "Add a payment method or credits if requested.",
    guideOpenCodeStep3: "Create or copy your API key from the Zen page.",
    guideOpenCodeStep4: "Select OpenCode Zen here, keep the suggested address, paste the key, and save.",
    guideGeminiIntro: "Gemini through Google AI Studio and its OpenAI-compatible API.",
    guideGeminiStep1: "Open Google AI Studio and sign in with your Google account.",
    guideGeminiStep2: "On the API keys page choose “Create API key” and link a project.",
    guideGeminiStep3: "Copy the key and check the project limits or billing.",
    guideGeminiStep4: "Return here, select Google Gemini, paste the key, and save.",
    guideClaudeIntro: "Claude uses Anthropic’s official Messages API.",
    guideClaudeStep1: "Open the Claude Console and sign in or create an account.",
    guideClaudeStep2: "Go to “Settings → API keys” and choose “Create key”.",
    guideClaudeStep3: "Name the key, choose its expiration, and copy it.",
    guideClaudeStep4: "Return here, select Anthropic Claude, paste the key, and save.",
    guideNvidiaIntro: "NVIDIA OpenAI-compatible endpoint with hosted models and automatic model browsing.",
    guideNvidiaStep1: "Open NVIDIA Build and sign in or create an NVIDIA account.",
    guideNvidiaStep2: "Choose a model, open its API section, and create an API key.",
    guideNvidiaStep3: "Copy the key and return here: the NVIDIA NIM endpoint is already filled in.",
    guideNvidiaStep4: "Select NVIDIA NIM, press “Browse Models”, choose a model, and save.",
    openNvidiaPage: "Open NVIDIA Build ↗",
    guideKiloIntro: "An OpenAI-compatible gateway for many models with one key.",
    guideKiloStep1: "Open Kilo and sign in or create an account.",
    guideKiloStep2: "Open your personal profile and find the API key section.",
    guideKiloStep3: "Copy the key and add credits if the model requires them.",
    guideKiloStep4: "Return here, select Kilo Gateway, paste the key, and save.",
    guideCustomIntro: "For an OpenAI-compatible endpoint you already use.",
    guideCustomStep1: "Choose “Custom provider”.",
    guideCustomStep2: "Enter the HTTPS base address without “/chat/completions”.",
    guideCustomStep3: "Enter the exact model name and API key.",
    guideCustomStep4: "Save and try “Organize only”.",
    helpCompleteTitle: "Full studio",
    helpCompleteBody: "Upload a PDF or image. Local Accessibility Studio extracts the text with OCR and creates audio. You only need to choose the file and, if you want, the voice.",
    helpOcrTitle: "OCR only",
    helpOcrBody: "Use this mode when you only need the extracted text. The original document is not changed and the result stays in local history.",
    helpOrganizeTitle: "Organize only",
    helpOrganizeBody: "Paste text and the app improves spacing and paragraphs for speech. Local LFM does not change words; online providers are used only when selected.",
    helpTtsTitle: "Voice only",
    helpTtsBody: "Paste or upload ready text, choose a voice, and start. Kokoro works offline; online providers send text to the service you choose.",
    helpHistoryTitle: "History",
    helpHistoryBody: "Find the results created on this computer. You can open text to edit it, listen to audio, or clear finished work.",
    helpSettingsTitle: "Settings",
    helpSettingsBody: "Configure API keys and voice engines once. Keys are saved in the app’s private folder and are not shown after saving.",
    helpApiGuideTitle: "API guide",
    helpApiGuideBody: "Choose a provider in the grid, use its “i” button to jump to the guide, and open the official link. Then paste the key into the form and save.",
    helpTtsSettingsTitle: "Voices and audio",
    helpTtsSettingsBody: "Choose the voice engine. Edge-TTS and premium providers work online; Kokoro stays on this computer and needs no key.",
    helpCloneSettingsTitle: "Voice cloning",
    helpCloneSettingsBody: "Upload a short sample only if you have the person’s consent. The temporary file is deleted after it is sent to the selected service.",
    organizationProvider: "Provider",
    model: "Model",
    baseUrl: "Provider address",
    apiKey: "API key",
    saveSettings: "Save settings",
    voiceProvidersTitle: "Voices and premium audio",
    voiceProvidersHelp: "Keys stay in a private folder and are never shown after saving.",
    defaultVoiceProvider: "Default voice provider",
    voiceId: "Voice ID",
    kokoroItalianVoice: "Italian Kokoro voice",
    kokoroEnglishVoice: "English Kokoro voice",
    cloneTitle: "Voice cloning",
    cloneHelp: "Use a sample only with the person’s consent. The sample is deleted from the computer after upload.",
    cloneProvider: "Service",
    cloneName: "Voice name",
    cloneSample: "Audio sample",
    cloneConsent: "I confirm that I have permission to use this voice.",
    createClone: "Create cloned voice",
    keyConfigured: "Key configured",
    keyMissing: "Key not configured",
    savedSettings: "Settings saved.",
    cloneCreated: "Voice created and ready to choose.",
  },
};

const VOICE_PROFILES = {
  it: [["it-IT-GiuseppeMultilingualNeural", "Maschile — Giuseppe", "Male — Giuseppe"], ["it-IT-ElsaNeural", "Femminile — Elsa", "Female — Elsa"]],
  "en-us": [["en-US-AndrewMultilingualNeural", "Maschile — Andrew", "Male — Andrew"], ["en-US-AvaMultilingualNeural", "Femminile — Ava", "Female — Ava"]],
  "en-gb": [["en-GB-RyanNeural", "Maschile — Ryan", "Male — Ryan"], ["en-GB-SoniaNeural", "Femminile — Sonia", "Female — Sonia"]],
};

const AI_PROVIDER_META = {
  local: {label: "Solo locale", description: {it: "LFM 230M lavora senza inviare testo online.", en: "LFM 230M works without sending text online."}},
  mistral: {label: "Mistral", description: {it: "Modelli Mistral tramite API.", en: "Mistral models through the API."}},
  opencode: {label: "OpenCode Zen", description: {it: "Gateway OpenCode con modelli curati.", en: "OpenCode gateway with curated models."}},
  gemini: {label: "Google Gemini", description: {it: "Gemini tramite Google AI Studio.", en: "Gemini through Google AI Studio."}},
  claude: {label: "Anthropic Claude", description: {it: "Claude tramite API Messages.", en: "Claude through the Messages API."}},
  "nvidia-nim": {label: "NVIDIA NIM", description: {it: "Modelli NVIDIA tramite endpoint NIM.", en: "NVIDIA models through the NIM endpoint."}},
  kilo: {label: "Kilo Gateway", description: {it: "Un accesso a molti modelli.", en: "One gateway to many models."}},
  custom: {label: "Provider personalizzato", description: {it: "Un endpoint OpenAI-compatible.", en: "An OpenAI-compatible endpoint."}},
};

const HELP_COPY_KEYS = {
  complete: ["helpCompleteTitle", "helpCompleteBody"],
  ocr: ["helpOcrTitle", "helpOcrBody"],
  organize: ["helpOrganizeTitle", "helpOrganizeBody"],
  tts: ["helpTtsTitle", "helpTtsBody"],
  history: ["helpHistoryTitle", "helpHistoryBody"],
  settings: ["helpSettingsTitle", "helpSettingsBody"],
  apiGuide: ["helpApiGuideTitle", "helpApiGuideBody"],
  ttsSettings: ["helpTtsSettingsTitle", "helpTtsSettingsBody"],
  cloneSettings: ["helpCloneSettingsTitle", "helpCloneSettingsBody"],
};

let language = localStorage.getItem("accessibility-language") || "it";
let product = null;
let engines = [];
let speechReady = false;
let reflowReady = false;
let ocrReady = false;
let providerStatus = {tts: {}, ai: {}};
let settings = null;
let offlineMode = false;
let modeSaving = false;
const busyForms = new Set();
let pollTimer = null;
let activeView = "complete";
let lastOcrJob = null;
let lastOrganizeJob = null;
let editingJob = null;
let documentValue = null;
let editingTextJob = null;
let textValue = null;
let browsedModels = [];
let selectedBrowseModel = "";
const RESUME_STORAGE_KEY = "local-accessibility-studio-session-v1";
const MAX_RESUME_TEXT = 512 * 1024;
let sessionReady = false;
let resumeTimer = null;
let restoredSession = null;
let workflows = {complete: null, ocr: null, organize: null, tts: null};
let sessionTouched = false;
let audioProgress = {complete: null, tts: null};
let lastAudioCheckpoint = 0;

function t(key) {
  return COPY[language]?.[key] ?? COPY.en[key] ?? key;
}

function sleep(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function boundedResumeText(value) {
  const text = String(value || "");
  return text.length <= MAX_RESUME_TEXT ? text : text.slice(0, MAX_RESUME_TEXT);
}

function readResumeState() {
  try {
    const parsed = JSON.parse(localStorage.getItem(RESUME_STORAGE_KEY) || "null");
    if (!parsed || parsed.version !== 1 || typeof parsed !== "object") return null;
    return parsed;
  } catch (_error) {
    return null;
  }
}

function resumeForms() {
  return {
    complete: {
      language: document.querySelector("#complete-language")?.value || "it",
      provider: document.querySelector("#complete-provider")?.value || workflowSpeechProvider(),
      voice: document.querySelector("#complete-voice")?.value || "",
      speed: document.querySelector("#complete-speed")?.value || "1",
    },
    organize: {
      title: document.querySelector("#organize-title-input")?.value || "",
      text: boundedResumeText(document.querySelector("#organize-input")?.value),
      provider: document.querySelector("#organize-provider")?.value || "local",
      device: document.querySelector("#organize-device")?.value || "auto",
    },
    tts: {
      title: document.querySelector("#tts-title-input")?.value || "",
      text: boundedResumeText(document.querySelector("#tts-input")?.value),
      language: document.querySelector("#tts-language")?.value || "it",
      provider: document.querySelector("#tts-provider")?.value || "edge-tts",
      voice: document.querySelector("#tts-voice")?.value || "",
      speed: document.querySelector("#tts-speed")?.value || "1",
    },
  };
}

function resumeEditor() {
  if (editingTextJob && textValue) {
    return {
      type: "text",
      jobId: editingTextJob.id,
      text: boundedResumeText(document.querySelector("#text-workspace")?.value || textValue.text),
    };
  }
  if (editingJob && documentValue) {
    const serialized = JSON.stringify(documentValue);
    if (serialized.length <= MAX_RESUME_TEXT * 2) {
      return {type: "document", jobId: editingJob.id, document: documentValue};
    }
    return {type: "document", jobId: editingJob.id};
  }
  return null;
}

function persistSession() {
  if (!sessionReady) return;
  const editor = resumeEditor();
  const hasWorkflow = Object.values(workflows).some((workflow) => workflow && typeof workflow === "object");
  const forms = resumeForms();
  const hasTextDraft = Boolean(forms.organize.text.trim() || forms.tts.text.trim());
  if (!sessionTouched && activeView === "complete" && !hasWorkflow && !editor && !hasTextDraft) {
    localStorage.removeItem(RESUME_STORAGE_KEY);
    return;
  }
  const state = {
    version: 1,
    savedAt: Date.now(),
    activeView,
    forms,
    workflows,
    editor,
    audio: audioProgress,
  };
  try {
    localStorage.setItem(RESUME_STORAGE_KEY, JSON.stringify(state));
  } catch (_error) {
    // A large draft must never stop the application. The server-side job remains safe.
  }
}

function schedulePersist() {
  if (!sessionReady) return;
  sessionTouched = true;
  window.clearTimeout(resumeTimer);
  resumeTimer = window.setTimeout(persistSession, 180);
}

function setWorkflow(name, value) {
  workflows[name] = value;
  sessionTouched = true;
  schedulePersist();
}

function clearWorkflow(name) {
  workflows[name] = null;
  persistSession();
}

function showResumeBanner(message = t("resumeBody")) {
  const banner = document.querySelector("#resume-banner");
  const text = document.querySelector("#resume-message");
  if (!banner || !text) return;
  text.textContent = message;
  banner.hidden = false;
}

function restoreResumeForms(forms = {}) {
  const setValue = (selector, value) => {
    if (value !== undefined && document.querySelector(selector)) document.querySelector(selector).value = value;
  };
  const complete = forms.complete || {};
  const organize = forms.organize || {};
  const tts = forms.tts || {};
  setValue("#complete-language", complete.language);
  setValue("#complete-provider", complete.provider);
  setValue("#complete-speed", complete.speed);
  fillVoiceSelect(document.querySelector("#complete-voice"), complete.language || "it", complete.voice);
  setValue("#organize-title-input", organize.title);
  setValue("#organize-input", organize.text);
  setValue("#organize-provider", organize.provider);
  setValue("#organize-device", organize.device);
  setValue("#tts-language", tts.language);
  setValue("#tts-title-input", tts.title);
  setValue("#tts-input", tts.text);
  setValue("#tts-provider", tts.provider);
  setValue("#tts-speed", tts.speed);
  renderProviderVoiceSelects();
  if (tts.voice) setValue("#tts-voice", tts.voice);
  document.querySelector("#complete-speed-value").textContent = `${Number(document.querySelector("#complete-speed").value).toFixed(2).replace(".", ",")}×`;
  document.querySelector("#tts-speed-value").textContent = `${Number(document.querySelector("#tts-speed").value).toFixed(2).replace(".", ",")}×`;
}

async function restoreEditor(editor) {
  if (!editor?.jobId) return;
  try {
    const job = await api(`/api/jobs/${encodeURIComponent(editor.jobId)}`);
    if (job.status !== "completed") return;
    if (editor.type === "document") {
      await openDocument(job);
      if (editor.document && editor.document.revision === documentValue?.revision) {
        documentValue = editor.document;
        renderDocument();
      }
    } else if (editor.type === "text") {
      await openTextJob(job);
      if (typeof editor.text === "string") document.querySelector("#text-workspace").value = editor.text;
    }
  } catch (_error) {
    // The history remains available even when a draft's original job was deleted.
  }
}

async function restoreSession() {
  restoredSession = readResumeState();
  if (restoredSession) {
    sessionTouched = true;
    workflows = {...workflows, ...(restoredSession.workflows || {})};
    audioProgress = {...audioProgress, ...(restoredSession.audio || {})};
    restoreResumeForms(restoredSession.forms || {});
    if (["complete", "ocr", "organize", "tts", "history", "settings"].includes(restoredSession.activeView)) {
      showView(restoredSession.activeView, false);
    }
    await restoreEditor(restoredSession.editor);
    restoreAudioState();
    const hasWorkflow = Object.values(workflows).some(Boolean);
    const hasAudio = Object.values(audioProgress).some((item) => item && item.jobId);
    showResumeBanner(hasWorkflow ? t("resumeJob") : hasAudio ? t("resumeAudio") : t("resumeBody"));
  }
  sessionReady = true;
  persistSession();
  await resumeActiveWorkflows();
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
  select.replaceChildren(...profile.map(([value, italian, english]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = language === "it" ? italian : english;
    return option;
  }));
  if (profile.some(([value]) => value === preferred)) select.value = preferred;
}

function renderProviderVoiceSelects() {
  const select = document.querySelector("#tts-voice");
  const provider = document.querySelector("#tts-provider")?.value || "edge-tts";
  const speechLanguage = document.querySelector("#tts-language")?.value || "it";
  const preferred = select?.value || "";
  if (!select) return;
  if (provider === "edge-tts") {
    fillVoiceSelect(select, speechLanguage, preferred);
  } else if (provider === "kokoro") {
    const voices = speechLanguage === "it"
      ? [["if_sara", "Sara — femminile", "Sara — female"], ["im_nicola", "Nicola — maschile", "Nicola — male"]]
      : [["af_heart", "Heart — femminile", "Heart — female"], ["am_michael", "Michael — maschile", "Michael — male"]];
    select.replaceChildren(...voices.map(([value, it, en]) => { const option = document.createElement("option"); option.value = value; option.textContent = language === "it" ? it : en; return option; }));
    if (voices.some(([value]) => value === preferred)) select.value = preferred;
  } else {
    const configured = settings?.settings?.tts?.[provider === "voxtral" ? "mistral" : provider]?.voice_id || "";
    const clones = (settings?.settings?.clones || []).filter((clone) => clone.provider === provider);
    const entries = [["", language === "it" ? "Voce predefinita del provider" : "Provider default voice"]];
    if (configured) entries.push([configured, language === "it" ? `Voce configurata (${configured})` : `Configured voice (${configured})`]);
    clones.forEach((clone) => entries.push([clone.voice_id, clone.name]));
    select.replaceChildren(...entries.map(([value, label]) => { const option = document.createElement("option"); option.value = value; option.textContent = label; return option; }));
    if (entries.some(([value]) => value === preferred)) select.value = preferred;
  }
  const label = document.querySelector("#tts-side-provider");
  if (label) label.textContent = ({"edge-tts": "Edge-TTS", kokoro: "Kokoro 82M", voxtral: "Voxtral", fish: "Fish Audio", "fish-local": "Fish Audio locale", elevenlabs: "ElevenLabs"})[provider] || provider;
}

function kokoroVoiceFor(language) {
  const voices = settings?.settings?.tts?.kokoro || {};
  return language === "it" ? (voices.voice_it || "if_sara") : (voices.voice_en || "af_heart");
}

function speechVoiceForProvider(provider, language, preferred = "") {
  if (provider === "kokoro") {
    const allowed = language === "it" ? ["if_sara", "im_nicola"] : ["af_heart", "am_michael"];
    return allowed.includes(preferred) ? preferred : kokoroVoiceFor(language);
  }
  if (provider === "edge-tts") return VOICE_PROFILES[language]?.some(([value]) => value === preferred) ? preferred : (VOICE_PROFILES[language]?.[0]?.[0] || "it-IT-GiuseppeMultilingualNeural");
  return preferred || "";
}

function workflowSpeechProvider() {
  if (offlineMode) return "kokoro";
  const selected = document.querySelector("#complete-provider")?.value;
  if (["edge-tts", "kokoro"].includes(selected)) return selected;
  const configured = settings?.settings?.tts?.default_provider;
  return ["edge-tts", "kokoro"].includes(configured) ? configured : "edge-tts";
}

function renderOfflineMode() {
  const savedProvider = settings?.settings?.tts?.default_provider || "edge-tts";
  const targetProvider = offlineMode ? "kokoro" : savedProvider;
  const toggle = document.querySelector("#offline-mode-toggle");
  const state = document.querySelector("#offline-mode-state");
  const basic = document.querySelector("#default-audio-provider");
  const complete = document.querySelector("#complete-provider");
  const tts = document.querySelector("#tts-provider");
  if (toggle) {
    toggle.classList.toggle("active", offlineMode);
    toggle.setAttribute("aria-pressed", String(offlineMode));
    toggle.setAttribute("title", offlineMode ? t("offlineModeStatus") : t("onlineMode"));
    toggle.disabled = modeSaving;
  }
  if (state) state.textContent = offlineMode ? t("offlineOn") : t("offlineOff");
  if (basic) { basic.value = offlineMode ? "kokoro" : "edge-tts"; basic.disabled = modeSaving; }
  if (complete) { complete.value = ["kokoro", "edge-tts"].includes(targetProvider) ? targetProvider : "edge-tts"; complete.disabled = modeSaving; }
  if (tts) {
    tts.value = targetProvider;
    tts.disabled = modeSaving;
  }
  const mode = document.querySelector("#basic-audio-mode");
  if (mode) mode.textContent = offlineMode ? t("offlineModeStatus") : t("onlineMode");
  renderProviderVoiceSelects();
  renderWorkflowVoices();
  updateTtsAvailability();
  updateCompleteAvailability();
}

async function setOfflineMode(enabled) {
  if (modeSaving) return;
  modeSaving = true;
  renderOfflineMode();
  setStatus(document.querySelector("#mode-status"), language === "it" ? "Cambio modalità…" : "Changing mode…");
  try {
    const provider = enabled ? "kokoro" : "edge-tts";
    const response = await api("/api/settings", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({tts: {default_provider: provider, offline_mode: Boolean(enabled)}}),
    });
    settings = settings ? {...settings, settings: response.settings} : {settings: response.settings};
    offlineMode = Boolean(response.settings.tts.offline_mode);
    document.querySelector("#default-tts-provider").value = provider;
    renderOfflineMode();
    setStatus(document.querySelector("#mode-status"), offlineMode ? t("offlineModeStatus") : t("onlineMode"));
    void renderStatus().catch(() => {});
  } catch (error) {
    setStatus(document.querySelector("#mode-status"), `${t("failed")} ${error.message}`, true);
  } finally {
    modeSaving = false;
    renderOfflineMode();
  }
}

function renderWorkflowVoices() {
  for (const [voiceId, languageId] of [["#complete-voice", "#complete-language"], ["#voice", "#speech-language"]]) {
    const select = document.querySelector(voiceId);
    if (!select || !document.querySelector(languageId)) continue;
    const speechLanguage = document.querySelector(languageId).value;
    const preferred = select.value;
    if (workflowSpeechProvider() === "kokoro") {
      const entries = speechLanguage === "it" ? [["if_sara", "Sara"], ["im_nicola", "Nicola"]] : [["af_heart", "Heart"], ["am_michael", "Michael"]];
      select.replaceChildren(...entries.map(([value, label]) => new Option(label, value)));
      select.value = speechVoiceForProvider("kokoro", speechLanguage, preferred);
    } else fillVoiceSelect(select, speechLanguage, preferred);
  }
}

function setStatus(node, message, error = false) {
  if (!node) return;
  node.textContent = message;
  node.classList.toggle("error", error);
}

function selectedTtsReady(provider) {
  return Boolean(providerStatus.tts?.[provider]?.ready);
}

function updateTtsAvailability() {
  const provider = document.querySelector("#tts-provider")?.value || "edge-tts";
  const ready = selectedTtsReady(provider);
  const button = document.querySelector("#tts-form button[type=submit]");
  if (button) button.disabled = !ready || modeSaving || busyForms.has("tts");
  const hint = document.querySelector("#tts-status");
  if (hint && !ready) setStatus(hint, language === "it" ? "Questo motore non è pronto: controlla Impostazioni." : "This engine is not ready: check Settings.", true);
}

function updateCompleteAvailability() {
  const provider = workflowSpeechProvider();
  const button = document.querySelector("#complete-form button[type=submit]");
  if (button) button.disabled = !ocrReady || !selectedTtsReady(provider) || modeSaving || busyForms.has("complete");
}

async function loadSettings() {
  try {
    const payload = await api("/api/settings");
    settings = payload;
    const value = payload.settings;
    const ai = value.ai;
    document.querySelector("#ai-provider").value = ai.provider;
    document.querySelector("#ai-base-url").value = ai.base_url || "";
    document.querySelector("#ai-model").value = ai.model || "";
    const localModel = document.querySelector("#local-text-model");
    if (localModel) localModel.value = ai.local_model || "lfm";
    renderAiKeyStatus();
    renderAiProviderMenu();
    document.querySelector("#default-tts-provider").value = value.tts.default_provider;
    offlineMode = Boolean(value.tts.offline_mode);
    document.querySelector("#default-audio-provider").value = offlineMode ? "kokoro" : "edge-tts";
    if (["edge-tts", "kokoro", "voxtral", "fish", "fish-local", "elevenlabs"].includes(value.tts.default_provider)) document.querySelector("#tts-provider").value = value.tts.default_provider;
    document.querySelector("#mistral-voice-id").value = value.tts.mistral.voice_id || "";
    document.querySelector("#fish-voice-id").value = value.tts.fish.voice_id || "";
    document.querySelector("#eleven-voice-id").value = value.tts.elevenlabs.voice_id || "";
    document.querySelector("#kokoro-voice-it").value = value.tts.kokoro.voice_it || "if_sara";
    document.querySelector("#kokoro-voice-en").value = value.tts.kokoro.voice_en || "af_heart";
    for (const provider of ["mistral", "fish", "elevenlabs"]) {
      document.querySelector(`#${provider}-status`).textContent = value.tts[provider].configured ? t("keyConfigured") : t("keyMissing");
    }
    renderOfflineMode();
    renderClones(value.clones || []);
  } catch (error) {
    setStatus(document.querySelector("#ai-settings-status"), `${t("failed")} ${error.message}`, true);
  }
}

async function saveLocalModel(event) {
  event.preventDefault();
  const selected = document.querySelector("#local-text-model").value;
  const status = document.querySelector("#local-model-status");
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const response = await api("/api/settings", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ai: {local_model: selected}}),
    });
    settings = settings ? {...settings, settings: response.settings} : {settings: response.settings};
    await renderStatus();
    setStatus(status, selected === "gemma4" ? "Gemma 4 selezionata." : "LFM2.5 selezionato.");
  } catch (error) {
    setStatus(status, `${t("failed")} ${error.message}`, true);
  } finally { button.disabled = false; }
}

async function installGemma() {
  const button = document.querySelector("#install-gemma");
  const status = document.querySelector("#local-model-status");
  button.disabled = true;
  try {
    const response = await api("/api/local-models/gemma4", {method: "POST"});
    setStatus(status, response.message);
    const poll = async () => {
      const state = await api("/api/local-models");
      setStatus(status, state.message);
      if (state.status === "running") window.setTimeout(poll, 2000);
      else { button.disabled = false; await renderStatus(); }
    };
    await poll();
  } catch (error) {
    setStatus(status, `${t("failed")} ${error.message}`, true);
    button.disabled = false;
  }
}

async function installFishLocal() {
  const button = document.querySelector("#install-fish-local");
  const status = document.querySelector("#local-model-status");
  button.disabled = true;
  try {
    const response = await api("/api/local-models/fish-local", {method: "POST"});
    setStatus(status, response.message);
    const poll = async () => {
      const state = await api("/api/local-models");
      setStatus(status, state.message);
      if (state.status === "running") window.setTimeout(poll, 2000);
      else { button.disabled = false; await renderStatus(); }
    };
    await poll();
  } catch (error) {
    setStatus(status, `${t("failed")} ${error.message}`, true);
    button.disabled = false;
  }
}

function renderClones(clones) {
  const container = document.querySelector("#clone-list");
  if (!container) return;
  container.replaceChildren();
  clones.forEach((clone) => {
    const item = document.createElement("p");
    item.className = "clone-item";
    item.textContent = `${clone.name} · ${clone.provider} · ${clone.voice_id}`;
    container.append(item);
  });
}

function renderAiKeyStatus() {
  const provider = document.querySelector("#ai-provider")?.value || "local";
  const configured = settings?.settings?.ai?.providers?.[provider]?.configured || provider === "local";
  const status = document.querySelector("#ai-key-status");
  if (status) status.textContent = configured && provider !== "local" ? t("keyConfigured") : t("keyMissing");
}

function renderAiProviderMenu() {
  const provider = document.querySelector("#ai-provider")?.value || "local";
  const providers = settings?.settings?.ai?.providers || {};
  document.querySelectorAll("[data-provider-card]").forEach((card) => {
    const selected = card.dataset.providerCard === provider;
    card.classList.toggle("selected", selected);
    const state = card.querySelector("[data-provider-state]");
    if (!state) return;
    const configured = card.dataset.providerCard === "local" || Boolean(providers[card.dataset.providerCard]?.configured);
    state.classList.toggle("ready", configured);
    state.textContent = configured ? t("configuredShort") : t("notConfiguredShort");
    state.title = state.textContent;
    state.setAttribute("aria-label", state.textContent);
  });
  const meta = AI_PROVIDER_META[provider] || AI_PROVIDER_META.local;
  const selectedName = document.querySelector("#selected-provider-name");
  const selectedDescription = document.querySelector("#selected-provider-description");
  if (selectedName) selectedName.textContent = meta.label;
  if (selectedDescription) selectedDescription.textContent = meta.description[language] || meta.description.en;
  updateAiConfigFields();
}

function aiKeyAvailable(provider = document.querySelector("#ai-provider")?.value || "local") {
  return provider === "local"
    || Boolean(document.querySelector("#ai-key")?.value.trim())
    || Boolean(settings?.settings?.ai?.providers?.[provider]?.configured);
}

function updateAiConfigFields() {
  const provider = document.querySelector("#ai-provider")?.value || "local";
  const baseUrl = document.querySelector("#ai-base-url");
  const model = document.querySelector("#ai-model");
  const browseButton = document.querySelector("#browse-models");
  const browseStatus = document.querySelector("#browse-models-status");
  const baseUrlIsFixed = provider !== "custom";
  const modelIsPreset = provider !== "custom";
  const keyAvailable = aiKeyAvailable(provider);
  if (baseUrl) {
    baseUrl.readOnly = baseUrlIsFixed;
    baseUrl.classList.toggle("readonly-field", baseUrlIsFixed);
  }
  if (model) {
    model.readOnly = modelIsPreset;
    model.classList.toggle("readonly-field", modelIsPreset);
  }
  if (browseButton) {
    browseButton.disabled = !keyAvailable;
    browseButton.title = keyAvailable ? "" : t("modelsNeedKey");
  }
  if (browseStatus && !keyAvailable && !browseStatus.textContent) {
    browseStatus.textContent = t("modelsNeedKey");
  } else if (browseStatus && keyAvailable && browseStatus.textContent === t("modelsNeedKey")) {
    browseStatus.textContent = "";
  }
}

function selectAiProvider(provider) {
  const select = document.querySelector("#ai-provider");
  if (!select || !AI_PROVIDER_META[provider]) return;
  select.value = provider;
  select.dispatchEvent(new Event("change"));
}

function showHelp(key) {
  const keys = HELP_COPY_KEYS[key];
  const dialog = document.querySelector("#help-dialog");
  if (!keys || !dialog) return;
  document.querySelector("#help-dialog-title").textContent = t(keys[0]);
  document.querySelector("#help-dialog-body").textContent = t(keys[1]);
  if (typeof dialog.showModal === "function") dialog.showModal();
  else window.alert(`${t(keys[0])}\n\n${t(keys[1])}`);
}

function focusGuide(targetId) {
  const target = document.getElementById(targetId);
  if (!target) return;
  target.tabIndex = -1;
  target.scrollIntoView({behavior: "smooth", block: "start"});
  target.focus({preventScroll: true});
  target.classList.add("guide-focus");
  window.setTimeout(() => target.classList.remove("guide-focus"), 1600);
}

function renderModelList() {
  const container = document.querySelector("#model-list");
  if (!container) return;
  const query = document.querySelector("#model-search")?.value.trim().toLowerCase() || "";
  const filtered = browsedModels.filter((model) => model.toLowerCase().includes(query));
  if (!filtered.length) {
    const empty = document.createElement("p");
    empty.className = "empty-models";
    empty.textContent = t("noModels");
    container.replaceChildren(empty);
    return;
  }
  container.replaceChildren(...filtered.map((model, index) => {
    const option = document.createElement("button");
    option.type = "button";
    option.className = `model-option${model === selectedBrowseModel ? " selected" : ""}`;
    option.setAttribute("role", "option");
    option.setAttribute("aria-selected", String(model === selectedBrowseModel));
    option.setAttribute("aria-posinset", String(index + 1));
    option.setAttribute("aria-setsize", String(filtered.length));
    option.dataset.modelOption = model;
    option.textContent = model;
    option.addEventListener("click", () => {
      selectedBrowseModel = model;
      renderModelList();
      [...container.querySelectorAll("[data-model-option]")].find((item) => item.dataset.modelOption === model)?.focus();
    });
    option.addEventListener("keydown", (event) => {
      const options = [...container.querySelectorAll("[data-model-option]")];
      const current = options.indexOf(option);
      if (current < 0) return;
      let next = current;
      if (event.key === "ArrowDown") next = Math.min(options.length - 1, current + 1);
      else if (event.key === "ArrowUp") next = Math.max(0, current - 1);
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = options.length - 1;
      else return;
      event.preventDefault();
      options[next]?.focus();
    });
    return option;
  }));
}

async function browseModels() {
  const provider = document.querySelector("#ai-provider")?.value || "local";
  const dialog = document.querySelector("#model-dialog");
  const status = document.querySelector("#model-dialog-status");
  const key = document.querySelector("#ai-key")?.value.trim() || "";
  selectedBrowseModel = document.querySelector("#ai-model")?.value || "";
  document.querySelector("#model-dialog-provider").textContent = AI_PROVIDER_META[provider]?.label || provider;
  document.querySelector("#model-search").value = "";
  setStatus(status, t("loadingModels"));
  document.querySelector("#model-list").replaceChildren();
  if (typeof dialog.showModal === "function") dialog.showModal();
  try {
    const payload = await api("/api/provider-models", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({provider, api_key: key, base_url: document.querySelector("#ai-base-url")?.value || ""}),
    });
    browsedModels = Array.isArray(payload.models) ? payload.models : [];
    renderModelList();
    setStatus(status, t("modelsLoaded").replace("{count}", String(browsedModels.length)));
  } catch (error) {
    browsedModels = [];
    renderModelList();
    setStatus(status, t("modelsLoadFailed"), true);
  }
}

function useSelectedModel() {
  if (!selectedBrowseModel) return;
  document.querySelector("#ai-model").value = selectedBrowseModel;
  setStatus(document.querySelector("#browse-models-status"), t("modelSelected"));
  document.querySelector("#model-dialog").close();
}

function renderLanguage() {
  document.documentElement.lang = language;
  document.querySelector("#language-select").value = language;
  document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((node) => { node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel)); });
  if (product) document.querySelector("#product-description").textContent = product[`description_${language}`];
  fillVoiceSelect(document.querySelector("#complete-voice"), document.querySelector("#complete-language").value);
  fillVoiceSelect(document.querySelector("#tts-voice"), document.querySelector("#tts-language").value);
  fillVoiceSelect(document.querySelector("#voice"), document.querySelector("#speech-language").value);
  renderOfflineMode();
  renderProviderVoiceSelects();
  renderAiProviderMenu();
  if (documentValue) renderDocument();
  renderJobs();
}

async function renderStatus() {
  const status = await api("/api/status");
  ocrReady = status.ocr.ready;
  speechReady = status.speech.ready;
  reflowReady = status.reflow.ready;
  providerStatus = status.providers || {tts: {}, ai: {}};
  const serviceName = document.querySelector("#speech-service-name");
  if (serviceName) serviceName.textContent = status.speech.engine || "Edge-TTS";
  for (const name of ["ocr", "speech", "reflow"]) {
    const ready = status[name].ready;
    document.querySelector(`#${name}-dot`).classList.toggle("ready", ready);
    document.querySelector(`#${name}-status`).textContent = t(ready ? "ready" : "unavailable");
  }
  updateCompleteAvailability();
  document.querySelector("#ocr-form button[type=submit]").disabled = !ocrReady;
  const organizeProvider = document.querySelector("#organize-provider")?.value || "local";
  document.querySelector("#organize-form button[type=submit]").disabled = organizeProvider === "local" ? !reflowReady : !providerStatus.ai?.configured_by_provider?.[organizeProvider]?.configured;
  document.querySelector("#tts-form button[type=submit]").disabled = !speechReady;
  document.querySelector("#create-speech").disabled = !speechReady;
  document.querySelector("#create-text-speech").disabled = !speechReady;
  document.querySelector("#reflow-document").disabled = !reflowReady;
  document.querySelector("#reflow-text").disabled = !reflowReady;
  updateTtsAvailability();
}

function showView(view, updateHash = true) {
  const allowed = ["complete", "ocr", "organize", "tts", "history", "settings"];
  activeView = allowed.includes(view) ? view : "complete";
  document.querySelectorAll(".view").forEach((section) => {
    const active = section.id === `view-${activeView}`;
    section.hidden = !active;
    section.classList.toggle("active-view", active);
  });
  document.querySelectorAll("[data-view-link]").forEach((link) => {
    const active = link.dataset.viewLink === activeView;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  if (activeView === "history") void renderJobs();
  if (activeView === "settings") void loadSettings();
  if (updateHash && window.location.hash !== `#${activeView}`) window.history.replaceState(null, "", `#${activeView}`);
  if (updateHash) {
    window.requestAnimationFrame(() => {
      const heading = document.querySelector(`#view-${activeView} h1`);
      if (!heading) return;
      heading.tabIndex = -1;
      heading.focus({preventScroll: true});
    });
  }
  schedulePersist();
}

function closeReview() {
  document.querySelector("#review-area").hidden = true;
  document.querySelector("#editor").hidden = true;
  document.querySelector("#text-editor").hidden = true;
  editingJob = null;
  documentValue = null;
  editingTextJob = null;
  textValue = null;
  schedulePersist();
}

function fileName(input, target) {
  input.addEventListener("change", () => {
    target.textContent = input.files[0]?.name || t("noFile");
  });
}

function jobType(job) {
  return t("jobTypes")[job.engine] || job.engine;
}

function jobMessage(job) {
  if (job.status === "failed") {
    const errorCopy = {
      ocr_failed: "ocrFailed",
      speech_failed: "speechFailed",
      organization_failed: "organizationFailed",
      text_failed: "textFailed",
      processing_failed: "jobFailed",
    };
    return t(errorCopy[job.error] || "jobFailed");
  }
  if (["queued", "running", "uploading"].includes(job.status)) return job.message || t("jobRunning");
  return job.message || t("jobCompleted");
}

function humanSummary(job) {
  const summary = job.summary || {};
  const values = [];
  if (summary.pages) values.push(`${summary.pages} ${language === "it" ? "pagine" : "pages"}`);
  if (summary.characters) values.push(`${summary.characters} ${language === "it" ? "caratteri" : "characters"}`);
  if (summary.device) values.push(summary.device === "auto" ? "auto" : summary.device);
  if (summary.reasoning === "off") values.push(language === "it" ? "ragionamento disattivato" : "reasoning off");
  if (summary.fallback_chunks) values.push(`${summary.fallback_chunks} fallback`);
  if (summary.provider) values.push(summary.provider);
  if (summary.fallback_from) values.push(language === "it" ? "ripiego offline automatico" : "automatic offline backup");
  return values;
}

function addArtifactLinks(container, job) {
  for (const artifact of (job.artifacts || []).filter((name) => !name.startsWith("pages/") && name !== "document.json" && name !== "speech.mp3" && name !== "reading.txt")) {
    const link = document.createElement("a");
    link.href = artifactUrl(job.id, artifact);
    link.textContent = `${t("download")}: ${artifact}`;
    link.className = "button-link secondary";
    container.append(link);
  }
}

function jobCard(job) {
  const card = document.createElement("article");
  card.className = "job";
  const head = document.createElement("div");
  head.className = "job-head";
  const titleWrap = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = job.input_name;
  const type = document.createElement("small");
  type.textContent = jobType(job);
  titleWrap.append(title, type);
  const badge = document.createElement("span");
  badge.className = `badge ${job.status}`;
  badge.textContent = COPY[language].statuses[job.status] || job.status;
  head.append(titleWrap, badge);
  card.append(head);
  const message = document.createElement("p");
  message.className = "job-message";
  message.textContent = jobMessage(job);
  card.append(message);
  const summaryValues = humanSummary(job);
  if (summaryValues.length) {
    const summary = document.createElement("div");
    summary.className = "summary";
    summaryValues.forEach((value) => { const item = document.createElement("span"); item.textContent = value; summary.append(item); });
    card.append(summary);
  }
  const actions = document.createElement("div");
  actions.className = "job-actions";
  if (job.status === "completed" && job.engine === "accessible-document") {
    const review = document.createElement("button");
    review.type = "button";
    review.textContent = t("reviewTitle");
    review.addEventListener("click", () => void openDocument(job));
    actions.append(review);
  }
  if (job.status === "completed" && ["plain-text", "lfm-reflow"].includes(job.engine)) {
    const openText = document.createElement("button");
    openText.type = "button";
    openText.textContent = t("openResult");
    openText.addEventListener("click", () => void openTextJob(job));
    actions.append(openText);
    const downloadText = document.createElement("a");
    downloadText.href = artifactUrl(job.id, "reading.txt");
    downloadText.download = "testo-per-la-voce.txt";
    downloadText.className = "button-link secondary";
    downloadText.textContent = t("downloadText");
    actions.append(downloadText);
  }
  if (job.status === "completed" && job.engine === "edge-tts") {
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.preload = "metadata";
    audio.src = artifactUrl(job.id, "speech.mp3");
    audio.setAttribute("aria-label", t("play"));
    card.append(audio);
    const download = document.createElement("a");
    download.href = artifactUrl(job.id, "speech.mp3");
    download.download = "audio.mp3";
    download.className = "button-link secondary";
    download.textContent = t("downloadAudio");
    actions.append(download);
  }
  addArtifactLinks(actions, job);
  if (["completed", "failed"].includes(job.status)) {
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "secondary danger";
    remove.textContent = t("delete");
    remove.addEventListener("click", async () => {
      if (!window.confirm(t("confirmDelete"))) return;
      try { await api(`/api/jobs/${encodeURIComponent(job.id)}`, {method: "DELETE"}); await renderJobs(); }
      catch (error) { window.alert(`${t("failed")} ${error.message}`); }
    });
    actions.append(remove);
  }
  if (actions.childNodes.length) card.append(actions);
  return card;
}

async function renderJobs() {
  const container = document.querySelector("#jobs");
  if (!container) return;
  try {
    const jobs = await api("/api/jobs");
    const cards = jobs.length
      ? jobs.map(jobCard)
      : [Object.assign(document.createElement("p"), {className: "empty-history", textContent: t("empty")})];
    container.replaceChildren(...cards);
    const active = jobs.some((job) => ["uploading", "queued", "running"].includes(job.status));
    document.querySelector("#clear-history").disabled = !jobs.some((job) => ["completed", "failed"].includes(job.status));
    window.clearTimeout(pollTimer);
    if (active) pollTimer = window.setTimeout(() => void renderJobs(), 1500);
  } catch (error) {
    container.textContent = `${t("failed")} ${error.message}`;
  }
}

async function waitForJob(jobId, update = () => {}) {
  for (let attempt = 0; attempt < 36000; attempt += 1) {
    const job = await api(`/api/jobs/${encodeURIComponent(jobId)}`);
    update(job);
    if (job.status === "completed") return job;
    if (job.status === "failed") {
      const failure = new Error(job.error || t("jobFailed"));
      failure.jobFailed = true;
      throw failure;
    }
    await sleep(1200);
  }
  throw new Error(language === "it" ? "Il lavoro sta impiegando troppo tempo." : "The job is taking too long.");
}

async function submitDocument(file, options) {
  const engine = engines.find((item) => item.user_upload);
  if (!engine) throw new Error(language === "it" ? "Motore OCR non disponibile." : "OCR engine unavailable.");
  const data = new FormData();
  data.append("engine", engine.id);
  data.append("file", file);
  data.append("options", JSON.stringify(options));
  return api("/api/jobs", {method: "POST", body: data});
}

async function submitText(title, text, options) {
  return api("/api/text", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({title, text, options}),
  });
}

async function queueReflow(jobId, device = "auto", provider = "local") {
  if (provider === "local" && !reflowReady) throw new Error(language === "it" ? "LFM non è disponibile." : "LFM is unavailable.");
  if (provider !== "local" && !providerStatus.ai?.configured_by_provider?.[provider]?.configured) throw new Error(language === "it" ? "Configura prima una chiave API in Impostazioni." : "Configure an API key in Settings first.");
  return api(`/api/jobs/${encodeURIComponent(jobId)}/reflow`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({device, provider})});
}

async function queueSpeech(jobId, voice, speed, speechLanguage, provider = workflowSpeechProvider()) {
  const effectiveProvider = offlineMode ? "kokoro" : provider;
  const effectiveVoice = speechVoiceForProvider(effectiveProvider, speechLanguage, voice);
  const available = providerStatus.tts?.[effectiveProvider]?.ready ?? speechReady;
  if (!available) throw new Error(language === "it" ? "Questo motore vocale non è disponibile. Controlla Impostazioni." : "This voice engine is unavailable. Check Settings.");
  return api(`/api/jobs/${encodeURIComponent(jobId)}/speech`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({voice: effectiveVoice, speed, language: speechLanguage, provider: effectiveProvider})});
}

function setFullStage(stage, message = "") {
  const steps = ["ocr", "speech"];
  steps.forEach((name, index) => {
    const step = document.querySelector(`#full-step-${name}`);
    const progress = document.querySelector(`#progress-${name}`);
    if (!step || !progress) return;
    step.classList.toggle("done", index < stage);
    step.classList.toggle("active", index === stage && stage < 2);
    progress.classList.toggle("done", index < stage || stage >= 2);
    progress.classList.toggle("active", index === stage && stage < 2);
  });
  document.querySelector("#complete-percent").textContent = stage >= 2 ? "2/2" : `${stage + 1}/2`;
  const progressBar = document.querySelector("#complete-progress-bar");
  progressBar.style.width = `${Math.max(8, Math.min(100, stage >= 2 ? 100 : ((stage + 1) / 2) * 100))}%`;
  progressBar.classList.toggle("working", stage < 2);
  document.querySelector("#complete-progress-message").textContent = message;
}

function showAudio(resultId, audioId, downloadId) {
  const audio = document.querySelector(`#${audioId}`);
  const source = artifactUrl(resultId, "speech.mp3");
  const slot = audioId.startsWith("complete") ? "complete" : "tts";
  audioProgress[slot] = {jobId: resultId, time: 0};
  audio.dataset.jobId = resultId;
  audio.src = source;
  document.querySelector(`#${downloadId}`).href = source;
  document.querySelector(`#${audioId.replace("audio", "result")}`).hidden = false;
  audio.load();
}

function restoreAudioState() {
  [["complete", "#complete-audio", "#complete-download", "#complete-result"], ["tts", "#tts-audio", "#tts-download", "#tts-result"]].forEach(([slot, audioSelector, downloadSelector, resultSelector]) => {
    const saved = audioProgress[slot];
    const audio = document.querySelector(audioSelector);
    if (!saved?.jobId || !audio) return;
    const source = artifactUrl(saved.jobId, "speech.mp3");
    audio.dataset.jobId = saved.jobId;
    audio.src = source;
    document.querySelector(downloadSelector).href = source;
    document.querySelector(resultSelector).hidden = false;
    audio.addEventListener("loadedmetadata", () => {
      const position = Number(saved.time);
      if (Number.isFinite(position) && position > 0 && position < audio.duration) audio.currentTime = position;
    }, {once: true});
    audio.load();
  });
}

function updateAudioProgress(audio, slot) {
  if (!audio.dataset.jobId) return;
  audioProgress[slot] = {jobId: audio.dataset.jobId, time: Math.max(0, Number(audio.currentTime) || 0)};
  const now = Date.now();
  if (now - lastAudioCheckpoint >= 2000) {
    lastAudioCheckpoint = now;
    persistSession();
  }
}

async function startFullWorkflow(event) {
  event.preventDefault();
  if (modeSaving || busyForms.has("complete")) return;
  const button = event.currentTarget.querySelector("button[type=submit]");
  const file = document.querySelector("#complete-file").files[0];
  const status = document.querySelector("#complete-status");
  if (!file) return;
  busyForms.add("complete");
  button.disabled = true;
  document.querySelector("#complete-progress").hidden = false;
  document.querySelector("#complete-result").hidden = true;
  setFullStage(0, t("completeStart"));
  try {
    const speechLanguage = document.querySelector("#complete-language").value;
    const provider = workflowSpeechProvider();
    const voice = speechVoiceForProvider(provider, speechLanguage, document.querySelector("#complete-voice").value);
    const speed = Number(document.querySelector("#complete-speed").value);
    const ocr = await submitDocument(file, {auto_speech: false, document_language: speechLanguage === "it" ? "it" : "en", speech_language: speechLanguage, speech_provider: provider, voice, speed});
    setWorkflow("complete", {phase: "ocr", ocrJobId: ocr.id, speechJobId: "", speechLanguage, provider, voice, speed});
    const completedOcr = await waitForJob(ocr.id, (job) => {
      const message = job.status === "queued" ? t("ocrQueued") : job.status === "running" ? t("ocrRunning") : jobMessage(job);
      setStatus(status, message, job.status === "failed");
      setFullStage(0, message);
    });
    lastOcrJob = completedOcr;
    setFullStage(1, t("completeOcr"));
    const speech = await queueSpeech(completedOcr.id, voice, speed, speechLanguage, provider);
    setWorkflow("complete", {phase: "speech", ocrJobId: ocr.id, speechJobId: speech.id, speechLanguage, provider, voice, speed});
    const completedSpeech = await waitForJob(speech.id, (job) => {
      const message = job.status === "queued" ? t("speechQueued") : job.status === "running" ? t("speechRunning") : jobMessage(job);
      setStatus(status, message, job.status === "failed");
      setFullStage(1, message);
    });
    const doneMessage = completedSpeech.summary?.fallback_from ? t("completeDoneFallback") : t("completeDone");
    setFullStage(2, doneMessage);
    showAudio(completedSpeech.id, "complete-audio", "complete-download");
    setStatus(status, doneMessage);
    clearWorkflow("complete");
    await renderJobs();
  } catch (error) {
    setStatus(status, `${t("failed")} ${error.message}`, true);
  } finally {
    busyForms.delete("complete");
    updateCompleteAvailability();
  }
}

async function startOcr(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  const file = document.querySelector("#ocr-file").files[0];
  const status = document.querySelector("#ocr-status-message");
  if (!file) return;
  button.disabled = true;
  try {
    const job = await submitDocument(file, {auto_speech: false, document_language: "it", speech_language: "it", voice: "it-IT-GiuseppeMultilingualNeural", speed: 1});
    setWorkflow("ocr", {jobId: job.id});
    setStatus(status, t("ocrQueued"));
    lastOcrJob = await waitForJob(job.id, (value) => {
      const message = value.status === "queued" ? t("ocrQueued") : value.status === "running" ? t("ocrRunning") : jobMessage(value);
      setStatus(status, message, value.status === "failed");
    });
    document.querySelector("#ocr-result").hidden = false;
    setStatus(status, t("ocrReady"));
    clearWorkflow("ocr");
    await renderJobs();
  } catch (error) { setStatus(status, `${t("failed")} ${error.message}`, true); }
  finally { button.disabled = false; }
}

async function textFromForm(textareaId, fileId) {
  const pasted = document.querySelector(textareaId).value;
  const file = document.querySelector(fileId).files[0];
  if (file) return {title: file.name, text: await file.text()};
  return {title: "testo.txt", text: pasted};
}

async function startOrganize(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  const status = document.querySelector("#organize-status");
  const input = await textFromForm("#organize-input", "#organize-file");
  if (!input.text.trim()) { setStatus(status, `${t("failed")} ${t("textRequired")}`, true); return; }
  button.disabled = true;
  try {
    const plain = await submitText(document.querySelector("#organize-title-input").value || input.title, input.text, {auto_speech: false, preserve_text: true, document_language: "it", speech_language: "it", voice: "it-IT-GiuseppeMultilingualNeural", speed: 1});
    const provider = document.querySelector("#organize-provider").value;
    const device = document.querySelector("#organize-device").value;
    setWorkflow("organize", {phase: "plain", plainJobId: plain.id, reflowJobId: "", provider, device});
    setStatus(status, t("organizeQueued"));
    const completedPlain = await waitForJob(plain.id, () => {});
    const reflow = await queueReflow(completedPlain.id, device, provider);
    setWorkflow("organize", {phase: "reflow", plainJobId: plain.id, reflowJobId: reflow.id, provider, device});
    lastOrganizeJob = await waitForJob(reflow.id, () => {});
    document.querySelector("#organize-result").hidden = false;
    setStatus(status, t("organizeReady"));
    clearWorkflow("organize");
    await renderJobs();
  } catch (error) { setStatus(status, `${t("failed")} ${error.message}`, true); }
  finally { button.disabled = false; }
}

async function startTts(event) {
  event.preventDefault();
  if (modeSaving || busyForms.has("tts")) return;
  const button = event.currentTarget.querySelector("button[type=submit]");
  const status = document.querySelector("#tts-status");
  const input = await textFromForm("#tts-input", "#tts-file");
  if (!input.text.trim()) { setStatus(status, `${t("failed")} ${t("textRequired")}`, true); return; }
  busyForms.add("tts");
  button.disabled = true;
  try {
    const speechLanguage = document.querySelector("#tts-language").value;
    const provider = offlineMode ? "kokoro" : document.querySelector("#tts-provider").value;
    const voice = speechVoiceForProvider(provider, speechLanguage, document.querySelector("#tts-voice").value);
    const speed = Number(document.querySelector("#tts-speed").value);
    const plain = await submitText(document.querySelector("#tts-title-input").value || input.title, input.text, {auto_speech: false, preserve_text: true, document_language: speechLanguage === "it" ? "it" : "en", speech_language: speechLanguage, speech_provider: provider, voice, speed});
    setWorkflow("tts", {phase: "plain", plainJobId: plain.id, speechJobId: "", voice, speed, speechLanguage, provider});
    setStatus(status, t("ttsQueued"));
    const completedPlain = await waitForJob(plain.id, () => {});
    const speech = await queueSpeech(completedPlain.id, voice, speed, speechLanguage, provider);
    setWorkflow("tts", {phase: "speech", plainJobId: plain.id, speechJobId: speech.id, voice, speed, speechLanguage, provider});
    const completedSpeech = await waitForJob(speech.id, (job) => {
      const message = job.status === "queued" ? t("speechQueued") : job.status === "running" ? t("speechRunning") : jobMessage(job);
      setStatus(status, message, job.status === "failed");
    });
    showAudio(completedSpeech.id, "tts-audio", "tts-download");
    setStatus(status, completedSpeech.summary?.fallback_from ? t("completeDoneFallback") : t("audioReady"));
    clearWorkflow("tts");
    await renderJobs();
  } catch (error) { setStatus(status, `${t("failed")} ${error.message}`, true); }
  finally { busyForms.delete("tts"); updateTtsAvailability(); }
}

async function resumeFullWorkflow(workflow) {
  const status = document.querySelector("#complete-status");
  const button = document.querySelector("#complete-form button[type=submit]");
  showView("complete");
  button.disabled = true;
  document.querySelector("#complete-progress").hidden = false;
  document.querySelector("#complete-result").hidden = true;
  setFullStage(workflow.phase === "speech" ? 1 : 0, t("resumeJob"));
  try {
    const completedOcr = await waitForJob(workflow.ocrJobId, () => {});
    lastOcrJob = completedOcr;
    let speechJobId = workflow.speechJobId;
    if (!speechJobId) {
      const provider = workflow.provider || workflowSpeechProvider();
      const voice = speechVoiceForProvider(provider, workflow.speechLanguage, workflow.voice);
      const speech = await queueSpeech(completedOcr.id, voice, workflow.speed, workflow.speechLanguage, provider);
      speechJobId = speech.id;
      setWorkflow("complete", {...workflow, phase: "speech", speechJobId, provider, voice});
    }
    const completedSpeech = await waitForJob(speechJobId, () => {});
    setFullStage(2, t("completeDone"));
    showAudio(completedSpeech.id, "complete-audio", "complete-download");
    setStatus(status, t("completeDone"));
    clearWorkflow("complete");
    await renderJobs();
  } catch (error) {
    setStatus(status, `${t("failed")} ${error.message}`, true);
    if (error.jobFailed) clearWorkflow("complete");
  } finally {
    button.disabled = false;
  }
}

async function resumeOcrWorkflow(workflow) {
  showView("ocr");
  const button = document.querySelector("#ocr-form button[type=submit]");
  button.disabled = true;
  try {
    lastOcrJob = await waitForJob(workflow.jobId, () => {});
    document.querySelector("#ocr-result").hidden = false;
    setStatus(document.querySelector("#ocr-status-message"), t("resumeJob"));
    clearWorkflow("ocr");
    await renderJobs();
  } catch (error) {
    setStatus(document.querySelector("#ocr-status-message"), `${t("failed")} ${error.message}`, true);
    if (error.jobFailed) clearWorkflow("ocr");
  } finally {
    button.disabled = false;
  }
}

async function resumeOrganizeWorkflow(workflow) {
  showView("organize");
  const status = document.querySelector("#organize-status");
  const button = document.querySelector("#organize-form button[type=submit]");
  button.disabled = true;
  try {
    const completedPlain = await waitForJob(workflow.plainJobId, () => {});
    let reflowJobId = workflow.reflowJobId;
    if (!reflowJobId) {
      const reflow = await queueReflow(completedPlain.id, workflow.device, workflow.provider);
      reflowJobId = reflow.id;
      setWorkflow("organize", {...workflow, phase: "reflow", reflowJobId});
    }
    lastOrganizeJob = await waitForJob(reflowJobId, () => {});
    document.querySelector("#organize-result").hidden = false;
    setStatus(status, t("organizeReady"));
    clearWorkflow("organize");
    await renderJobs();
  } catch (error) {
    setStatus(status, `${t("failed")} ${error.message}`, true);
    if (error.jobFailed) clearWorkflow("organize");
  } finally {
    button.disabled = false;
  }
}

async function resumeTtsWorkflow(workflow) {
  showView("tts");
  const status = document.querySelector("#tts-status");
  const button = document.querySelector("#tts-form button[type=submit]");
  button.disabled = true;
  try {
    const completedPlain = await waitForJob(workflow.plainJobId, () => {});
    let speechJobId = workflow.speechJobId;
    if (!speechJobId) {
      const speech = await queueSpeech(completedPlain.id, workflow.voice, workflow.speed, workflow.speechLanguage, workflow.provider);
      speechJobId = speech.id;
      setWorkflow("tts", {...workflow, phase: "speech", speechJobId});
    }
    const completedSpeech = await waitForJob(speechJobId, () => {});
    showAudio(completedSpeech.id, "tts-audio", "tts-download");
    setStatus(status, t("audioReady"));
    clearWorkflow("tts");
    await renderJobs();
  } catch (error) {
    setStatus(status, `${t("failed")} ${error.message}`, true);
    if (error.jobFailed) clearWorkflow("tts");
  } finally {
    button.disabled = false;
  }
}

async function resumeActiveWorkflows() {
  const active = Object.entries(workflows).find(([, workflow]) => workflow && typeof workflow === "object");
  if (!active) return;
  showResumeBanner(t("resumeJob"));
  const [name, workflow] = active;
  if (name === "complete") return resumeFullWorkflow(workflow);
  if (name === "ocr") return resumeOcrWorkflow(workflow);
  if (name === "organize") return resumeOrganizeWorkflow(workflow);
  return resumeTtsWorkflow(workflow);
}

function roleOptions(selected) {
  const roles = language === "it" ? {heading1: "Titolo principale", heading2: "Titolo di sezione", heading3: "Sottotitolo", paragraph: "Paragrafo", list_item: "Elemento elenco", page_number: "Numero di pagina (non letto)", exclude: "Escludi dalla lettura"} : {heading1: "Main heading", heading2: "Section heading", heading3: "Subheading", paragraph: "Paragraph", list_item: "List item", page_number: "Page number (not read)", exclude: "Exclude from reading"};
  return Object.entries(roles).map(([role, label]) => { const option = document.createElement("option"); option.value = role; option.textContent = label; option.selected = role === selected; return option; });
}

function pageHasPossibleColumns(page) {
  const starts = page.blocks
    .map((block) => Number(block.bbox?.[0]))
    .filter((value) => Number.isFinite(value));
  if (starts.length < 4) return false;
  const spread = Math.max(...starts) - Math.min(...starts);
  const groups = new Set(starts.map((value) => Math.round(value / 80)));
  return spread >= 180 && groups.size >= 2;
}

function blockEditor(block, page, index) {
  const item = document.createElement("div");
  item.className = "block-editor";
  item.setAttribute("role", "group");
  item.setAttribute("aria-label", `${language === "it" ? "Blocco" : "Block"} ${index + 1}`);
  const meta = document.createElement("div");
  meta.className = "block-meta";
  const select = document.createElement("select");
  select.setAttribute("aria-label", t("blockRoleLabel").replace("{number}", String(index + 1)));
  select.replaceChildren(...roleOptions(block.role));
  select.addEventListener("change", () => { block.role = select.value; schedulePersist(); });
  const confidence = document.createElement("span");
  confidence.className = `confidence ${block.confidence < 0.82 ? "low-confidence" : ""}`;
  confidence.textContent = `${language === "it" ? "Confidenza" : "Confidence"}: ${Math.round(block.confidence * 100)}%`;
  const moveActions = document.createElement("span");
  moveActions.className = "block-move-actions";
  [[-1, "↑", "moveBlockUp"], [1, "↓", "moveBlockDown"]].forEach(([offset, symbol, labelKey]) => {
    const move = document.createElement("button");
    move.type = "button";
    move.className = "block-move";
    move.textContent = symbol;
    move.title = t(labelKey);
    move.setAttribute("aria-label", `${t(labelKey)}: ${block.id}`);
    move.dataset.blockId = block.id;
    move.dataset.moveOffset = String(offset);
    move.disabled = index + offset < 0 || index + offset >= page.blocks.length;
    move.addEventListener("click", () => {
      const target = index + offset;
      if (target < 0 || target >= page.blocks.length) return;
      [page.blocks[index], page.blocks[target]] = [page.blocks[target], page.blocks[index]];
      renderDocument();
      const replacement = [...document.querySelectorAll(".block-move")].find((button) => button.dataset.blockId === block.id && button.dataset.moveOffset === String(offset));
      replacement?.focus();
      const liveStatus = document.querySelector("#review-live-status");
      if (liveStatus) {
        liveStatus.textContent = t("blockMoved")
          .replace("{number}", block.id)
          .replace("{position}", String(target + 1));
      }
      schedulePersist();
    });
    moveActions.append(move);
  });
  meta.append(select, confidence, moveActions);
  const textarea = document.createElement("textarea");
  textarea.value = block.text;
  textarea.setAttribute("aria-label", t("blockTextLabel").replace("{number}", String(index + 1)));
  textarea.addEventListener("input", () => { block.text = textarea.value; schedulePersist(); });
  item.append(meta, textarea);
  return item;
}

function renderDocument() {
  if (!documentValue || !editingJob) return;
  document.querySelector("#document-title").value = documentValue.title;
  document.querySelector("#document-language").value = documentValue.language;
  const speechLanguage = document.querySelector("#speech-language");
  speechLanguage.value = documentValue.speech_language || (documentValue.language === "en" ? "en-us" : "it");
  fillVoiceSelect(document.querySelector("#voice"), speechLanguage.value);
  document.querySelector("#download-html").href = artifactUrl(editingJob.id, "accessible.html");
  document.querySelector("#download-text").href = artifactUrl(editingJob.id, "reading.txt");
  document.querySelector("#pages").replaceChildren(...documentValue.pages.map((page) => {
    const section = document.createElement("article"); section.className = "page-editor";
    const heading = document.createElement("h3"); heading.textContent = `${language === "it" ? "Pagina" : "Page"} ${page.number}`;
    const layout = document.createElement("div"); layout.className = "page-layout";
    const image = page.preview ? document.createElement("img") : document.createElement("div"); image.className = page.preview ? "page-preview" : "page-preview no-preview";
    if (page.preview) { image.loading = "lazy"; image.src = artifactUrl(editingJob.id, page.preview); image.alt = heading.textContent; } else image.textContent = language === "it" ? "Nessuna anteprima disponibile." : "No page preview available.";
    const blocks = document.createElement("div"); blocks.className = "blocks"; blocks.replaceChildren(...page.blocks.map((block, index) => blockEditor(block, page, index)));
    if (pageHasPossibleColumns(page)) {
      const warning = document.createElement("p");
      warning.className = "layout-warning";
      warning.setAttribute("role", "note");
      warning.textContent = t("columnWarning");
      section.append(warning);
    }
    layout.append(image, blocks); section.append(heading, layout); return section;
  }));
}

function renderTextEditor() {
  if (textValue) document.querySelector("#text-workspace").value = textValue.text;
}

async function openDocument(job) {
  try {
    editingJob = job; documentValue = await api(`/api/jobs/${encodeURIComponent(job.id)}/document`); renderDocument();
    document.querySelector("#review-area").hidden = false; document.querySelector("#editor").hidden = false; document.querySelector("#text-editor").hidden = true;
    document.querySelector("#review-area").scrollIntoView({behavior: "smooth", block: "start"}); document.querySelector("#document-title").focus();
    schedulePersist();
  } catch (error) { window.alert(`${t("failed")} ${error.message}`); }
}

async function openTextJob(job) {
  try {
    editingTextJob = job; textValue = await api(`/api/jobs/${encodeURIComponent(job.id)}/text`); renderTextEditor();
    document.querySelector("#review-area").hidden = false; document.querySelector("#text-editor").hidden = false; document.querySelector("#editor").hidden = true;
    document.querySelector("#review-area").scrollIntoView({behavior: "smooth", block: "start"}); document.querySelector("#text-workspace").focus();
    schedulePersist();
  } catch (error) { window.alert(`${t("failed")} ${error.message}`); }
}

async function saveDocument() {
  if (!editingJob || !documentValue) throw new Error("No document");
  documentValue.title = document.querySelector("#document-title").value;
  documentValue.language = document.querySelector("#document-language").value;
  documentValue.speech_language = document.querySelector("#speech-language").value;
  setStatus(document.querySelector("#save-status"), t("saving"));
  documentValue = await api(`/api/jobs/${encodeURIComponent(editingJob.id)}/document`, {method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify(documentValue)});
  setStatus(document.querySelector("#save-status"), t("saved"));
  schedulePersist();
  return documentValue;
}

async function saveText() {
  if (!editingTextJob || !textValue) throw new Error("No text");
  const text = document.querySelector("#text-workspace").value;
  textValue = await api(`/api/jobs/${encodeURIComponent(editingTextJob.id)}/text`, {method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify({text})});
  schedulePersist();
  return textValue;
}

function bindFileInputs() {
  fileName(document.querySelector("#complete-file"), document.querySelector("#complete-file-name"));
  fileName(document.querySelector("#ocr-file"), document.querySelector("#ocr-file-name"));
  ["#organize-file", "#tts-file"].forEach((selector) => document.querySelector(selector).addEventListener("change", (event) => { if (event.currentTarget.files.length) document.querySelector(selector === "#organize-file" ? "#organize-input" : "#tts-input").value = ""; schedulePersist(); }));
}

function bindRange(inputId, outputId) {
  const input = document.querySelector(inputId); const output = document.querySelector(outputId);
  const update = () => { output.textContent = `${Number(input.value).toFixed(2).replace(".", ",")}×`; };
  input.addEventListener("input", update); update();
}

async function saveAiSettings(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await api("/api/settings", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ai: {provider: document.querySelector("#ai-provider").value, base_url: document.querySelector("#ai-base-url").value, model: document.querySelector("#ai-model").value, api_key: document.querySelector("#ai-key").value}}),
    });
    document.querySelector("#ai-key").value = "";
    setStatus(document.querySelector("#ai-settings-status"), t("savedSettings"));
    await loadSettings();
    await renderStatus();
  } catch (error) { setStatus(document.querySelector("#ai-settings-status"), `${t("failed")} ${error.message}`, true); }
  finally { button.disabled = false; }
}

async function saveTtsSettings(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await api("/api/settings", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({tts: {
        default_provider: document.querySelector("#default-tts-provider").value,
        offline_mode: offlineMode,
        mistral: {api_key: document.querySelector("#mistral-key").value, voice_id: document.querySelector("#mistral-voice-id").value},
        fish: {api_key: document.querySelector("#fish-key").value, voice_id: document.querySelector("#fish-voice-id").value},
        elevenlabs: {api_key: document.querySelector("#eleven-key").value, voice_id: document.querySelector("#eleven-voice-id").value},
        kokoro: {voice_it: document.querySelector("#kokoro-voice-it").value, voice_en: document.querySelector("#kokoro-voice-en").value},
      }}),
    });
    ["#mistral-key", "#fish-key", "#eleven-key"].forEach((selector) => { document.querySelector(selector).value = ""; });
    setStatus(document.querySelector("#tts-settings-status"), t("savedSettings"));
    await loadSettings();
    await renderStatus();
  } catch (error) { setStatus(document.querySelector("#tts-settings-status"), `${t("failed")} ${error.message}`, true); }
  finally { button.disabled = false; }
}

async function createVoiceClone(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  const file = document.querySelector("#clone-file").files[0];
  const status = document.querySelector("#clone-status");
  if (!file) { setStatus(status, language === "it" ? "Scegli prima un campione audio." : "Choose an audio sample first.", true); return; }
  button.disabled = true;
  const data = new FormData();
  data.append("provider", document.querySelector("#clone-provider").value);
  data.append("name", document.querySelector("#clone-name").value || "Voce clonata");
  data.append("consent", document.querySelector("#clone-consent").checked ? "true" : "false");
  data.append("reference_text", document.querySelector("#clone-reference-text")?.value || "");
  data.append("file", file);
  try {
    await api("/api/voice-clones", {method: "POST", body: data});
    setStatus(status, t("cloneCreated"));
    document.querySelector("#clone-form").reset();
    await loadSettings();
    await renderStatus();
  } catch (error) { setStatus(status, `${t("failed")} ${error.message}`, true); }
  finally { button.disabled = false; }
}

async function initialize() {
  [product, engines] = await Promise.all([api("/api/product"), api("/api/engines")]);
  document.title = product.name;
  document.querySelector("#product-name").textContent = product.name;
  const hash = window.location.hash.slice(1);
  activeView = ["complete", "ocr", "organize", "tts", "history", "settings"].includes(hash) ? hash : "complete";
  document.querySelector("#complete-language").value = language === "en" ? "en-us" : "it";
  document.querySelector("#tts-language").value = language === "en" ? "en-us" : "it";
  document.querySelector("#speech-language").value = language === "en" ? "en-us" : "it";
  renderLanguage();
  showView(activeView, false);
  bindFileInputs();
  bindRange("#complete-speed", "#complete-speed-value");
  bindRange("#tts-speed", "#tts-speed-value");
  bindRange("#speed", "#speed-value");
  await loadSettings();
  await Promise.all([renderStatus(), renderJobs()]);
  await restoreSession();
}

document.querySelectorAll("[data-view-link]").forEach((link) => link.addEventListener("click", (event) => { event.preventDefault(); closeReview(); showView(link.dataset.viewLink); }));
window.addEventListener("hashchange", () => showView(window.location.hash.slice(1), false));
window.addEventListener("beforeunload", persistSession);
document.querySelector("#dismiss-resume").addEventListener("click", () => { document.querySelector("#resume-banner").hidden = true; });
document.querySelector("#language-select").addEventListener("change", (event) => { language = event.target.value; localStorage.setItem("accessibility-language", language); renderLanguage(); schedulePersist(); });
document.querySelector("#offline-mode-toggle").addEventListener("click", () => void setOfflineMode(!offlineMode));
document.querySelector("#default-audio-provider").addEventListener("change", (event) => void setOfflineMode(event.target.value === "kokoro"));
document.querySelector("#complete-form").addEventListener("submit", (event) => void startFullWorkflow(event));
document.querySelector("#ocr-form").addEventListener("submit", (event) => void startOcr(event));
document.querySelector("#organize-form").addEventListener("submit", (event) => void startOrganize(event));
document.querySelector("#tts-form").addEventListener("submit", (event) => void startTts(event));
document.querySelector("#complete-language").addEventListener("change", () => { renderWorkflowVoices(); schedulePersist(); });
document.querySelector("#complete-provider").addEventListener("change", (event) => void setOfflineMode(event.target.value === "kokoro"));
document.querySelector("#tts-language").addEventListener("change", () => { renderProviderVoiceSelects(); schedulePersist(); });
document.querySelector("#tts-provider").addEventListener("change", (event) => { if (["kokoro", "edge-tts"].includes(event.target.value)) void setOfflineMode(event.target.value === "kokoro"); else { renderProviderVoiceSelects(); updateTtsAvailability(); schedulePersist(); } });
document.querySelector("#organize-provider").addEventListener("change", () => {
  const provider = document.querySelector("#organize-provider").value;
  document.querySelector("#organize-form button[type=submit]").disabled = provider === "local" ? !reflowReady : !providerStatus.ai?.configured_by_provider?.[provider]?.configured;
  schedulePersist();
});
document.querySelector("#document-language").addEventListener("change", (event) => { const value = event.target.value === "en" ? "en-us" : "it"; document.querySelector("#speech-language").value = value; fillVoiceSelect(document.querySelector("#voice"), value); schedulePersist(); });
document.querySelector("#speech-language").addEventListener("change", (event) => { document.querySelector("#document-language").value = event.target.value === "it" ? "it" : "en"; fillVoiceSelect(document.querySelector("#voice"), event.target.value); schedulePersist(); });
[
  "#complete-voice", "#complete-speed", "#organize-title-input", "#organize-input", "#organize-device",
  "#tts-title-input", "#tts-input", "#tts-speed", "#tts-voice", "#text-workspace",
  "#document-title", "#voice", "#speed", "#document-reflow-device",
].forEach((selector) => {
  const field = document.querySelector(selector);
  if (field) {
    field.addEventListener("input", schedulePersist);
    field.addEventListener("change", schedulePersist);
  }
});
[["#complete-audio", "complete"], ["#tts-audio", "tts"]].forEach(([selector, slot]) => {
  const audio = document.querySelector(selector);
  if (!audio) return;
  audio.addEventListener("timeupdate", () => updateAudioProgress(audio, slot));
  audio.addEventListener("pause", () => { updateAudioProgress(audio, slot); persistSession(); });
  audio.addEventListener("ended", () => { if (audio.dataset.jobId) { audioProgress[slot] = {jobId: audio.dataset.jobId, time: 0}; persistSession(); } });
});
document.querySelector("#refresh").addEventListener("click", () => void renderJobs());
document.querySelector("#clear-history").addEventListener("click", async (event) => { if (!window.confirm(t("confirmClearHistory"))) return; const button = event.currentTarget; button.disabled = true; try { const result = await api("/api/jobs", {method: "DELETE"}); setStatus(document.querySelector("#history-status"), t("historyCleared").replace("{count}", result.deleted)); await renderJobs(); } catch (error) { setStatus(document.querySelector("#history-status"), `${t("failed")} ${error.message}`, true); } finally { button.disabled = false; } });
document.querySelector("#ocr-open-result").addEventListener("click", () => { if (lastOcrJob) void openDocument(lastOcrJob); });
document.querySelector("#organize-open-result").addEventListener("click", () => { if (lastOrganizeJob) void openTextJob(lastOrganizeJob); });
document.querySelector("#close-editor").addEventListener("click", closeReview);
document.querySelector("#close-text-editor").addEventListener("click", closeReview);
document.querySelector("#save-document").addEventListener("click", async (event) => { const button = event.currentTarget; button.disabled = true; try { await saveDocument(); } catch (error) { setStatus(document.querySelector("#save-status"), `${t("failed")} ${error.message}`, true); } finally { button.disabled = false; } });
document.querySelector("#create-speech").addEventListener("click", async (event) => { const button = event.currentTarget; button.disabled = true; try { await saveDocument(); const speechLanguage = document.querySelector("#speech-language").value; const provider = workflowSpeechProvider(); const voice = speechVoiceForProvider(provider, speechLanguage, document.querySelector("#voice").value); await queueSpeech(editingJob.id, voice, Number(document.querySelector("#speed").value), speechLanguage, provider); setStatus(document.querySelector("#save-status"), t("speechQueued")); await renderJobs(); } catch (error) { setStatus(document.querySelector("#save-status"), `${t("failed")} ${error.message}`, true); } finally { button.disabled = false; } });
document.querySelector("#reflow-document").addEventListener("click", async (event) => { const button = event.currentTarget; button.disabled = true; try { await saveDocument(); await queueReflow(editingJob.id, document.querySelector("#document-reflow-device").value); setStatus(document.querySelector("#save-status"), t("reflowQueued")); await renderJobs(); } catch (error) { setStatus(document.querySelector("#save-status"), `${t("failed")} ${error.message}`, true); } finally { button.disabled = false; } });
document.querySelector("#save-text").addEventListener("click", async (event) => { const button = event.currentTarget; button.disabled = true; try { await saveText(); setStatus(document.querySelector("#text-editor-status"), t("saved")); } catch (error) { setStatus(document.querySelector("#text-editor-status"), `${t("failed")} ${error.message}`, true); } finally { button.disabled = false; } });
document.querySelector("#create-text-speech").addEventListener("click", async (event) => { const button = event.currentTarget; button.disabled = true; try { await saveText(); const provider = workflowSpeechProvider(); await queueSpeech(editingTextJob.id, speechVoiceForProvider(provider, "it"), 1, "it", provider); setStatus(document.querySelector("#text-editor-status"), t("speechQueued")); await renderJobs(); } catch (error) { setStatus(document.querySelector("#text-editor-status"), `${t("failed")} ${error.message}`, true); } finally { button.disabled = false; } });
document.querySelector("#reflow-text").addEventListener("click", async (event) => { const button = event.currentTarget; button.disabled = true; try { await saveText(); await queueReflow(editingTextJob.id, "auto"); setStatus(document.querySelector("#text-editor-status"), t("reflowQueued")); await renderJobs(); } catch (error) { setStatus(document.querySelector("#text-editor-status"), `${t("failed")} ${error.message}`, true); } finally { button.disabled = false; } });
document.querySelector("#ai-provider").addEventListener("change", (event) => {
  const preset = settings?.ai_presets?.[event.target.value];
  if (preset) {
    document.querySelector("#ai-base-url").value = preset.base_url || "";
    document.querySelector("#ai-model").value = preset.model || "";
  } else {
    document.querySelector("#ai-base-url").value = "";
    document.querySelector("#ai-model").value = "";
  }
  renderAiKeyStatus();
  renderAiProviderMenu();
});
document.querySelector("#ai-key").addEventListener("input", updateAiConfigFields);
document.querySelector("#browse-models").addEventListener("click", () => void browseModels());
document.querySelector("#model-search").addEventListener("input", renderModelList);
document.querySelector("#close-model-dialog").addEventListener("click", () => document.querySelector("#model-dialog").close());
document.querySelector("#cancel-model-dialog").addEventListener("click", () => document.querySelector("#model-dialog").close());
document.querySelector("#use-model").addEventListener("click", useSelectedModel);
document.querySelector("#model-dialog").addEventListener("click", (event) => {
  if (event.target === event.currentTarget) event.currentTarget.close();
});
document.querySelector("#ai-settings-form").addEventListener("submit", (event) => void saveAiSettings(event));
document.querySelector("#tts-settings-form").addEventListener("submit", (event) => void saveTtsSettings(event));
document.querySelector("#local-text-model")?.addEventListener("change", (event) => void saveLocalModel(event));
document.querySelector("#install-gemma")?.addEventListener("click", () => void installGemma());
document.querySelector("#install-fish-local")?.addEventListener("click", () => void installFishLocal());
document.querySelector("#clone-form").addEventListener("submit", (event) => void createVoiceClone(event));

document.querySelectorAll("[data-provider-select]").forEach((button) => {
  button.addEventListener("click", () => selectAiProvider(button.dataset.providerSelect));
});
document.querySelectorAll("[data-guide-target]").forEach((button) => {
  button.addEventListener("click", () => focusGuide(button.dataset.guideTarget));
});
document.querySelectorAll("[data-help-key]").forEach((button) => {
  button.addEventListener("click", () => showHelp(button.dataset.helpKey));
});
document.querySelector("#close-help-dialog").addEventListener("click", () => document.querySelector("#help-dialog").close());
document.querySelector("#help-dialog-ok").addEventListener("click", () => document.querySelector("#help-dialog").close());
document.querySelector("#help-dialog").addEventListener("click", (event) => {
  if (event.target === event.currentTarget) event.currentTarget.close();
});

void initialize().catch((error) => setStatus(document.querySelector("#complete-status"), `${t("failed")} ${error.message}`, true));
