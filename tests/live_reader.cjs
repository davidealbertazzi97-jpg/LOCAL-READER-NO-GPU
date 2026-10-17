const assert = require('node:assert/strict');
const {Reader, paragraphs, chunks, words} = require('../static/live-reader.js');

assert.deepEqual(paragraphs('  Primo.\r\n\r\n Secondo.\n \nTerzo. '), ['Primo.', 'Secondo.', 'Terzo.']);
const unicode = 'Ciao 🌍, città! Un’altra frase.';
for (const chunk of chunks(unicode)) assert.equal(unicode.slice(chunk.start, chunk.start + chunk.text.length), chunk.text);
for (const chunk of chunks(('Lettura 🌍 molto lunga. ').repeat(70), 5)) {
  assert.ok(chunk.text.length <= 240);
  assert.ok(!/[\uD800-\uDBFF]$/u.test(chunk.text), 'no broken surrogate pairs');
}
const tokens = words(unicode);
assert.equal(tokens[2].text, 'città!');
assert.equal(tokens[2].start, unicode.indexOf('città'));

const utterances = [];
const events = [];
const synth = {paused: false, cancel() {}, speak(u) {utterances.push(u);}, pause() {this.paused = true;}, resume() {this.paused = false;}};
const reader = new Reader(synth, class Utterance {constructor(text) {this.text = text;}}, event => events.push(event));
reader.voice = {voiceURI: 'local:it', lang: 'it-IT', localService: true};
reader.load('Prima frase. Seconda frase.\n\nAltro paragrafo.');
reader.play();
let utterance = utterances.at(-1);
utterance.onstart();
assert.equal(events.at(-1).word, null, 'phrase highlighting until real word events arrive');
utterance.onboundary({name: 'sentence', charIndex: 0});
assert.equal(events.at(-1).word, null, 'sentence event is not a word event');
utterance.onboundary({name: 'word', charIndex: 6});
assert.equal(reader.offset, 6);
assert.equal(events.at(-1).word, 6);
reader.toggle();
assert.equal(reader.state, 'paused');
assert.equal(synth.paused, true);
reader.toggle();
assert.equal(reader.state, 'speaking');
assert.equal(synth.paused, false);
// A paragraph click cancels the old voice. Late completion/error cannot restart it.
reader.play(1, 0);
const count = utterances.length;
utterance.onend();
utterance.onerror({error: 'interrupted'});
utterance.onboundary({name: 'word', charIndex: 0});
assert.equal(utterances.length, count);
assert.equal(reader.paragraph, 1);
utterance = utterances.at(-1);
utterance.onstart();
utterance.onend();
assert.equal(reader.state, 'finished');
reader.toggle();
assert.equal(reader.paragraph, 0, 'read after completion starts at beginning');
reader.continuous = false;
let safety = 0;
while (reader.state !== 'finished' && safety++ < 10) { utterance = utterances.at(-1); utterance.onstart(); utterance.onend(); }
assert.equal(reader.paragraph, 0, 'single paragraph mode stops at its end');
reader.continuous = true;
reader.play();
safety = 0;
while (reader.state !== 'finished' && safety++ < 10) { utterance = utterances.at(-1); utterance.onstart(); utterance.onend(); }
assert.equal(reader.paragraph, 1, 'continuous mode advances across paragraphs');
reader.play(0, 6);
utterance = utterances.at(-1);
utterance.onstart();
utterance.onboundary({name: 'word', charIndex: 0});
assert.equal(events.at(-1).word, 6, 'resume uses the original paragraph offset');
reader.stop();
utterance.onend();
assert.equal(reader.state, 'idle');
reader.voice = null;
assert.equal(reader.play(), false);
console.log('Live reader passed: Unicode offsets, chunking, real boundaries, pause/resume, paragraph jumps, stale events, continuous/single reading and missing voices.');
// Speech Dispatcher has no native pause. Cancel without advancing and restart
// the current phrase, while native Windows/device pause keeps its exact timing.
reader.voice = {voiceURI: 'urn:moz-tts:speechd:Italian?it', lang: 'it', localService: false};
reader.play(0, 13);
utterance = utterances.at(-1);
utterance.onstart();
const pausedText = utterance.text;
reader.toggle();
assert.equal(reader.state, 'paused');
assert.equal(reader.restartOnResume, true);
const pausedCount = utterances.length;
utterance.onend();
assert.equal(utterances.length, pausedCount, 'cancel completion cannot advance paused speech');
reader.toggle();
assert.equal(reader.restartOnResume, false);
assert.equal(utterances.at(-1).text, pausedText, 'resume starts from the same actual text position');
reader.stop();
console.log('Linux Speech Dispatcher pause/resume regression passed.');
