# Changelog

## 0.1.7
- **Code Quality Improvements**: Extracted `_read_header()` to shared module, eliminating duplication across api.py, verify.py, and packset.py
- **TypeScript Enhancements**: Added request timeouts (30s default) to all fetch calls to prevent hanging requests
- **Documentation**: Added comprehensive float16 precision documentation (docs/FLOAT16_PRECISION.md) with benchmarks and best practices
- **Type Safety**: Improved type hints and added docstrings to `_MetaLookup` and `_try_import_torch()`
- **All 39 tests passing**: Verified backward compatibility

## 0.1.6
- Version bump for PyPI publish (0.1.5 artifacts already released)
- Same release contents as 0.1.5

## 0.1.5
- Deterministic tiny-dataset centroid fallback to avoid FAISS aborts
- Registry defaults hardened with required secrets, upload caps, and rate limits
- Overflow checks and safer allocations in ann_engine
- Security tooling (CodeQL, audits) and documentation updates

## 0.1.4
- Stage-all gate script and CI integration
- Packaging exclusions for web build artifacts
- Dev extras include build/twine for release checks

## 0.1.3
- PackSet lifecycle commands + canary tooling
- Web client + UI workspaces and registry skeleton
- Structured logging helpers and extended docs

## 0.1.2
- PEP 561 typing marker and expanded API/CLI docs
- Minimal web client skeleton and WASM build notes
- CI scripts for smoke + determinism checks
- Documentation improvements and release script
