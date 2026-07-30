#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCHER_DIR="${HOME}/.local/bin"
APPLICATION_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
LAUNCHER="${LAUNCHER_DIR}/local-accessibility-studio"
DESKTOP_FILE="${APPLICATION_DIR}/local-accessibility-studio.desktop"
ICON="${ICON_DIR}/local-accessibility-studio.svg"

mkdir -p "${LAUNCHER_DIR}" "${APPLICATION_DIR}" "${ICON_DIR}"
escaped_start="$(printf '%q' "${APP_DIR}/start.sh")"
{
  echo '#!/usr/bin/env bash'
  echo 'set -euo pipefail'
  echo "exec ${escaped_start} \"\$@\""
} > "${LAUNCHER}"
chmod 0755 "${LAUNCHER}"
install -m 0644 "${APP_DIR}/static/icon.svg" "${ICON}"

{
  echo '[Desktop Entry]'
  echo 'Type=Application'
  echo 'Name=Local Accessibility Studio'
  echo 'Comment=OCR accessibile e sintesi vocale italiana completamente in locale'
  echo "Exec=${LAUNCHER}"
  echo "Icon=${ICON}"
  echo 'Terminal=false'
  echo 'Categories=Utility;Accessibility;'
  echo 'StartupNotify=true'
} > "${DESKTOP_FILE}"
chmod 0644 "${DESKTOP_FILE}"

if command -v desktop-file-validate >/dev/null 2>&1; then
  desktop-file-validate "${DESKTOP_FILE}"
fi
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${APPLICATION_DIR}" >/dev/null
fi
echo "Desktop launcher installed."
