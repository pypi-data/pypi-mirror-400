#!/usr/bin/env bash
set -euo pipefail

log() {
  echo "[security_audit] $*"
}

PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python)}"

if command -v pip-audit >/dev/null 2>&1; then
  log "pip-audit"
  pip-audit
else
  log "pip-audit not found; install with: $PYTHON_BIN -m pip install pip-audit"
fi

if command -v npm >/dev/null 2>&1; then
  log "npm audit (web workspace)"
  pushd web >/dev/null
  npm audit --omit=dev || true
  popd >/dev/null
else
  log "npm not found; skipping npm audit"
fi

log "done"
