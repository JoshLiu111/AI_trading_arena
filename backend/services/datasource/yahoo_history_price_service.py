# backend/services/datasource/yahoo_history_price_service.py

"""
Yahoo History Price Service - Historical price data from Yahoo Finance
Uses yfinance to fetch historical stock price data
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from datetime import date, timedelta


class YahooService:
    """Unified Yahoo Finance service"""

    def get_historical_data(
        self, 
        ticker: str, 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None,
        retries: int = 3
    ) -> List[Dict]:
        """Get historical price data for a single ticker with retry logic"""
        import time
        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                
                if start and end:
                    df = stock.history(start=start, end=end)
                else:
                    df = stock.history(period=period)
                
                if df.empty:
                    return []
                
                result = []
                for index, row in df.iterrows():
                    result.append({
                        "date": index.date() if isinstance(index, pd.Timestamp) else index,
                        "open": float(row["Open"]) if pd.notna(row["Open"]) else None,
                        "high": float(row["High"]) if pd.notna(row["High"]) else None,
                        "low": float(row["Low"]) if pd.notna(row["Low"]) else None,
                        "close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                        "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else None,
                        "adj_close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                    })
                
                return result
                
            except Exception as e:
                from core.logging import get_logger
                import json
                from requests.exceptions import HTTPError
                logger = get_logger(__name__)
                error_str = str(e).lower()
                is_rate_limit = "429" in error_str or "too many requests" in error_str or "rate limit" in error_str
                is_json_error = isinstance(e, (json.JSONDecodeError, ValueError))
                
                if attempt < retries - 1:
                    # Longer wait for rate limits and JSON errors (which often indicate rate limits)
                    if is_rate_limit or is_json_error:
                        wait_time = 10 * (2 ** attempt)  # 10s, 20s, 40s
                    else:
                        wait_time = 3 * (2 ** attempt)  # 3s, 6s, 12s
                    logger.warning(f"Error fetching historical data for {ticker} (attempt {attempt + 1}/{retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.exception(f"Error fetching historical data for {ticker} after {retries} attempts")
                return []
        
        return []

    def download_bulk(
        self, 
        tickers: List[str], 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Bulk download historical price data for multiple tickers
        For 5-10 stocks, simple loop is sufficient
        Adds delay to avoid rate limiting
        """
        import time
        result = {}
        for i, ticker in enumerate(tickers):
            if i > 0:  # Don't delay before first request
                time.sleep(3)  # Wait 3 seconds between requests to avoid rate limiting
            result[ticker] = self.get_historical_data(ticker, period, start, end)
        return result

    def get_latest_prices_bulk(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get latest price data for multiple tickers (bulk fetch)
        Uses yfinance batch download - simplest approach for 5-10 stocks
        """
        try:
            # Use yfinance batch download - one API call for all tickers
            df = yf.download(tickers, period="1d", progress=False, threads=True, auto_adjust=False)
            
            if df.empty:
                return {ticker: None for ticker in tickers}
            
            result = {}
            last_row = df.iloc[-1]
            last_date = df.index[-1]
            
            # yfinance returns columns like 'Open', 'High', etc. for single ticker
            # or multi-level columns like ('AAPL', 'Open') for multiple tickers
            for ticker in tickers:
                try:
                    if len(tickers) == 1:
                        # Single ticker: columns are just 'Open', 'High', etc.
                        result[ticker] = {
                            "date": last_date.date() if isinstance(last_date, pd.Timestamp) else last_date,
                            "open": float(last_row["Open"]) if pd.notna(last_row["Open"]) else None,
                            "high": float(last_row["High"]) if pd.notna(last_row["High"]) else None,
                            "low": float(last_row["Low"]) if pd.notna(last_row["Low"]) else None,
                            "close": float(last_row["Close"]) if pd.notna(last_row["Close"]) else None,
                            "volume": int(last_row["Volume"]) if pd.notna(last_row["Volume"]) else None,
                            "adj_close": float(last_row["Close"]) if pd.notna(last_row["Close"]) else None,
                        }
                    else:
                        # Multiple tickers: columns are tuples like ('Close', 'AAPL') - note: (PriceType, Ticker) order
                        if ("Close", ticker) in df.columns:
                            result[ticker] = {
                                "date": last_date.date() if isinstance(last_date, pd.Timestamp) else last_date,
                                "open": float(last_row[("Open", ticker)]) if pd.notna(last_row[("Open", ticker)]) else None,
                                "high": float(last_row[("High", ticker)]) if pd.notna(last_row[("High", ticker)]) else None,
                                "low": float(last_row[("Low", ticker)]) if pd.notna(last_row[("Low", ticker)]) else None,
                                "close": float(last_row[("Close", ticker)]) if pd.notna(last_row[("Close", ticker)]) else None,
                                "volume": int(last_row[("Volume", ticker)]) if pd.notna(last_row[("Volume", ticker)]) else None,
                                "adj_close": float(last_row[("Adj Close", ticker)]) if ("Adj Close", ticker) in df.columns and pd.notna(last_row[("Adj Close", ticker)]) else None,
                            }
                        else:
                            from core.logging import get_logger
                            logger = get_logger(__name__)
                            logger.warning(f"Column ('Close', '{ticker}') not found in DataFrame. Available columns: {df.columns.tolist()[:10]}")
                            result[ticker] = None
                except Exception as e:
                    from core.logging import get_logger
                    logger = get_logger(__name__)
                    logger.exception(f"Error processing {ticker}")
                    result[ticker] = None
            
            return result
            
        except Exception as e:
            from core.logging import get_logger
            logger = get_logger(__name__)
            logger.exception("Error fetching latest prices")
            return {ticker: None for ticker in tickers}

