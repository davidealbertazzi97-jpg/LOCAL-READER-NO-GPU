#!/usr/bin/env bash
set -euo pipefail

app_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$app_dir"

run_tool() {
  local package="$1"
  local command="$2"
  shift 2
  if command -v uvx >/dev/null 2>&1; then
    uvx --from "$package" "$command" "$@"
  elif command -v uv >/dev/null 2>&1; then
    uv tool run --from "$package" "$command" "$@"
  elif [[ -x .tools/uv ]]; then
    .tools/uv tool run --from "$package" "$command" "$@"
  else
    echo "uv/uvx is required. Run ./install.sh first." >&2
    return 1
  fi
}

if [[ ! -x .venv/bin/python ]]; then
  echo "The core environment is missing. Run ./install.sh --core-only first." >&2
  exit 1
fi

run_tool "ruff==0.16.0" ruff check .
run_tool "ruff==0.16.0" ruff format --check .
run_tool "bandit==1.9.4" bandit -q -c pyproject.toml \
  -r app packaging runtime_guard scripts workers

while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find scripts packaging -type f -name '*.sh' -print0)
bash -n install.sh start.sh packaging/AppRun

if command -v node >/dev/null 2>&1; then
  node --check static/app.js
fi

.venv/bin/python -m compileall -q app packaging runtime_guard scripts tests workers
.venv/bin/python -m unittest discover -s tests -p "test_*.py"
.venv/bin/python tests/smoke_local.py

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git diff --check
  test -z "$(git ls-files models .venv .venv-ocr .venv-tts bin data outputs)"
  private_marker='-----BEGIN '"(RSA |EC |OPENSSH )?PRIVATE KEY-----"
  github_fine_grained='github'_'pat_[[:alnum:]_]{20,}'
  github_classic='ghp'_'[[:alnum:]]{20,}'
  aws_access_key='AKIA''[[:alnum:]]{16}'
  google_api_key='AIza''[[:alnum:]_-]{20,}'
  slack_token='xox''[baprs]-[[:alnum:]-]{10,}'
  secret_pattern="${private_marker}|${github_fine_grained}|${github_classic}|${aws_access_key}|${google_api_key}|${slack_token}"
  tracked_secrets="$(
    git grep -IlE -- "$secret_pattern" -- . || true
  )"
  if [[ -n "$tracked_secrets" ]]; then
    printf 'Possible secret material found in tracked files:\n%s\n' \
      "$tracked_secrets" >&2
    exit 1
  fi
fi

.venv/bin/python scripts/check_portability.py

printf 'Static, unit, security, and core smoke checks passed.\n'
