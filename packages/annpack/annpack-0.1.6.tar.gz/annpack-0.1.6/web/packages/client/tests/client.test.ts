import { describe, expect, it, vi } from 'vitest';
import { MemoryCache } from '../src/cache';
import { RangeFetcher } from '../src/http';
import { openPack } from '../src/pack';

const makeResponse = (status: number, body: Uint8Array, headers?: Record<string, string>) => {
  const map = headers ?? {};
  return {
    status,
    ok: status >= 200 && status < 300,
    headers: { get: (key: string) => map[key] ?? null },
    arrayBuffer: async () => body.buffer.slice(body.byteOffset, body.byteOffset + body.byteLength),
  } as Response;
};

const buildTinyAnnpack = () => {
  const headerSize = 72;
  const dim = 2;
  const nLists = 1;
  const nVectors = 1;
  const centroidsBytes = nLists * dim * 4;
  const listOffset = headerSize + centroidsBytes;
  const listLength = 4 + 8 + dim * 2;
  const tablePos = listOffset + listLength;
  const total = tablePos + nLists * 16;
  const buf = new ArrayBuffer(total);
  const view = new DataView(buf);

  view.setBigUint64(0, BigInt(0x504e4e41), true);
  view.setUint32(8, 1, true);
  view.setUint32(12, 1, true);
  view.setUint32(16, headerSize, true);
  view.setUint32(20, dim, true);
  view.setUint32(24, 1, true);
  view.setUint32(28, nLists, true);
  view.setUint32(32, nVectors, true);
  view.setBigUint64(36, BigInt(tablePos), true);

  view.setFloat32(headerSize, 1, true);
  view.setFloat32(headerSize + 4, 0, true);

  view.setUint32(listOffset, 1, true);
  view.setBigUint64(listOffset + 4, BigInt(7), true);
  view.setUint16(listOffset + 12, 0x3c00, true);
  view.setUint16(listOffset + 14, 0x0000, true);

  view.setBigUint64(tablePos, BigInt(listOffset), true);
  view.setBigUint64(tablePos + 8, BigInt(listLength), true);

  return new Uint8Array(buf);
};

describe('MemoryCache', () => {
  it('stores and retrieves entries', async () => {
    const cache = new MemoryCache();
    await cache.set({ key: 'k', bytes: new Uint8Array([1, 2]), etag: 'x' });
    const entry = await cache.get('k');
    expect(entry?.etag).toBe('x');
    expect(entry?.bytes[0]).toBe(1);
  });
});

describe('RangeFetcher', () => {
  it('uses If-None-Match and cache on 304', async () => {
    const cache = new MemoryCache();
    await cache.set({ key: 'u:0-1', bytes: new Uint8Array([1, 2]), etag: 'etag1' });

    const fetchMock = vi.fn().mockResolvedValue(makeResponse(304, new Uint8Array(), {}));
    // @ts-expect-error override global fetch
    globalThis.fetch = fetchMock;

    const rf = new RangeFetcher({ cache });
    const resp = await rf.fetchRange('u', 0, 1);
    expect(resp.bytes[0]).toBe(1);
    expect(fetchMock.mock.calls[0][1]?.headers?.['If-None-Match']).toBe('etag1');
  });
});

describe('openPack', () => {
  it('parses manifest', async () => {
    const manifest = { schema_version: 2, shards: [{ name: 's', annpack: 'a', meta: 'm' }] };
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => manifest,
    });
    // @ts-expect-error override global fetch
    globalThis.fetch = fetchMock;

    const pack = await openPack('http://example/pack.manifest.json');
    expect(pack.manifest.shards.length).toBe(1);
  });
});

describe('Pack search', () => {
  it('searches annpack via range fetch', async () => {
    const annpack = buildTinyAnnpack();
    const manifest = {
      schema_version: 2,
      shards: [{ name: 's', annpack: 'pack.annpack', meta: 'pack.meta.jsonl' }],
    };

    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (url.endsWith('pack.manifest.json')) {
        return {
          ok: true,
          status: 200,
          json: async () => manifest,
        } as Response;
      }
      if (url.endsWith('pack.annpack') && init?.headers) {
        const range = (init.headers as Record<string, string>).Range;
        if (!range) {
          throw new Error('Missing Range header');
        }
        const [startStr, endStr] = range.replace('bytes=', '').split('-');
        const start = Number(startStr);
        const end = Number(endStr);
        const slice = annpack.slice(start, end + 1);
        return makeResponse(206, slice, { ETag: 'etag1' });
      }
      throw new Error(`unexpected fetch ${url}`);
    });
    // @ts-expect-error override global fetch
    globalThis.fetch = fetchMock;

    const pack = await openPack('http://example/pack.manifest.json', { meta: { load: false } });
    const hits = await pack.search({
      queryVector: [1, 0],
      topK: 1,
      normalized: true,
      probe: 1,
    });
    expect(hits.length).toBe(1);
    expect(hits[0].id).toBe(7);
  });
});
