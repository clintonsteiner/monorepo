"""LMP data processing utilities."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from lib_ercot.shared.datetime_fmt import DateTimeFormatter
from lib_ercot.shared.validators import ValidationError, Validator


class LMPDataProcessor:
    """Process and extract LMP data from dataframes."""

    # Locations we require in the data
    REQUIRED_LOCATIONS = ("HB_HOUSTON", "LZ_HOUSTON")
    # Settlement points that must be present
    REQUIRED_SETTLEMENT_POINTS = ("Settlement Point", "HB_HOUSTON", "LZ_HOUSTON")

    @staticmethod
    def filter_locations(df: pd.DataFrame) -> pd.DataFrame:
        """Filter dataframe to required settlement points.

        Args:
            df: Raw dataframe with settlement point data.

        Returns:
            Filtered dataframe containing only required settlement points.

        Raises:
            ValidationError: If dataframe is empty.
        """
        filtered = df[df[0].isin(LMPDataProcessor.REQUIRED_SETTLEMENT_POINTS)]
        return Validator.not_empty_dataframe(filtered, "No required settlement points found in data")

    @staticmethod
    def select_columns(df: pd.DataFrame, columns: list[int]) -> pd.DataFrame:
        """Select specific columns from dataframe.

        Args:
            df: Dataframe to filter.
            columns: List of column indices to keep.

        Returns:
            Dataframe with only selected columns.

        Raises:
            ValidationError: If result is empty.
        """
        filtered = df[columns]
        return Validator.not_empty_dataframe(filtered, "No columns selected")

    @staticmethod
    def extract_location_row(df: pd.DataFrame, location: str) -> list:
        """Extract values from a specific location row.

        Args:
            df: Dataframe containing location data (with location in column 0).
            location: The location name to extract.

        Returns:
            List of values from the row (excluding location name in column 0).

        Raises:
            ValidationError: If location is not found.
        """
        filtered = df[df[0] == location]
        if filtered.empty:
            raise ValidationError(f"Location '{location}' not found in data")

        row = filtered.iloc[0]
        return row.drop(0).tolist()

    @staticmethod
    def extract_all_locations(df: pd.DataFrame) -> dict[str, list]:
        """Extract values for all required locations.

        Args:
            df: Dataframe containing location data.

        Returns:
            Dictionary mapping location names to their row values.

        Raises:
            ValidationError: If any required location is missing.
        """
        result = {}
        for location in LMPDataProcessor.REQUIRED_LOCATIONS:
            result[location] = LMPDataProcessor.extract_location_row(df, location)
        return result

    @staticmethod
    def build_csv_row(df: pd.DataFrame, update_time: datetime) -> list[object]:
        """Build a CSV row from LMP dataframe and update time.

        Produces row format: [date, time, ...HB_HOUSTON_values, ...LZ_HOUSTON_values]

        Args:
            df: Filtered LMP dataframe with location data.
            update_time: Timestamp of the data.

        Returns:
            List of values ready to append to CSV.

        Raises:
            ValidationError: If required locations are missing.
        """
        date_str, time_str = DateTimeFormatter.format_iso_date_time(update_time)
        row: list[object] = [date_str, time_str]

        # Extract values for each location and append in consistent order
        for location in LMPDataProcessor.REQUIRED_LOCATIONS:
            row.extend(LMPDataProcessor.extract_location_row(df, location))

        return row
