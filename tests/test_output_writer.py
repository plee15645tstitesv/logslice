"""Tests for logslice.output_writer."""

from __future__ import annotations

import gzip
import io
import sys
from pathlib import Path

import pytest

from logslice.output_writer import write_lines


@pytest.fixture()
def out_dir(tmp_path: Path) -> Path:
    return tmp_path


LINES = ["2024-01-01 00:00:01 hello\n", "2024-01-01 00:00:02 world\n"]


class TestWriteLines:
    def test_writes_plain_file(self, out_dir: Path) -> None:
        dest = out_dir / "out.log"
        count = write_lines(LINES, dest)
        assert count == 2
        assert dest.read_text() == "".join(LINES)

    def test_returns_line_count(self, out_dir: Path) -> None:
        dest = out_dir / "out.log"
        count = write_lines(LINES, dest)
        assert count == len(LINES)

    def test_writes_gzip_when_compress_flag(self, out_dir: Path) -> None:
        dest = out_dir / "out.log"
        write_lines(LINES, dest, compress=True)
        with gzip.open(dest, "rt") as fh:
            content = fh.read()
        assert content == "".join(LINES)

    def test_writes_gzip_when_gz_extension(self, out_dir: Path) -> None:
        dest = out_dir / "out.log.gz"
        write_lines(LINES, dest)
        with gzip.open(dest, "rt") as fh:
            content = fh.read()
        assert content == "".join(LINES)

    def test_appends_newline_if_missing(self, out_dir: Path) -> None:
        dest = out_dir / "out.log"
        write_lines(["no newline"], dest)
        assert dest.read_bytes().endswith(b"\n")

    def test_empty_iterable_writes_nothing(self, out_dir: Path) -> None:
        dest = out_dir / "out.log"
        count = write_lines([], dest)
        assert count == 0
        assert dest.read_bytes() == b""

    def test_writes_to_stdout(self, capsysbinary: pytest.CaptureFixture) -> None:
        count = write_lines(LINES, dest=None)
        captured = capsysbinary.readouterr()
        assert count == 2
        assert captured.out == "".join(LINES).encode()

    def test_bytes_lines_accepted(self, out_dir: Path) -> None:
        dest = out_dir / "out.log"
        byte_lines = [l.encode() for l in LINES]
        count = write_lines(byte_lines, dest)  # type: ignore[arg-type]
        assert count == 2
        assert dest.read_text() == "".join(LINES)
