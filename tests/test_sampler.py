"""Tests for logslice.sampler.LineSampler."""

import pytest

from logslice.sampler import LineSampler


LINES = [f"line {i}\n" for i in range(10)]


# ---------------------------------------------------------------------------
# construction / validation
# ---------------------------------------------------------------------------

class TestLineSamplerInit:
    def test_default_rate_is_one(self):
        s = LineSampler()
        assert s.rate == 1

    def test_default_offset_is_zero(self):
        s = LineSampler()
        assert s.offset == 0

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError, match="rate must be >= 1"):
            LineSampler(rate=0)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError, match="rate must be >= 1"):
            LineSampler(rate=-5)

    def test_offset_out_of_range_raises(self):
        with pytest.raises(ValueError, match="offset must be in"):
            LineSampler(rate=3, offset=3)

    def test_negative_offset_raises(self):
        with pytest.raises(ValueError, match="offset must be in"):
            LineSampler(rate=3, offset=-1)


# ---------------------------------------------------------------------------
# is_noop
# ---------------------------------------------------------------------------

class TestIsNoop:
    def test_rate_one_is_noop(self):
        assert LineSampler(rate=1).is_noop() is True

    def test_rate_two_is_not_noop(self):
        assert LineSampler(rate=2).is_noop() is False


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------

class TestApply:
    def test_rate_one_keeps_all_lines(self):
        result = list(LineSampler(rate=1).apply(LINES))
        assert result == LINES

    def test_rate_two_keeps_even_indexed_lines(self):
        result = list(LineSampler(rate=2).apply(LINES))
        assert result == LINES[::2]

    def test_rate_two_offset_one_keeps_odd_indexed_lines(self):
        result = list(LineSampler(rate=2, offset=1).apply(LINES))
        assert result == LINES[1::2]

    def test_rate_ten_keeps_first_line(self):
        result = list(LineSampler(rate=10).apply(LINES))
        assert result == [LINES[0]]

    def test_rate_larger_than_input_keeps_one_line(self):
        result = list(LineSampler(rate=100).apply(LINES))
        assert result == [LINES[0]]

    def test_empty_input_returns_empty(self):
        result = list(LineSampler(rate=3).apply([]))
        assert result == []

    def test_rate_three_offset_two(self):
        result = list(LineSampler(rate=3, offset=2).apply(LINES))
        # indices 2, 5, 8
        assert result == [LINES[2], LINES[5], LINES[8]]
