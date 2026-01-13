"""Artifact manifest helpers (skeleton)."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence
import json


def read_manifest(manifest_path: Path) -> Sequence[Mapping[str, object]]:
    """Load artifact entries from the manifest path."""
    if not manifest_path.exists():
        return []
    with manifest_path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if isinstance(data, list):
        return data
    raise ValueError("artifact manifest must be a JSON list")
