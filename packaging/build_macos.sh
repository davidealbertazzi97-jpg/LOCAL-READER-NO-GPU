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
  --name "Local Reader No GPU" \
  --osx-bundle-identifier "org.localreadernogpu.app" \
  --distpath "${BUILD_DIR}/pyinstaller-dist" \
  --workpath "${BUILD_DIR}/pyinstaller-work" \
  --specpath "${BUILD_DIR}" \
  --add-data "${BUILD_DIR}/payload.zip:." \
  "${APP_DIR}/packaging/launcher.py"

BUNDLE="${BUILD_DIR}/pyinstaller-dist/Local Reader No GPU.app"
OUTPUT="${DIST_DIR}/Local-Reader-No-GPU-0.3.2-macos-arm64.app"
rm -rf "${OUTPUT}"
ditto "${BUNDLE}" "${OUTPUT}"
ditto -c -k --sequesterRsrc --keepParent "${OUTPUT}" "${OUTPUT}.zip"
hdiutil create -volname "Local Reader No GPU" -srcfolder "${OUTPUT}" \
  -ov -format UDZO "${DIST_DIR}/Local-Reader-No-GPU-0.3.2-macos-arm64.dmg"
echo "Built ${OUTPUT}"
