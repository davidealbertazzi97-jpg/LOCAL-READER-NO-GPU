#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Local Accessibility Studio"
DEFAULT_ARCHIVE_URL="https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/archive/refs/heads/main.tar.gz"
ARCHIVE_URL="${LAS_ARCHIVE_URL:-${DEFAULT_ARCHIVE_URL}}"
INSTALL_ROOT="${LAS_INSTALL_ROOT:-${HOME}/Library/Application Support/${APP_NAME}}"
SOURCE_DIR="${INSTALL_ROOT}/source"
DRY_RUN="${LAS_INSTALLER_DRY_RUN:-0}"

die() {
  echo "Local Accessibility Studio: $*" >&2
  exit 1
}

system_name="${LAS_TEST_PLATFORM:-$(uname -s)}"
machine_name="${LAS_TEST_ARCH:-$(uname -m)}"
if [[ "${system_name}-${machine_name}" != "Darwin-arm64" ]]; then
  die "questo installer richiede macOS Apple Silicon (arm64)."
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  printf 'Piano installazione macOS Apple Silicon:\n'
  printf '  archivio: %s\n' "${ARCHIVE_URL}"
  printf '  destinazione: %s\n' "${INSTALL_ROOT}"
  printf '  modelli automatici: PaddleOCR, Kokoro 82M, LFM2.5 e llama.cpp\n'
  printf '  collegamento Desktop: %s\n' "${HOME}/Desktop/${APP_NAME}.app"
  exit 0
fi

for command in curl tar shasum; do
  command -v "${command}" >/dev/null 2>&1 || die "comando mancante: ${command}"
done

mkdir -p "${INSTALL_ROOT}"
chmod 0700 "${INSTALL_ROOT}"
temporary_root="$(mktemp -d "${TMPDIR:-/tmp}/local-accessibility-studio.XXXXXX")"
cleanup() {
  rm -rf "${temporary_root}"
}
trap cleanup EXIT

archive="${temporary_root}/source.tar.gz"
echo "Scarico Local Accessibility Studio…"
curl --fail --silent --show-error --location \
  --proto '=https' --proto-redir '=https' --tlsv1.2 \
  "${ARCHIVE_URL}" --output "${archive}"

while IFS= read -r member; do
  case "${member}" in
    /*|../*|*/../*|..)
      die "archivio con un percorso non sicuro"
      ;;
  esac
done < <(tar -tzf "${archive}")

archive_root="$(tar -tzf "${archive}" | awk -F/ 'NF {print $1; exit}')"
[[ -n "${archive_root}" ]] || die "archivio vuoto"
tar -xzf "${archive}" -C "${temporary_root}"
staged_source="${temporary_root}/source"
mv "${temporary_root}/${archive_root}" "${staged_source}"
if find "${staged_source}" -type l -print -quit | grep -q .; then
  die "il codice scaricato contiene un collegamento non consentito"
fi

if [[ -e "${SOURCE_DIR}" ]]; then
  [[ -d "${SOURCE_DIR}" ]] || die "la destinazione esiste ma non è una cartella"
  previous="${INSTALL_ROOT}/source.previous.$(date +%Y%m%d%H%M%S)"
  mv "${SOURCE_DIR}" "${previous}"
  for persistent in .tools .venv .venv-ocr .venv-tts .venv-mac-voice models; do
    if [[ -e "${previous}/${persistent}" ]]; then
      mv "${previous}/${persistent}" "${staged_source}/${persistent}"
    fi
  done
  echo "Versione precedente conservata in: ${previous}"
fi
mv "${staged_source}" "${SOURCE_DIR}"
chmod 0700 "${SOURCE_DIR}"

echo "Preparo dipendenze e modelli necessari; può richiedere tempo e spazio…"
bash "${SOURCE_DIR}/install.sh"
bash "${SOURCE_DIR}/scripts/install-macos-desktop.sh"

if [[ "${LAS_INSTALL_OPTIONAL_MODELS:-0}" == "1" ]]; then
  uv="${SOURCE_DIR}/.tools/uv"
  [[ -x "${uv}" ]] || die "uv non trovato dopo l’installazione"
  echo "Scarico anche Gemma 4 e Fish Audio locale (oltre 11 GB)…"
  "${SOURCE_DIR}/.venv-tts/bin/python" "${SOURCE_DIR}/scripts/install_gemma.py"
  LOCAL_AI_APP_UV="${uv}" "${uv}" run --no-project --python 3.12 \
    "${SOURCE_DIR}/scripts/install_mac_fish.py"
fi

bash "${SOURCE_DIR}/scripts/install-macos-desktop.sh" --launch
echo "Installazione completata. L’app è sul Desktop e si apre nel browser."
