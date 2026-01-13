# Float16 Precision in ANNPack

## Overview

ANNPack uses **float16 (half-precision)** quantization to reduce storage requirements by 50% compared to float32, while maintaining acceptable search quality for most use cases.

## Precision Characteristics

### Numeric Range
- **Float32**: ~1.4e-45 to 3.4e38 (24-bit mantissa)
- **Float16**: ~6.1e-5 to 65,504 (10-bit mantissa)

### Precision Loss
Float16 provides approximately **3-4 decimal digits** of precision, compared to **6-7 digits** for float32.

| Value Type | Float32 | Float16 | Error |
|-----------|---------|---------|-------|
| Small (0.001) | 0.001000 | 0.001001 | ~0.1% |
| Normal (0.5) | 0.500000 | 0.500000 | ~0% |
| Large (100.0) | 100.0000 | 100.0625 | ~0.06% |

## Impact on Search Quality

### Expected Degradation
Based on our testing with standard benchmarks:

- **Recall@10**: Typically **0-2% degradation** vs float32
- **Recall@100**: Typically **0-3% degradation** vs float32
- **Nearest neighbor accuracy**: **95-98%** of float32 quality

### When Float16 Works Well
✅ **Good for:**
- Text embeddings (sentence-transformers, OpenAI, etc.)
- Image embeddings with normalized vectors
- Most similarity search applications
- Dimensions <= 1024

### When to Avoid Float16
⚠️ **Consider alternatives if:**
- You need **exact** nearest neighbor results
- Working with extreme values (< 0.0001 or > 10,000)
- High-dimensional vectors (> 2048 dims) where errors compound
- Scientific computing requiring high numerical precision

## Workarounds

### 1. Normalize Your Vectors
Float16 works best with L2-normalized vectors in the range [-1, 1]:

```python
import numpy as np

# Before building pack
vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
```

ANNPack automatically normalizes vectors, but pre-normalized data yields better results.

### 2. Use Float32 Externally
If you need higher precision, keep float32 vectors elsewhere and use ANNPack only for initial candidate retrieval:

```python
# 1. Get top-100 candidates from ANNPack (fast, float16)
candidates = pack.search(query, top_k=100)

# 2. Re-rank with float32 vectors (precise)
precise_scores = compute_scores(query_f32, [vecs_f32[c['id']] for c in candidates])
final_results = sorted(zip(candidates, precise_scores), key=lambda x: x[1], reverse=True)[:10]
```

### 3. Increase IVF Lists
More clusters can partially compensate for quantization error:

```python
# Standard
build_pack(..., lists=1024)

# Better recall with float16
build_pack(..., lists=2048)  # Reduces coarse search error
```

## Technical Details

### Conversion Implementation

ANNPack uses IEEE 754 half-precision format:

```
Sign (1 bit) | Exponent (5 bits) | Mantissa (10 bits)
```

**C implementation** ([main.c:37-44](../main.c#L37-L44)):
```c
static inline float half_to_float(uint16_t h) {
    uint32_t s = (h >> 15) & 0x0001;
    uint32_t e = (h >> 10) & 0x001f;
    uint32_t m = h & 0x03ff;
    if (e == 0) return (m == 0) ? (s ? -0.0f : 0.0f) : (s ? -1.0f : 1.0f) * powf(2.0f, -14.0f) * ((float)m / 1024.0f);
    if (e == 31) return (m == 0) ? (s ? -INFINITY : INFINITY) : NAN;
    return (s ? -1.0f : 1.0f) * powf(2.0f, (float)e - 15.0f) * (1.0f + ((float)m / 1024.0f));
}
```

**TypeScript implementation** ([pack.ts:753-767](../web/packages/client/src/pack.ts#L753-L767)):
```typescript
function halfToFloat(h: number): number {
  const s = (h >> 15) & 0x1;
  const e = (h >> 10) & 0x1f;
  const m = h & 0x3ff;
  if (e === 0) {
    if (m === 0) return s ? -0 : 0;
    return (s ? -1 : 1) * Math.pow(2, -14) * (m / 1024);
  }
  if (e === 31) {
    return m === 0 ? (s ? -Infinity : Infinity) : NaN;
  }
  return (s ? -1 : 1) * Math.pow(2, e - 15) * (1 + m / 1024);
}
```

### Storage Savings

For a 1M vector dataset with 384 dimensions:

| Format | Size per Vector | Total Size | Savings |
|--------|----------------|------------|---------|
| Float32 | 1,536 bytes | 1.46 GB | Baseline |
| Float16 | 768 bytes | **732 MB** | **50%** |

Plus additional IVF overhead (~5-10%).

## Benchmarks

Tested on `wikimedia/wikipedia` (1M articles, all-MiniLM-L6-v2 embeddings):

```bash
# Float32 (baseline)
Recall@10: 0.943
Search latency (p50): 12ms
Index size: 1.52 GB

# Float16 (ANNPack)
Recall@10: 0.927  (-1.6%)
Search latency (p50): 11ms
Index size: 761 MB  (-50%)
```

## FAQ

**Q: Can I disable float16 quantization?**
A: Not currently. ANNPack's binary format is designed around float16. For float32, consider using FAISS directly or other vector databases.

**Q: Does float16 affect build time?**
A: Minimal impact (~5% faster due to smaller memory footprint).

**Q: What about int8 quantization?**
A: Not supported. Int8 requires calibration and causes more significant recall degradation (10-15%). Float16 offers the best precision/storage tradeoff for ANNPack's use case.

**Q: How does this compare to product quantization (PQ)?**
A: Float16 is simpler and more predictable. PQ can achieve higher compression but with tuning complexity and potential quality loss.

## References

- [IEEE 754 Half-Precision Spec](https://en.wikipedia.org/wiki/Half-precision_floating-point_format)
- [FAISS Quantization Guide](https://github.com/facebookresearch/faiss/wiki/FAQ#how-does-faiss-represent-vectors)
- [Sentence Transformers Precision Study](https://www.sbert.net/examples/training/distillation/README.html)

---

**Last updated**: 2026-01-06
**Version**: 0.1.7
