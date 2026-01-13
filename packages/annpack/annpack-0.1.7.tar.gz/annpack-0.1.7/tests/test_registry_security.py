import importlib
import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
from fastapi import HTTPException


def _load_registry(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("REGISTRY_STORAGE", str(tmp_path))
    monkeypatch.setenv("REGISTRY_DEV_MODE", "1")
    monkeypatch.setenv("REGISTRY_JWT_SECRET", "dev-secret")
    monkeypatch.setenv("REGISTRY_RATE_LIMIT_RPS", "0")
    monkeypatch.setenv("REGISTRY_RATE_LIMIT_BURST", "0")
    sys.modules.pop("registry.app", None)
    return importlib.import_module("registry.app")


@pytest.mark.parametrize(
    ("org", "project", "version"),
    [
        ("..", "proj", "v1"),
        ("org", "..", "v1"),
        ("org", "proj", ".."),
        ("org/extra", "proj", "v1"),
        ("org", "proj/extra", "v1"),
        ("org", "proj", "v1/extra"),
        ("org\\extra", "proj", "v1"),
        ("org", "proj\\extra", "v1"),
        ("org", "proj", "v1\\extra"),
        ("", "proj", "v1"),
        ("org", "", "v1"),
        ("org", "proj", ""),
    ],
)
def test_version_path_rejects_bad_components(tmp_path, monkeypatch, org, project, version):
    module = _load_registry(tmp_path, monkeypatch)
    with pytest.raises(HTTPException) as exc:
        module._version_path(org, project, version)
    assert exc.value.status_code == 400
    assert exc.value.detail.startswith("Invalid")


@pytest.mark.parametrize(
    "rel",
    ["../../etc/passwd", "/etc/passwd", "..\\..\\windows\\system32"],
)
def test_safe_path_rejects_traversal(tmp_path, monkeypatch, rel):
    module = _load_registry(tmp_path, monkeypatch)
    with pytest.raises(HTTPException) as exc:
        module._safe_path(module.STORAGE_ROOT, rel)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid path"


def test_safe_path_rejects_symlink_escape(tmp_path, monkeypatch):
    module = _load_registry(tmp_path, monkeypatch)
    base = module.STORAGE_ROOT
    base.mkdir(parents=True, exist_ok=True)
    outside = tmp_path / "outside"
    outside.mkdir(parents=True, exist_ok=True)
    (outside / "file.txt").write_text("data", encoding="utf-8")
    link = base / "link"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported")
    with pytest.raises(HTTPException) as exc:
        module._safe_path(base, "link/file.txt")
    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid path"
