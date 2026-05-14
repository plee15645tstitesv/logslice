"""Tests for logslice.log_archive.LogArchive."""

import gzip
from pathlib import Path

import pytest

from logslice.log_archive import LogArchive


@pytest.fixture()
def log_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


def _write_gz(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    with gzip.open(p, "wt") as fh:
        fh.write(content)
    return p


class TestLogArchiveFromPath:
    def test_creates_archive_with_correct_file_count(self, log_dir):
        for name in ["app.log", "app.log.1", "app.log.2"]:
            _write(log_dir, name, "")
        archive = LogArchive.from_path(str(log_dir / "app.log"))
        assert len(archive) == 3

    def test_base_path_is_resolved(self, log_dir):
        _write(log_dir, "app.log", "")
        archive = LogArchive.from_path(str(log_dir / "app.log"))
        assert archive.base_path.is_absolute()

    def test_iter_yields_paths(self, log_dir):
        _write(log_dir, "app.log", "")
        archive = LogArchive.from_path(str(log_dir / "app.log"))
        paths = list(archive)
        assert all(isinstance(p, Path) for p in paths)


class TestLogArchiveTotalSize:
    def test_total_size_bytes_sums_files(self, log_dir):
        _write(log_dir, "app.log", "hello\n")  # 6 bytes
        _write(log_dir, "app.log.1", "world\n")  # 6 bytes
        archive = LogArchive.from_path(str(log_dir / "app.log"))
        assert archive.total_size_bytes == 12


class TestLogArchiveIterLines:
    def test_iter_lines_plain_text(self, log_dir):
        _write(log_dir, "app.log.1", "old line\n")
        _write(log_dir, "app.log", "new line\n")
        archive = LogArchive.from_path(str(log_dir / "app.log"))
        lines = list(archive.iter_lines())
        assert lines[0] == "old line\n"
        assert lines[-1] == "new line\n"

    def test_iter_lines_gz_transparent(self, log_dir):
        _write_gz(log_dir, "app.log.2.gz", "compressed line\n")
        _write(log_dir, "app.log.1", "plain line\n")
        _write(log_dir, "app.log", "current line\n")
        archive = LogArchive.from_path(str(log_dir / "app.log"))
        lines = list(archive.iter_lines())
        assert "compressed line\n" in lines
        assert lines[0] == "compressed line\n"

    def test_iter_lines_empty_archive(self, log_dir):
        archive = LogArchive(base_path=log_dir / "app.log", files=[])
        assert list(archive.iter_lines()) == []
