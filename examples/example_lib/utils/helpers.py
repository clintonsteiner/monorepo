"""Helper utilities for example_lib."""

from __future__ import annotations


def validate_input(value: str) -> bool:
    """Validate input value.

    Args:
        value: The value to validate.

    Returns:
        True if valid, False otherwise.

    Example:
        >>> validate_input("test")
        True
        >>> validate_input("")
        False
    """
    return bool(value and value.strip())


def format_output(data: dict[str, str]) -> str:
    """Format dictionary data as a string.

    Args:
        data: Dictionary to format.

    Returns:
        Formatted string representation.

    Example:
        >>> format_output({"key": "value"})
        'key: value'
    """
    return "\n".join(f"{k}: {v}" for k, v in data.items())
