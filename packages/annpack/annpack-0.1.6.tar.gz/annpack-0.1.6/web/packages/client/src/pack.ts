import { RangeFetcher } from './http';
import { Cache } from './cache';
import {
  DeltaEntry,
  ManifestShard,
  ManifestV2,
  ManifestV3,
  SearchRequest,
  SearchResult,
  TelemetryHook,
} from './types';

export type PackLimits = {
  maxDim?: number;
  maxLists?: number;
  maxListBytes?: number;
  maxCentroidBytes?: number;
  maxTableBytes?: number;
  maxProbe?: number;
  maxTopK?: number;
};

export type MetaOptions = {
  load?: boolean;
  maxBytes?: number;
  maxLineBytes?: number;
  allowLarge?: boolean;
};

export type PackOptions = {
  fetcher?: RangeFetcher;
  cache?: Cache;
  telemetry?: TelemetryHook;
  verify?: boolean;
  limits?: PackLimits;
  meta?: MetaOptions;
  probe?: number;
};

type Header = {
  magic: number;
  version: number;
  endian: number;
  headerSize: number;
  dim: number;
  metric: number;
  nLists: number;
  nVectors: number;
  offsetTablePos: number;
};

type IndexData = {
  header: Header;
  centroids: Float32Array;
  offsets: Float64Array;
  lengths: Float64Array;
};

type MetaMode = 'none' | 'ids' | 'full';

type MetaState = {
  mode: MetaMode;
  ids: Set<number>;
  rows?: Map<number, Record<string, unknown>>;
};

type ShardState = {
  shard: ManifestShard;
  name: string;
  annpackUrl: string;
  metaUrl: string;
  header?: Header;
  headerPromise?: Promise<Header>;
  indexPromise?: Promise<IndexData>;
  meta?: MetaState;
  metaPromise?: Promise<MetaState>;
  metaMode?: MetaMode;
};

type DeltaState = {
  entry: DeltaEntry;
  pack: Pack;
  tombstones: Set<number>;
  overriddenIds: Set<number>;
};

const DEFAULT_LIMITS: Required<PackLimits> = {
  maxDim: 4096,
  maxLists: 1_000_000,
  maxListBytes: 64 * 1024 * 1024,
  maxCentroidBytes: 512 * 1024 * 1024,
  maxTableBytes: 256 * 1024 * 1024,
  maxProbe: 64,
  maxTopK: 1000,
};

const DEFAULT_META: Required<MetaOptions> = {
  load: false,
  maxBytes: 64 * 1024 * 1024,
  maxLineBytes: 1024 * 1024,
  allowLarge: false,
};

const DEFAULT_PROBE = 8;

export class Pack {
  readonly manifest: ManifestV2;
  readonly baseUrl: string;
  private fetcher: RangeFetcher;
  private telemetry?: TelemetryHook;
  private limits: Required<PackLimits>;
  private metaOpts: Required<MetaOptions>;
  private probe: number;
  private shards: ShardState[];

  constructor(manifest: ManifestV2, baseUrl: string, opts: PackOptions = {}) {
    this.manifest = manifest;
    this.baseUrl = baseUrl;
    this.fetcher =
      opts.fetcher ?? new RangeFetcher({ cache: opts.cache, telemetry: opts.telemetry });
    this.telemetry = opts.telemetry;
    this.limits = resolveLimits(opts.limits);
    this.metaOpts = resolveMeta(opts.meta);
    this.probe = opts.probe ?? DEFAULT_PROBE;
    this.shards = manifest.shards.map((shard) => {
      const annpackUrl = new URL(shard.annpack, baseUrl).toString();
      const metaUrl = new URL(shard.meta, baseUrl).toString();
      return {
        shard,
        name: shard.name ?? shard.annpack,
        annpackUrl,
        metaUrl,
      };
    });
  }

  async search(req: SearchRequest): Promise<SearchResult[]> {
    const query = toFloat32Array(req.queryVector);
    const vector = req.normalized ? query : normalizeVector(query);
    const topK = clampInt(req.topK, 1, this.limits.maxTopK, 'topK');
    const hasFilters = req.filters && Object.keys(req.filters).length > 0;
    if (hasFilters && !this.metaOpts.load) {
      throw new Error('Filters require metadata loading; set meta.load=true');
    }

    this.telemetry?.({ name: 'search', detail: { topK } });

    const perShardK = hasFilters ? Math.min(this.limits.maxTopK, topK * 5) : topK;
    const shardResults = await Promise.all(
      this.shards.map((shard) => this.searchShard(shard, vector, perShardK, req)),
    );
    const merged = shardResults.flat();
    merged.sort((a, b) => b.score - a.score);
    const filtered = hasFilters ? applyFilters(merged, req.filters!) : merged;
    return filtered.slice(0, topK);
  }

  async readHeader(): Promise<Record<string, number>> {
    const header = await this.loadHeader(this.shards[0]);
    return {
      magic: header.magic,
      version: header.version,
      endian: header.endian,
      headerSize: header.headerSize,
      dim: header.dim,
      metric: header.metric,
      nLists: header.nLists,
      nVectors: header.nVectors,
      offsetTablePos: header.offsetTablePos,
    };
  }

  private async searchShard(
    shard: ShardState,
    vector: Float32Array,
    topK: number,
    req: SearchRequest,
  ): Promise<SearchResult[]> {
    const index = await this.loadIndexData(shard);
    const header = index.header;

    if (vector.length !== header.dim) {
      throw new Error(`Vector length ${vector.length} does not match dim ${header.dim}`);
    }

    const probe = clampInt(req.probe ?? this.probe, 1, this.limits.maxProbe, 'probe');
    const bestLists = new Int32Array(probe);
    const bestScores = new Float32Array(probe);
    for (let i = 0; i < probe; i += 1) {
      bestLists[i] = -1;
      bestScores[i] = -1e9;
    }

    for (let listId = 0; listId < header.nLists; listId += 1) {
      const score = dotCentroid(index.centroids, listId, header.dim, vector);
      if (score > bestScores[probe - 1]) {
        let pos = probe - 1;
        while (pos > 0 && score > bestScores[pos - 1]) {
          pos -= 1;
        }
        for (let m = probe - 1; m > pos; m -= 1) {
          bestScores[m] = bestScores[m - 1];
          bestLists[m] = bestLists[m - 1];
        }
        bestScores[pos] = score;
        bestLists[pos] = listId;
      }
    }

    const topScores = new Float32Array(topK);
    const topIds: number[] = new Array(topK);
    const topSources: string[] = new Array(topK);
    let topCount = 0;
    for (let i = 0; i < topK; i += 1) {
      topScores[i] = -1e9;
    }

    for (let p = 0; p < bestLists.length; p += 1) {
      const listId = bestLists[p];
      if (listId < 0) {
        continue;
      }
      const offset = index.offsets[listId];
      const length = index.lengths[listId];
      if (length <= 0 || length > this.limits.maxListBytes) {
        this.telemetry?.({
          name: 'list_skip',
          detail: { shard: shard.name, listId, length },
        });
        continue;
      }
      const end = offset + length - 1;
      const resp = await this.fetcher.fetchRange(shard.annpackUrl, offset, end);
      const bytes = resp.bytes;
      if (bytes.byteLength < 4) {
        continue;
      }

      const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
      const count = view.getUint32(0, true);
      if (count === 0) {
        continue;
      }
      const needed = 4 + count * 8 + count * header.dim * 2;
      if (needed > bytes.byteLength) {
        continue;
      }

      const vecBase = 4 + count * 8;
      for (let i = 0; i < count; i += 1) {
        let score = 0;
        const vecOffset = vecBase + i * header.dim * 2;
        for (let d = 0; d < header.dim; d += 1) {
          const half = view.getUint16(vecOffset + d * 2, true);
          score += vector[d] * halfToFloat(half);
        }

        if (topCount < topK || score > topScores[topCount - 1]) {
          const idOffset = 4 + i * 8;
          const id = numberFromBigInt(view.getBigUint64(idOffset, true), 'id');
          let pos = topCount > 0 ? Math.min(topCount - 1, topK - 1) : 0;
          while (pos >= 0 && score > topScores[pos]) {
            pos -= 1;
          }
          pos += 1;
          if (topCount < topK) {
            topCount += 1;
          }
          for (let m = topCount - 1; m > pos; m -= 1) {
            topScores[m] = topScores[m - 1];
            topIds[m] = topIds[m - 1];
            topSources[m] = topSources[m - 1];
          }
          topScores[pos] = score;
          topIds[pos] = id;
          topSources[pos] = shard.name;
        }
      }
    }

    const wantMeta = this.metaOpts.load;
    const metaState = wantMeta ? await this.loadMeta(shard, 'full') : undefined;
    const results: SearchResult[] = [];
    for (let i = 0; i < topCount; i += 1) {
      const id = topIds[i];
      results.push({
        id,
        score: Number(topScores[i]),
        source: topSources[i],
        meta: metaState?.rows?.get(id) ?? null,
      });
    }
    return results;
  }

  private async loadHeader(shard: ShardState): Promise<Header> {
    if (shard.header) {
      return shard.header;
    }
    if (shard.headerPromise) {
      return shard.headerPromise;
    }
    shard.headerPromise = (async () => {
      const resp = await this.fetcher.fetchRange(shard.annpackUrl, 0, 71);
      if (resp.bytes.byteLength < 72) {
        throw new Error('Header too small');
      }
      const view = new DataView(resp.bytes.buffer, resp.bytes.byteOffset, 72);
      const magic = numberFromBigInt(view.getBigUint64(0, true), 'magic');
      const version = view.getUint32(8, true);
      const endian = view.getUint32(12, true);
      const headerSize = view.getUint32(16, true);
      const dim = view.getUint32(20, true);
      const metric = view.getUint32(24, true);
      const nLists = view.getUint32(28, true);
      const nVectors = view.getUint32(32, true);
      const offsetTablePos = numberFromBigInt(view.getBigUint64(36, true), 'offset_table_pos');

      if (magic !== 0x504e4e41) {
        throw new Error('Invalid magic');
      }
      if (version !== 1 || endian !== 1) {
        throw new Error('Unsupported header');
      }
      if (headerSize < 72) {
        throw new Error('Invalid header size');
      }
      if (dim <= 0 || dim > this.limits.maxDim) {
        throw new Error(`dim out of bounds: ${dim}`);
      }
      if (nLists <= 0 || nLists > this.limits.maxLists) {
        throw new Error(`nLists out of bounds: ${nLists}`);
      }
      if (offsetTablePos <= headerSize) {
        throw new Error('Invalid offset table position');
      }

      const header: Header = {
        magic,
        version,
        endian,
        headerSize,
        dim,
        metric,
        nLists,
        nVectors,
        offsetTablePos,
      };
      shard.header = header;
      return header;
    })();
    return shard.headerPromise;
  }

  private async loadIndexData(shard: ShardState): Promise<IndexData> {
    if (shard.indexPromise) {
      return shard.indexPromise;
    }
    shard.indexPromise = (async () => {
      const header = await this.loadHeader(shard);
      const centroidsBytes = header.nLists * header.dim * 4;
      if (centroidsBytes > this.limits.maxCentroidBytes) {
        throw new Error(`Centroids too large: ${centroidsBytes} bytes`);
      }
      const centroidsResp = await this.fetcher.fetchRange(
        shard.annpackUrl,
        header.headerSize,
        header.headerSize + centroidsBytes - 1,
      );
      if (centroidsResp.bytes.byteLength !== centroidsBytes) {
        throw new Error('Centroid fetch length mismatch');
      }
      const centroids = new Float32Array(
        centroidsResp.bytes.buffer,
        centroidsResp.bytes.byteOffset,
        centroidsResp.bytes.byteLength / 4,
      );

      const tableBytes = header.nLists * 16;
      if (tableBytes > this.limits.maxTableBytes) {
        throw new Error(`Offset table too large: ${tableBytes} bytes`);
      }
      const tableResp = await this.fetcher.fetchRange(
        shard.annpackUrl,
        header.offsetTablePos,
        header.offsetTablePos + tableBytes - 1,
      );
      if (tableResp.bytes.byteLength !== tableBytes) {
        throw new Error('Offset table fetch length mismatch');
      }
      const offsets = new Float64Array(header.nLists);
      const lengths = new Float64Array(header.nLists);
      const view = new DataView(
        tableResp.bytes.buffer,
        tableResp.bytes.byteOffset,
        tableResp.bytes.byteLength,
      );
      for (let i = 0; i < header.nLists; i += 1) {
        const off = numberFromBigInt(view.getBigUint64(i * 16, true), 'offset');
        const len = numberFromBigInt(view.getBigUint64(i * 16 + 8, true), 'length');
        offsets[i] = off;
        lengths[i] = len;
      }
      return { header, centroids, offsets, lengths };
    })();
    return shard.indexPromise;
  }

  private async loadMeta(shard: ShardState, mode: MetaMode): Promise<MetaState> {
    if (mode === 'none') {
      return { mode: 'none', ids: new Set() };
    }
    if (shard.meta && (shard.meta.mode === 'full' || shard.meta.mode === mode)) {
      return shard.meta;
    }
    if (
      shard.metaPromise &&
      shard.metaMode &&
      (shard.metaMode === 'full' || shard.metaMode === mode)
    ) {
      return shard.metaPromise;
    }
    shard.metaMode = mode;
    shard.metaPromise = loadMetaFromUrl(shard.metaUrl, this.metaOpts, mode).then((meta) => {
      shard.meta = meta;
      return meta;
    });
    return shard.metaPromise;
  }
}

export class PackSet {
  readonly manifest: ManifestV3;
  readonly baseUrl: string;
  readonly deltas: DeltaEntry[];
  private basePack: Pack;
  private deltaStates: DeltaState[];
  private telemetry?: TelemetryHook;
  private limits: Required<PackLimits>;
  private metaOpts: Required<MetaOptions>;
  private probe: number;
  private tombstonedIds: Set<number>;
  private overriddenIds: Set<number>;

  constructor(
    manifest: ManifestV3,
    baseUrl: string,
    basePack: Pack,
    deltaStates: DeltaState[],
    telemetry?: TelemetryHook,
    limits?: PackLimits,
    metaOpts?: MetaOptions,
    probe?: number,
  ) {
    this.manifest = manifest;
    this.baseUrl = baseUrl;
    this.basePack = basePack;
    this.deltas = deltaStates.map((state) => state.entry);
    this.deltaStates = deltaStates;
    this.telemetry = telemetry;
    this.limits = resolveLimits(limits);
    this.metaOpts = resolveMeta(metaOpts);
    this.probe = probe ?? DEFAULT_PROBE;
    this.tombstonedIds = new Set();
    this.overriddenIds = new Set();
    for (const delta of deltaStates) {
      for (const id of delta.tombstones) {
        this.tombstonedIds.add(id);
      }
      for (const id of delta.overriddenIds) {
        this.overriddenIds.add(id);
      }
    }
  }

  async search(req: SearchRequest): Promise<SearchResult[]> {
    const query = toFloat32Array(req.queryVector);
    const vector = req.normalized ? query : normalizeVector(query);
    const topK = clampInt(req.topK, 1, this.limits.maxTopK, 'topK');
    const perPackK = Math.min(this.limits.maxTopK, Math.max(topK * 5, topK));
    const probe = clampInt(req.probe ?? this.probe, 1, this.limits.maxProbe, 'probe');

    this.telemetry?.({ name: 'packset_search', detail: { topK } });

    const seen = new Set<number>();
    const results: SearchResult[] = [];

    const deltas = this.deltaStates.slice().sort((a, b) => b.entry.seq - a.entry.seq);
    for (const delta of deltas) {
      const hits = await delta.pack.search({
        queryVector: vector,
        topK: perPackK,
        normalized: true,
        probe,
        filters: req.filters,
      });
      for (const row of hits) {
        if (this.tombstonedIds.has(row.id) || seen.has(row.id)) {
          continue;
        }
        seen.add(row.id);
        results.push({ ...row, source: `delta:${delta.entry.seq}` });
        if (results.length >= topK) {
          return results;
        }
      }
    }

    const baseHits = await this.basePack.search({
      queryVector: vector,
      topK: perPackK,
      normalized: true,
      probe,
      filters: req.filters,
    });

    for (const row of baseHits) {
      if (this.tombstonedIds.has(row.id) || this.overriddenIds.has(row.id) || seen.has(row.id)) {
        continue;
      }
      results.push({ ...row, source: row.source ?? 'base' });
      if (results.length >= topK) {
        break;
      }
    }
    return results;
  }

  async readHeader(): Promise<Record<string, number>> {
    return this.basePack.readHeader();
  }
}

export async function openPack(source: string | File, opts: PackOptions = {}): Promise<Pack> {
  const manifest =
    typeof source === 'string' ? await fetchJson<ManifestV2>(source) : await parseFile(source);
  if (!manifest.shards || manifest.shards.length === 0) {
    throw new Error('manifest has no shards');
  }
  const baseUrl = typeof source === 'string' ? new URL('.', source).toString() : 'file://';
  const pack = new Pack(manifest, baseUrl, opts);
  if (opts.verify) {
    await verifyManifest(manifest, baseUrl);
  }
  return pack;
}

export async function openPackSet(
  baseUrl: string,
  deltaUrls: string[] = [],
  opts: PackOptions = {},
): Promise<PackSet> {
  const maybeManifest = await fetchJson<ManifestV3 | ManifestV2>(baseUrl);
  if ((maybeManifest as ManifestV3).schema_version === 3) {
    const manifest = maybeManifest as ManifestV3;
    const baseDir = new URL('.', baseUrl).toString();
    const baseManifestUrl = new URL(
      'pack.manifest.json',
      new URL(manifest.base.annpack, baseDir),
    ).toString();
    const basePack = await openPack(baseManifestUrl, opts);
    const deltas = (manifest.deltas ?? []).slice().sort((a, b) => a.seq - b.seq);
    const metaOpts = resolveMeta(opts.meta);

    const deltaStates: DeltaState[] = [];
    for (const entry of deltas) {
      const deltaManifest: ManifestV2 = {
        schema_version: 2,
        shards: [
          {
            name: `delta-${entry.seq}`,
            annpack: entry.annpack,
            meta: entry.meta,
          },
        ],
      };
      const pack = new Pack(deltaManifest, baseDir, opts);
      const tombstonesUrl = new URL(entry.tombstones, baseDir).toString();
      const tombstones = await loadTombstones(tombstonesUrl, metaOpts);
      const metaMode: MetaMode = metaOpts.load ? 'full' : 'ids';
      const meta = await loadMetaFromUrl(
        new URL(entry.meta, baseDir).toString(),
        metaOpts,
        metaMode,
      );
      deltaStates.push({ entry, pack, tombstones, overriddenIds: meta.ids });
    }

    if (opts.verify) {
      await verifyPackSet(manifest, baseDir);
    }
    return new PackSet(
      manifest,
      baseDir,
      basePack,
      deltaStates,
      opts.telemetry,
      opts.limits,
      opts.meta,
      opts.probe,
    );
  }

  const baseManifest = maybeManifest as ManifestV2;
  if (opts.verify) {
    await verifyManifest(baseManifest, new URL('.', baseUrl).toString());
  }
  const basePack = new Pack(baseManifest, new URL('.', baseUrl).toString(), opts);
  const synthetic: ManifestV3 = {
    schema_version: 3,
    base: {
      annpack: basePack.manifest.shards[0].annpack,
      meta: basePack.manifest.shards[0].meta,
    },
    deltas: deltaUrls.map((url, idx) => ({
      seq: idx + 1,
      annpack: url,
      meta: url,
      tombstones: url,
    })),
  };
  return new PackSet(synthetic, new URL('.', baseUrl).toString(), basePack, [], opts.telemetry);
}

async function fetchJson<T>(url: string): Promise<T> {
  const resp = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!resp.ok) {
    throw new Error(`Failed to fetch ${url}: ${resp.status}`);
  }
  return (await resp.json()) as T;
}

async function parseFile(file: File): Promise<ManifestV2> {
  const text = await file.text();
  return JSON.parse(text) as ManifestV2;
}

async function verifyManifest(manifest: ManifestV2, baseUrl: string): Promise<void> {
  for (const shard of manifest.shards) {
    await verifyFile(new URL(shard.annpack, baseUrl).toString());
    await verifyFile(new URL(shard.meta, baseUrl).toString());
  }
}

async function verifyPackSet(manifest: ManifestV3, baseUrl: string): Promise<void> {
  await verifyFile(
    new URL(manifest.base.annpack, baseUrl).toString(),
    manifest.base.sha256_annpack,
  );
  await verifyFile(new URL(manifest.base.meta, baseUrl).toString(), manifest.base.sha256_meta);
  for (const delta of manifest.deltas ?? []) {
    await verifyFile(new URL(delta.annpack, baseUrl).toString(), delta.sha256_annpack);
    await verifyFile(new URL(delta.meta, baseUrl).toString(), delta.sha256_meta);
    await verifyFile(new URL(delta.tombstones, baseUrl).toString(), delta.sha256_tombstones);
  }
}

async function verifyFile(url: string, expected?: string): Promise<void> {
  if (!expected) {
    return;
  }
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`Integrity check failed: ${url} (${resp.status})`);
  }
  const buf = await resp.arrayBuffer();
  const hash = await sha256Hex(buf);
  if (hash !== expected) {
    throw new Error(`Hash mismatch for ${url}`);
  }
}

async function sha256Hex(buf: ArrayBuffer): Promise<string> {
  if (!globalThis.crypto?.subtle) {
    throw new Error('WebCrypto is unavailable; integrity checks require crypto.subtle');
  }
  const digest = await globalThis.crypto.subtle.digest('SHA-256', buf);
  return toHex(new Uint8Array(digest));
}

function toHex(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function resolveLimits(opts?: PackLimits): Required<PackLimits> {
  return { ...DEFAULT_LIMITS, ...opts };
}

function resolveMeta(opts?: MetaOptions): Required<MetaOptions> {
  return { ...DEFAULT_META, ...opts };
}

function clampInt(value: number, min: number, max: number, label: string): number {
  if (!Number.isFinite(value)) {
    throw new Error(`${label} must be a finite number`);
  }
  const rounded = Math.floor(value);
  if (rounded < min) {
    return min;
  }
  if (rounded > max) {
    return max;
  }
  return rounded;
}

function numberFromBigInt(value: bigint, label: string): number {
  if (value > BigInt(Number.MAX_SAFE_INTEGER)) {
    throw new Error(`${label} exceeds max safe integer`);
  }
  return Number(value);
}

function toFloat32Array(input: number[] | Float32Array): Float32Array {
  if (input instanceof Float32Array) {
    return input;
  }
  return new Float32Array(input);
}

function normalizeVector(vec: Float32Array): Float32Array {
  let sum = 0;
  for (let i = 0; i < vec.length; i += 1) {
    sum += vec[i] * vec[i];
  }
  const norm = Math.sqrt(sum);
  if (!Number.isFinite(norm) || norm === 0) {
    throw new Error('Zero vector');
  }
  const out = new Float32Array(vec.length);
  for (let i = 0; i < vec.length; i += 1) {
    out[i] = vec[i] / norm;
  }
  return out;
}

function dotCentroid(
  centroids: Float32Array,
  listId: number,
  dim: number,
  query: Float32Array,
): number {
  let score = 0;
  const base = listId * dim;
  for (let i = 0; i < dim; i += 1) {
    score += centroids[base + i] * query[i];
  }
  return score;
}

function halfToFloat(h: number): number {
  const s = (h >> 15) & 0x1;
  const e = (h >> 10) & 0x1f;
  const m = h & 0x3ff;
  if (e === 0) {
    if (m === 0) {
      return s ? -0 : 0;
    }
    return (s ? -1 : 1) * Math.pow(2, -14) * (m / 1024);
  }
  if (e === 31) {
    return m === 0 ? (s ? -Infinity : Infinity) : NaN;
  }
  return (s ? -1 : 1) * Math.pow(2, e - 15) * (1 + m / 1024);
}

async function loadMetaFromUrl(
  url: string,
  opts: Required<MetaOptions>,
  mode: MetaMode,
): Promise<MetaState> {
  if (mode === 'none') {
    return { mode: 'none', ids: new Set() };
  }
  const resp = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!resp.ok) {
    throw new Error(`Failed to fetch metadata: ${resp.status}`);
  }
  const sizeHeader = resp.headers.get('Content-Length');
  if (sizeHeader && !opts.allowLarge) {
    const size = Number(sizeHeader);
    if (Number.isFinite(size) && size > opts.maxBytes) {
      throw new Error(`Metadata exceeds maxBytes (${opts.maxBytes})`);
    }
  }
  const text = await resp.text();
  if (!opts.allowLarge && text.length > opts.maxBytes) {
    throw new Error(`Metadata exceeds maxBytes (${opts.maxBytes})`);
  }

  const ids = new Set<number>();
  const rows = mode === 'full' ? new Map<number, Record<string, unknown>>() : undefined;
  const lines = text.split(/\r?\n/);
  for (const line of lines) {
    if (!line.trim()) {
      continue;
    }
    if (line.length > opts.maxLineBytes) {
      throw new Error('Metadata line exceeds maxLineBytes');
    }
    const row = JSON.parse(line) as Record<string, unknown>;
    if (row.id === undefined || row.id === null) {
      continue;
    }
    const id = Number(row.id);
    if (!Number.isFinite(id)) {
      continue;
    }
    ids.add(id);
    if (rows) {
      rows.set(id, row);
    }
  }
  return { mode, ids, rows };
}

async function loadTombstones(url: string, opts: Required<MetaOptions>): Promise<Set<number>> {
  const resp = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!resp.ok) {
    throw new Error(`Failed to fetch tombstones: ${resp.status}`);
  }
  const sizeHeader = resp.headers.get('Content-Length');
  if (sizeHeader && !opts.allowLarge) {
    const size = Number(sizeHeader);
    if (Number.isFinite(size) && size > opts.maxBytes) {
      throw new Error(`Tombstones exceed maxBytes (${opts.maxBytes})`);
    }
  }
  const text = await resp.text();
  if (!opts.allowLarge && text.length > opts.maxBytes) {
    throw new Error(`Tombstones exceed maxBytes (${opts.maxBytes})`);
  }
  const ids = new Set<number>();
  const lines = text.split(/\r?\n/);
  for (const line of lines) {
    if (!line.trim()) {
      continue;
    }
    if (line.length > opts.maxLineBytes) {
      throw new Error('Tombstone line exceeds maxLineBytes');
    }
    const row = JSON.parse(line) as Record<string, unknown>;
    if (row.id === undefined || row.id === null) {
      continue;
    }
    const id = Number(row.id);
    if (Number.isFinite(id)) {
      ids.add(id);
    }
  }
  return ids;
}

function applyFilters(
  rows: SearchResult[],
  filters: Record<string, string | number | boolean>,
): SearchResult[] {
  return rows.filter((row) => {
    if (!row.meta) {
      return false;
    }
    for (const [key, value] of Object.entries(filters)) {
      if ((row.meta as Record<string, unknown>)[key] !== value) {
        return false;
      }
    }
    return true;
  });
}
