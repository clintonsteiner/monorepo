from datetime import datetime

import pandas as pd

from lib_ercot.shared.datetime_fmt import DateTimeFormatter
from lib_ercot.shared.lmp_processor import LMPDataProcessor


def test_parse_ercot_timestamp():
    """Test parsing ERCOT timestamp format."""
    dt = DateTimeFormatter.parse_ercot_timestamp("Last Updated:  Oct 21, 2025 23:15:10")
    assert dt == datetime(2025, 10, 21, 23, 15, 10)


def test_build_csv_row_hb_lz():
    """Test building CSV row from LMP dataframe."""
    df = pd.DataFrame(
        {
            0: ["Settlement Point", "HB_HOUSTON", "LZ_HOUSTON"],
            1: [50.0, 1.23, 7.89],
            3: [2.5, 4.56, 0.12],
        }
    )
    ts = datetime(2025, 10, 21, 23, 15, 10)
    row = LMPDataProcessor.build_csv_row(df, ts)

    # Check date and time
    assert row[0] == "2025-10-21"
    assert row[1] == "23:15:10"

    # Check location values
    assert row[2:4] == [1.23, 4.56]  # HB_HOUSTON
    assert row[4:6] == [7.89, 0.12]  # LZ_HOUSTON
