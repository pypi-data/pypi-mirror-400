# Text Search Template

Minimal text search PackSet with a delta + tombstone.

## Build

```bash
annpack packset build-base --input data.csv --packset ./packset --lists 128 --seed 1234 --offline
annpack packset build-delta \
  --base ./packset/base \
  --add delta_add.csv \
  --delete-ids-file delta_delete.jsonl \
  --out ./packset/deltas/0001.delta \
  --packset ./packset
```

## Inspect

```bash
annpack packset status --packset ./packset
```

## Serve locally

```bash
annpack serve ./packset --port 8000
```

## Publish to registry

```bash
annpack registry upload --org demo --project text-search --version v1 --pack-dir ./packset
```
