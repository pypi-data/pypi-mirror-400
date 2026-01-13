# Log Search Template

Sample log messages for search + triage workflows.

## Build

```bash
annpack packset build-base --input logs.csv --packset ./packset --text-col message --id-col id --lists 128 --seed 1234 --offline
annpack packset build-delta \
  --base ./packset/base \
  --add delta_add.csv \
  --delete-ids-file delta_delete.jsonl \
  --out ./packset/deltas/0001.delta \
  --packset ./packset \
  --text-col message
```

## Inspect

```bash
annpack packset status --packset ./packset
```
