from datetime import datetime

import pandas as pd

from lib_ercot.utils.core import extract_row, parse_update_time


def test_parse_update_time():
    dt = parse_update_time(["Last Updated:  Oct 21, 2025 23:15:10"])
    assert dt == datetime(2025, 10, 21, 23, 15, 10)


def test_extract_row_hb_lz():
    df = pd.DataFrame(
        [
            ["Settlement Point", "LMP", "X", "SPP"],
            ["HB_HOUSTON", 1.23, "X", 4.56],
            ["LZ_HOUSTON", 7.89, "X", 0.12],
        ]
    )
    ts = datetime(2025, 10, 21, 23, 15, 10)
    row = extract_row(df[[0, 1, 3]], ts)
    assert row[0] == "2025-10-21"
    assert row[1] == "23:15:10"
    assert row[2:] == [1.23, 4.56, 7.89, 0.12]
