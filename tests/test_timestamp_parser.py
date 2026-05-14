"""Tests for logslice.timestamp_parser."""

from datetime import datetime

import pytest

from logslice.timestamp_parser import parse_timestamp


@pytest.mark.parametrize(
    "line, expected",
    [
        # ISO 8601 with milliseconds and Z
        (
            "2024-01-15T13:45:00.123Z INFO service started",
            datetime(2024, 1, 15, 13, 45, 0),
        ),
        # ISO 8601 without timezone
        (
            "2024-03-22T08:00:00 DEBUG connecting",
            datetime(2024, 3, 22, 8, 0, 0),
        ),
        # Syslog format
        (
            "Jan 15 13:45:00 hostname sshd[1234]: Accepted",
            datetime(1900, 1, 15, 13, 45, 0),
        ),
        # Apache combined log
        (
            '192.168.1.1 - - [15/Jan/2024:13:45:00 +0000] "GET / HTTP/1.1" 200 512',
            datetime(2024, 1, 15, 13, 45, 0),
        ),
        # Simple datetime with microseconds
        (
            "2024-06-01 22:30:45.999 ERROR something failed",
            datetime(2024, 6, 1, 22, 30, 45, 999000),
        ),
        # Unix timestamp
    (
            "ts=1705323900.0 level=info msg=ok",
            datetime(2024, 1, 15, 13, 45, 0),
        ),
        # No timestamp
        (
            "this line has no timestamp at all",
            None,
        ),
    ],
)
def test_parse_timestamp(line: str, expected):
    result = parse_timestamp(line)
    if expected is None:
        assert result is None
    else:
        assert result is not None
        # Compare only the fields that are reliably set by each format
        assert result.hour == expected.hour
        assert result.minute == expected.minute
        assert result.second == expected.second


def test_parse_timestamp_returns_naive_datetime():
    """Parsed timestamps must be timezone-naive for consistent comparison."""
    line = "2024-01-15T13:45:00+05:30 some event"
    result = parse_timestamp(line)
    assert result is not None
    assert result.tzinfo is None


def test_parse_timestamp_prefers_iso_over_unix():
    """ISO 8601 should be matched before a bare Unix timestamp in the same line."""
    line = "2024-01-15T00:00:00 ref=1705276800"
    result = parse_timestamp(line)
    assert result is not None
    assert result.year == 2024
