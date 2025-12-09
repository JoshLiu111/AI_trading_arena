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

You can fetch data from Polygon.io API and save it locally:

```python
# scripts/fetch_and_save_data.py (create this)
import requests
import json
from datetime import date, timedelta
import os

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "WMT"]
end_date = date.today()
start_date = end_date - timedelta(days=14)

data = {}
for ticker in tickers:
    endpoint = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start_date.isoformat()}/{end_date.isoformat()}"
    response = requests.get(endpoint, params={"apikey": POLYGON_API_KEY})
    response.raise_for_status()
    result = response.json()
    
    if "results" in result:
        data[ticker] = []
        for item in result["results"]:
            timestamp_ms = item.get("t", 0)
            price_date = datetime.fromtimestamp(timestamp_ms / 1000).date()
            data[ticker].append({
                "date": price_date.isoformat(),
                "open": float(item.get("o", 0)),
                "high": float(item.get("h", 0)),
                "low": float(item.get("l", 0)),
                "close": float(item.get("c", 0)),
                "volume": int(item.get("v", 0)),
                "adj_close": float(item.get("c", 0))
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

### Option 2: Download from Polygon.io Manually

1. Use Polygon.io API or dashboard to download historical data
2. Convert to the required format
3. Save as `stock_data.csv` or `stock_data.json` in this directory

## Automatic Import

When you start a competition for the first time (when database is empty), the system will:

1. Check if `data/stock_data.csv` or `data/stock_data.json` exists
2. If found, import the data automatically
3. If not found, fetch data from Polygon.io API

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

