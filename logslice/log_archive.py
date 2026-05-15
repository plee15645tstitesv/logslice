"""High-level interface representing a (possibly rotated) log archive."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, List

from logslice.file_finder import find_rotated_files


@dataclass
class LogArchive:
    """Represents an ordered collection of rotated log files.

    Attributes:
        base_path: Path to the *current* (active) log file.
        files: Ordered list of paths, oldest first.
    """

    base_path: Path
    files: List[Path] = field(default_factory=list)

    @classmethod
    def from_path(cls, base_path: str) -> "LogArchive":
        """Discover all rotated files for *base_path* and return a LogArchive.

        Args:
            base_path: Path to the active log file.

        Returns:
            A :class:`LogArchive` instance with *files* populated, oldest first.
        """
        resolved = Path(base_path).resolve()
        files = find_rotated_files(str(resolved))
        return cls(base_path=resolved, files=files)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.files)

    def __iter__(self) -> Iterator[Path]:
        return iter(self.files)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"LogArchive(base_path={self.base_path!r}, "
            f"file_count={len(self.files)})"
        )

    @property
    def total_size_bytes(self) -> int:
        """Sum of sizes of all files in the archive."""
        return sum(f.stat().st_size for f in self.files if f.exists())

    def iter_lines(self) -> Iterator[str]:
        """Yield every line from every file, oldest file first.

        Compressed files (*.gz) are transparently decompressed.
        """
        import gzip

        for path in self.files:
            opener = gzip.open if path.suffix == ".gz" else open
            with opener(path, "rt", errors="replace") as fh:  # type: ignore[call-overload]
                yield from fh

    def grep(self, pattern: str) -> Iterator[str]:
        """Yield lines matching *pattern* across all files, oldest first.

        The match is a simple case-sensitive substring check.  For more
        advanced filtering callers should use :meth:`iter_lines` directly
        with their own predicate.

        Args:
            pattern: Substring to search for in each line.

        Yields:
            Lines that contain *pattern* (newline included if present).
        """
        for line in self.iter_lines():
            if pattern in line:
                yield line
