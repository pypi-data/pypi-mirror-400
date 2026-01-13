# @annpack/client

Minimal browser/worker-friendly client for ANNPack packs and packsets.

## Usage

```ts
import { openPack, MemoryCache, RangeFetcher } from '@annpack/client';

const pack = await openPack('/pack/pack.manifest.json', {
  cache: new MemoryCache(),
  meta: { load: false, maxBytes: 32 * 1024 * 1024 },
});

const results = await pack.search({ queryVector: [0.1, 0.2], topK: 5, probe: 8 });
console.log(results);
```
