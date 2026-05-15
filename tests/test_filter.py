"""Tests for logslice.filter.LineFilter."""

import pytest

from logslice.filter import LineFilter


LINES = [
    "2024-01-01 INFO  server started",
    "2024-01-01 DEBUG request received",
    "2024-01-01 ERROR disk full",
    "2024-01-01 WARN  memory low",
    "2024-01-01 INFO  server stopped",
]


class TestLineFilterIsNoop:
    def test_no_patterns_is_noop(self):
        f = LineFilter()
        assert f.is_noop is True

    def test_include_not_noop(self):
        f = LineFilter(include="ERROR")
        assert f.is_noop is False

    def test_exclude_not_noop(self):
        f = LineFilter(exclude="DEBUG")
        assert f.is_noop is False


class TestLineFilterMatches:
    def test_include_keeps_matching_lines(self):
        f = LineFilter(include="ERROR")
        assert f.matches("2024-01-01 ERROR disk full") is True
        assert f.matches("2024-01-01 INFO  server started") is False

    def test_exclude_drops_matching_lines(self):
        f = LineFilter(exclude="DEBUG")
        assert f.matches("2024-01-01 DEBUG request received") is False
        assert f.matches("2024-01-01 INFO  server started") is True

    def test_include_and_exclude_combined(self):
        f = LineFilter(include="INFO", exclude="stopped")
        assert f.matches("2024-01-01 INFO  server started") is True
        assert f.matches("2024-01-01 INFO  server stopped") is False
        assert f.matches("2024-01-01 ERROR disk full") is False

    def test_case_insensitive_include(self):
        f = LineFilter(include="error", case_sensitive=False)
        assert f.matches("2024-01-01 ERROR disk full") is True

    def test_case_sensitive_include_no_match(self):
        f = LineFilter(include="error", case_sensitive=True)
        assert f.matches("2024-01-01 ERROR disk full") is False


class TestLineFilterApply:
    def test_noop_yields_all_lines(self):
        f = LineFilter()
        assert list(f.apply(LINES)) == LINES

    def test_include_filters_correctly(self):
        f = LineFilter(include=r"(ERROR|WARN)")
        result = list(f.apply(LINES))
        assert len(result) == 2
        assert all("ERROR" in ln or "WARN" in ln for ln in result)

    def test_exclude_filters_correctly(self):
        f = LineFilter(exclude="DEBUG")
        result = list(f.apply(LINES))
        assert all("DEBUG" not in ln for ln in result)
        assert len(result) == len(LINES) - 1

    def test_empty_input_yields_nothing(self):
        f = LineFilter(include="ERROR")
        assert list(f.apply([])) == []
