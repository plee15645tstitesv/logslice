# logslice

Fast log file slicer that extracts time-range segments from large rotated log archives.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourusername/logslice.git
cd logslice && pip install .
```

---

## Usage

```bash
# Extract logs between two timestamps
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:30:00" /var/log/app/*.log

# Output to a file
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:30:00" /var/log/app/*.log -o output.log

# Use a custom timestamp format
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:30:00" \
         --format "%Y-%m-%dT%H:%M:%S" /var/log/app/*.log.gz
```

Python API:

```python
from logslice import slice_logs

results = slice_logs(
    paths=["/var/log/app/app.log", "/var/log/app/app.log.1"],
    start="2024-01-15 08:00:00",
    end="2024-01-15 09:30:00",
)

for line in results:
    print(line)
```

---

## Features

- Handles rotated and gzip-compressed log files (`.log`, `.log.gz`)
- Binary search for fast range detection in large files
- Supports custom timestamp formats
- Streams output to avoid high memory usage

---

## License

This project is licensed under the [MIT License](LICENSE).