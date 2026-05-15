"""Command-line interface for logslice.

Provides the `logslice` entry point that wires together file discovery,
time-range slicing, progress reporting, and output writing.
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from logslice.log_archive import LogArchive
from logslice.output_writer import write_lines
from logslice.progress import SliceProgress
from logslice.slicer import slice_archive
from logslice.timestamp_parser import parse_timestamp


_DATE_FORMATS_HELP = (
    "Accepted formats: ISO-8601 (2024-01-15T08:00:00), "
    "Unix timestamp (1705305600), or date only (2024-01-15 treated as 00:00:00)."
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Extract a time-range segment from rotated log archives.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_DATE_FORMATS_HELP,
    )
    parser.add_argument(
        "log_path",
        metavar="LOG_PATH",
        help="Base log file path (e.g. /var/log/app.log). "
             "Rotated siblings are discovered automatically.",
    )
    parser.add_argument(
        "--start",
        required=True,
        metavar="TIMESTAMP",
        help="Start of the time range (inclusive).",
    )
    parser.add_argument(
        "--end",
        required=True,
        metavar="TIMESTAMP",
        help="End of the time range (inclusive).",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout. "
             "Use a .gz extension to compress automatically.",
    )
    parser.add_argument(
        "--compress",
        "-z",
        action="store_true",
        default=False,
        help="Compress output with gzip (implied when --output ends with .gz).",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="Suppress progress output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:  # noqa: UP007
    """Entry point for the `logslice` CLI.

    Returns an exit code (0 = success, non-zero = error).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    # --- parse timestamps ---------------------------------------------------
    try:
        start_dt = parse_timestamp(args.start)
        end_dt = parse_timestamp(args.end)
    except ValueError as exc:
        parser.error(f"Invalid timestamp: {exc}")
        return 1  # unreachable; parser.error() exits, but satisfies type checkers

    if start_dt > end_dt:
        parser.error("--start must not be later than --end")

    # --- discover archive ---------------------------------------------------
    try:
        archive = LogArchive.from_path(args.log_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"logslice: error: {exc}", file=sys.stderr)
        return 2

    # --- set up progress reporting -----------------------------------------
    progress = SliceProgress(output=sys.stderr)
    if args.quiet:
        progress.disable()

    # --- slice --------------------------------------------------------------
    lines = slice_archive(archive, start_dt, end_dt, progress=progress)

    # --- write output -------------------------------------------------------
    compress = args.compress or (
        args.output is not None and str(args.output).endswith(".gz")
    )
    try:
        count = write_lines(
            lines,
            destination=args.output,
            compress=compress,
        )
    except OSError as exc:
        print(f"logslice: error writing output: {exc}", file=sys.stderr)
        return 3

    progress.finish()

    if not args.quiet:
        print(f"logslice: wrote {count} line(s).", file=sys.stderr)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
