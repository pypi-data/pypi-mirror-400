from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import sqlite3
import struct
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import unquote

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt

logger = logging.getLogger("annpack.registry")
if logger.parent and logger.parent.name == "annpack":
    # Keep registry logs visible even if annpack logger disables propagation.
    logger.parent = logging.getLogger()
logger.propagate = True

STORAGE_ROOT = Path(os.environ.get("REGISTRY_STORAGE", "registry_storage")).resolve()
DB_PATH = STORAGE_ROOT / "registry.db"
DEV_MODE = os.getenv("REGISTRY_DEV_MODE", "").lower() in {"1", "true", "yes"}
JWT_SECRET = os.getenv("REGISTRY_JWT_SECRET")
if not DEV_MODE and not JWT_SECRET:
    raise RuntimeError("REGISTRY_JWT_SECRET is required when REGISTRY_DEV_MODE is disabled")
if DEV_MODE and not JWT_SECRET:
    logger.warning("DEV_MODE enabled without REGISTRY_JWT_SECRET; bearer tokens disabled.")
JWT_ALG = os.environ.get("REGISTRY_JWT_ALG", "HS256")
JWT_AUD = os.environ.get("REGISTRY_JWT_AUD", "annpack-registry")
JWT_ISS = os.environ.get("REGISTRY_JWT_ISS", "annpack-registry")
MAX_UPLOAD_MB = int(os.getenv("REGISTRY_MAX_UPLOAD_MB", "100") or "100")
MAX_UPLOAD_BYTES = max(1, MAX_UPLOAD_MB) * 1024 * 1024
MAX_JSON_BYTES = int(os.environ.get("REGISTRY_MAX_JSON_BYTES", str(1024 * 1024)))
MAX_EXTRACT_MB = int(os.getenv("REGISTRY_MAX_EXTRACT_MB", "512") or "512")
MAX_EXTRACT_BYTES = max(1, MAX_EXTRACT_MB) * 1024 * 1024
MAX_EXTRACT_FILES = int(os.getenv("REGISTRY_MAX_EXTRACT_FILES", "2000") or "2000")
MAX_EXTRACT_FILE_MB = int(os.getenv("REGISTRY_MAX_EXTRACT_FILE_MB", "256") or "256")
MAX_EXTRACT_FILE_BYTES = max(1, MAX_EXTRACT_FILE_MB) * 1024 * 1024
MAX_MANIFEST_BYTES = int(os.getenv("REGISTRY_MAX_MANIFEST_BYTES", str(1024 * 1024)))
MAX_ANNPACK_LISTS = int(os.getenv("REGISTRY_MAX_LISTS", "1000000") or "1000000")
MAX_ANNPACK_DIM = int(os.getenv("REGISTRY_MAX_DIM", "4096") or "4096")
RATE_LIMIT_RPS = float(os.getenv("REGISTRY_RATE_LIMIT_RPS", "0" if DEV_MODE else "5") or "0")
RATE_LIMIT_BURST = int(os.getenv("REGISTRY_RATE_LIMIT_BURST", "0" if DEV_MODE else "20") or "0")
_RATE_BUCKETS: Dict[str, Tuple[float, float]] = {}
VERIFY_ON_UPLOAD = os.getenv("REGISTRY_VERIFY_ON_UPLOAD")
if VERIFY_ON_UPLOAD is None:
    VERIFY_ON_UPLOAD = "0" if DEV_MODE else "1"
VERIFY_ON_UPLOAD = VERIFY_ON_UPLOAD.lower() in {"1", "true", "yes"}
VERIFY_DEEP = os.getenv("REGISTRY_VERIFY_DEEP", "0").lower() in {"1", "true", "yes"}
REQUIRE_SIGNATURE = os.getenv("REGISTRY_REQUIRE_SIGNATURE", "0").lower() in {"1", "true", "yes"}
PUBKEY_PATH = os.getenv("REGISTRY_PUBKEY_PATH")

app = FastAPI(title="ANNPack Registry", version="0.1")


def _rate_limit(request: Request) -> None:
    if RATE_LIMIT_RPS <= 0 or RATE_LIMIT_BURST <= 0:
        return
    key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    tokens, last = _RATE_BUCKETS.get(key, (float(RATE_LIMIT_BURST), now))
    tokens = min(float(RATE_LIMIT_BURST), tokens + (now - last) * RATE_LIMIT_RPS)
    if tokens < 1.0:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    _RATE_BUCKETS[key] = (tokens - 1.0, now)


@app.middleware("http")
async def _rate_limit_middleware(request: Request, call_next):
    _rate_limit(request)
    return await call_next(request)


@app.middleware("http")
async def _security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    return response


class _BodyLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length"})
            ctype = (request.headers.get("content-type") or "").lower()
            if "application/json" in ctype and size > MAX_JSON_BYTES:
                return JSONResponse(status_code=413, content={"detail": "JSON body too large"})
            if "multipart/form-data" in ctype and size > MAX_UPLOAD_BYTES:
                return JSONResponse(status_code=413, content={"detail": "Upload too large"})
        return await call_next(request)


app.add_middleware(_BodyLimitMiddleware)


def init_db() -> None:
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS orgs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                UNIQUE(org_id, name)
            );
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                version TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at REAL NOT NULL,
                UNIQUE(project_id, version)
            );
            CREATE TABLE IF NOT EXISTS aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                UNIQUE(project_id, name)
            );
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            """
        )


@app.on_event("startup")
def _startup() -> None:
    if not DEV_MODE:
        if not JWT_SECRET or len(JWT_SECRET) < 16:
            raise RuntimeError(
                "REGISTRY_JWT_SECRET is required and must be at least 16 characters "
                "when REGISTRY_DEV_MODE=0"
            )
        if not JWT_AUD or not JWT_ISS:
            raise RuntimeError("REGISTRY_JWT_AUD and REGISTRY_JWT_ISS must be set")
    if REQUIRE_SIGNATURE:
        if not PUBKEY_PATH:
            raise RuntimeError("REGISTRY_PUBKEY_PATH is required when REGISTRY_REQUIRE_SIGNATURE=1")
        if not Path(PUBKEY_PATH).exists():
            raise RuntimeError(f"REGISTRY_PUBKEY_PATH not found: {PUBKEY_PATH}")
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True}


def log_audit(actor: str, action: str, details: dict) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO audit(actor, action, details, created_at) VALUES(?,?,?,?)",
            (actor, action, json.dumps(details), time.time()),
        )
        conn.commit()


def get_user(authorization: Optional[str] = Header(None)) -> dict:
    if DEV_MODE and not authorization:
        return {"sub": "dev", "role": "admin"}
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    if DEV_MODE and not JWT_SECRET:
        raise HTTPException(status_code=401, detail="Bearer auth disabled in dev mode")
    token = authorization.split(" ", 1)[1]
    try:
        options = {"require": ["sub"]}
        if DEV_MODE:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG], options=options)
        else:
            data = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALG],
                audience=JWT_AUD,
                issuer=JWT_ISS,
                options=options,
            )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    return data


def require_role(user: dict, roles: set[str]) -> None:
    if user.get("role") not in roles:
        raise HTTPException(status_code=403, detail="Insufficient role")


@app.get("/stats")
def stats(user: dict = Depends(get_user)) -> dict:
    require_role(user, {"admin", "dev", "viewer"})
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM orgs")
        orgs = int(cur.fetchone()[0])
        cur = conn.execute("SELECT COUNT(*) FROM projects")
        projects = int(cur.fetchone()[0])
        cur = conn.execute("SELECT COUNT(*) FROM versions")
        versions = int(cur.fetchone()[0])
        cur = conn.execute("SELECT COUNT(*) FROM aliases")
        aliases = int(cur.fetchone()[0])
        cur = conn.execute("SELECT COUNT(*) FROM audit")
        audits = int(cur.fetchone()[0])
    return {
        "ok": True,
        "orgs": orgs,
        "projects": projects,
        "versions": versions,
        "aliases": aliases,
        "audits": audits,
    }


@app.post("/auth/dev-token")
def dev_token(role: str = "admin"):
    if not DEV_MODE:
        raise HTTPException(status_code=403, detail="Dev tokens disabled")
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="REGISTRY_JWT_SECRET is required")
    payload = {"sub": "dev", "role": role}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return {"token": token}


@app.post("/orgs")
def create_org(name: str, user: dict = Depends(get_user)):
    require_role(user, {"admin"})
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO orgs(name) VALUES(?)", (name,))
        conn.commit()
    log_audit(user["sub"], "create_org", {"name": name})
    return {"name": name}


@app.post("/orgs/{org}/projects")
def create_project(org: str, name: str, user: dict = Depends(get_user)):
    require_role(user, {"admin", "dev"})
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT id FROM orgs WHERE name=?", (org,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Org not found")
        org_id = row[0]
        conn.execute("INSERT INTO projects(org_id, name) VALUES(?,?)", (org_id, name))
        conn.commit()
    log_audit(user["sub"], "create_project", {"org": org, "name": name})
    return {"org": org, "name": name}


def _project_id(conn: sqlite3.Connection, org: str, project: str) -> int:
    cur = conn.execute(
        "SELECT projects.id FROM projects JOIN orgs ON projects.org_id=orgs.id WHERE orgs.name=? AND projects.name=?",
        (org, project),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    return int(row[0])


def _resolve_version(conn: sqlite3.Connection, project_id: int, version: str) -> str:
    cur = conn.execute(
        "SELECT version FROM versions WHERE project_id=? AND version=?",
        (project_id, version),
    )
    row = cur.fetchone()
    if row:
        return str(row[0])
    cur = conn.execute(
        "SELECT version FROM aliases WHERE project_id=? AND name=?",
        (project_id, version),
    )
    row = cur.fetchone()
    if row:
        return str(row[0])
    raise HTTPException(status_code=404, detail="Version not found")


_SAFE_COMPONENT_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def _validate_path_component(name: str, value: str) -> str:
    if value in {".", ".."}:
        raise HTTPException(status_code=400, detail=f"Invalid {name}")
    if not _SAFE_COMPONENT_RE.match(value):
        raise HTTPException(status_code=400, detail=f"Invalid {name}")
    return value


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_extract(zip_path: Path, out_dir: Path) -> None:
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            total = 0
            files = 0
            for member in zf.infolist():
                if member.is_dir():
                    continue
                files += 1
                if files > MAX_EXTRACT_FILES:
                    raise HTTPException(status_code=413, detail="Too many files in bundle")
                if member.file_size < 0 or member.file_size > MAX_EXTRACT_FILE_BYTES:
                    raise HTTPException(status_code=413, detail="Bundle file too large")
                total += member.file_size
                if total > MAX_EXTRACT_BYTES:
                    raise HTTPException(status_code=413, detail="Bundle extract exceeds limit")
                target = _safe_path(out_dir, member.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(target, "wb") as dst:
                    dst.write(src.read())
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip")


def _safe_path(base: Path, rel: str) -> Path:
    rel_norm = unquote(rel).replace("\\", "/")
    if (
        not rel_norm
        or rel_norm.startswith("/")
        or rel_norm.startswith("//")
        or rel_norm.startswith("~")
        or "\x00" in rel_norm
    ):
        raise HTTPException(status_code=400, detail="Invalid path")
    parts = [part for part in rel_norm.split("/") if part]
    if not parts:
        raise HTTPException(status_code=400, detail="Invalid path")
    for part in parts:
        if part in {".", ".."}:
            raise HTTPException(status_code=400, detail="Invalid path")
        if not _SAFE_COMPONENT_RE.match(part):
            raise HTTPException(status_code=400, detail="Invalid path")

    base_resolved = base.resolve(strict=False)
    target = os.path.normpath(os.path.join(str(base_resolved), *parts))
    if os.path.commonpath([str(base_resolved), target]) != str(base_resolved):
        raise HTTPException(status_code=400, detail="Invalid path")
    current = base_resolved
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise HTTPException(status_code=400, detail="Invalid path")
    resolved_target = Path(target).resolve(strict=False)
    if os.path.commonpath([str(base_resolved), str(resolved_target)]) != str(base_resolved):
        raise HTTPException(status_code=400, detail="Invalid path")
    return Path(target)


def _load_manifest(root: Path) -> Tuple[Path, Dict[str, Any]]:
    candidates = list(root.glob("*.manifest.json")) + list(root.glob("manifest.json"))
    if not candidates:
        raise HTTPException(status_code=400, detail="Manifest not found in bundle")
    if len(candidates) > 1:
        raise HTTPException(status_code=400, detail="Multiple manifests found in bundle")
    manifest_path = candidates[0]
    if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
        raise HTTPException(status_code=413, detail="Manifest too large")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid manifest JSON: {exc}") from exc
    return manifest_path, data


def _verify_manifest_hashes(root: Path, data: Dict[str, Any]) -> None:
    if data.get("schema_version") != 3:
        return
    base = data.get("base") or {}
    base_sha = base.get("sha256_annpack")
    base_ann = root / str(base.get("annpack", ""))
    base_meta = root / str(base.get("meta", ""))
    if base_sha and _sha256_file(base_ann) != base_sha:
        raise HTTPException(status_code=400, detail="Base annpack hash mismatch")
    if base.get("sha256_meta") and _sha256_file(base_meta) != base["sha256_meta"]:
        raise HTTPException(status_code=400, detail="Base meta hash mismatch")

    for delta in data.get("deltas") or []:
        ann = root / str(delta.get("annpack", ""))
        meta = root / str(delta.get("meta", ""))
        tomb = root / str(delta.get("tombstones", ""))
        if (
            base_sha
            and delta.get("base_sha256_annpack")
            and delta["base_sha256_annpack"] != base_sha
        ):
            raise HTTPException(status_code=400, detail="Delta base hash mismatch")
        if delta.get("sha256_annpack") and _sha256_file(ann) != delta["sha256_annpack"]:
            raise HTTPException(status_code=400, detail="Delta annpack hash mismatch")
        if delta.get("sha256_meta") and _sha256_file(meta) != delta["sha256_meta"]:
            raise HTTPException(status_code=400, detail="Delta meta hash mismatch")
        if delta.get("sha256_tombstones") and _sha256_file(tomb) != delta["sha256_tombstones"]:
            raise HTTPException(status_code=400, detail="Delta tombstones hash mismatch")


def _verify_manifest_signature(manifest_path: Path) -> None:
    if not REQUIRE_SIGNATURE:
        return
    if not PUBKEY_PATH:
        raise HTTPException(status_code=500, detail="REGISTRY_PUBKEY_PATH missing")
    sig_path = manifest_path.with_suffix(manifest_path.suffix + ".sig")
    if not sig_path.exists():
        raise HTTPException(status_code=400, detail="Manifest signature missing")
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Signature verification unavailable: {exc}")
    key_bytes = Path(PUBKEY_PATH).read_bytes()
    key = load_pem_public_key(key_bytes)
    if not isinstance(key, Ed25519PublicKey):
        raise HTTPException(status_code=500, detail="Invalid Ed25519 public key")
    try:
        key.verify(sig_path.read_bytes(), manifest_path.read_bytes())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Manifest signature invalid: {exc}")


def _validate_annpack_header(path: Path, deep: bool = False) -> None:
    size = path.stat().st_size
    if size < 72:
        raise HTTPException(status_code=400, detail=f"ANNPack too small: {path.name}")
    with path.open("rb") as handle:
        header = handle.read(72)
    fields = struct.unpack("<QIIIIIIIQ", header[:44])
    magic, version, endian, header_size, dim, _, n_lists, _, offset_table_pos = fields
    if magic != 0x504E4E41:
        raise HTTPException(status_code=400, detail=f"Bad magic for {path.name}")
    if version != 1 or endian != 1 or header_size != 72:
        raise HTTPException(status_code=400, detail=f"Unsupported header for {path.name}")
    if dim <= 0 or dim > MAX_ANNPACK_DIM:
        raise HTTPException(status_code=400, detail=f"dim out of bounds for {path.name}")
    if n_lists <= 0 or n_lists > MAX_ANNPACK_LISTS:
        raise HTTPException(status_code=400, detail=f"n_lists out of bounds for {path.name}")
    table_size = int(n_lists) * 16
    if offset_table_pos <= 0 or offset_table_pos + table_size > size:
        raise HTTPException(status_code=400, detail=f"Offset table out of bounds for {path.name}")
    if not deep:
        return
    with path.open("rb") as handle:
        handle.seek(offset_table_pos)
        table = handle.read(table_size)
        for i in range(int(n_lists)):
            off, length = struct.unpack_from("<QQ", table, i * 16)
            if length == 0:
                continue
            if off + length > size:
                raise HTTPException(status_code=400, detail=f"List out of bounds for {path.name}")
            if length < 4:
                raise HTTPException(status_code=400, detail=f"List too small for {path.name}")
            handle.seek(off)
            count_bytes = handle.read(4)
            if len(count_bytes) != 4:
                raise HTTPException(status_code=400, detail=f"List header short for {path.name}")
            count = struct.unpack("<I", count_bytes)[0]
            needed = 4 + int(count) * 8 + int(count) * int(dim) * 2
            if needed > length:
                raise HTTPException(
                    status_code=400, detail=f"List payload exceeds size for {path.name}"
                )


def _validate_bundle(root: Path, deep: bool = False) -> Tuple[Path, Dict[str, Any]]:
    manifest_path, data = _load_manifest(root)
    schema = data.get("schema_version", 2)
    if schema == 3:
        base = data.get("base") or {}
        base_ann = base.get("annpack")
        base_meta = base.get("meta")
        if not base_ann or not base_meta:
            raise HTTPException(status_code=400, detail="PackSet base missing annpack/meta")
        base_ann_path = _safe_path(root, str(base_ann))
        base_meta_path = _safe_path(root, str(base_meta))
        if not base_ann_path.exists() or not base_meta_path.exists():
            raise HTTPException(status_code=400, detail="PackSet base files missing")
        _validate_annpack_header(base_ann_path, deep=deep)

        deltas = data.get("deltas") or []
        for delta in deltas:
            ann = delta.get("annpack")
            meta = delta.get("meta")
            tomb = delta.get("tombstones")
            if not ann or not meta or not tomb:
                raise HTTPException(status_code=400, detail="Delta entry missing files")
            ann_path = _safe_path(root, str(ann))
            meta_path = _safe_path(root, str(meta))
            tomb_path = _safe_path(root, str(tomb))
            if not ann_path.exists() or not meta_path.exists() or not tomb_path.exists():
                raise HTTPException(status_code=400, detail="Delta files missing")
            _validate_annpack_header(ann_path, deep=deep)
        return manifest_path, data

    shards = data.get("shards") or []
    if not shards:
        raise HTTPException(status_code=400, detail="Manifest contains no shards")
    for shard in shards:
        ann = shard.get("annpack")
        meta = shard.get("meta")
        if not ann or not meta:
            raise HTTPException(status_code=400, detail="Shard entry missing annpack/meta")
        ann_path = _safe_path(root, str(ann))
        meta_path = _safe_path(root, str(meta))
        if not ann_path.exists() or not meta_path.exists():
            raise HTTPException(status_code=400, detail="Shard files missing")
        _validate_annpack_header(ann_path, deep=deep)
    return manifest_path, data


@app.post("/orgs/{org}/projects/{project}/packs")
def upload_pack(
    org: str,
    project: str,
    version: str,
    bundle: UploadFile = File(...),
    user: dict = Depends(get_user),
):
    require_role(user, {"admin", "dev"})
    tmp = STORAGE_ROOT / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    bundle_path = tmp / f"upload_{int(time.time() * 1000)}.zip"
    total = 0
    with bundle_path.open("wb") as handle:
        while True:
            chunk = bundle.file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Upload too large")
            handle.write(chunk)

    safe_org = _validate_path_component("org", org)
    safe_project = _validate_path_component("project", project)
    safe_version = _validate_path_component("version", version)

    dest_dir = _safe_path(STORAGE_ROOT, "/".join([safe_org, safe_project, safe_version]))
    try:
        with sqlite3.connect(DB_PATH) as conn:
            project_id = _project_id(conn, org, project)
            cur = conn.execute(
                "SELECT 1 FROM versions WHERE project_id=? AND version=?", (project_id, version)
            )
            if cur.fetchone():
                raise HTTPException(status_code=409, detail="Version already exists")

            if dest_dir.exists() and any(dest_dir.iterdir()):
                raise HTTPException(status_code=409, detail="Version directory not empty")
            dest_dir.mkdir(parents=True, exist_ok=True)
            try:
                _safe_extract(bundle_path, dest_dir)
                manifest_path, data = _validate_bundle(
                    dest_dir, deep=(VERIFY_ON_UPLOAD and VERIFY_DEEP)
                )
                if VERIFY_ON_UPLOAD:
                    _verify_manifest_hashes(dest_dir, data)
                _verify_manifest_signature(manifest_path)
            except HTTPException:
                shutil.rmtree(dest_dir, ignore_errors=True)
                raise
            except Exception as exc:
                shutil.rmtree(dest_dir, ignore_errors=True)
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            rel_dest = dest_dir.relative_to(STORAGE_ROOT).as_posix()
            conn.execute(
                "INSERT INTO versions(project_id, version, path, created_at) VALUES(?,?,?,?)",
                (project_id, version, rel_dest, time.time()),
            )
            conn.commit()
    finally:
        bundle_path.unlink(missing_ok=True)
    log_audit(user["sub"], "upload_pack", {"org": org, "project": project, "version": version})
    return {"org": org, "project": project, "version": version}


@app.get("/orgs/{org}/projects/{project}/packs")
def list_versions(org: str, project: str, user: dict = Depends(get_user)):
    require_role(user, {"admin", "dev", "viewer"})
    with sqlite3.connect(DB_PATH) as conn:
        project_id = _project_id(conn, org, project)
        cur = conn.execute(
            "SELECT version FROM versions WHERE project_id=? ORDER BY created_at DESC",
            (project_id,),
        )
        versions = [row[0] for row in cur.fetchall()]
        cur = conn.execute(
            "SELECT name, version FROM aliases WHERE project_id=? ORDER BY name ASC",
            (project_id,),
        )
        aliases = [{"name": row[0], "version": row[1]} for row in cur.fetchall()]
    return {"org": org, "project": project, "versions": versions, "aliases": aliases}


@app.get("/orgs/{org}/projects/{project}/aliases")
def list_aliases(org: str, project: str, user: dict = Depends(get_user)):
    require_role(user, {"admin", "dev", "viewer"})
    with sqlite3.connect(DB_PATH) as conn:
        project_id = _project_id(conn, org, project)
        cur = conn.execute(
            "SELECT name, version FROM aliases WHERE project_id=? ORDER BY name ASC",
            (project_id,),
        )
        aliases = [{"name": row[0], "version": row[1]} for row in cur.fetchall()]
    return {"org": org, "project": project, "aliases": aliases}


@app.get("/orgs/{org}/projects/{project}/aliases/{alias}")
def get_alias(org: str, project: str, alias: str, user: dict = Depends(get_user)):
    require_role(user, {"admin", "dev", "viewer"})
    safe_alias = _validate_path_component("alias", alias)
    with sqlite3.connect(DB_PATH) as conn:
        project_id = _project_id(conn, org, project)
        cur = conn.execute(
            "SELECT version FROM aliases WHERE project_id=? AND name=?",
            (project_id, safe_alias),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Alias not found")
    return {"org": org, "project": project, "alias": safe_alias, "version": row[0]}


@app.post("/orgs/{org}/projects/{project}/aliases/{alias}")
def set_alias(org: str, project: str, alias: str, version: str, user: dict = Depends(get_user)):
    require_role(user, {"admin", "dev"})
    safe_alias = _validate_path_component("alias", alias)
    safe_version = _validate_path_component("version", version)
    with sqlite3.connect(DB_PATH) as conn:
        project_id = _project_id(conn, org, project)
        cur = conn.execute(
            "SELECT 1 FROM versions WHERE project_id=? AND version=?",
            (project_id, safe_version),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Version not found")
        now = time.time()
        conn.execute(
            """
            INSERT INTO aliases(project_id, name, version, created_at, updated_at)
            VALUES(?,?,?,?,?)
            ON CONFLICT(project_id, name) DO UPDATE SET
              version=excluded.version,
              updated_at=excluded.updated_at
            """,
            (project_id, safe_alias, safe_version, now, now),
        )
        conn.commit()
    log_audit(
        user["sub"],
        "set_alias",
        {"org": org, "project": project, "alias": safe_alias, "version": safe_version},
    )
    return {"org": org, "project": project, "alias": safe_alias, "version": safe_version}


@app.delete("/orgs/{org}/projects/{project}/aliases/{alias}")
def delete_alias(org: str, project: str, alias: str, user: dict = Depends(get_user)):
    require_role(user, {"admin", "dev"})
    safe_alias = _validate_path_component("alias", alias)
    with sqlite3.connect(DB_PATH) as conn:
        project_id = _project_id(conn, org, project)
        cur = conn.execute(
            "DELETE FROM aliases WHERE project_id=? AND name=?",
            (project_id, safe_alias),
        )
        conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Alias not found")
    log_audit(user["sub"], "delete_alias", {"org": org, "project": project, "alias": safe_alias})
    return {"org": org, "project": project, "alias": safe_alias, "deleted": True}


def _version_path(org: str, project: str, version: str) -> Path:
    safe_org = _validate_path_component("org", org)
    safe_project = _validate_path_component("project", project)
    safe_version = _validate_path_component("version", version)
    with sqlite3.connect(DB_PATH) as conn:
        project_id = _project_id(conn, safe_org, safe_project)
        resolved = _resolve_version(conn, project_id, safe_version)
        safe_version = _validate_path_component("version", resolved)
        cur = conn.execute(
            "SELECT path FROM versions WHERE project_id=? AND version=?",
            (project_id, safe_version),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Version not found")
    path = _safe_path(STORAGE_ROOT, row[0])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Version not found")
    return path


@app.get("/orgs/{org}/projects/{project}/packs/{version}/manifest")
def get_manifest(org: str, project: str, version: str, user: dict = Depends(get_user)):
    require_role(user, {"admin", "dev", "viewer"})
    path = _version_path(org, project, version)
    manifest = next(path.glob("*.manifest.json"), None)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return FileResponse(manifest)


@app.get("/orgs/{org}/projects/{project}/packs/{version}/files/{file_path:path}")
def get_file(
    org: str,
    project: str,
    version: str,
    file_path: str,
    range: Optional[str] = Header(None),
    user: dict = Depends(get_user),
):
    require_role(user, {"admin", "dev", "viewer"})
    base = _version_path(org, project, version)
    target = _safe_path(base, file_path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    file_size = target.stat().st_size
    if range and range.startswith("bytes="):
        try:
            start_s, end_s = range.replace("bytes=", "").split("-")
            start = int(start_s)
            end = int(end_s) if end_s else file_size - 1
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Range header")
        if start >= file_size:
            return Response(status_code=416)
        end = min(end, file_size - 1)
        length = end - start + 1
        with target.open("rb") as f:
            f.seek(start)
            data = f.read(length)
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        }
        return Response(
            content=data, status_code=206, headers=headers, media_type="application/octet-stream"
        )

    response = FileResponse(target)
    response.headers["Accept-Ranges"] = "bytes"
    return response
