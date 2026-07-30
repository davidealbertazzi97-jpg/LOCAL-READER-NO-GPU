#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UV_VERSION="0.11.16"
TOOLS_DIR="${APP_DIR}/.tools"
ARCHIVE="${TOOLS_DIR}/uv-download"

case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)
    ASSET="uv-x86_64-unknown-linux-gnu.tar.gz"
    SHA256="74947fe2c03315cf07e82ab3acc703eddef01aba4d5232a98e4c6825ec116131"
    ;;
  Darwin-arm64)
    ASSET="uv-aarch64-apple-darwin.tar.gz"
    SHA256="2b25be1af546be330b340b0a76b99f989daa6d92678fdffb87438e661e9d88fb"
    ;;
  *)
    echo "Unsupported installer platform: $(uname -s)/$(uname -m)" >&2
    exit 1
    ;;
esac

mkdir -p "${TOOLS_DIR}"
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.2 \
  "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/${ASSET}" \
  --output "${ARCHIVE}"

if command -v sha256sum >/dev/null 2>&1; then
  echo "${SHA256}  ${ARCHIVE}" | sha256sum --check -
else
  test "$(shasum -a 256 "${ARCHIVE}" | awk '{print $1}')" = "${SHA256}"
fi

UNPACKED="$(mktemp -d "${TOOLS_DIR}/uv-unpacked.XXXXXX")"
tar -xzf "${ARCHIVE}" -C "${UNPACKED}"
UV_PATH="$(find "${UNPACKED}" -type f -name uv -perm -u+x -print -quit)"
test -n "${UV_PATH}"
install -m 0755 "${UV_PATH}" "${TOOLS_DIR}/uv"
rm -rf "${UNPACKED}"
rm -f "${ARCHIVE}"

export LOCAL_AI_APP_UV="${TOOLS_DIR}/uv"
exec "${LOCAL_AI_APP_UV}" run --no-project --python 3.12 \
  "${APP_DIR}/scripts/bootstrap.py" "$@"
