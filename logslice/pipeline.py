"""High-level pipeline that wires filter + formatter into the slicer."""

from __future__ import annotations

from typing import IO, Iterable, Iterator, Optional

from logslice.filter import LineFilter
from logslice.formatter import format_lines


def build_pipeline(
    lines: Iterable[str],
    *,
    include: Optional[str] = None,
    exclude: Optional[str] = None,
    case_sensitive: bool = True,
    filename: Optional[str] = None,
    line_numbers: bool = False,
    strip_color: bool = False,
    prefix: Optional[str] = None,
) -> Iterator[str]:
    """Filter then format *lines* according to the given options.

    Filtering is applied before formatting so that line-number counters
    reflect only the lines that survive the filter.

    Parameters
    ----------
    lines:          Raw lines from the slicer (newline-terminated).
    include:        Regex — keep only matching lines.
    exclude:        Regex — drop matching lines.
    case_sensitive: Controls regex case sensitivity.
    filename:       Prepend filename to each output line.
    line_numbers:   Prepend sequential line numbers.
    strip_color:    Strip ANSI colour codes before output.
    prefix:         Arbitrary string prepended after all other transforms.
    """
    flt = LineFilter(
        include=include,
        exclude=exclude,
        case_sensitive=case_sensitive,
    )
    filtered = flt.apply(lines)
    formatted = format_lines(
        filtered,
        filename=filename,
        line_numbers=line_numbers,
        strip_color=strip_color,
        prefix=prefix,
    )
    yield from formatted


def run_pipeline(
    lines: Iterable[str],
    output: IO[str],
    **kwargs,
) -> int:
    """Write pipeline output to *output* and return the number of lines written.

    All keyword arguments are forwarded to :func:`build_pipeline`.
    """
    count = 0
    for line in build_pipeline(lines, **kwargs):
        output.write(line)
        count += 1
    return count
