# Docs Search Template

Docs-style content with URL + title metadata.

## Build

```bash
annpack packset build-base --input docs.csv --packset ./packset --text-col content --id-col id --lists 256 --seed 1234 --offline
annpack packset build-delta \
  --base ./packset/base \
  --add delta_add.csv \
  --delete-ids-file delta_delete.jsonl \
  --out ./packset/deltas/0001.delta \
  --packset ./packset \
  --text-col content
```

## Inspect

```bash
annpack packset status --packset ./packset
```
