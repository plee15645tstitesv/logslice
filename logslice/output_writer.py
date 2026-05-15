"""Output writer: writes sliced log lines to a file or stdout."""

from __future__ import annotations

import gzip
import sys
from pathlib import Path
from typing import Iterable, IO, Optional


def _open_output(dest: Optional[Path], compress: bool) -> IO[bytes]:
    """Open the output destination for writing.

    Parameters
    ----------
    dest:
        Path to write output to.  ``None`` means stdout.
    compress:
        When *True* the output is gzip-compressed.  Ignored when writing
        to stdout (compression is never applied to stdout).
    """
    if dest is None:
        return sys.stdout.buffer  # type: ignore[return-value]

    if compress or dest.suffix == ".gz":
        return gzip.open(dest, "wb")

    return dest.open("wb")


def write_lines(
    lines: Iterable[str],
    dest: Optional[Path] = None,
    *,
    compress: bool = False,
    encoding: str = "utf-8",
) -> int:
    """Write *lines* to *dest*, returning the number of lines written.

    Parameters
    ----------
    lines:
        Iterable of log lines (each should already include its newline).
    dest:
        Output file path.  ``None`` writes to stdout.
    compress:
        Force gzip compression regardless of file extension.
    encoding:
        Text encoding used to encode each line before writing.

    Returns
    -------
    int
        Number of lines written.
    """
    count = 0
    fh = _open_output(dest, compress)
    try:
        for line in lines:
            raw = line if isinstance(line, bytes) else line.encode(encoding)
            if not raw.endswith(b"\n"):
                raw += b"\n"
            fh.write(raw)
            count += 1
    finally:
        if fh is not sys.stdout.buffer:
            fh.close()
    return count
