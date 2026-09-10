#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${APP_DIR}/build/macos"
DIST_DIR="${APP_DIR}/dist"
UV="${LOCAL_AI_APP_UV:-}"

if [[ "$(uname -s)-$(uname -m)" != "Darwin-arm64" ]]; then
  echo "The macOS builder requires macOS Apple Silicon." >&2
  exit 1
fi
if [[ -z "${UV}" ]]; then
  UV="$(command -v uv || true)"
fi
if [[ -z "${UV}" ]]; then
  echo "uv is required to build the package." >&2
  exit 1
fi

rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}" "${DIST_DIR}"
python3 "${APP_DIR}/packaging/create_payload.py" \
  --output "${BUILD_DIR}/payload.zip"

"${UV}" run --no-project --python 3.12 \
  --with "pyinstaller==6.19.0" pyinstaller \
  --clean --noconfirm --windowed --onedir \
  --name "Local Accessibility Studio" \
  --osx-bundle-identifier "org.localaccessibility.studio" \
  --distpath "${BUILD_DIR}/pyinstaller-dist" \
  --workpath "${BUILD_DIR}/pyinstaller-work" \
  --specpath "${BUILD_DIR}" \
  --add-data "${BUILD_DIR}/payload.zip:." \
  "${APP_DIR}/packaging/launcher.py"

BUNDLE="${BUILD_DIR}/pyinstaller-dist/Local Accessibility Studio.app"
OUTPUT="${DIST_DIR}/Local-Accessibility-Studio-0.3.0-macos-arm64.app"
rm -rf "${OUTPUT}"
ditto "${BUNDLE}" "${OUTPUT}"
echo "Built ${OUTPUT}"
