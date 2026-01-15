"""Output type conversion utilities for tests."""

from __future__ import annotations


class OutputConverter:
    """Convert between bytes and string representations."""

    @staticmethod
    def to_bytes(output: bytes | str) -> bytes:
        """Convert output to bytes.

        Args:
            output: Output as bytes or string.

        Returns:
            Output as bytes.
        """
        return output if isinstance(output, bytes) else output.encode()

    @staticmethod
    def to_str(output: bytes | str) -> str:
        """Convert output to string.

        Args:
            output: Output as bytes or string.

        Returns:
            Output as string.
        """
        return output.decode() if isinstance(output, bytes) else output

    @staticmethod
    def contains(output: bytes | str, needle: bytes | str) -> bool:
        """Check if output contains needle.

        Args:
            output: The output to search.
            needle: The text to search for.

        Returns:
            True if needle found in output.
        """
        output_bytes = OutputConverter.to_bytes(output)
        needle_bytes = OutputConverter.to_bytes(needle)
        return needle_bytes in output_bytes
