"""logslice — Fast log file slicer for time-range extraction from rotated archives."""

from logslice.log_archive import LogArchive
from logslice.slicer import slice_archive, slice_path

__version__ = "0.1.0"

__all__ = [
    "LogArchive",
    "slice_archive",
    "slice_path",
    "__version__",
]
