"""Shared utilities for reading ANNPack binary headers."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Dict


def read_header(path: Path) -> Dict[str, int]:
    """Read the ANNPack header and return a dict of fields.

    Args:
        path: Path to the .annpack file

    Returns:
        Dictionary with header fields: magic, version, endian, header_size,
        dim, metric, n_lists, n_vectors, offset_table_pos

    Raises:
        ValueError: If the file is too small to contain a valid header
    """
    if path.stat().st_size < 72:
        raise ValueError(f"File too small to contain ANNPack header: {path}")

    with path.open("rb") as handle:
        header = handle.read(72)

    fields = struct.unpack("<QIIIIIIIQ", header[:44])
    magic, version, endian, header_size, dim, metric, n_lists, n_vectors, offset_table_pos = fields

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


def validate_header(header: Dict[str, int], max_dim: int = 4096, max_lists: int = 1_000_000) -> None:
    """Validate header fields are within acceptable bounds.

    Args:
        header: Header dictionary from read_header()
        max_dim: Maximum allowed dimensionality
        max_lists: Maximum allowed number of lists

    Raises:
        ValueError: If any header field is invalid
    """
    if header["magic"] != 0x504E4E41:
        raise ValueError(f"Invalid magic number: {hex(header['magic'])}")

    if header["version"] != 1:
        raise ValueError(f"Unsupported version: {header['version']}")

    if header["endian"] != 1:
        raise ValueError(f"Unsupported endian: {header['endian']}")

    if header["header_size"] != 72:
        raise ValueError(f"Invalid header size: {header['header_size']}")

    if header["dim"] <= 0 or header["dim"] > max_dim:
        raise ValueError(f"Dimension out of bounds: {header['dim']} (max: {max_dim})")

    if header["n_lists"] <= 0 or header["n_lists"] > max_lists:
        raise ValueError(f"Number of lists out of bounds: {header['n_lists']} (max: {max_lists})")

    if header["n_vectors"] < 0:
        raise ValueError(f"Invalid number of vectors: {header['n_vectors']}")

    if header["offset_table_pos"] <= 0:
        raise ValueError(f"Invalid offset table position: {header['offset_table_pos']}")
