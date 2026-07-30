# Security policy

## Scope

Local Accessibility Studio is a single-user workstation application. It must
not be exposed to a LAN or public network.

The launcher binds to `127.0.0.1`, creates a private per-installation token,
checks browser origin, and injects a Python network guard into the web, OCR, and
speech processes. Linux installations with a compiler add an `LD_PRELOAD`
guard. Upload size, page count, pixel count, edit size, artifact path, model
hash, and accepted extensions are bounded.

Source working copies are removed after completion, failure, or interrupted
restart. Page previews, reviewed text, semantic HTML, and WAV files are intended
durable results and can contain confidential information. They are stored in
the user's results folder with private directory permissions where supported.

OCR and structural inference are untrusted suggestions. They can omit text,
misread words, or produce an incorrect reading order. Kokoro can mispronounce
content. Human review is required before relying on any result.

## Reporting a vulnerability

Do not attach real confidential documents, tokens, page previews, or audio to a
public issue. Use private vulnerability reporting when enabled and provide a
minimal synthetic reproduction.
