"""High-level API for slicing a log archive by time range."""

import gzip
import io
from datetime import datetime
from pathlib import Path
from typing import Iterator

from logslice.line_scanner import find_end_offset, find_start_offset
from logslice.log_archive import LogArchive
from logslice.timestamp_parser import parse_timestamp


def _open_file(path: Path) -> io.RawIOBase:
    """Open a plain or gzip-compressed log file for binary reading."""
    if path.suffix == ".gz":
        return gzip.open(path, "rb")  # type: ignore[return-value]
    return open(path, "rb")  # noqa: WPS515


def _iter_lines_in_range(
    path: Path,
    start_time: datetime,
    end_time: datetime,
) -> Iterator[str]:
    """Yield decoded log lines from *path* that fall within [start_time, end_time]."""
    with _open_file(path) as fh:
        # Binary search is only reliable on seekable, uncompressed files.
        seekable = fh.seekable()

        if seekable:
            start_offset = find_start_offset(fh, start_time)  # type: ignore[arg-type]
            end_offset = find_end_offset(fh, end_time)  # type: ignore[arg-type]
            if end_offset <= start_offset:
                return
            fh.seek(start_offset)
            data = fh.read(end_offset - start_offset)
        else:
            data = fh.read()

    for raw_line in data.splitlines():
        line = raw_line.decode("utf-8", errors="replace")
        ts = parse_timestamp(line)
        if ts is None:
            continue
        if start_time <= ts <= end_time:
            yield line


def slice_archive(
    archive: LogArchive,
    start_time: datetime,
    end_time: datetime,
) -> Iterator[str]:
    """Iterate over all log lines in *archive* within [start_time, end_time].

    Files are visited oldest-first (as ordered by :class:`LogArchive`).
    """
    if start_time > end_time:
        raise ValueError(f"start_time ({start_time}) must be <= end_time ({end_time})")

    for path in archive:
        yield from _iter_lines_in_range(path, start_time, end_time)


def slice_path(
    base_path: Path,
    start_time: datetime,
    end_time: datetime,
) -> Iterator[str]:
    """Convenience wrapper: build a :class:`LogArchive` from *base_path* and slice it."""
    archive = LogArchive.from_path(base_path)
    yield from slice_archive(archive, start_time, end_time)
