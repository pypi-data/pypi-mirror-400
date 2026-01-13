# CLI Usage

## Build

```bash
annpack build --input tiny_docs.csv --text-col text --id-col id --output ./out/pack --lists 4 --seed 1234
```

## Templates

```bash
annpack templates
annpack init --template text-search --out ./my-pack
```

## Serve

```bash
annpack serve ./out/pack --port 8000
```
The UI is served from packaged assets and the pack is mounted at `/pack/`.

## Smoke test

```bash
annpack smoke ./out/pack --port 8000
```

## Verify / Inspect / Sign

```bash
annpack verify ./out/pack --deep
annpack inspect ./out/pack
annpack sign ./out/pack --key ./ed25519.pem
annpack verify ./out/pack --pubkey ./ed25519.pub --sig ./pack.manifest.json.sig
```

## Diagnose

```bash
annpack diagnose
```

## PackSet management

```bash
annpack packset build-base --input tiny_docs.csv --packset ./packset --lists 4 --seed 1234 --offline
annpack packset build-delta --base ./packset/base --add delta_add.csv --out ./packset/deltas/0001.delta --packset ./packset
annpack packset status --packset ./packset
annpack packset create --base ./base --delta ./deltas/0001.delta --out ./packset
annpack packset promote-delta --packset ./packset --delta ./deltas/0002.delta
annpack packset revert --packset ./packset --to 1
annpack packset rebase --packset ./packset --out ./packset_rebased
```

## Registry

```bash
annpack registry upload --org demo --project sample --version v1 --pack-dir ./packset
annpack registry list --org demo --project sample
annpack registry download --org demo --project sample --version v1 --out ./packset_local
annpack registry alias set --org demo --project sample --alias latest --version v1
annpack registry alias get --org demo --project sample --alias latest
```

## Canary compare

```bash
annpack canary --base ./base --candidate ./candidate --queries ./queries.jsonl
```

## Offline mode

```bash
export ANNPACK_OFFLINE=1
annpack build --input tiny_docs.csv --text-col text --id-col id --output ./out/pack --lists 4
```
