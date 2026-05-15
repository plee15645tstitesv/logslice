"""Line-level filtering for extracted log segments."""

from __future__ import annotations

import re
from typing import Iterable, Iterator, Optional


class LineFilter:
    """Apply include/exclude patterns to log lines.

    Parameters
    ----------
    include:
        If given, only lines matching this regex are kept.
    exclude:
        If given, lines matching this regex are dropped.
    case_sensitive:
        Whether regex matching is case-sensitive (default True).
    """

    def __init__(
        self,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        case_sensitive: bool = True,
    ) -> None:
        flags = 0 if case_sensitive else re.IGNORECASE
        self._include: Optional[re.Pattern[str]] = (
            re.compile(include, flags) if include else None
        )
        self._exclude: Optional[re.Pattern[str]] = (
            re.compile(exclude, flags) if exclude else None
        )

    @property
    def is_noop(self) -> bool:
        """True when no patterns are configured."""
        return self._include is None and self._exclude is None

    def matches(self, line: str) -> bool:
        """Return True if *line* passes all configured filters."""
        if self._include is not None and not self._include.search(line):
            return False
        if self._exclude is not None and self._exclude.search(line):
            return False
        return True

    def apply(self, lines: Iterable[str]) -> Iterator[str]:
        """Yield only lines that pass the filter."""
        if self.is_noop:
            yield from lines
            return
        for line in lines:
            if self.matches(line):
                yield line

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"LineFilter(include={self._include!r}, "
            f"exclude={self._exclude!r})"
        )
