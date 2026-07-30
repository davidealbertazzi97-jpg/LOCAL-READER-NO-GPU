#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "${APP_DIR}/bin"
cc -O2 -Wall -Wextra -Werror -fPIC -shared \
  "${APP_DIR}/native/netguard.c" \
  -o "${APP_DIR}/bin/liblocal_ai_netguard.so"
chmod 0755 "${APP_DIR}/bin/liblocal_ai_netguard.so"
echo "Linux native network guard installed."
