#!/usr/bin/env bash
set -euo pipefail

log() {
  echo "[prod_gate] $*"
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

log "stage_all"
bash tools/stage_all.sh

if command -v emcc >/dev/null 2>&1; then
  log "build wasm"
  bash tools/build_wasm.sh
else
  log "emcc not found; skipping wasm build"
fi

log "bench (offline)"
if [ "$(uname -s)" = "Darwin" ]; then
  # Avoid OpenMP duplicate runtime abort on macOS.
  export KMP_DUPLICATE_LIB_OK=TRUE
fi
ANNPACK_OFFLINE=1 python tools/bench/bench.py --rows 2000 --lists 64

log "pack integrity demo"
if [ -d out ] && ls out/*.manifest.json >/dev/null 2>&1; then
  echo "[prod_gate] found out/ manifests; run tools/pack_integrity.sh manually with keys"
else
  echo "[prod_gate] no out/ packs found; skipping"
fi

log "done"
