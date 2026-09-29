#!/usr/bin/env bash
# Download a versioned native package, verify SHA-256, then launch it.
set -euo pipefail
LAS_VERSION="0.3.3"
LAS_BASE="https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/releases/download/v${LAS_VERSION}"
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) LAS_ASSET="Local-Reader-No-GPU-${LAS_VERSION}-linux-x86_64.AppImage" ;;
  Darwin-arm64) LAS_ASSET="Local-Reader-No-GPU-${LAS_VERSION}-macos-arm64.app.zip" ;;
  *) echo 'Supported: Linux x86-64 / macOS Apple Silicon.' >&2; exit 1 ;;
esac
LAS_TEMP="$(mktemp -d -t las-install.XXXXXXXX)"
trap 'rm -rf -- "${LAS_TEMP}"' EXIT
echo 'Scarico e verifico il pacchetto / Downloading and verifying the package…'
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.2 \
  "${LAS_BASE}/SHA256SUMS.txt" --output "${LAS_TEMP}/SHA256SUMS.txt"
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.2 \
  "${LAS_BASE}/${LAS_ASSET}" --output "${LAS_TEMP}/${LAS_ASSET}"
LAS_EXPECTED="$(awk -v name="${LAS_ASSET}" 'NF == 2 && $2 == name {print $1}' "${LAS_TEMP}/SHA256SUMS.txt")"
[[ "${LAS_EXPECTED}" =~ ^[a-f0-9]{64}$ ]] || { echo 'Missing or invalid checksum.' >&2; exit 1; }
if command -v sha256sum >/dev/null 2>&1; then
  LAS_ACTUAL="$(sha256sum "${LAS_TEMP}/${LAS_ASSET}" | cut -d ' ' -f 1)"
else
  LAS_ACTUAL="$(shasum -a 256 "${LAS_TEMP}/${LAS_ASSET}" | cut -d ' ' -f 1)"
fi
[[ "${LAS_ACTUAL}" == "${LAS_EXPECTED}" ]] || { echo 'Checksum mismatch. Nothing executed.' >&2; exit 1; }
if [[ "$(uname -s)" == Darwin ]]; then
  LAS_DEST="${HOME}/Applications/Local Reader No GPU ${LAS_VERSION}"
  mkdir -p "${LAS_DEST}"
  ditto -x -k "${LAS_TEMP}/${LAS_ASSET}" "${LAS_DEST}"
  open "${LAS_DEST}/Local-Reader-No-GPU-${LAS_VERSION}-macos-arm64.app"
else
  LAS_DEST="${XDG_DATA_HOME:-${HOME}/.local/share}/local-reader-no-gpu/packages/${LAS_VERSION}"
  mkdir -p "${LAS_DEST}"
  install -m 0755 "${LAS_TEMP}/${LAS_ASSET}" "${LAS_DEST}/${LAS_ASSET}"
  echo "Pacchetto installato / Installed: ${LAS_DEST}/${LAS_ASSET}"
  # Extraction mode works without FUSE and without administrator privileges.
  APPIMAGE_EXTRACT_AND_RUN=1 "${LAS_DEST}/${LAS_ASSET}"
fi
