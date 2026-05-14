"""Integration tests for logslice.slicer."""

import gzip
from datetime import datetime
from pathlib import Path

import pytest

from logslice.log_archive import LogArchive
from logslice.slicer import slice_archive, slice_path


@pytest.fixture()
def log_dir(tmp_path):
    return tmp_path


def _write(path: Path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_gz(path: Path, lines):
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


LINES_DAY1 = [
    "2024-03-01T08:00:00 boot",
    "2024-03-01T09:00:00 login alice",
    "2024-03-01T10:00:00 logout alice",
]

LINES_DAY2 = [
    "2024-03-02T08:00:00 boot",
    "2024-03-02T09:30:00 login bob",
    "2024-03-02T11:00:00 error disk full",
]


class TestSliceArchive:
    def test_returns_lines_within_range(self, log_dir):
        _write(log_dir / "app.log.2", LINES_DAY1)
        _write(log_dir / "app.log", LINES_DAY2)
        archive = LogArchive.from_path(log_dir / "app.log")
        results = list(
            slice_archive(
                archive,
                datetime(2024, 3, 1, 9, 0, 0),
                datetime(2024, 3, 2, 9, 30, 0),
            )
        )
        assert any("login alice" in r for r in results)
        assert any("login bob" in r for r in results)
        assert not any("boot" in r and "03-01" in r for r in results)
        assert not any("error" in r for r in results)

    def test_gz_file_included(self, log_dir):
        _write_gz(log_dir / "app.log.1.gz", LINES_DAY1)
        _write(log_dir / "app.log", LINES_DAY2)
        archive = LogArchive.from_path(log_dir / "app.log")
        results = list(
            slice_archive(
                archive,
                datetime(2024, 3, 1, 0, 0, 0),
                datetime(2024, 3, 2, 23, 59, 59),
            )
        )
        assert any("login alice" in r for r in results)
        assert any("login bob" in r for r in results)

    def test_invalid_range_raises(self, log_dir):
        _write(log_dir / "app.log", LINES_DAY1)
        archive = LogArchive.from_path(log_dir / "app.log")
        with pytest.raises(ValueError, match="start_time"):
            list(
                slice_archive(
                    archive,
                    datetime(2024, 3, 2),
                    datetime(2024, 3, 1),
                )
            )

    def test_no_matching_lines_returns_empty(self, log_dir):
        _write(log_dir / "app.log", LINES_DAY1)
        archive = LogArchive.from_path(log_dir / "app.log")
        results = list(
            slice_archive(
                archive,
                datetime(2025, 1, 1),
                datetime(2025, 1, 2),
            )
        )
        assert results == []


class TestSlicePath:
    def test_convenience_wrapper(self, log_dir):
        _write(log_dir / "svc.log", LINES_DAY2)
        results = list(
            slice_path(
                log_dir / "svc.log",
                datetime(2024, 3, 2, 9, 0, 0),
                datetime(2024, 3, 2, 10, 0, 0),
            )
        )
        assert any("login bob" in r for r in results)
        assert not any("error" in r for r in results)
