# Stock Historical Data Files

This directory contains local stock historical data files that can be imported into the database on first startup.

## File Formats

### CSV Format (`stock_data.csv`)

```csv
ticker,date,open,high,low,close,volume,adj_close
AAPL,2024-12-01,150.0,155.0,149.0,152.0,1000000,152.0
AAPL,2024-12-02,152.0,153.0,151.0,152.5,950000,152.5
MSFT,2024-12-01,380.0,385.0,379.0,382.0,2000000,382.0
MSFT,2024-12-02,382.0,383.0,381.0,382.5,1900000,382.5
```

**Required columns:**
- `ticker`: Stock ticker symbol (e.g., AAPL, MSFT)
- `date`: Date in YYYY-MM-DD format
- `open`, `high`, `low`, `close`: Price values (floats)
- `volume`: Trading volume (integer, optional)
- `adj_close`: Adjusted close price (float, optional)

### JSON Format (`stock_data.json`)

```json
{
  "AAPL": [
    {
      "date": "2024-12-01",
      "open": 150.0,
      "high": 155.0,
      "low": 149.0,
      "close": 152.0,
      "volume": 1000000,
      "adj_close": 152.0
    },
    {
      "date": "2024-12-02",
      "open": 152.0,
      "high": 153.0,
      "low": 151.0,
      "close": 152.5,
      "volume": 950000,
      "adj_close": 152.5
    }
  ],
  "MSFT": [
    {
      "date": "2024-12-01",
      "open": 380.0,
      "high": 385.0,
      "low": 379.0,
      "close": 382.0,
      "volume": 2000000,
      "adj_close": 382.0
    }
  ]
}
```

## How to Generate Data Files

### Option 1: Use the Import Script

You can fetch data locally and save it:

```python
# scripts/fetch_and_save_data.py (create this)
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import json

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "WMT"]
end_date = date.today()
start_date = end_date - timedelta(days=14)

data = {}
for ticker in tickers:
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date.isoformat(), end=end_date.isoformat())
    
    data[ticker] = []
    for index, row in df.iterrows():
        data[ticker].append({
            "date": index.date().isoformat(),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]),
            "adj_close": float(row["Close"])
        })

# Save as JSON
with open("data/stock_data.json", "w") as f:
    json.dump(data, f, indent=2)

# Or save as CSV
import csv
with open("data/stock_data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["ticker", "date", "open", "high", "low", "close", "volume", "adj_close"])
    writer.writeheader()
    for ticker, prices in data.items():
        for price in prices:
            writer.writerow({
                "ticker": ticker,
                "date": price["date"],
                "open": price["open"],
                "high": price["high"],
                "low": price["low"],
                "close": price["close"],
                "volume": price["volume"],
                "adj_close": price["adj_close"]
            })
```

### Option 2: Download from Yahoo Finance Manually

1. Go to Yahoo Finance
2. Download historical data for each stock
3. Convert to the required format
4. Save as `stock_data.csv` or `stock_data.json` in this directory

## Automatic Import

When you start a competition for the first time (when database is empty), the system will:

1. Check if `data/stock_data.csv` or `data/stock_data.json` exists
2. If found, import the data automatically
3. If not found, fetch data from Yahoo Finance API (may be slow due to rate limits)

## Manual Import

You can also manually import data using the script:

```bash
# Import from CSV
python scripts/import_historical_data.py --file data/stock_data.csv

# Import from JSON
python scripts/import_historical_data.py --file data/stock_data.json --format json

# Import from directory (all CSV/JSON files)
python scripts/import_historical_data.py --dir data/

# Import specific tickers only
python scripts/import_historical_data.py --file data/stock_data.csv --tickers AAPL MSFT GOOGL
```

## Notes

- Data files should contain at least 7 days of historical data (as configured in `HISTORY_DAYS`)
- Dates should be in YYYY-MM-DD format
- The system will only import data for tickers in the `STOCK_POOL` configuration
- If data already exists in database, the system will skip local file import and fetch fresh data from API

