"""Collect and report slice operation statistics."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FileStats:
    path: str
    lines_scanned: int = 0
    lines_matched: int = 0
    bytes_read: int = 0
    duration_sec: float = 0.0


@dataclass
class SliceStats:
    start_time: float = field(default_factory=time.monotonic)
    end_time: Optional[float] = None
    files: List[FileStats] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    def record_file(
        self,
        path: str,
        lines_scanned: int,
        lines_matched: int,
        bytes_read: int,
        duration_sec: float,
    ) -> FileStats:
        fs = FileStats(
            path=path,
            lines_scanned=lines_scanned,
            lines_matched=lines_matched,
            bytes_read=bytes_read,
            duration_sec=duration_sec,
        )
        self.files.append(fs)
        return fs

    def finish(self) -> None:
        self.end_time = time.monotonic()

    # ------------------------------------------------------------------ #
    @property
    def total_lines_scanned(self) -> int:
        return sum(f.lines_scanned for f in self.files)

    @property
    def total_lines_matched(self) -> int:
        return sum(f.lines_matched for f in self.files)

    @property
    def total_bytes_read(self) -> int:
        return sum(f.bytes_read for f in self.files)

    @property
    def elapsed_sec(self) -> float:
        end = self.end_time if self.end_time is not None else time.monotonic()
        return end - self.start_time

    # ------------------------------------------------------------------ #
    def summary(self) -> str:
        lines = [
            f"Files processed : {len(self.files)}",
            f"Lines scanned   : {self.total_lines_scanned:,}",
            f"Lines matched   : {self.total_lines_matched:,}",
            f"Bytes read      : {self.total_bytes_read:,}",
            f"Elapsed         : {self.elapsed_sec:.3f}s",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SliceStats(files={len(self.files)}, "
            f"matched={self.total_lines_matched}, "
            f"elapsed={self.elapsed_sec:.3f}s)"
        )
