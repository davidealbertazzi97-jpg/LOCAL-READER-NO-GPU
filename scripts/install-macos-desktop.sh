#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${APP_DIR}"
DESKTOP_DIR="${HOME}/Desktop"
APP_BUNDLE="${DESKTOP_DIR}/Local Reader No GPU.app"
CONTENTS_DIR="${APP_BUNDLE}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
EXECUTABLE="${MACOS_DIR}/Local Reader No GPU"

if [[ "$(uname -s)-$(uname -m)" != "Darwin-arm64" ]]; then
  echo "Questo installer richiede macOS Apple Silicon (arm64)." >&2
  exit 1
fi

mkdir -p "${MACOS_DIR}" "${CONTENTS_DIR}/Resources"

{
  printf '%s\n' '<?xml version="1.0" encoding="UTF-8"?>'
  printf '%s\n' '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
  printf '%s\n' '<plist version="1.0"><dict>'
  printf '%s\n' '<key>CFBundleDisplayName</key><string>Local Reader No GPU</string>'
  printf '%s\n' '<key>CFBundleExecutable</key><string>Local Reader No GPU</string>'
  printf '%s\n' '<key>CFBundleIdentifier</key><string>org.localreadernogpu.app</string>'
  printf '%s\n' '<key>CFBundleName</key><string>Local Reader No GPU</string>'
  printf '%s\n' '<key>CFBundlePackageType</key><string>APPL</string>'
  printf '%s\n' '<key>CFBundleShortVersionString</key><string>0.3.0</string>'
  printf '%s\n' '<key>CFBundleVersion</key><string>0.3.0</string>'
  printf '%s\n' '<key>LSMinimumSystemVersion</key><string>12.0</string>'
  printf '%s\n' '<key>LSUIElement</key><true/>'
  printf '%s\n' '<key>NSHighResolutionCapable</key><true/>'
  printf '%s\n' '</dict></plist>'
} > "${CONTENTS_DIR}/Info.plist"

{
  printf '%s\n' '#!/bin/zsh' 'set -euo pipefail'
  printf 'SOURCE_DIR=%q\n' "${SOURCE_DIR}"
  printf '%s\n' 'exec "${SOURCE_DIR}/start.sh" "$@"'
} > "${EXECUTABLE}"
chmod 0755 "${EXECUTABLE}"

if [[ "${1:-}" == "--launch" ]] && command -v open >/dev/null 2>&1; then
  open "${APP_BUNDLE}"
fi

echo "Installata: ${APP_BUNDLE}"
