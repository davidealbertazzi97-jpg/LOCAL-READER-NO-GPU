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

Security fixes target the latest source on `main`. Version 0.3.0 is the current
prepared source release. The Linux AppImage can be built and verified locally;
Windows and macOS packages must be built and tested on their native target
systems before distribution.

## Scope and deployment boundary

Local Accessibility Studio is a single-user workstation application. It is not
designed to be exposed to a LAN, reverse proxy, shared server, container
platform, or the public internet.

The launcher:

- binds the service to numeric loopback `127.0.0.1`;
- creates a private random token per installation;
- checks the exact browser origin on state-changing API requests;
- rejects oversized uploads before multipart parsing;
- injects a Python outbound-network guard into web, OCR, and local reflow
  processes; the Edge-TTS child is the documented remote-network exception;
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
