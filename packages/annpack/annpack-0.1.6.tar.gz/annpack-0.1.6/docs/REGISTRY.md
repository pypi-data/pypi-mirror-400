# Registry

ANNPack includes a local FastAPI-based registry for versioned packs and Range delivery.

## Features
- Immutable pack versions per org/project
- JWT auth with admin/dev/viewer roles
- Range support for pack files
- Local filesystem storage backend
- Optional version aliases (e.g., `latest`, `prod`)
- Optional signature + hash verification on upload

## Run (development only)

```bash
export REGISTRY_STORAGE=registry_storage
export REGISTRY_DEV_MODE=1
export REGISTRY_JWT_SECRET=dev-only-secret-change-me
uvicorn registry.app:app --host 0.0.0.0 --port 8080
```

## Production config (example)

```bash
export REGISTRY_STORAGE=/var/lib/annpack/registry
export REGISTRY_DEV_MODE=0
export REGISTRY_JWT_SECRET="change-this-to-a-strong-secret"
export REGISTRY_JWT_AUD="annpack-registry"
export REGISTRY_JWT_ISS="annpack-registry"
export REGISTRY_RATE_LIMIT_RPS=5
export REGISTRY_RATE_LIMIT_BURST=20
export REGISTRY_MAX_UPLOAD_MB=100
export REGISTRY_MAX_JSON_BYTES=$((1024*1024))
export REGISTRY_MAX_EXTRACT_MB=512
export REGISTRY_MAX_EXTRACT_FILES=2000
export REGISTRY_MAX_EXTRACT_FILE_MB=256
export REGISTRY_MAX_MANIFEST_BYTES=$((1024*1024))
export REGISTRY_MAX_LISTS=1000000
export REGISTRY_MAX_DIM=4096
export REGISTRY_VERIFY_ON_UPLOAD=1
export REGISTRY_VERIFY_DEEP=0
export REGISTRY_REQUIRE_SIGNATURE=0
export REGISTRY_PUBKEY_PATH=/etc/annpack/ed25519.pub
uvicorn registry.app:app --host 0.0.0.0 --port 8080
```

Notes:
- `REGISTRY_DEV_MODE` defaults to off; production requires `REGISTRY_JWT_SECRET`.
- In dev mode without a secret, the registry logs a warning and disables bearer tokens.
- Health check: `GET /health`
- Stats snapshot: `GET /stats`
- Aliases resolve in URLs where a `version` is expected.

## CLI examples

```bash
annpack registry upload --org demo --project sample --version v1 --pack-dir ./packset
annpack registry alias set --org demo --project sample --alias latest --version v1
```

See `registry/README.md` for upload and token examples.
