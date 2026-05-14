"""Tests for logslice.line_scanner binary-search helpers."""

import io
from datetime import datetime

import pytest

from logslice.line_scanner import find_end_offset, find_start_offset, _read_line_at


def _make_fh(lines):
    """Return a seekable BytesIO pre-filled with timestamped log lines."""
    content = "\n".join(lines).encode() + b"\n"
    return io.BytesIO(content)


LINES = [
    "2024-01-01T00:00:00 startup complete",
    "2024-01-01T01:00:00 user login",
    "2024-01-01T02:00:00 cache miss",
    "2024-01-01T03:00:00 db query",
    "2024-01-01T04:00:00 shutdown",
]


class TestReadLineAt:
    def test_reads_first_line(self):
        fh = _make_fh(LINES)
        offset, line = _read_line_at(fh, 0)
        assert offset == 0
        assert line == LINES[0]

    def test_empty_file_returns_none(self):
        fh = io.BytesIO(b"")
        _, line = _read_line_at(fh, 0)
        assert line is None

    def test_mid_line_rewinds_to_start(self):
        fh = _make_fh(LINES)
        # Seek to byte 5 (inside first line) — should still return first line.
        offset, line = _read_line_at(fh, 5)
        assert line == LINES[0]
        assert offset == 0


class TestFindStartOffset:
    def test_start_before_all_lines_returns_zero(self):
        fh = _make_fh(LINES)
        dt = datetime(2023, 12, 31)
        assert find_start_offset(fh, dt) == 0

    def test_start_after_all_lines_returns_file_size(self):
        fh = _make_fh(LINES)
        dt = datetime(2025, 1, 1)
        fh.seek(0, 2)
        size = fh.tell()
        assert find_start_offset(fh, dt) == size

    def test_start_at_exact_timestamp(self):
        fh = _make_fh(LINES)
        dt = datetime(2024, 1, 1, 2, 0, 0)
        offset = find_start_offset(fh, dt)
        fh.seek(offset)
        line = fh.readline().decode()
        assert "02:00:00" in line

    def test_empty_file(self):
        fh = io.BytesIO(b"")
        assert find_start_offset(fh, datetime(2024, 1, 1)) == 0


class TestFindEndOffset:
    def test_end_after_all_lines_returns_file_size(self):
        fh = _make_fh(LINES)
        dt = datetime(2025, 1, 1)
        fh.seek(0, 2)
        size = fh.tell()
        assert find_end_offset(fh, dt) == size

    def test_end_before_all_lines_returns_zero(self):
        fh = _make_fh(LINES)
        dt = datetime(2023, 1, 1)
        assert find_end_offset(fh, dt) == 0

    def test_end_at_exact_timestamp_includes_that_line(self):
        fh = _make_fh(LINES)
        dt = datetime(2024, 1, 1, 2, 0, 0)
        offset = find_end_offset(fh, dt)
        fh.seek(0)
        content = fh.read(offset).decode()
        assert "02:00:00" in content
        assert "03:00:00" not in content
