# Security policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability involving
authentication, origin checks, file access, path traversal, model integrity,
network isolation, cleanup, or confidential results.

Use GitHub's **Private vulnerability reporting** feature when it is enabled for
the repository. Include the affected version, minimal reproduction steps,
impact, and any suggested mitigation.

Never attach a real confidential document, token, page preview, OCR export,
voice file, or application database. Use the smallest synthetic reproduction
that demonstrates the problem.

## Supported version

Security fixes target the latest source on `main` and the latest release.
The 0.3.3 release removes Pocket TTS. Native release automation builds and
runs first-install, OCR and speech smoke tests on Linux x86-64, Windows x86-64
and macOS Apple Silicon before publishing. Packages are not commercially
signed; the macOS app is not notarized. Tests are not a security certification.

## Scope and deployment boundary

Local Reader No GPU is a single-user workstation application. It is not
designed to be exposed to a LAN, reverse proxy, shared server, container
platform, or the public internet.

The launcher:

- binds the service to numeric loopback `127.0.0.1`;
- creates a private random token per installation;
- checks the exact browser origin on state-changing API requests;
- rejects oversized uploads before multipart parsing;
- injects a Python outbound-network guard into web, OCR, and local reflow
  processes; explicitly selected cloud speech/AI children are documented
  remote-network exceptions, disabled by offline mode;
- adds a native `LD_PRELOAD` network guard on Linux when compilation is
  available.

Upload size, page count, pixel count, frame count, edit size, speech size,
artifact paths, language/voice combinations, and model hashes are bounded or
validated. User/OCR text is escaped into fixed HTML and is never executed as
markup.

Private working copies are removed after completion, failure, deletion, and an
interrupted restart. Active OCR, reflow, and speech process groups are
terminated during an orderly application shutdown. Page previews, reviewed
text, HTML, reports, and MP3 files are intentional durable results and can contain confidential
information. They are stored in the user's results directory with private
permissions where the operating system supports them.

API keys and voice samples are local private files, not encrypted storage.
Do not publish user runtime directories, browser state, results, model caches
or real voice samples. Release payloads exclude these directories. SHA-256
pins cover uv, Kokoro, LFM, llama.cpp and AppImage tooling/runtime; pip uses
hash-locked wheels. Paddle model prefetch uses upstream download/cache
controls rather than a project-maintained model hash manifest. A compromised
upstream model host or wheel publisher is outside this audit\'s guarantee.
Release checksum files share the repository trust boundary; they are not
independent signatures. Install scripts must be reviewed/trusted before use.

## Known non-security limitations

Incorrect OCR, reading order, semantic roles, or pronunciation are functional
accuracy limitations, not by themselves security vulnerabilities. They still
matter: users must review output before relying on or sharing it.

The default browser runs outside the application's network guard and may
perform its own background network requests. Local processing alone does not
establish accessibility, GDPR, or other regulatory compliance.

The Python and native network guards are defense-in-depth controls. They are
not an operating-system sandbox and cannot protect against malicious native
code, a compromised dependency, or another process already running as the same
user. Use an appropriate OS sandbox or virtual machine when handling a crafted
file from an untrusted source.
