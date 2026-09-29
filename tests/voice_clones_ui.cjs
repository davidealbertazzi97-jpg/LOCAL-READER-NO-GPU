// Behavioral tests for UI state and recorder handling, without browser automation.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/app.js'), 'utf8');
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {value: '', disabled: false, hidden: false,
    classList: {toggle() {}}, setAttribute() {}, removeAttribute() {}, pause() {},
    textContent: '', files: [], src: ''});
  return elements.get(id);
}
const context = vm.createContext({
  settings: {settings: {clones: [], tts: {default_provider: 'kokoro', offline_provider: 'kokoro'}}},
  language: 'it', offlineMode: true, modeSaving: false,
  cloneBusy: false, cloneRecorder: null, cloneRecordingTimer: null,
  clonePreviewUrl: '', recordedCloneBlob: null, cloneRecordingChunks: [],
  Blob, URL: {createObjectURL: () => 'blob:test', revokeObjectURL() {}},
  document: {querySelector: element},
  t: key => key, selectedTtsReady: () => true,
  renderProviderVoiceSelects() {}, renderWorkflowVoices() {},
  updateTtsAvailability() {}, updateCompleteAvailability() {},
  window: {setTimeout() {return 1;}, clearTimeout() {}, MediaRecorder: true},
  navigator: {mediaDevices: {}}, setStatus: (node, message, error) => {node.textContent = message; node.error = error;},
});
function load(name) {
  const match = source.match(new RegExp(`(?:async )?function ${name}\\([\\s\\S]*?(?=\\n(?:async )?function )`));
  assert.ok(match, `function ${name} exists`);
  vm.runInContext(match[0], context);
}
for (const name of ['speechVoiceForProvider', 'workflowSpeechProvider', 'renderOfflineMode', 'restoreResumeForms', 'clearCloneRecording', 'toggleCloneRecording']) load(name);

(async () => {
  assert.ok(!source.toLowerCase().includes('pocket'), 'retired provider absent from UI');
  const html = fs.readFileSync(path.join(__dirname, '../static/index.html'), 'utf8');
  assert.ok(!html.toLowerCase().includes('pocket'));
  assert.ok(html.includes('id="cloned-voices"'));
  assert.equal(context.speechVoiceForProvider('kokoro', 'it', 'if_sara'), 'if_sara');
  context.renderOfflineMode();
  for (const id of ['#tts-provider', '#complete-provider', '#default-audio-provider']) assert.equal(element(id).value, 'kokoro');
  assert.equal(context.workflowSpeechProvider(), 'kokoro');
  for (const id of ['#tts-provider', '#complete-provider']) {
    element(id).tagName = 'SELECT';
    element(id).options = [{value: 'kokoro'}, {value: 'edge-tts'}];
  }
  element('#tts-voice').tagName = 'SELECT';
  element('#tts-voice').options = [{value: 'if_sara'}];
  element('#tts-voice').value = 'if_sara';
  context.fillVoiceSelect = () => {};
  context.restoreResumeForms({complete: {provider: 'retired-engine'}, tts: {provider: 'retired-engine', voice: 'retired-voice'}});
  assert.equal(element('#tts-provider').value, 'kokoro');
  assert.equal(element('#complete-provider').value, 'kokoro');
  assert.equal(element('#tts-voice').value, 'if_sara');
  context.offlineMode = false;
  context.settings.settings.tts.default_provider = 'edge-tts';
  context.renderOfflineMode();
  assert.equal(context.workflowSpeechProvider(), 'edge-tts');

  context.navigator.mediaDevices.getUserMedia = async () => {throw Object.assign(new Error(), {name: 'NotAllowedError'});};
  await context.toggleCloneRecording();
  assert.ok(element('#clone-status').textContent.includes('autorizzazioni'));
  assert.equal(element('#clone-record').disabled, false);
  let stopped = 0;
  context.navigator.mediaDevices.getUserMedia = async () => ({getTracks: () => [{stop() {stopped++;}}]});
  class Recorder {
    static isTypeSupported(type) {return type === 'audio/mp4';}
    constructor(stream, options) {this.mimeType = options.mimeType; this.state = 'inactive';}
    start() {this.state = 'recording';}
    stop() {this.state = 'inactive'; this.ondataavailable({data: new Blob(['sample'], {type: this.mimeType})}); this.onstop();}
  }
  context.MediaRecorder = Recorder;
  await context.toggleCloneRecording();
  assert.equal(context.cloneRecorder.mimeType, 'audio/mp4', 'Safari format negotiation');
  assert.equal(element('#clone-form button[type=submit]').disabled, true);
  context.cloneRecorder.stop();
  assert.equal(context.recordedCloneBlob.type, 'audio/mp4');
  assert.equal(stopped, 1);
  assert.equal(element('#clone-preview').hidden, false);
  assert.equal(element('#clone-form button[type=submit]').disabled, false);
  context.clearCloneRecording();
  assert.equal(context.recordedCloneBlob, null);
  assert.equal(element('#clone-preview').hidden, true);
  console.log('Voice UI regressions passed (retired provider removed, offline toggle, recorder formats and errors).');
})().catch(error => {console.error(error); process.exitCode = 1;});
