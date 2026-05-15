"""Tests for logslice.cache."""

import json
import pytest
from pathlib import Path

from logslice.cache import load_offsets, save_offsets, clear_cache, _file_key


@pytest.fixture()
def log_file(tmp_path: Path) -> Path:
    p = tmp_path / "app.log"
    p.write_text("2024-01-01 00:00:00 hello\n2024-01-01 01:00:00 world\n")
    return p


@pytest.fixture()
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / "cache"


class TestSaveAndLoad:
    def test_returns_none_on_cold_cache(self, log_file, cache_dir):
        result = load_offsets(log_file, "2024-01-01", "2024-01-02", cache_dir)
        assert result is None

    def test_round_trip(self, log_file, cache_dir):
        save_offsets(log_file, "2024-01-01", "2024-01-02", 0, 128, cache_dir)
        result = load_offsets(log_file, "2024-01-01", "2024-01-02", cache_dir)
        assert result == (0, 128)

    def test_different_ranges_stored_independently(self, log_file, cache_dir):
        save_offsets(log_file, "2024-01-01", "2024-01-02", 0, 50, cache_dir)
        save_offsets(log_file, "2024-01-02", "2024-01-03", 50, 200, cache_dir)
        assert load_offsets(log_file, "2024-01-01", "2024-01-02", cache_dir) == (0, 50)
        assert load_offsets(log_file, "2024-01-02", "2024-01-03", cache_dir) == (50, 200)

    def test_cache_dir_created_automatically(self, log_file, tmp_path):
        cache_dir = tmp_path / "deep" / "nested" / "cache"
        assert not cache_dir.exists()
        save_offsets(log_file, "A", "B", 0, 10, cache_dir)
        assert cache_dir.exists()

    def test_stale_cache_after_file_modification(self, log_file, cache_dir):
        save_offsets(log_file, "2024-01-01", "2024-01-02", 0, 100, cache_dir)
        # Modify the file so mtime changes
        log_file.write_text(log_file.read_text() + "extra line\n")
        result = load_offsets(log_file, "2024-01-01", "2024-01-02", cache_dir)
        assert result is None

    def test_corrupted_cache_file_returns_none(self, log_file, cache_dir):
        cache_dir.mkdir(parents=True)
        key = _file_key(log_file)
        (cache_dir / f"{key}.json").write_text("not-json{{{")
        result = load_offsets(log_file, "2024-01-01", "2024-01-02", cache_dir)
        assert result is None


class TestClearCache:
    def test_clear_empty_dir_returns_zero(self, cache_dir):
        cache_dir.mkdir()
        assert clear_cache(cache_dir) == 0

    def test_clear_nonexistent_dir_returns_zero(self, tmp_path):
        assert clear_cache(tmp_path / "no_such_dir") == 0

    def test_clear_removes_all_json_files(self, log_file, cache_dir):
        save_offsets(log_file, "A", "B", 0, 10, cache_dir)
        save_offsets(log_file, "C", "D", 10, 20, cache_dir)
        removed = clear_cache(cache_dir)
        # Both ranges share the same key file, so only 1 file written
        assert removed >= 1
        assert list(cache_dir.glob("*.json")) == []
