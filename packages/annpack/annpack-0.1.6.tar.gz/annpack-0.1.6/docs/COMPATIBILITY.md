# Compatibility Matrix

## Python
- Supported: 3.10+
- Recommended: 3.11 or 3.12

## OS
- macOS (Intel/Apple Silicon)
- Linux (x86_64)

## Key Dependencies
- `faiss-cpu` (IVF training/search)
- `numpy` / `polars`
- `cryptography` (sign/verify)

## Browser Runtime
- Modern Chromium, Firefox, and Safari
- Requires `fetch` with Range support and `crypto.subtle` for integrity checks

## Node (for building web assets)
- Recommended: Node.js 18+

## Registry
- Python 3.10+
- FastAPI + Uvicorn

If you need a stricter matrix (e.g., pinned FAISS build), document it here for your deployment.
