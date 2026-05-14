"""Timestamp detection and parsing for common log formats."""

import re
from datetime import datetime
from typing import Optional

# Common log timestamp patterns ordered by specificity
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2024-01-15T13:45:00.123Z or 2024-01-15T13:45:00+00:00
    (
        r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)",
        ["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"],
    ),
    # Common syslog: Jan 15 13:45:00
    (
        r"([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})",
        ["%b %d %H:%M:%S", "%b  %d %H:%M:%S"],
    ),
    # Apache/Nginx: 15/Jan/2024:13:45:00 +0000
    (
        r"(\d{2}/[A-Z][a-z]{2}/\d{4}:\d{2}:\d{2}:\d{2}\s[+-]\d{4})",
        ["%d/%b/%Y:%H:%M:%S %z"],
    ),
    # Simple datetime: 2024-01-15 13:45:00
    (
        r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}(?:\.\d+)?)",
        ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"],
    ),
    # Unix timestamp (10 or 13 digits)
    (
        r"\b(\d{10}(?:\.\d+)?)\b",
        ["unix"],
    ),
]


def parse_timestamp(line: str) -> Optional[datetime]:
    """Extract and parse the first recognisable timestamp from a log line.

    Returns a timezone-naive UTC datetime, or None if no timestamp is found.
    """
    for pattern, formats in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if not match:
            continue
        raw = match.group(1)
        for fmt in formats:
            if fmt == "unix":
                try:
                    return datetime.utcfromtimestamp(float(raw))
                except (ValueError, OSError):
                    continue
            try:
                dt = datetime.strptime(raw.strip(), fmt)
                # Normalise to naive UTC
                if dt.tzinfo is not None:
                    dt = dt.utctimetuple()
                    dt = datetime(*dt[:6])
                return dt
            except ValueError:
                continue
    return None
