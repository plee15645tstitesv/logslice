"""Tests for logslice.formatter."""

import pytest

from logslice.formatter import (
    add_filename_prefix,
    add_line_numbers,
    add_prefix,
    format_lines,
    strip_ansi,
)

LINES = ["alpha\n", "beta\n", "gamma\n"]


class TestAddPrefix:
    def test_prepends_to_all_lines(self):
        result = list(add_prefix(LINES, ">> "))
        assert result == [">> alpha\n", ">> beta\n", ">> gamma\n"]

    def test_empty_prefix_unchanged(self):
        assert list(add_prefix(LINES, "")) == LINES


class TestAddFilenamePrefix:
    def test_prepends_filename(self):
        result = list(add_filename_prefix(LINES, "app.log"))
        assert result[0] == "app.log:alpha\n"
        assert result[2] == "app.log:gamma\n"


class TestAddLineNumbers:
    def test_starts_at_one(self):
        result = list(add_line_numbers(["hello\n"]))
        assert result[0].startswith("     1  ")

    def test_custom_start(self):
        result = list(add_line_numbers(["x\n"], start=42))
        assert result[0].startswith("    42  ")

    def test_increments(self):
        result = list(add_line_numbers(LINES))
        assert result[0].startswith("     1  ")
        assert result[2].startswith("     3  ")


class TestStripAnsi:
    def test_removes_colour_codes(self):
        coloured = "\x1b[31mERROR\x1b[0m disk full"
        assert strip_ansi(coloured) == "ERROR disk full"

    def test_plain_text_unchanged(self):
        assert strip_ansi("plain text") == "plain text"


class TestFormatLines:
    def test_no_options_passthrough(self):
        assert list(format_lines(LINES)) == LINES

    def test_filename_option(self):
        result = list(format_lines(["hi\n"], filename="f.log"))
        assert result == ["f.log:hi\n"]

    def test_line_numbers_option(self):
        result = list(format_lines(["hi\n"], line_numbers=True))
        assert "1" in result[0]
        assert "hi" in result[0]

    def test_strip_color_option(self):
        coloured = ["\x1b[32mOK\x1b[0m\n"]
        result = list(format_lines(coloured, strip_color=True))
        assert result == ["OK\n"]

    def test_prefix_applied_last(self):
        result = list(format_lines(["hi\n"], prefix="--"))
        assert result == ["--hi\n"]

    def test_combined_options(self):
        result = list(
            format_lines(["hi\n"], filename="f.log", line_numbers=True)
        )
        assert "f.log:" in result[0]
        assert "1" in result[0]
