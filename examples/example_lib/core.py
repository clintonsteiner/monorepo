"""Core functionality for example_lib."""

from __future__ import annotations

from typing import Any


class ExampleClass:
    """Example class demonstrating library structure.

    Attributes:
        name: The name attribute.
        value: The value attribute.
    """

    def __init__(self, name: str, value: int = 0) -> None:
        """Initialize ExampleClass.

        Args:
            name: Name to assign.
            value: Initial value (default: 0).
        """
        self.name = name
        self.value = value

    def increment(self, amount: int = 1) -> int:
        """Increment the value.

        Args:
            amount: Amount to increment by (default: 1).

        Returns:
            The new value.
        """
        self.value += amount
        return self.value

    def __repr__(self) -> str:
        """Return string representation."""
        return f"ExampleClass(name={self.name!r}, value={self.value})"


def process_data(data: list[Any]) -> list[Any]:
    """Process a list of data.

    Args:
        data: List of items to process.

    Returns:
        Processed list.

    Example:
        >>> process_data([1, 2, 3])
        [2, 4, 6]
    """
    return [item * 2 for item in data]
