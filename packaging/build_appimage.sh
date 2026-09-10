#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${APP_DIR}/build/appimage"
DIST_DIR="${APP_DIR}/dist"
UV="${LOCAL_AI_APP_UV:-}"

if [[ "$(uname -s)-$(uname -m)" != "Linux-x86_64" ]]; then
  echo "The AppImage builder requires Linux x86-64." >&2
  exit 1
fi
if [[ -z "${UV}" ]]; then
  UV="$(command -v uv || true)"
fi
if [[ -z "${UV}" && -x "${APP_DIR}/.tools/uv" ]]; then
  UV="${APP_DIR}/.tools/uv"
fi
if [[ -z "${UV}" ]]; then
  echo "uv is required. Run ./install.sh --core-only first." >&2
  exit 1
fi

rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}" "${DIST_DIR}"
python3 "${APP_DIR}/packaging/create_payload.py" \
  --output "${BUILD_DIR}/payload.zip"

"${UV}" run --no-project --python 3.12 \
  --with "pyinstaller==6.19.0" pyinstaller \
  --clean --noconfirm --onefile \
  --name local-accessibility-studio \
  --distpath "${BUILD_DIR}/pyinstaller-dist" \
  --workpath "${BUILD_DIR}/pyinstaller-work" \
  --specpath "${BUILD_DIR}" \
  --add-data "${BUILD_DIR}/payload.zip:." \
  "${APP_DIR}/packaging/launcher.py"

APP_ROOT="${BUILD_DIR}/AppDir"
rm -rf "${APP_ROOT}"
mkdir -p "${APP_ROOT}/usr/bin" \
  "${APP_ROOT}/usr/share/applications" \
  "${APP_ROOT}/usr/share/icons/hicolor/scalable/apps"
install -m 0755 "${BUILD_DIR}/pyinstaller-dist/local-accessibility-studio" \
  "${APP_ROOT}/usr/bin/local-accessibility-studio"
install -m 0755 "${APP_DIR}/packaging/AppRun" "${APP_ROOT}/AppRun"
install -m 0644 "${APP_DIR}/packaging/local-accessibility-studio.desktop" \
  "${APP_ROOT}/local-accessibility-studio.desktop"
install -m 0644 "${APP_DIR}/packaging/local-accessibility-studio.desktop" \
  "${APP_ROOT}/usr/share/applications/local-accessibility-studio.desktop"
install -m 0644 "${APP_DIR}/static/icon.svg" \
  "${APP_ROOT}/local-accessibility-studio.svg"
install -m 0644 "${APP_DIR}/static/icon.svg" \
  "${APP_ROOT}/usr/share/icons/hicolor/scalable/apps/local-accessibility-studio.svg"

APPIMAGETOOL="${APPIMAGETOOL:-}"
if [[ -z "${APPIMAGETOOL}" ]]; then
  APPIMAGETOOL="$(find "${APP_DIR}/.." -type f -name appimagetool.AppImage -print -quit 2>/dev/null || true)"
fi
if [[ -z "${APPIMAGETOOL}" || ! -x "${APPIMAGETOOL}" ]]; then
  echo "Set APPIMAGETOOL to an executable appimagetool.AppImage." >&2
  exit 1
fi

OUTPUT="${DIST_DIR}/Local-Accessibility-Studio-${LOCAL_ACCESSIBILITY_STUDIO_VERSION:-0.3.1}-linux-x86_64.AppImage"
APPIMAGE_EXTRACT_AND_RUN=1 "${APPIMAGETOOL}" "${APP_ROOT}" "${OUTPUT}"
chmod 0755 "${OUTPUT}"
echo "Built ${OUTPUT}"
