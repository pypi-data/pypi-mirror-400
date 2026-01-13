#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <pack_dir> <ed25519_private_key> [ed25519_public_key]"
  exit 1
fi

PACK_DIR="$1"
KEY="$2"
PUBKEY="${3:-}"

annpack verify "$PACK_DIR" --deep
annpack sign "$PACK_DIR" --key "$KEY"

if [ -n "$PUBKEY" ]; then
  annpack verify "$PACK_DIR" --pubkey "$PUBKEY"
fi

echo "[pack_integrity] OK"
