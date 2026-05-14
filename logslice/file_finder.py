"""Discovers and orders rotated log files for a given base log path."""

import os
import re
from pathlib import Path
from typing import List


# Matches common rotation suffixes: .1, .2, .gz, .1.gz, .2023-01-15, etc.
_ROTATION_PATTERN = re.compile(
    r"^(?P<base>.+?)"
    r"(?P<suffix>(?:\.\d+)?(?:\.[0-9]{4}-[0-9]{2}-[0-9]{2})?(?:\.gz)?)?$"
)


def find_rotated_files(base_path: str) -> List[Path]:
    """Return all log files related to *base_path*, ordered oldest-first.

    Rotation conventions handled:
        - app.log          (current)
        - app.log.1        (most recent rotated)
        - app.log.2        (older)
        - app.log.2023-01-15
        - app.log.1.gz
        - app.log.gz

    Args:
        base_path: Absolute or relative path to the active log file.

    Returns:
        List of :class:`pathlib.Path` objects, oldest file first.

    Raises:
        FileNotFoundError: If the directory containing *base_path* does not exist.
    """
    base = Path(base_path)
    directory = base.parent
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    base_name = base.name
    candidates: List[Path] = []

    for entry in directory.iterdir():
        if not entry.is_file():
            continue
        name = entry.name
        # Must start with the base filename
        if name == base_name or name.startswith(base_name + "."):
            candidates.append(entry)

    return _sort_rotated_files(base, candidates)


def _rotation_sort_key(base: Path, path: Path):
    """Return a sort key so that older rotated files come first."""
    name = path.name
    suffix = name[len(base.name):]

    if suffix == "":
        # Current log — newest, goes last
        return (1, 0, "")

    # Numeric rotation: .1 is most recent, higher numbers are older
    numeric_match = re.match(r"^\.(\d+)(\.gz)?$", suffix)
    if numeric_match:
        num = int(numeric_match.group(1))
        return (0, -num, "")  # higher number = older = earlier in list

    # Date-based rotation: lexicographic on the date string is sufficient
    date_match = re.match(r"^\.([0-9]{4}-[0-9]{2}-[0-9]{2})(\.gz)?$", suffix)
    if date_match:
        return (0, 0, date_match.group(1))

    # Unknown suffix — sort by mtime as fallback
    return (0, 0, str(path.stat().st_mtime))


def _sort_rotated_files(base: Path, files: List[Path]) -> List[Path]:
    return sorted(files, key=lambda p: _rotation_sort_key(base, p))
