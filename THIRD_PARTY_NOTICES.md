# Third-party notices

Local AI App Starter is licensed under GNU GPL version 3 only. That licence
applies to the original code and documentation in this repository. Dependencies
and tools retain their own licences.

The source repository does not contain a virtual environment, Python wheel,
model weight, generated native library, font, icon library, or user document.

| Component | Pinned version | Licence | Distribution |
| --- | ---: | --- | --- |
| FastAPI | 0.140.13 | MIT | Installed from its upstream Python package |
| Uvicorn | 0.51.0 | BSD-3-Clause | Installed from its upstream Python package |
| python-multipart | 0.0.32 | Apache-2.0 | Installed from its upstream Python package |
| uv | 0.11.16 | Apache-2.0 OR MIT | Downloaded by the installer, verified by SHA-256, not committed |
| Ruff | 0.16.0 | MIT | Development-only package |
| Bandit | 1.9.4 | Apache-2.0 | Development-only package |

Transitive dependencies retain their upstream terms. Before distributing a
preassembled environment or binary application, generate a complete inventory
for the exact platform artifacts being shipped.

No AI model is part of this starter. Every derived application must document
the code, weights, voice data, sample data, and runtime licences it introduces.
This inventory is release-preparation information, not legal advice.
