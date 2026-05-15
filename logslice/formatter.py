"""Output formatting helpers for sliced log lines."""

from __future__ import annotations

from typing import Iterable, Iterator, Optional


def add_prefix(lines: Iterable[str], prefix: str) -> Iterator[str]:
    """Prepend *prefix* to every line."""
    for line in lines:
        yield f"{prefix}{line}"


def add_filename_prefix(
    lines: Iterable[str], filename: str
) -> Iterator[str]:
    """Prepend ``filename:`` to every line (grep-style)."""
    return add_prefix(lines, f"{filename}:")


def add_line_numbers(
    lines: Iterable[str], start: int = 1
) -> Iterator[str]:
    """Yield lines with a leading line-number column.

    Format: ``{n:>6}  {line}``
    """
    for n, line in enumerate(lines, start=start):
        yield f"{n:>6}  {line}"


def strip_ansi(line: str) -> str:
    """Remove ANSI escape sequences from *line*."""
    import re
    return re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", line)


def format_lines(
    lines: Iterable[str],
    *,
    filename: Optional[str] = None,
    line_numbers: bool = False,
    strip_color: bool = False,
    prefix: Optional[str] = None,
) -> Iterator[str]:
    """Apply a chain of formatting transforms to *lines*.

    Parameters
    ----------
    lines:        Source lines (already newline-terminated).
    filename:     If set, prepend ``filename:`` to each line.
    line_numbers: If True, prepend a line-number column.
    strip_color:  If True, strip ANSI colour codes.
    prefix:       Arbitrary string prepended after other transforms.
    """
    it: Iterable[str] = lines
    if strip_color:
        it = (strip_ansi(ln) for ln in it)
    if filename:
        it = add_filename_prefix(it, filename)
    if line_numbers:
        it = add_line_numbers(it)
    if prefix:
        it = add_prefix(it, prefix)
    yield from it
