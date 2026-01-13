#!/usr/bin/env bash
set -euo pipefail

log() {
  echo "[build_artifacts] $*"
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python)}"

log "python artifacts"
rm -rf dist build
"$PYTHON_BIN" -m build

if command -v emcc >/dev/null 2>&1; then
  log "wasm build"
  bash tools/build_wasm.sh
else
  log "emcc not found; skipping wasm"
fi

if command -v npm >/dev/null 2>&1; then
  log "web build"
  pushd web >/dev/null
  npm run build
  popd >/dev/null
else
  log "npm not found; skipping web build"
fi

log "done"
