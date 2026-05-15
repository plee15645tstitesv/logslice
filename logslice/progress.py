"""Progress reporting for log slicing operations."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Optional, TextIO


@dataclass
class SliceProgress:
    """Tracks and reports progress while scanning log files."""

    total_files: int
    output: TextIO = field(default_factory=lambda: sys.stderr)
    _current_file: int = field(default=0, init=False)
    _current_filename: str = field(default="", init=False)
    _lines_emitted: int = field(default=0, init=False)
    _bytes_scanned: int = field(default=0, init=False)
    _enabled: bool = field(default=True, init=False)

    def disable(self) -> None:
        """Suppress all progress output (e.g. when stdout is a pipe)."""
        self._enabled = False

    def start_file(self, filename: str) -> None:
        """Signal that scanning of *filename* is beginning."""
        self._current_file += 1
        self._current_filename = filename
        self._render()

    def update(self, bytes_scanned: int, lines_emitted: int) -> None:
        """Accumulate *bytes_scanned* and *lines_emitted* since last call."""
        self._bytes_scanned += bytes_scanned
        self._lines_emitted += lines_emitted
        self._render()

    def finish(self) -> None:
        """Print a final summary line."""
        if not self._enabled:
            return
        summary = (
            f"\rDone. "
            f"{self._current_file}/{self.total_files} files scanned, "
            f"{self._bytes_scanned:,} bytes read, "
            f"{self._lines_emitted:,} lines matched.\n"
        )
        self.output.write(summary)
        self.output.flush()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _render(self) -> None:
        if not self._enabled:
            return
        name = self._current_filename
        if len(name) > 30:
            name = "..." + name[-27:]
        line = (
            f"\r[{self._current_file}/{self.total_files}] "
            f"{name:<30} "
            f"{self._lines_emitted:>6} lines matched"
        )
        self.output.write(line)
        self.output.flush()


def make_progress(
    total_files: int,
    *,
    quiet: bool = False,
    output: Optional[TextIO] = None,
) -> SliceProgress:
    """Factory that creates a :class:`SliceProgress` instance.

    Parameters
    ----------
    total_files:
        Total number of files that will be processed.
    quiet:
        When *True* progress output is suppressed.
    output:
        Writable text stream for progress messages (defaults to *stderr*).
    """
    out = output if output is not None else sys.stderr
    tracker = SliceProgress(total_files=total_files, output=out)
    if quiet:
        tracker.disable()
    return tracker
