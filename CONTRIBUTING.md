# Contributing

Thank you for helping improve Local Accessibility Studio.

## Development setup

1. Use Python 3.12 and `uv`.
2. Install the lightweight web core:

   ```bash
   ./install.sh --core-only --skip-desktop
   ```

   On Windows:

   ```powershell
   .\install.ps1 --core-only --skip-desktop
   ```

3. For complete OCR and speech work, run the normal installer. The optional
   `--fast-tts` profile downloads the larger FP32 Kokoro model.
4. Run `./scripts/check.sh` before opening a pull request.
5. Run `.venv/bin/python tests/smoke_local.py` for the core integration test.
6. Run `.venv/bin/python tests/smoke_local.py --full` only after installing the
   OCR and Kokoro environments.

Tests must use synthetic fixtures. Never commit real personal documents,
tokens, model weights, voice bundles, virtual environments, generated page
previews, audio, databases, or application state.

## Project rules

- Keep the service bound to numeric loopback.
- Preserve token authentication, exact-origin checks, and network guards.
- Do not add telemetry, remote inference, CDN assets, or account requirements.
- Treat OCR structure and accessibility output as review candidates.
- Keep user/OCR text escaped from executable HTML.
- Preserve cleanup on success, failure, deletion, and interrupted restart.
- Bound new file formats and resource-intensive operations.
- Pin direct runtime dependencies.
- Document new runtime components, models, and licenses in
  `THIRD_PARTY_NOTICES.md`.
- Keep third-party code, weights, and voice data under their original terms.

## Pull requests

Explain the user-visible change, security or privacy impact, tests performed,
and any dependency or license changes. Do not include confidential test
material in commits, screenshots, issues, or CI logs.

By submitting a contribution, you agree that it may be distributed under the
repository's GNU GPL version 3 only.
