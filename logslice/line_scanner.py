"""Binary-search-based line scanner for locating timestamp boundaries in log files."""

import io
from datetime import datetime
from typing import Optional, Tuple

from logslice.timestamp_parser import parse_timestamp


def _read_line_at(fh: io.RawIOBase, pos: int) -> Tuple[int, Optional[str]]:
    """Seek to *pos*, rewind to the start of the current line, and return
    (line_start_offset, line_text).  Returns (pos, None) if the file is empty."""
    fh.seek(0, 2)
    file_size = fh.tell()
    if file_size == 0:
        return 0, None

    pos = min(pos, file_size - 1)
    fh.seek(pos)

    # Walk backward to find the start of the line.
    while pos > 0:
        fh.seek(pos - 1)
        ch = fh.read(1)
        if ch == b"\n":
            break
        pos -= 1

    line_start = pos
    fh.seek(line_start)
    line = fh.readline().decode("utf-8", errors="replace").rstrip("\n")
    return line_start, line


def find_start_offset(fh: io.RawIOBase, start_time: datetime) -> int:
    """Return the byte offset of the first line whose timestamp >= *start_time*.

    Uses binary search over the file.  If no such line exists, returns the
    file size (i.e., nothing to read).
    """
    fh.seek(0, 2)
    file_size = fh.tell()
    if file_size == 0:
        return 0

    lo, hi = 0, file_size - 1

    while lo < hi:
        mid = (lo + hi) // 2
        _, line = _read_line_at(fh, mid)
        if line is None:
            break
        ts = parse_timestamp(line)
        if ts is not None and ts < start_time:
            # Advance past this line.
            fh.seek(0, 2)
            lo = min(fh.tell(), mid + len(line.encode()) + 1)
        else:
            hi = mid

    return lo


def find_end_offset(fh: io.RawIOBase, end_time: datetime) -> int:
    """Return the byte offset *past* the last line whose timestamp <= *end_time*.

    Returns 0 if no lines qualify.
    """
    fh.seek(0, 2)
    file_size = fh.tell()
    if file_size == 0:
        return 0

    lo, hi = 0, file_size - 1
    result = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        line_start, line = _read_line_at(fh, mid)
        if line is None:
            break
        ts = parse_timestamp(line)
        if ts is not None and ts <= end_time:
            # This line qualifies; record position after it.
            fh.seek(line_start)
            fh.readline()
            result = fh.tell()
            lo = result
        else:
            if mid == 0:
                break
            hi = mid - 1

    return result
