"""Tests for logslice.file_finder."""

import os
from pathlib import Path

import pytest

from logslice.file_finder import find_rotated_files, _rotation_sort_key


@pytest.fixture()
def log_dir(tmp_path: Path) -> Path:
    return tmp_path


def _touch(directory: Path, name: str, content: str = "") -> Path:
    p = directory / name
    p.write_text(content)
    return p


class TestFindRotatedFiles:
    def test_returns_only_base_file_when_no_rotation(self, log_dir):
        _touch(log_dir, "app.log", "line1\n")
        result = find_rotated_files(str(log_dir / "app.log"))
        assert [p.name for p in result] == ["app.log"]

    def test_numeric_rotation_ordered_oldest_first(self, log_dir):
        for name in ["app.log", "app.log.1", "app.log.2", "app.log.3"]:
            _touch(log_dir, name)
        result = find_rotated_files(str(log_dir / "app.log"))
        assert [p.name for p in result] == [
            "app.log.3",
            "app.log.2",
            "app.log.1",
            "app.log",
        ]

    def test_gz_files_included(self, log_dir):
        for name in ["app.log", "app.log.1", "app.log.2.gz"]:
            _touch(log_dir, name)
        result = find_rotated_files(str(log_dir / "app.log"))
        names = [p.name for p in result]
        assert "app.log.2.gz" in names
        assert names.index("app.log.2.gz") < names.index("app.log.1")

    def test_date_based_rotation_ordered(self, log_dir):
        for name in ["app.log", "app.log.2023-01-10", "app.log.2023-01-15"]:
            _touch(log_dir, name)
        result = find_rotated_files(str(log_dir / "app.log"))
        names = [p.name for p in result]
        assert names.index("app.log.2023-01-10") < names.index("app.log.2023-01-15")
        assert names[-1] == "app.log"

    def test_unrelated_files_excluded(self, log_dir):
        _touch(log_dir, "app.log")
        _touch(log_dir, "other.log")
        _touch(log_dir, "app.log.bak")
        result = find_rotated_files(str(log_dir / "app.log"))
        names = [p.name for p in result]
        assert "other.log" not in names

    def test_raises_when_directory_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            find_rotated_files(str(tmp_path / "nonexistent" / "app.log"))

    def test_empty_directory_returns_empty_list(self, log_dir):
        result = find_rotated_files(str(log_dir / "app.log"))
        assert result == []
