"""Tests for logslice.progress."""

from __future__ import annotations

import io

import pytest

from logslice.progress import SliceProgress, make_progress


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _buf() -> io.StringIO:
    return io.StringIO()


# ---------------------------------------------------------------------------
# SliceProgress
# ---------------------------------------------------------------------------

class TestSliceProgress:
    def test_start_file_increments_counter(self):
        buf = _buf()
        p = SliceProgress(total_files=3, output=buf)
        p.start_file("app.log")
        assert p._current_file == 1
        assert p._current_filename == "app.log"

    def test_start_file_writes_to_output(self):
        buf = _buf()
        p = SliceProgress(total_files=2, output=buf)
        p.start_file("app.log")
        assert buf.getvalue() != ""

    def test_update_accumulates_bytes_and_lines(self):
        buf = _buf()
        p = SliceProgress(total_files=1, output=buf)
        p.update(bytes_scanned=512, lines_emitted=10)
        p.update(bytes_scanned=256, lines_emitted=5)
        assert p._bytes_scanned == 768
        assert p._lines_emitted == 15

    def test_finish_writes_summary(self):
        buf = _buf()
        p = SliceProgress(total_files=1, output=buf)
        p.start_file("app.log")
        p.update(bytes_scanned=100, lines_emitted=3)
        p.finish()
        out = buf.getvalue()
        assert "Done" in out
        assert "3" in out

    def test_disabled_produces_no_output(self):
        buf = _buf()
        p = SliceProgress(total_files=5, output=buf)
        p.disable()
        p.start_file("app.log")
        p.update(bytes_scanned=1024, lines_emitted=20)
        p.finish()
        assert buf.getvalue() == ""

    def test_long_filename_is_truncated_in_output(self):
        buf = _buf()
        long_name = "a" * 50 + ".log"
        p = SliceProgress(total_files=1, output=buf)
        p.start_file(long_name)
        rendered = buf.getvalue()
        # The raw filename should NOT appear verbatim; ellipsis prefix used
        assert long_name not in rendered
        assert "..." in rendered


# ---------------------------------------------------------------------------
# make_progress factory
# ---------------------------------------------------------------------------

class TestMakeProgress:
    def test_returns_slice_progress_instance(self):
        p = make_progress(total_files=4)
        assert isinstance(p, SliceProgress)
        assert p.total_files == 4

    def test_quiet_disables_output(self):
        buf = _buf()
        p = make_progress(total_files=2, quiet=True, output=buf)
        p.start_file("x.log")
        p.finish()
        assert buf.getvalue() == ""

    def test_custom_output_stream(self):
        buf = _buf()
        p = make_progress(total_files=1, output=buf)
        p.start_file("x.log")
        assert buf.getvalue() != ""
