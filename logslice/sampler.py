"""Line sampler: keep every N-th line from a stream of log lines."""

from __future__ import annotations

from typing import Iterable, Iterator


class LineSampler:
    """Yield only every *rate*-th line from an iterable of strings.

    Parameters
    ----------
    rate:
        Sampling rate.  ``1`` means keep every line (no-op).  ``10`` means
        keep one line out of every ten.  Must be a positive integer.
    offset:
        Which line within each block of *rate* lines to keep (0-based).
        Defaults to ``0`` (the first line of each block).
    """

    def __init__(self, rate: int = 1, offset: int = 0) -> None:
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate!r}")
        if not (0 <= offset < rate):
            raise ValueError(
                f"offset must be in [0, rate), got offset={offset!r}, rate={rate!r}"
            )
        self.rate = rate
        self.offset = offset

    # ------------------------------------------------------------------
    # public helpers
    # ------------------------------------------------------------------

    def is_noop(self) -> bool:
        """Return *True* when every line is kept (rate == 1)."""
        return self.rate == 1

    def apply(self, lines: Iterable[str]) -> Iterator[str]:
        """Yield sampled lines from *lines*."""
        if self.is_noop():
            yield from lines
            return
        for index, line in enumerate(lines):
            if index % self.rate == self.offset:
                yield line

    def __repr__(self) -> str:  # pragma: no cover
        return f"LineSampler(rate={self.rate!r}, offset={self.offset!r})"
