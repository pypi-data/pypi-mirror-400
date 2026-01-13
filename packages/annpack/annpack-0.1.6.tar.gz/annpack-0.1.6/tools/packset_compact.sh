#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <packset_dir> <out_dir> [lists] [seed]"
  exit 1
fi

PACKSET="$1"
OUT="$2"
LISTS="${3:-1024}"
SEED="${4:-0}"

annpack packset rebase --packset "$PACKSET" --out "$OUT" --lists "$LISTS" --seed "$SEED"
annpack verify "$OUT" --deep

echo "[packset_compact] OK"
