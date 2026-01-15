"""DateTime formatting and parsing utilities."""

from __future__ import annotations

from datetime import datetime


class DateTimeFormatter:
    """Centralized DateTime formatting with consistent format strings."""

    # Format used by ERCOT website for update timestamps
    ERCOT_TIMESTAMP_FORMAT = "%b %d, %Y %H:%M:%S"
    # ISO date format (YYYY-MM-DD)
    ISO_DATE_FORMAT = "%Y-%m-%d"
    # ISO time format (HH:MM:SS)
    ISO_TIME_FORMAT = "%H:%M:%S"

    @staticmethod
    def parse_ercot_timestamp(text: str) -> datetime:
        """Parse ERCOT timestamp string.

        Expected format: 'Last Updated:  Oct 21, 2025 23:15:10'

        Args:
            text: The timestamp text, may include 'Last Updated:' prefix.

        Returns:
            Parsed datetime object.

        Raises:
            ValueError: If text cannot be parsed.
        """
        cleaned = text.replace("Last Updated:", "").strip()
        return datetime.strptime(cleaned, DateTimeFormatter.ERCOT_TIMESTAMP_FORMAT)

    @staticmethod
    def format_iso_date_time(dt: datetime) -> tuple[str, str]:
        """Format datetime as separate ISO date and time strings.

        Args:
            dt: The datetime to format.

        Returns:
            Tuple of (ISO_date_string, ISO_time_string).
        """
        date_str = dt.strftime(DateTimeFormatter.ISO_DATE_FORMAT)
        time_str = dt.strftime(DateTimeFormatter.ISO_TIME_FORMAT)
        return date_str, time_str

    @staticmethod
    def format_iso_datetime(dt: datetime) -> str:
        """Format datetime as combined ISO 8601 string.

        Args:
            dt: The datetime to format.

        Returns:
            Combined ISO datetime string (YYYY-MM-DDTHH:MM:SS).
        """
        return dt.strftime(f"{DateTimeFormatter.ISO_DATE_FORMAT}T{DateTimeFormatter.ISO_TIME_FORMAT}")
