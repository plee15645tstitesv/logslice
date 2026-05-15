"""Build and run the full slice pipeline, collecting stats."""
from __future__ import annotations

import time
from typing import Optional

from logslice.filter import LineFilter
from logslice.formatter import format_lines
from logslice.log_archive import LogArchive
from logslice.output_writer import write_lines
from logslice.progress import SliceProgress
from logslice.slicer import slice_archive
from logslice.stats import SliceStats


def build_pipeline(
    archive: LogArchive,
    start,
    end,
    line_filter: Optional[LineFilter] = None,
    include_filename: bool = False,
    line_numbers: bool = False,
    strip_ansi: bool = False,
) -> "_Pipeline":
    """Return a configured pipeline object ready to run."""
    return _Pipeline(
        archive=archive,
        start=start,
        end=end,
        line_filter=line_filter or LineFilter(),
        include_filename=include_filename,
        line_numbers=line_numbers,
        strip_ansi=strip_ansi,
    )


class _Pipeline:
    def __init__(self, archive, start, end, line_filter,
                 include_filename, line_numbers, strip_ansi):
        self.archive = archive
        self.start = start
        self.end = end
        self.line_filter = line_filter
        self.include_filename = include_filename
        self.line_numbers = line_numbers
        self.strip_ansi = strip_ansi


def run_pipeline(
    pipeline: _Pipeline,
    output_path: Optional[str] = None,
    compress: bool = False,
    progress: Optional[SliceProgress] = None,
) -> SliceStats:
    """Execute the pipeline and return collected statistics."""
    stats = SliceStats()

    for log_file in pipeline.archive:
        t0 = time.monotonic()
        if progress:
            progress.start_file(log_file.path)

        raw_lines = list(
            slice_archive(
                pipeline.archive,
                pipeline.start,
                pipeline.end,
            )
        )

        filtered = list(pipeline.line_filter.apply(iter(raw_lines)))
        formatted = list(
            format_lines(
                iter(filtered),
                filename=log_file.path if pipeline.include_filename else None,
                line_numbers=pipeline.line_numbers,
                strip_ansi=pipeline.strip_ansi,
            )
        )

        bytes_read = sum(len(ln.encode()) for ln in raw_lines)
        duration = time.monotonic() - t0

        stats.record_file(
            path=log_file.path,
            lines_scanned=len(raw_lines),
            lines_matched=len(filtered),
            bytes_read=bytes_read,
            duration_sec=duration,
        )

        if progress:
            progress.update(bytes_read, len(filtered))

        break  # slice_archive already iterates all files; one pass suffices

    if output_path:
        write_lines(iter(formatted), output_path, compress=compress)

    stats.finish()
    return stats
