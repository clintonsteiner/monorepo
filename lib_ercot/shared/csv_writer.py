"""CSV file handling utilities."""

from __future__ import annotations

import csv
from pathlib import Path


class CSVWriter:
    """Manages CSV file operations with consistent error handling."""

    def __init__(self, filename: str):
        """Initialize CSV writer.

        Args:
            filename: Path to CSV file.
        """
        self.filename = Path(filename)

    def ensure_headers(self, headers: list[str]) -> None:
        """Ensure headers exist in CSV file, creating file if needed.

        If file already exists, this is a no-op. Otherwise, creates the file
        with the provided headers.

        Args:
            headers: List of header column names.
        """
        if self.filename.exists():
            return

        self.filename.parent.mkdir(parents=True, exist_ok=True)
        with self.filename.open("w", newline="") as f:
            csv.writer(f).writerow(headers)

    def append_row(self, row: list[object]) -> None:
        """Append a row to the CSV file.

        Args:
            row: List of values to append as a row.

        Raises:
            OSError: If file operation fails.
        """
        with self.filename.open("a", newline="") as f:
            csv.writer(f).writerow(row)

    def read_rows(self) -> list[list[str]]:
        """Read all rows from CSV file.

        Returns:
            List of rows (each row is a list of strings).

        Raises:
            OSError: If file doesn't exist or can't be read.
        """
        if not self.filename.exists():
            return []

        rows = []
        with self.filename.open("r", newline="") as f:
            rows = list(csv.reader(f))
        return rows

    def clear(self) -> None:
        """Delete the CSV file if it exists."""
        if self.filename.exists():
            self.filename.unlink()
