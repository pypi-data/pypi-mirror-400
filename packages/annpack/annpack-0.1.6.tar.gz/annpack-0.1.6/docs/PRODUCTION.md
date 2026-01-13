# Production Guide (Internal/Self-Hosted)

This guide targets internal snapshot search deployments where packs are built in a trusted environment
and served from local storage or a private CDN.

## Build + Integrity Pipeline

1) Build packs deterministically:

```bash
export ANNPACK_OFFLINE=1
annpack build --input my.csv --text-col text --id-col id --output ./out/pack --lists 1024 --seed 1234
```

2) Verify structure and hashes:

```bash
annpack verify ./out/pack --deep
```

3) Sign and store the manifest:

```bash
annpack sign ./out/pack --key ./ed25519.pem
annpack verify ./out/pack --pubkey ./ed25519.pub
```

4) Distribute pack directories as immutable artifacts.

Build metadata (seed/model/device/offline/etc.) is recorded in `pack.manifest.json` under `build`.

## Registry publish (optional)

```bash
annpack registry upload --org demo --project search --version v1 --pack-dir ./out/pack
annpack registry alias set --org demo --project search --alias latest --version v1
```

## PackSet (Base + Delta + Tombstones)

- Build a base packset:

```bash
python - <<'PY'
from annpack.packset import build_packset_base
build_packset_base(
    "tiny_docs.csv",
    "./packset",
    text_col="text",
    id_col="id",
    lists=256,
    seed=1234,
    offline=True,
)
PY
```

- Build a delta and update the manifest:

```bash
python - <<'PY'
from annpack.packset import build_delta, update_packset_manifest
build_delta(
    base_dir="./packset/base",
    add_csv="delta_add.csv",
    delete_ids=[1, 2],
    out_delta_dir="./packset/deltas/0001.delta",
    text_col="text",
    id_col="id",
    lists=256,
    seed=1234,
    offline=True,
)
update_packset_manifest("./packset", "./packset/deltas/0001.delta", seq=1)
PY
```

- Rebase/compact deltas into a fresh base:

```bash
annpack packset rebase --packset ./packset --out ./packset_rebased --lists 256 --seed 1234
```

Or use the helper script:

```bash
bash tools/packset_compact.sh ./packset ./packset_rebased 256 1234
```

## Serving Packs

- Local demo server (CORS enabled, UI served):

```bash
annpack serve ./out/pack --port 8000
```

- Validate with smoke test:

```bash
annpack smoke ./out/pack --port 8000
```

- Health check: `GET /health`

## Determinism Controls

- `ANNPACK_OFFLINE=1` for deterministic dummy embeddings.
- `ANNPACK_DEVICE=cpu` to stabilize hardware differences.
- `--seed` on builds for stable IVF clustering.
- `ANNPACK_FAISS_THREADS=1` to reduce non-determinism in clustering.

For real embeddings, install extras:

```bash
pip install annpack[embed]
```

## Security Limits (Default Caps)

- `ANNPACK_MAX_DIM` (default 4096)
- `ANNPACK_MAX_LISTS` (default 1,000,000)
- `ANNPACK_MAX_LIST_BYTES` (default 128 MB)
- `ANNPACK_MAX_META_BYTES` (default 1 GB)
- `ANNPACK_META_MAX_LINE` (default 1 MB)
- `ANNPACK_ALLOW_LARGE_META=1` to bypass caps in trusted environments

## Observability

- `ANNPACK_LOG_LEVEL=INFO|DEBUG`
- `ANNPACK_LOG_JSON=1` for structured logs
- Registry health check: `GET /health`

## Benchmarks

Run the lightweight offline benchmark:

```bash
ANNPACK_OFFLINE=1 python tools/bench/bench.py --rows 2000 --lists 64
```

## Release Gates

- Full repo gate:

```bash
bash tools/stage_all.sh
```

- Production gate (includes stage_all + offline bench):

```bash
bash tools/prod_gate.sh
```
- Release build (Python):

```bash
bash tools/release.sh
```

- Build local artifacts only:

```bash
bash tools/build_artifacts.sh
```
- Security audit (optional):

```bash
bash tools/security_audit.sh
```

- Web assets (optional if you ship UI/client artifacts):

```bash
cd web
npm run build
```

## Integrity Helper

```bash
bash tools/pack_integrity.sh ./out/pack ./ed25519.pem ./ed25519.pub
```

## Compatibility

See `docs/COMPATIBILITY.md` for supported versions.
