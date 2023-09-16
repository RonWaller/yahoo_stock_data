"""Get historical data from Yahoo Finance by month store as csv"""
import datetime
import time
from pathlib import Path

import pandas as pd

symbol = "AAPL"
period1 = int(time.mktime(datetime.datetime(2023, 2, 28, 23, 59).timetuple()))
period2 = int(time.mktime(datetime.datetime(2023, 3, 31, 23, 59).timetuple()))
interval = "1d"  # "1w" "1m"
path = Path(f"stock_data/{symbol}", "historical_data_by_month.csv")


url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true"

df = pd.read_csv(url)
print(df)

if path.is_file():
    # Append DataFrame to existing CSV File
    df.to_csv(
        f"stock_data/{symbol}/historical_data_by_month.csv",
        header=False,
        index=False,
        mode="a",
    )
else:
    df.to_csv(
        f"stock_data/{symbol}/historical_data_by_month.csv",
        index=False,
    )
