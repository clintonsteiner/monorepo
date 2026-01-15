from __future__ import annotations

import csv
import io
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup


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
    cols = list(columns)
    headers: list[str] = ["Date", "Time"]
    headers.extend([f"HB_HOUSTON_{c}" for c in cols])
    headers.extend([f"LZ_HOUSTON_{c}" for c in cols])
    return headers


def ensure_csv_headers(csv_filename: str, headers: list[str]) -> None:
    path = Path(csv_filename)
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        csv.writer(f).writerow(headers)


def parse_update_time(update_lines: list[str]) -> datetime:
    # Example: 'Last Updated:  Oct 21, 2025 23:15:10'
    if not update_lines:
        return datetime.now()
    ts = update_lines[0].replace("Last Updated:", "").strip()
    return datetime.strptime(ts, "%b %d, %Y %H:%M:%S")


def fetch_lmp_table(url: str) -> tuple[pd.DataFrame, datetime]:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("No table found on page")

    df = pd.read_html(io.StringIO(str(table)))[0]

    # Keep rows we care about
    df_filtered = df[df[0].isin(["Settlement Point", "HB_HOUSTON", "LZ_HOUSTON"])]

    # Keep only required columns: Settlement Point + (LMP/SPP columns in current page layout)
    # Original script used [0,1,3] which corresponds to: name, LMP, SPP on that page today.
    df_filtered = df_filtered[[0, 1, 3]]

    # Extract "Last Updated"
    update_text = soup.get_text()
    update_lines = [line for line in update_text.splitlines() if "Last Updated" in line]
    update_time = parse_update_time(update_lines)

    return df_filtered, update_time


def extract_row(df_filtered: pd.DataFrame, update_time: datetime) -> list[object]:
    date_str = update_time.strftime("%Y-%m-%d")
    time_str = update_time.strftime("%H:%M:%S")

    hb = df_filtered[df_filtered[0] == "HB_HOUSTON"]
    lz = df_filtered[df_filtered[0] == "LZ_HOUSTON"]
    if hb.empty or lz.empty:
        raise RuntimeError("Expected HB_HOUSTON and LZ_HOUSTON rows were not found")

    hb_row = hb.iloc[0]
    lz_row = lz.iloc[0]

    row: list[object] = [date_str, time_str]
    row.extend(hb_row.drop(0).tolist())
    row.extend(lz_row.drop(0).tolist())
    return row


def append_csv_row(csv_filename: str, row: list[object]) -> None:
    with open(csv_filename, "a", newline="") as f:
        csv.writer(f).writerow(row)


def run_monitor(config: MonitorConfig) -> None:
    headers = build_headers(config.columns)
    ensure_csv_headers(config.csv_filename, headers)

    last_update: datetime | None = None
    sleep_time = config.poll_sleep_seconds

    print("Monitoring ERCOT LMP page. Press Ctrl+C to stop.")
    while True:
        try:
            df, update_time = fetch_lmp_table(config.url)
            if last_update is None or update_time != last_update:
                row = extract_row(df, update_time)
                append_csv_row(config.csv_filename, row)
                last_update = update_time
                print(f"New data detected at {update_time}, recorded 1 row.")
                sleep_time = config.expected_update_interval_seconds
            else:
                print(f"No change detected at {datetime.now().isoformat()}.")
                sleep_time = config.poll_sleep_seconds
        except Exception as e:
            print(f"Error fetching or processing data: {e}")
            sleep_time = config.poll_sleep_seconds

        time.sleep(sleep_time)

