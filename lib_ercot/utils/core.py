from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

from lib_ercot.shared.csv_writer import CSVWriter
from lib_ercot.shared.datetime_fmt import DateTimeFormatter
from lib_ercot.shared.lmp_processor import LMPDataProcessor
from lib_ercot.shared.retry_policy import RetryPolicy
from lib_ercot.shared.string_utils import StringUtil
from lib_ercot.shared.validators import Validator

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.ercot.com/content/cdr/html/hb_lz.html"
DEFAULT_COLUMNS = ("LMP", "SPP")


@dataclass(frozen=True)
class MonitorConfig:
    url: str = DEFAULT_URL
    csv_filename: str = "ercot_lmp_filtered_log.csv"
    columns: Tuple[str, ...] = DEFAULT_COLUMNS
    poll_sleep_seconds: int = 5
    expected_update_interval_seconds: int = 290  # ~4m50s for 5-min updates


def build_headers(columns: Iterable[str]) -> list[str]:
    """Build CSV headers for LMP data.

    Args:
        columns: Column names to include (e.g., 'LMP', 'SPP').

    Returns:
        List of header strings with location prefixes.
    """
    cols = list(columns)
    headers: list[str] = ["Date", "Time"]
    headers.extend([f"HB_HOUSTON_{c}" for c in cols])
    headers.extend([f"LZ_HOUSTON_{c}" for c in cols])
    return headers


def fetch_lmp_table(url: str) -> tuple[pd.DataFrame, datetime]:
    """Fetch LMP table from ERCOT website.

    Args:
        url: URL to ERCOT LMP page.

    Returns:
        Tuple of (filtered dataframe, update datetime).

    Raises:
        RuntimeError: If table not found or parsing fails.
    """
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    Validator.not_none(table, "No table found on page")

    df = pd.read_html(io.StringIO(str(table)))[0]

    # Filter to required settlement points and columns
    df_filtered = LMPDataProcessor.filter_locations(df)
    df_filtered = LMPDataProcessor.select_columns(df_filtered, [0, 1, 3])

    # Extract "Last Updated" timestamp
    update_text = soup.get_text()
    update_line = StringUtil.extract_first_line_containing(update_text, "Last Updated")
    update_time = DateTimeFormatter.parse_ercot_timestamp(update_line or DateTimeFormatter.format_iso_datetime(datetime.now()))

    return df_filtered, update_time


def run_monitor(config: MonitorConfig) -> None:
    """Monitor ERCOT LMP page and append updates to CSV.

    Polls the ERCOT page at intervals. When new data is detected, appends
    a row to the CSV file. Uses exponential backoff on errors.

    Args:
        config: Monitor configuration.
    """
    headers = build_headers(config.columns)
    csv_writer = CSVWriter(config.csv_filename)
    csv_writer.ensure_headers(headers)

    last_update: datetime | None = None
    sleep_time = config.poll_sleep_seconds

    # Retry policy: 3 attempts with 1s backoff, exponential multiplier 2.0
    retry_policy = RetryPolicy(max_attempts=3, backoff_seconds=1, backoff_multiplier=2.0)

    logger.info("Monitoring ERCOT LMP page. Press Ctrl+C to stop.")

    for i in range(5):  # Remove for production: try: while True:

        def fetch_and_process():
            df, update_time = fetch_lmp_table(config.url)
            return df, update_time

        def on_error(exc: Exception, attempt: int):
            logger.error(f"Error fetching LMP table (attempt {attempt + 1}): {exc}")

        try:
            df, update_time = retry_policy.execute(
                fetch_and_process,
                on_error=on_error,
            )

            if last_update is None or update_time != last_update:
                row = LMPDataProcessor.build_csv_row(df, update_time)
                csv_writer.append_row(row)
                last_update = update_time
                logger.info(f"New data detected at {update_time}, recorded 1 row.")
                sleep_time = config.expected_update_interval_seconds
            else:
                logger.debug(f"No change detected at {datetime.now().isoformat()}.")
                sleep_time = config.poll_sleep_seconds

        except Exception as e:
            logger.exception(f"Failed after retries: {e}")
            sleep_time = config.poll_sleep_seconds

        import time

        time.sleep(sleep_time)
