from __future__ import annotations

import argparse

from lib_ercot.utils.core import MonitorConfig, run_monitor


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Monitor ERCOT HB/LZ Houston LMP page and append to CSV.")
    p.add_argument("--url", default=MonitorConfig.url)
    p.add_argument("--csv", default=MonitorConfig.csv_filename)
    p.add_argument("--poll-sleep", type=int, default=MonitorConfig.poll_sleep_seconds)
    p.add_argument("--expected-interval", type=int, default=MonitorConfig.expected_update_interval_seconds)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = MonitorConfig(
        url=args.url,
        csv_filename=args.csv,
        poll_sleep_seconds=args.poll_sleep,
        expected_update_interval_seconds=args.expected_interval,
    )
    run_monitor(cfg)


if __name__ == "__main__":
    main()

