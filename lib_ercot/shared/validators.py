"""Validation utilities for common operations."""

from __future__ import annotations

from typing import TypeVar

import pandas as pd

T = TypeVar("T")


class ValidationError(ValueError):
    """Custom validation error."""

    pass


class Validator:
    """Central validation utility for common checks."""

    @staticmethod
    def not_none(value: T, message: str = "Value cannot be None") -> T:
        """Validate that value is not None.

        Args:
            value: The value to check.
            message: Error message if validation fails.

        Returns:
            The value if valid.

        Raises:
            ValidationError: If value is None.
        """
        if value is None:
            raise ValidationError(message)
        return value

    @staticmethod
    def not_empty_str(value: str, message: str = "String cannot be empty or whitespace") -> str:
        """Validate that string is not empty or whitespace.

        Args:
            value: The string to check.
            message: Error message if validation fails.

        Returns:
            The value if valid.

        Raises:
            ValidationError: If string is empty or whitespace.
        """
        if not value or not value.strip():
            raise ValidationError(message)
        return value

    @staticmethod
    def not_empty_dataframe(df: pd.DataFrame, message: str = "DataFrame is empty") -> pd.DataFrame:
        """Validate that dataframe is not empty.

        Args:
            df: The dataframe to check.
            message: Error message if validation fails.

        Returns:
            The dataframe if valid.

        Raises:
            ValidationError: If dataframe is empty.
        """
        if df.empty:
            raise ValidationError(message)
        return df

    @staticmethod
    def dataframe_contains_columns(df: pd.DataFrame, columns: list[str], message: str = "") -> pd.DataFrame:
        """Validate that dataframe contains required columns.

        Args:
            df: The dataframe to check.
            columns: List of required column names.
            message: Error message if validation fails (auto-generated if empty).

        Returns:
            The dataframe if valid.

        Raises:
            ValidationError: If any required columns are missing.
        """
        missing = [col for col in columns if col not in df.columns]
        if missing:
            if not message:
                message = f"DataFrame missing required columns: {missing}"
            raise ValidationError(message)
        return df
