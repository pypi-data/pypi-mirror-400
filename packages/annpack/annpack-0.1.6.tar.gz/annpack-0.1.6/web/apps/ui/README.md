# ANNPack UI

Minimal React UI for inspecting packs and running vector queries (including PackSets).

## Dev

```bash
cd web
npm install
npm run build -w @annpack/client
npm run dev -w annpack-ui
```

The UI expects a pack mounted at `/pack/pack.manifest.json` when served by `annpack serve`.

Notes:

- Vector search runs client-side with Range requests to `*.annpack`.
- Metadata loading is optional and size-capped.
