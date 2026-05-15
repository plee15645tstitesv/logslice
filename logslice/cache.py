"""Simple file-offset cache to avoid re-scanning log files on repeated queries."""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional, Tuple

_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "logslice"


def _file_key(path: Path) -> str:
    """Produce a stable cache key from path + mtime + size."""
    stat = path.stat()
    raw = f"{path.resolve()}:{stat.st_mtime}:{stat.st_size}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _cache_path(key: str, cache_dir: Path) -> Path:
    return cache_dir / f"{key}.json"


def load_offsets(
    path: Path,
    start_ts: str,
    end_ts: str,
    cache_dir: Optional[Path] = None,
) -> Optional[Tuple[int, int]]:
    """Return (start_offset, end_offset) from cache, or None on miss."""
    cache_dir = cache_dir or _DEFAULT_CACHE_DIR
    key = _file_key(path)
    cp = _cache_path(key, cache_dir)
    if not cp.exists():
        return None
    try:
        data = json.loads(cp.read_text())
        entry = data.get(f"{start_ts}/{end_ts}")
        if entry is None:
            return None
        return (entry["start_offset"], entry["end_offset"])
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def save_offsets(
    path: Path,
    start_ts: str,
    end_ts: str,
    start_offset: int,
    end_offset: int,
    cache_dir: Optional[Path] = None,
) -> None:
    """Persist (start_offset, end_offset) for a file + time-range pair."""
    cache_dir = cache_dir or _DEFAULT_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _file_key(path)
    cp = _cache_path(key, cache_dir)
    data: dict = {}
    if cp.exists():
        try:
            data = json.loads(cp.read_text())
        except (json.JSONDecodeError, ValueError):
            data = {}
    data[f"{start_ts}/{end_ts}"] = {
        "start_offset": start_offset,
        "end_offset": end_offset,
    }
    cp.write_text(json.dumps(data))


def clear_cache(cache_dir: Optional[Path] = None) -> int:
    """Delete all cached entries; return the number of files removed."""
    cache_dir = cache_dir or _DEFAULT_CACHE_DIR
    if not cache_dir.exists():
        return 0
    removed = 0
    for entry in cache_dir.glob("*.json"):
        entry.unlink()
        removed += 1
    return removed
