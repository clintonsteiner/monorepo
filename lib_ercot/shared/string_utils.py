"""String utilities for common text operations."""

from __future__ import annotations


class StringUtil:
    """Utilities for string operations."""

    @staticmethod
    def is_empty_or_whitespace(value: str) -> bool:
        """Check if string is empty or contains only whitespace.

        Args:
            value: The string to check.

        Returns:
            True if empty or whitespace only, False otherwise.
        """
        return not value or not value.strip()

    @staticmethod
    def clean_string(value: str, prefix: str = "") -> str:
        """Remove optional prefix and strip whitespace.

        Args:
            value: The string to clean.
            prefix: Optional prefix to remove.

        Returns:
            Cleaned string.
        """
        result = value
        if prefix and result.startswith(prefix):
            result = result[len(prefix) :]
        return result.strip()

    @staticmethod
    def filter_lines_containing(text: str, keyword: str) -> list[str]:
        """Get all lines from text that contain a keyword.

        Args:
            text: The full text to search.
            keyword: The keyword to search for.

        Returns:
            List of lines containing the keyword.
        """
        return [line for line in text.splitlines() if keyword in line]

    @staticmethod
    def extract_first_line_containing(text: str, keyword: str) -> str | None:
        """Get first line containing keyword.

        Args:
            text: The full text to search.
            keyword: The keyword to search for.

        Returns:
            First matching line, or None if not found.
        """
        lines = StringUtil.filter_lines_containing(text, keyword)
        return lines[0] if lines else None
