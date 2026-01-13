"""ANNPack command-line interface."""

from __future__ import annotations

import argparse
import http.client
import os
import json
import mimetypes
import shutil
import socket
import sys
import threading
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from importlib import resources
from importlib.resources import as_file

from typing import Any, Dict, List, Optional, Sequence, Tuple, cast

from .build import build_index, build_index_from_hf_wikipedia
from .logutil import log_event
from .verify import (
    diagnose_env,
    inspect_pack,
    sign_manifest,
    verify_pack,
    verify_manifest_signature,
)
from .packset import (
    build_delta,
    build_packset_base,
    create_packset,
    packset_status,
    promote_delta,
    rebase_packset,
    revert_packset,
    run_canary,
    update_packset_manifest,
)
from . import __version__


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_header(path: Path) -> Dict[str, int]:
    """Read ANNPack header fields from a file path."""
    import struct

    with open(path, "rb") as f:
        header = f.read(72)
    magic, version, endian, header_size, dim, metric, n_lists, n_vectors, offset_table_pos = (
        struct.unpack("<QIIIIIIIQ", header[:44])
    )
    return {
        "magic": magic,
        "version": version,
        "endian": endian,
        "header_size": header_size,
        "dim": dim,
        "metric": metric,
        "n_lists": n_lists,
        "n_vectors": n_vectors,
        "offset_table_pos": offset_table_pos,
    }


def _find_manifest(pack_dir: Path) -> Optional[Path]:
    """Return the first manifest in a pack directory, if any."""
    candidates = (
        list(pack_dir.glob("*.manifest.json"))
        + list(pack_dir.glob("manifest.json"))
        + list(pack_dir.glob("manifest.jsonl"))
    )
    return candidates[0] if candidates else None


def _materialize_ui_root() -> Path:
    """Copy packaged UI assets to a temp dir and return its path."""
    ui = resources.files("annpack.ui")
    tmp = Path(tempfile.mkdtemp(prefix="annpack_ui_"))
    with as_file(ui) as ui_path:
        if ui_path.is_dir():
            shutil.copytree(ui_path, tmp, dirs_exist_ok=True)
        else:
            shutil.copy(ui_path, tmp / "index.html")
    return tmp


def _write_manifest(
    prefix: Path, ann_path: Path, meta_path: Path, build_info: Optional[Dict[str, Any]] = None
) -> Path:
    """Write a simple shard manifest if missing."""
    info = _read_header(ann_path)
    manifest = {
        "schema_version": 2,
        "version": 1,
        "created_by": "annpack.cli",
        "dim": info["dim"],
        "n_lists": info["n_lists"],
        "n_vectors": info["n_vectors"],
        "shards": [
            {
                "name": prefix.name,
                "annpack": ann_path.name,
                "meta": meta_path.name,
                "n_vectors": info["n_vectors"],
            }
        ],
    }
    if build_info:
        manifest["build"] = build_info
    manifest_path = prefix.with_suffix(".manifest.json")
    if manifest_path.exists():
        print(f"[write] Manifest already exists, keeping: {manifest_path}")
        return manifest_path
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[write] Manifest: {manifest_path}")
    return manifest_path


def _port_in_use(host: str, port: int) -> bool:
    """Return True if host:port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def _start_http_server(
    host: str, port: int, root_dir: Path, pack_dir: Path, quiet: bool = False
) -> ThreadingHTTPServer:
    """Start a threaded HTTP server with /pack mounted."""

    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self, path: str) -> str:
            parsed = urlparse(path)
            clean = parsed.path
            base_root = Path(root_dir)
            base_pack = Path(pack_dir)
            if clean.startswith("/pack/"):
                rel = clean[len("/pack/") :]
                base = base_pack
            else:
                rel = clean.lstrip("/")
                base = base_root
            return str((base / rel).resolve())

        def do_GET(self) -> None:  # noqa: N802
            if self.path.rstrip("/") == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
                return
            super().do_GET()

        def end_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, fmt: str, *args: Any) -> None:
            if quiet:
                return
            super().log_message(fmt, *args)

    server = ThreadingHTTPServer((host, port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _health_check(url: str) -> Tuple[int, bytes]:
    """Fetch a URL and return (status, body)."""
    req = Request(url, headers={"User-Agent": "annpack-smoke"})
    with urlopen(req, timeout=5) as resp:
        return resp.status, resp.read()


def _parse_delete_ids(raw: Optional[str], path: Optional[str]) -> List[int]:
    ids: List[int] = []
    if raw:
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            ids.append(int(part))
    if path:
        with Path(path).expanduser().open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    ids.append(int(line))
                    continue
                if isinstance(row, dict) and "id" in row:
                    ids.append(int(row["id"]))
                elif isinstance(row, list):
                    for item in row:
                        ids.append(int(item))
                elif isinstance(row, int):
                    ids.append(int(row))
    return sorted(set(ids))


def _resolve_offline(args: argparse.Namespace) -> Optional[bool]:
    if getattr(args, "offline", False) and getattr(args, "online", False):
        raise SystemExit("Cannot set both --offline and --online")
    if getattr(args, "offline", False):
        return True
    if getattr(args, "online", False):
        return False
    return None


def _next_delta_seq(packset_dir: Path) -> int:
    manifest_path = packset_dir / "pack.manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    deltas = data.get("deltas") or []
    return max((int(d["seq"]) for d in deltas), default=0) + 1


def _bundle_pack_dir(pack_dir: Path) -> Path:
    tmp_dir = Path(tempfile.mkdtemp(prefix="annpack_bundle_"))
    zip_path = tmp_dir / f"{pack_dir.name}-{uuid.uuid4().hex[:8]}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pack_dir.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            arcname = path.relative_to(pack_dir).as_posix()
            zf.write(path, arcname)
    return zip_path


def _registry_base_url(args: argparse.Namespace) -> str:
    return args.registry or os.environ.get("ANNPACK_REGISTRY_URL", "http://127.0.0.1:8080")


def _registry_token(args: argparse.Namespace) -> str:
    token = cast(Optional[str], getattr(args, "token", None))
    if token:
        return token
    token_file = cast(Optional[str], getattr(args, "token_file", None))
    if token_file:
        return Path(token_file).expanduser().read_text(encoding="utf-8").strip()
    env_token = os.environ.get("ANNPACK_REGISTRY_TOKEN")
    if not env_token:
        raise SystemExit("Registry token missing (set ANNPACK_REGISTRY_TOKEN or pass --token)")
    return env_token


def _registry_headers(token: Optional[str] = None) -> Dict[str, str]:
    headers = {"User-Agent": "annpack-cli"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _registry_json_request(
    method: str, url: str, token: Optional[str], payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = _registry_headers(token)
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, method=method, headers=headers)
    with urlopen(req, timeout=30) as resp:
        body = resp.read()
    return json.loads(body) if body else {}


def _registry_get_bytes(url: str, token: Optional[str]) -> bytes:
    headers = _registry_headers(token)
    req = Request(url, headers=headers)
    with urlopen(req, timeout=60) as resp:
        return cast(bytes, resp.read())


def _registry_download_file(url: str, token: Optional[str], dest: Path) -> None:
    headers = _registry_headers(token)
    req = Request(url, headers=headers)
    with urlopen(req, timeout=60) as resp:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as handle:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)


def _registry_post_bundle(url: str, token: str, bundle_path: Path) -> Dict[str, Any]:
    boundary = f"annpack-{uuid.uuid4().hex}"
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit(f"Unsupported registry URL scheme: {parsed.scheme}")
    host = parsed.hostname or ""
    port = parsed.port
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    filename = bundle_path.name
    content_type = mimetypes.guess_type(filename)[0] or "application/zip"
    file_size = bundle_path.stat().st_size

    file_header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="bundle"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8")
    file_footer = b"\r\n"
    end = f"--{boundary}--\r\n".encode("utf-8")
    content_length = len(file_header) + file_size + len(file_footer) + len(end)

    conn_cls = (
        http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    )
    conn = conn_cls(host, port=port, timeout=120)
    conn.putrequest("POST", path)
    conn.putheader("Content-Type", f"multipart/form-data; boundary={boundary}")
    conn.putheader("Content-Length", str(content_length))
    conn.putheader("User-Agent", "annpack-cli")
    conn.putheader("Authorization", f"Bearer {token}")
    conn.endheaders()
    conn.send(file_header)
    with bundle_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            conn.send(chunk)
    conn.send(file_footer)
    conn.send(end)
    resp = conn.getresponse()
    body = resp.read()
    if resp.status >= 400:
        raise SystemExit(
            f"Registry upload failed ({resp.status}): {body.decode('utf-8', 'ignore')}"
        )
    return json.loads(body) if body else {}


def cmd_build(args: argparse.Namespace) -> None:
    """Handle `annpack build`."""
    output_prefix = Path(args.output).expanduser().resolve()
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    text_col = args.text_col or "text"
    device = args.device

    if args.hf_dataset:
        if args.hf_dataset not in ("wikimedia/wikipedia", "wikipedia"):
            raise SystemExit(
                f"HF dataset '{args.hf_dataset}' not supported. Try --hf-dataset wikimedia/wikipedia."
            )
        build_index_from_hf_wikipedia(
            output_prefix=str(output_prefix),
            dataset_name=args.hf_dataset,
            config=args.hf_config or "20231101.en",
            split=args.hf_split,
            max_rows=args.max_rows,
            model_name=args.model,
            n_lists=args.lists if args.lists else 4096,
            batch_size=args.batch_size,
            device=device,
            seed=args.seed,
        )
    else:
        if not args.input:
            raise SystemExit("--input is required for local build")
        build_index(
            input_path=args.input,
            text_col=text_col,
            id_col=args.id_col,
            output_prefix=str(output_prefix),
            model_name=args.model,
            n_lists=args.lists,
            max_rows=args.max_rows,
            batch_size=args.batch_size,
            device=device,
            seed=args.seed,
        )

    ann_path = output_prefix.with_suffix(".annpack")
    meta_path = output_prefix.with_suffix(".meta.jsonl")
    offline = (
        os.environ.get("ANNPACK_OFFLINE") == "1" or os.environ.get("ANNPACK_OFFLINE_DUMMY") == "1"
    )
    build_info = {
        "seed": args.seed,
        "model": args.model,
        "device": args.device or os.environ.get("ANNPACK_DEVICE") or "auto",
        "offline": offline,
        "lists_requested": args.lists,
        "max_rows": args.max_rows,
        "batch_size": args.batch_size,
        "text_col": text_col,
        "id_col": args.id_col,
        "hf_dataset": args.hf_dataset,
        "hf_config": args.hf_config,
        "hf_split": args.hf_split,
    }
    _write_manifest(output_prefix, ann_path, meta_path, build_info=build_info)
    print("[done] Build complete.")


def cmd_serve(args: argparse.Namespace) -> None:
    """Handle `annpack serve`."""
    pack_dir = Path(args.pack_dir).expanduser().resolve()
    if not pack_dir.exists():
        raise SystemExit(f"Pack dir not found: {pack_dir}")

    ui_root = _materialize_ui_root()
    root_dir = ui_root
    manifest = _find_manifest(pack_dir)
    manifest_hint = f"/pack/{manifest.name}" if manifest else "none found"

    try:
        server = _start_http_server(
            args.host, args.port, root_dir=root_dir, pack_dir=pack_dir, quiet=False
        )
    except OSError as e:
        raise SystemExit(f"Failed to start server on {args.host}:{args.port}: {e}")

    actual_port = server.server_address[1]
    log_event("serve_start", {"host": args.host, "port": actual_port})
    base = f"http://{args.host}:{actual_port}"
    print(f"[serve] Serving from {root_dir}")
    print(f"[serve] Pack mounted at /pack/ -> {pack_dir}")
    if manifest:
        print(f"[serve] Manifest candidate: {manifest_hint}")
    print(f"[serve] Open: {base}/")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[serve] Stopping server...")
        server.shutdown()


def _resolve_root_and_manifest(pack_dir: Path) -> Tuple[Path, Optional[Path]]:
    """Return UI root and manifest path for a pack dir."""
    root_dir = _materialize_ui_root()
    manifest = _find_manifest(pack_dir)
    return root_dir, manifest


def cmd_smoke(args: argparse.Namespace) -> None:
    """Handle `annpack smoke`."""
    pack_dir = Path(args.pack_dir).expanduser().resolve()
    if not pack_dir.exists():
        raise SystemExit(f"Pack dir not found: {pack_dir}")
    root_dir, manifest = _resolve_root_and_manifest(pack_dir)
    if not manifest:
        raise SystemExit(
            f"No manifest found in {pack_dir} (looked for *.manifest.json / manifest.json)"
        )

    host, port = args.host, args.port
    if port != 0 and _port_in_use(host, port):
        raise SystemExit(f"Port {port} is already in use; start a fresh server first.")

    server = _start_http_server(host, port, root_dir=root_dir, pack_dir=pack_dir, quiet=True)
    actual_port = server.server_address[1]
    base = f"http://{host}:{actual_port}"
    time.sleep(0.2)

    index_url = base + "/index.html"
    try:
        status, _ = _health_check(index_url)
    except Exception:
        status, _ = _health_check(base + "/")
        index_url = base + "/"
    if status != 200:
        server.shutdown()
        raise SystemExit(f"Index page check failed ({status}): {index_url}")
    # Also ensure root path responds
    status_root, _ = _health_check(base + "/")
    if status_root != 200:
        server.shutdown()
        raise SystemExit(f"Root page check failed ({status_root}): {base}/")

    manifest_url = base + (
        f"/{manifest.name}" if root_dir == pack_dir else f"/pack/{manifest.name}"
    )
    try:
        status, manifest_body = _health_check(manifest_url)
    except Exception as e:
        server.shutdown()
        raise SystemExit(f"Manifest check failed: {e}")
    if status != 200:
        server.shutdown()
        raise SystemExit(f"Manifest check failed ({status}): {manifest_url}")
    data = json.loads(manifest_body)
    shards = data.get("shards") or []
    if not shards:
        server.shutdown()
        raise SystemExit("Manifest contains no shards.")

    manifest_base = manifest_url.rsplit("/", 1)[0] + "/"
    for shard in shards:
        ann_url = urljoin(manifest_base, shard.get("annpack"))
        meta_url = urljoin(manifest_base, shard.get("meta"))
        for label, url in (("annpack", ann_url), ("meta", meta_url)):
            try:
                s, _ = _health_check(url)
            except Exception as e:
                server.shutdown()
                raise SystemExit(f"{label} check failed: {e}")
            if s != 200:
                server.shutdown()
                raise SystemExit(f"{label} check failed ({s}): {url}")
    server.shutdown()
    print("PASS smoke")


def cmd_verify(args: argparse.Namespace) -> None:
    """Handle `annpack verify`."""
    result = verify_pack(args.pack_dir, deep=args.deep)
    if args.pubkey:
        verify_manifest_signature(args.pack_dir, args.pubkey, sig_path=args.sig)
        result["signature"] = "ok"
    print(json.dumps(result, indent=2))


def cmd_inspect(args: argparse.Namespace) -> None:
    """Handle `annpack inspect`."""
    info = inspect_pack(args.pack_dir)
    print(json.dumps(info, indent=2))


def cmd_sign(args: argparse.Namespace) -> None:
    """Handle `annpack sign`."""
    sig_path = sign_manifest(args.pack_dir, args.key, out_path=args.out)
    print(json.dumps({"signature": sig_path}, indent=2))


def cmd_diagnose(args: argparse.Namespace) -> None:
    """Handle `annpack diagnose`."""
    info = diagnose_env()
    print(json.dumps(info, indent=2))


def cmd_packset_build_base(args: argparse.Namespace) -> None:
    """Handle `annpack packset build-base`."""
    offline = _resolve_offline(args)
    result = build_packset_base(
        args.input,
        args.packset,
        text_col=args.text_col,
        id_col=args.id_col,
        lists=args.lists,
        seed=args.seed,
        offline=offline,
        model_name=args.model,
        device=args.device,
        max_rows=args.max_rows,
        batch_size=args.batch_size,
    )
    print(json.dumps(result, indent=2))


def cmd_packset_build_delta(args: argparse.Namespace) -> None:
    """Handle `annpack packset build-delta`."""
    offline = _resolve_offline(args)
    delete_ids = _parse_delete_ids(args.delete_ids, args.delete_ids_file)
    info = build_delta(
        base_dir=args.base,
        add_csv=args.add,
        delete_ids=delete_ids,
        out_delta_dir=args.out,
        text_col=args.text_col,
        id_col=args.id_col,
        lists=args.lists,
        seed=args.seed,
        offline=offline,
        model_name=args.model,
        device=args.device,
        max_rows=args.max_rows,
        batch_size=args.batch_size,
    )
    result: Dict[str, Any] = {
        "delta_dir": str(info.path),
        "manifest": str(info.path / "delta.manifest.json"),
    }
    if args.packset:
        seq = args.seq if args.seq is not None else _next_delta_seq(Path(args.packset))
        manifest = update_packset_manifest(args.packset, str(info.path), seq=seq)
        result["packset_manifest"] = str(manifest)
        result["seq"] = seq
    print(json.dumps(result, indent=2))


def cmd_packset_status(args: argparse.Namespace) -> None:
    """Handle `annpack packset status`."""
    status = packset_status(
        args.packset,
        count_meta=not args.skip_meta,
        count_tombstones=not args.skip_tombstones,
        unique_tombstones=args.unique_tombstones,
    )
    print(json.dumps(status, indent=2))


def cmd_packset_create(args: argparse.Namespace) -> None:
    """Handle `annpack packset create`."""
    manifest = create_packset(args.base, args.delta, args.out)
    print(json.dumps({"manifest": str(manifest)}, indent=2))


def cmd_packset_promote(args: argparse.Namespace) -> None:
    """Handle `annpack packset promote-delta`."""
    manifest = promote_delta(args.packset, args.delta)
    print(json.dumps({"manifest": str(manifest)}, indent=2))


def cmd_packset_revert(args: argparse.Namespace) -> None:
    """Handle `annpack packset revert`."""
    manifest = revert_packset(args.packset, args.to)
    print(json.dumps({"manifest": str(manifest)}, indent=2))


def cmd_packset_rebase(args: argparse.Namespace) -> None:
    """Handle `annpack packset rebase`."""
    manifest = rebase_packset(
        args.packset,
        args.out,
        text_col=args.text_col,
        id_col=args.id_col,
        lists=args.lists,
        seed=args.seed,
        offline=os.environ.get("ANNPACK_OFFLINE") == "1",
    )
    print(json.dumps({"manifest": str(manifest)}, indent=2))


def cmd_canary(args: argparse.Namespace) -> None:
    """Handle `annpack canary`."""
    result = run_canary(
        args.base,
        args.candidate,
        args.queries,
        top_k=args.top_k,
        min_overlap=args.min_overlap,
        avg_overlap=args.avg_overlap,
    )
    print(json.dumps(result, indent=2))


def cmd_templates(args: argparse.Namespace) -> None:
    """Handle `annpack templates`."""
    root = resources.files("annpack.templates")
    templates = sorted(
        [p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith("__")]
    )
    print(json.dumps({"templates": templates}, indent=2))


def cmd_init(args: argparse.Namespace) -> None:
    """Handle `annpack init`."""
    root = resources.files("annpack.templates") / args.template
    if not root.exists():
        raise SystemExit(f"Template not found: {args.template}")
    out_dir = Path(args.out).expanduser().resolve()
    if out_dir.exists() and any(out_dir.iterdir()) and not args.force:
        raise SystemExit(f"Output dir not empty: {out_dir} (use --force to overwrite)")
    out_dir.mkdir(parents=True, exist_ok=True)
    with as_file(root) as template_dir:
        shutil.copytree(template_dir, out_dir, dirs_exist_ok=True)
    print(json.dumps({"template": args.template, "out": str(out_dir)}, indent=2))


def _registry_create_org_project(base_url: str, token: str, org: str, project: str) -> None:
    from urllib.error import HTTPError

    try:
        _registry_json_request(
            "POST",
            f"{base_url}/orgs?{urlencode({'name': org})}",
            token,
        )
    except HTTPError as exc:
        if exc.code != 409:
            raise
    try:
        _registry_json_request(
            "POST",
            f"{base_url}/orgs/{org}/projects?{urlencode({'name': project})}",
            token,
        )
    except HTTPError as exc:
        if exc.code != 409:
            raise


def cmd_registry_upload(args: argparse.Namespace) -> None:
    """Handle `annpack registry upload`."""
    pack_dir = Path(args.pack_dir).expanduser().resolve()
    if not pack_dir.exists():
        raise SystemExit(f"Pack dir not found: {pack_dir}")
    token = _registry_token(args)
    base_url = _registry_base_url(args)
    if args.create:
        _registry_create_org_project(base_url, token, args.org, args.project)
    if not args.skip_verify:
        verify_pack(str(pack_dir), deep=args.deep)
    if args.sign_key:
        sign_manifest(str(pack_dir), args.sign_key, out_path=args.sign_out)
    bundle = _bundle_pack_dir(pack_dir)
    try:
        url = f"{base_url}/orgs/{args.org}/projects/{args.project}/packs?{urlencode({'version': args.version})}"
        result = _registry_post_bundle(url, token, bundle)
        if args.alias:
            alias_url = (
                f"{base_url}/orgs/{args.org}/projects/{args.project}/aliases/{args.alias}"
                f"?{urlencode({'version': args.version})}"
            )
            _registry_json_request("POST", alias_url, token)
        print(json.dumps(result, indent=2))
    finally:
        bundle.unlink(missing_ok=True)


def _registry_token_optional(args: argparse.Namespace) -> Optional[str]:
    if getattr(args, "no_auth", False):
        return None
    token = cast(Optional[str], getattr(args, "token", None))
    if token:
        return token
    token_file = cast(Optional[str], getattr(args, "token_file", None))
    if token_file:
        return Path(token_file).expanduser().read_text(encoding="utf-8").strip()
    return os.environ.get("ANNPACK_REGISTRY_TOKEN")


def cmd_registry_list(args: argparse.Namespace) -> None:
    """Handle `annpack registry list`."""
    base_url = _registry_base_url(args)
    token = _registry_token_optional(args)
    url = f"{base_url}/orgs/{args.org}/projects/{args.project}/packs"
    result = _registry_json_request("GET", url, token)
    print(json.dumps(result, indent=2))


def cmd_registry_download(args: argparse.Namespace) -> None:
    """Handle `annpack registry download`."""
    base_url = _registry_base_url(args)
    token = _registry_token_optional(args)
    out_dir = Path(args.out).expanduser().resolve()
    manifest_url = (
        f"{base_url}/orgs/{args.org}/projects/{args.project}/packs/{args.version}/manifest"
    )
    manifest_bytes = _registry_get_bytes(manifest_url, token)
    manifest = json.loads(manifest_bytes)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "pack.manifest.json"
    manifest_path.write_bytes(manifest_bytes)

    def download_file(rel_path: str) -> None:
        file_url = f"{base_url}/orgs/{args.org}/projects/{args.project}/packs/{args.version}/files/{rel_path}"
        _registry_download_file(file_url, token, out_dir / rel_path)

    if manifest.get("schema_version") == 3:
        base_info = manifest["base"]
        download_file(str(base_info["annpack"]))
        download_file(str(base_info["meta"]))
        for delta in manifest.get("deltas") or []:
            download_file(str(delta["annpack"]))
            download_file(str(delta["meta"]))
            download_file(str(delta["tombstones"]))
    else:
        for shard in manifest.get("shards") or []:
            download_file(str(shard["annpack"]))
            download_file(str(shard["meta"]))
    print(json.dumps({"out": str(out_dir), "manifest": str(manifest_path)}, indent=2))


def cmd_registry_alias_set(args: argparse.Namespace) -> None:
    """Handle `annpack registry alias set`."""
    token = _registry_token(args)
    base_url = _registry_base_url(args)
    url = (
        f"{base_url}/orgs/{args.org}/projects/{args.project}/aliases/{args.alias}"
        f"?{urlencode({'version': args.version})}"
    )
    result = _registry_json_request("POST", url, token)
    print(json.dumps(result, indent=2))


def cmd_registry_alias_get(args: argparse.Namespace) -> None:
    """Handle `annpack registry alias get`."""
    token = _registry_token_optional(args)
    base_url = _registry_base_url(args)
    url = f"{base_url}/orgs/{args.org}/projects/{args.project}/aliases/{args.alias}"
    result = _registry_json_request("GET", url, token)
    print(json.dumps(result, indent=2))


def cmd_registry_alias_list(args: argparse.Namespace) -> None:
    """Handle `annpack registry alias list`."""
    token = _registry_token_optional(args)
    base_url = _registry_base_url(args)
    url = f"{base_url}/orgs/{args.org}/projects/{args.project}/aliases"
    result = _registry_json_request("GET", url, token)
    print(json.dumps(result, indent=2))


def cmd_registry_alias_delete(args: argparse.Namespace) -> None:
    """Handle `annpack registry alias delete`."""
    token = _registry_token(args)
    base_url = _registry_base_url(args)
    url = f"{base_url}/orgs/{args.org}/projects/{args.project}/aliases/{args.alias}"
    result = _registry_json_request("DELETE", url, token)
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level CLI parser."""
    p = argparse.ArgumentParser(prog="annpack", description="ANNPack tools (build, serve, smoke)")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    tmpl = sub.add_parser("templates", help="List bundled project templates")
    tmpl.set_defaults(func=cmd_templates)

    init = sub.add_parser("init", help="Scaffold a project from a template")
    init.add_argument("--template", required=True, help="Template name (see `annpack templates`)")
    init.add_argument("--out", required=True, help="Output directory")
    init.add_argument("--force", action="store_true", help="Overwrite existing files")
    init.set_defaults(func=cmd_init)

    b = sub.add_parser("build", help="Build an ANNPack from CSV/Parquet or HF Wikipedia")
    b.add_argument("--input", help="Path to input CSV/Parquet")
    b.add_argument("--text-col", help="Text column name (default: text)")
    b.add_argument("--id-col", help="Optional ID column (int64)")
    b.add_argument("--output", required=True, help="Output prefix (e.g., ./out/tiny)")
    b.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
    b.add_argument("--lists", type=int, default=1024, help="Number of IVF lists/clusters")
    b.add_argument("--max-rows", type=int, default=100000, help="Maximum rows to index")
    b.add_argument("--batch-size", type=int, default=512, help="Embedding batch size")
    b.add_argument("--seed", type=int, default=1234, help="Seed for deterministic builds")
    b.add_argument(
        "--device",
        choices=["cpu", "cuda", "mps"],
        help="Force embedding device (default: auto or ANNPACK_DEVICE)",
    )
    b.add_argument("--hf-dataset", help="HuggingFace dataset name (optional)")
    b.add_argument("--hf-config", help="HF dataset config")
    b.add_argument("--hf-split", default="train", help="HF dataset split (default: train)")
    b.set_defaults(func=cmd_build)

    s = sub.add_parser("serve", help="Serve the UI with a pack mounted at /pack/")
    s.add_argument("pack_dir", help="Directory containing .annpack/.meta/.manifest")
    s.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    s.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    s.set_defaults(func=cmd_serve)

    demo_alias = sub.add_parser("demo", help=argparse.SUPPRESS)
    demo_alias.add_argument("pack_dir", help=argparse.SUPPRESS)
    demo_alias.add_argument("--host", default="127.0.0.1", help=argparse.SUPPRESS)
    demo_alias.add_argument("--port", type=int, default=8000, help=argparse.SUPPRESS)
    demo_alias.set_defaults(func=cmd_serve)

    sm = sub.add_parser("smoke", help="Start demo server (if needed) and verify assets + manifest")
    sm.add_argument("pack_dir", help="Directory containing .annpack/.meta/.manifest")
    sm.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    sm.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    sm.set_defaults(func=cmd_smoke)

    v = sub.add_parser("verify", help="Verify pack structure + manifest checks")
    v.add_argument("pack_dir", help="Directory containing .annpack/.meta/.manifest")
    v.add_argument("--deep", action="store_true", help="Validate list payload sizes")
    v.add_argument("--pubkey", help="Ed25519 public key (PEM) to verify signature")
    v.add_argument("--sig", help="Signature path (optional)")
    v.set_defaults(func=cmd_verify)

    i = sub.add_parser("inspect", help="Print pack header + manifest info")
    i.add_argument("pack_dir", help="Directory containing .annpack/.meta/.manifest")
    i.set_defaults(func=cmd_inspect)

    sg = sub.add_parser("sign", help="Sign a manifest with an Ed25519 key")
    sg.add_argument("pack_dir", help="Directory containing .annpack/.meta/.manifest")
    sg.add_argument("--key", required=True, help="Path to Ed25519 private key (PEM)")
    sg.add_argument("--out", help="Signature output path (optional)")
    sg.set_defaults(func=cmd_sign)

    dg = sub.add_parser("diagnose", help="Print environment + dependency versions")
    dg.set_defaults(func=cmd_diagnose)

    ps = sub.add_parser("packset", help="PackSet management")
    ps_sub = ps.add_subparsers(dest="packset_cmd", required=True)

    psb = ps_sub.add_parser("build-base", help="Build a base packset from a CSV/Parquet")
    psb.add_argument("--input", required=True, help="Input CSV/Parquet")
    psb.add_argument("--packset", required=True, help="Output packset directory")
    psb.add_argument("--text-col", default="text", help="Text column name")
    psb.add_argument("--id-col", default="id", help="ID column name")
    psb.add_argument("--lists", type=int, default=1024, help="Number of IVF lists")
    psb.add_argument("--seed", type=int, default=0, help="Seed for deterministic builds")
    psb.add_argument("--offline", action="store_true", help="Force offline embeddings")
    psb.add_argument("--online", action="store_true", help="Force online embeddings")
    psb.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
    psb.add_argument(
        "--device",
        choices=["cpu", "cuda", "mps"],
        help="Force embedding device (default: auto or ANNPACK_DEVICE)",
    )
    psb.add_argument("--max-rows", type=int, default=100000, help="Maximum rows to index")
    psb.add_argument("--batch-size", type=int, default=512, help="Embedding batch size")
    psb.set_defaults(func=cmd_packset_build_base)

    psd = ps_sub.add_parser("build-delta", help="Build a delta pack (adds/updates + tombstones)")
    psd.add_argument("--base", required=True, help="Base pack directory")
    psd.add_argument("--add", required=True, help="CSV/Parquet with adds/updates")
    psd.add_argument("--out", required=True, help="Output delta directory")
    psd.add_argument("--packset", help="Packset dir to update manifest")
    psd.add_argument("--seq", type=int, help="Delta sequence number (default: next)")
    psd.add_argument("--delete-ids", help="Comma-separated delete ids")
    psd.add_argument("--delete-ids-file", help="JSONL or newline ids to delete")
    psd.add_argument("--text-col", default="text", help="Text column name")
    psd.add_argument("--id-col", default="id", help="ID column name")
    psd.add_argument("--lists", type=int, default=1024, help="Number of IVF lists")
    psd.add_argument("--seed", type=int, default=0, help="Seed for deterministic builds")
    psd.add_argument("--offline", action="store_true", help="Force offline embeddings")
    psd.add_argument("--online", action="store_true", help="Force online embeddings")
    psd.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
    psd.add_argument(
        "--device",
        choices=["cpu", "cuda", "mps"],
        help="Force embedding device (default: auto or ANNPACK_DEVICE)",
    )
    psd.add_argument("--max-rows", type=int, default=100000, help="Maximum rows to index")
    psd.add_argument("--batch-size", type=int, default=512, help="Embedding batch size")
    psd.set_defaults(func=cmd_packset_build_delta)

    pss = ps_sub.add_parser("status", help="Summarize packset state")
    pss.add_argument("--packset", required=True, help="Packset directory")
    pss.add_argument("--skip-meta", action="store_true", help="Skip counting meta rows")
    pss.add_argument("--skip-tombstones", action="store_true", help="Skip tombstone counts")
    pss.add_argument(
        "--unique-tombstones", action="store_true", help="Compute unique tombstone ids"
    )
    pss.set_defaults(func=cmd_packset_status)

    psc = ps_sub.add_parser("create", help="Create a packset from base + deltas")
    psc.add_argument("--base", required=True, help="Base pack directory")
    psc.add_argument(
        "--delta", action="append", default=[], help="Delta pack directories (repeatable)"
    )
    psc.add_argument("--out", required=True, help="Output packset directory")
    psc.set_defaults(func=cmd_packset_create)

    psp = ps_sub.add_parser("promote-delta", help="Promote a delta into an existing packset")
    psp.add_argument("--packset", required=True, help="Packset directory")
    psp.add_argument("--delta", required=True, help="Delta pack directory")
    psp.set_defaults(func=cmd_packset_promote)

    psr = ps_sub.add_parser("revert", help="Revert a packset to a delta sequence")
    psr.add_argument("--packset", required=True, help="Packset directory")
    psr.add_argument("--to", type=int, required=True, help="Delta sequence to keep (inclusive)")
    psr.set_defaults(func=cmd_packset_revert)

    psb = ps_sub.add_parser("rebase", help="Compact deltas into a new base packset")
    psb.add_argument("--packset", required=True, help="Packset directory")
    psb.add_argument("--out", required=True, help="Output packset directory")
    psb.add_argument("--text-col", default="text", help="Text column name")
    psb.add_argument("--id-col", default="id", help="ID column name")
    psb.add_argument("--lists", type=int, default=1024, help="Number of IVF lists")
    psb.add_argument("--seed", type=int, default=0, help="Seed for deterministic builds")
    psb.set_defaults(func=cmd_packset_rebase)

    cn = sub.add_parser("canary", help="Compare base vs candidate packs with queries")
    cn.add_argument("--base", required=True, help="Base pack directory")
    cn.add_argument("--candidate", required=True, help="Candidate pack directory")
    cn.add_argument("--queries", required=True, help="JSONL queries (text or vector)")
    cn.add_argument("--top-k", type=int, default=5, help="Top K results")
    cn.add_argument("--min-overlap", type=float, default=0.7, help="Min overlap threshold")
    cn.add_argument("--avg-overlap", type=float, default=0.8, help="Avg overlap threshold")
    cn.set_defaults(func=cmd_canary)

    rg = sub.add_parser("registry", help="Registry operations (upload/list/download)")
    rg_sub = rg.add_subparsers(dest="registry_cmd", required=True)

    rgu = rg_sub.add_parser("upload", help="Bundle + upload a pack or packset")
    rgu.add_argument("--org", required=True, help="Registry org")
    rgu.add_argument("--project", required=True, help="Registry project")
    rgu.add_argument("--version", required=True, help="Version to publish")
    rgu.add_argument("--pack-dir", required=True, help="Pack or packset directory")
    rgu.add_argument("--registry", help="Registry base URL")
    rgu.add_argument("--token", help="JWT token")
    rgu.add_argument("--token-file", help="JWT token file")
    rgu.add_argument("--create", action="store_true", help="Create org/project if missing")
    rgu.add_argument("--skip-verify", action="store_true", help="Skip annpack verify")
    rgu.add_argument("--deep", action="store_true", help="Deep verify lists")
    rgu.add_argument("--sign-key", help="Ed25519 private key (PEM) to sign manifest")
    rgu.add_argument("--sign-out", help="Signature output path")
    rgu.add_argument("--alias", help="Alias to set after upload")
    rgu.set_defaults(func=cmd_registry_upload)

    rgl = rg_sub.add_parser("list", help="List versions for a project")
    rgl.add_argument("--org", required=True, help="Registry org")
    rgl.add_argument("--project", required=True, help="Registry project")
    rgl.add_argument("--registry", help="Registry base URL")
    rgl.add_argument("--token", help="JWT token")
    rgl.add_argument("--token-file", help="JWT token file")
    rgl.add_argument("--no-auth", action="store_true", help="Skip auth headers")
    rgl.set_defaults(func=cmd_registry_list)

    rgd = rg_sub.add_parser("download", help="Download a pack or packset")
    rgd.add_argument("--org", required=True, help="Registry org")
    rgd.add_argument("--project", required=True, help="Registry project")
    rgd.add_argument("--version", required=True, help="Version or alias to download")
    rgd.add_argument("--out", required=True, help="Output directory")
    rgd.add_argument("--registry", help="Registry base URL")
    rgd.add_argument("--token", help="JWT token")
    rgd.add_argument("--token-file", help="JWT token file")
    rgd.add_argument("--no-auth", action="store_true", help="Skip auth headers")
    rgd.set_defaults(func=cmd_registry_download)

    rga = rg_sub.add_parser("alias", help="Manage version aliases")
    rga_sub = rga.add_subparsers(dest="alias_cmd", required=True)

    rgs = rga_sub.add_parser("set", help="Set or update an alias")
    rgs.add_argument("--org", required=True, help="Registry org")
    rgs.add_argument("--project", required=True, help="Registry project")
    rgs.add_argument("--alias", required=True, help="Alias name")
    rgs.add_argument("--version", required=True, help="Version to map to alias")
    rgs.add_argument("--registry", help="Registry base URL")
    rgs.add_argument("--token", help="JWT token")
    rgs.add_argument("--token-file", help="JWT token file")
    rgs.set_defaults(func=cmd_registry_alias_set)

    rgg = rga_sub.add_parser("get", help="Get alias mapping")
    rgg.add_argument("--org", required=True, help="Registry org")
    rgg.add_argument("--project", required=True, help="Registry project")
    rgg.add_argument("--alias", required=True, help="Alias name")
    rgg.add_argument("--registry", help="Registry base URL")
    rgg.add_argument("--token", help="JWT token")
    rgg.add_argument("--token-file", help="JWT token file")
    rgg.add_argument("--no-auth", action="store_true", help="Skip auth headers")
    rgg.set_defaults(func=cmd_registry_alias_get)

    rgls = rga_sub.add_parser("list", help="List aliases for a project")
    rgls.add_argument("--org", required=True, help="Registry org")
    rgls.add_argument("--project", required=True, help="Registry project")
    rgls.add_argument("--registry", help="Registry base URL")
    rgls.add_argument("--token", help="JWT token")
    rgls.add_argument("--token-file", help="JWT token file")
    rgls.add_argument("--no-auth", action="store_true", help="Skip auth headers")
    rgls.set_defaults(func=cmd_registry_alias_list)

    rgdlt = rga_sub.add_parser("delete", help="Delete an alias")
    rgdlt.add_argument("--org", required=True, help="Registry org")
    rgdlt.add_argument("--project", required=True, help="Registry project")
    rgdlt.add_argument("--alias", required=True, help="Alias name")
    rgdlt.add_argument("--registry", help="Registry base URL")
    rgdlt.add_argument("--token", help="JWT token")
    rgdlt.add_argument("--token-file", help="JWT token file")
    rgdlt.set_defaults(func=cmd_registry_alias_delete)

    return p


def main(argv: Optional[Sequence[str]] = None) -> None:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
