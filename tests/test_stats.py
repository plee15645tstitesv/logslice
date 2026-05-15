"""Tests for logslice.stats."""
import time

import pytest

from logslice.stats import FileStats, SliceStats


class TestFileStats:
    def test_defaults_are_zero(self):
        fs = FileStats(path="/var/log/app.log")
        assert fs.lines_scanned == 0
        assert fs.lines_matched == 0
        assert fs.bytes_read == 0
        assert fs.duration_sec == 0.0

    def test_stores_path(self):
        fs = FileStats(path="/var/log/app.log")
        assert fs.path == "/var/log/app.log"


class TestSliceStats:
    def test_record_file_appends_entry(self):
        stats = SliceStats()
        stats.record_file("/a.log", lines_scanned=100, lines_matched=10,
                          bytes_read=2048, duration_sec=0.5)
        assert len(stats.files) == 1
        assert stats.files[0].path == "/a.log"

    def test_record_file_returns_file_stats(self):
        stats = SliceStats()
        fs = stats.record_file("/b.log", 50, 5, 1024, 0.1)
        assert isinstance(fs, FileStats)
        assert fs.lines_scanned == 50

    def test_total_lines_scanned_sums_files(self):
        stats = SliceStats()
        stats.record_file("/a.log", 100, 10, 1000, 0.1)
        stats.record_file("/b.log", 200, 20, 2000, 0.2)
        assert stats.total_lines_scanned == 300

    def test_total_lines_matched_sums_files(self):
        stats = SliceStats()
        stats.record_file("/a.log", 100, 10, 1000, 0.1)
        stats.record_file("/b.log", 200, 25, 2000, 0.2)
        assert stats.total_lines_matched == 35

    def test_total_bytes_read_sums_files(self):
        stats = SliceStats()
        stats.record_file("/a.log", 100, 10, 1024, 0.1)
        stats.record_file("/b.log", 200, 20, 4096, 0.2)
        assert stats.total_bytes_read == 5120

    def test_elapsed_sec_increases_over_time(self):
        stats = SliceStats()
        time.sleep(0.05)
        assert stats.elapsed_sec >= 0.04

    def test_finish_freezes_elapsed(self):
        stats = SliceStats()
        stats.finish()
        frozen = stats.elapsed_sec
        time.sleep(0.05)
        assert stats.elapsed_sec == pytest.approx(frozen, abs=1e-9)

    def test_summary_contains_key_labels(self):
        stats = SliceStats()
        stats.record_file("/a.log", 100, 10, 1024, 0.1)
        stats.finish()
        summary = stats.summary()
        assert "Files processed" in summary
        assert "Lines scanned" in summary
        assert "Lines matched" in summary
        assert "Bytes read" in summary
        assert "Elapsed" in summary

    def test_summary_values_are_correct(self):
        stats = SliceStats()
        stats.record_file("/a.log", 42, 7, 512, 0.0)
        summary = stats.summary()
        assert "42" in summary
        assert "7" in summary
        assert "512" in summary

    def test_empty_stats_summary(self):
        stats = SliceStats()
        stats.finish()
        summary = stats.summary()
        assert "0" in summary
