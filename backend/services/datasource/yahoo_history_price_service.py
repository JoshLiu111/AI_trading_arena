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
        Uses yfinance batch download - one API call for all tickers to avoid rate limiting
        """
        from core.logging import get_logger
        import time
        import json
        from requests.exceptions import HTTPError
        
        logger = get_logger(__name__)
        result = {ticker: [] for ticker in tickers}
        
        # Try bulk download with retries
        max_bulk_retries = 3
        for bulk_attempt in range(max_bulk_retries):
            try:
                # Use yfinance batch download - one API call for all tickers
                if start and end:
                    df = yf.download(tickers, start=start, end=end, progress=False, threads=True, auto_adjust=False)
                else:
                    df = yf.download(tickers, period=period, progress=False, threads=True, auto_adjust=False)
                
                if not df.empty:
                    # Success - process the data
                    break
                else:
                    # Empty DataFrame - might be rate limited
                    if bulk_attempt < max_bulk_retries - 1:
                        wait_time = 10 * (2 ** bulk_attempt)  # 10s, 20s, 40s
                        logger.warning(f"Bulk download returned empty DataFrame (attempt {bulk_attempt + 1}/{max_bulk_retries}), retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.warning("Bulk download returned empty DataFrame after all retries, falling back to individual requests")
                        # Fallback to individual requests if bulk download fails
                        time.sleep(5)  # Wait before starting individual requests
                        for i, ticker in enumerate(tickers):
                            if i > 0:
                                time.sleep(5)  # Wait 5 seconds between requests
                            result[ticker] = self.get_historical_data(ticker, period, start, end)
                        return result
            except (HTTPError, json.JSONDecodeError, ValueError) as e:
                error_str = str(e).lower()
                is_rate_limit = "429" in error_str or "too many requests" in error_str or "rate limit" in error_str
                
                if bulk_attempt < max_bulk_retries - 1:
                    wait_time = 10 * (2 ** bulk_attempt)  # 10s, 20s, 40s
                    logger.warning(f"Bulk download failed (attempt {bulk_attempt + 1}/{max_bulk_retries}): {str(e)[:100]}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"Bulk download failed after all retries: {e}, falling back to individual requests")
                    # Fallback to individual requests if bulk download fails completely
                    time.sleep(5)  # Wait before starting individual requests
                    for i, ticker in enumerate(tickers):
                        if i > 0:
                            time.sleep(5)  # Wait 5 seconds between requests
                        result[ticker] = self.get_historical_data(ticker, period, start, end)
                    return result
            except Exception as e:
                if bulk_attempt < max_bulk_retries - 1:
                    wait_time = 10 * (2 ** bulk_attempt)
                    logger.warning(f"Bulk download error (attempt {bulk_attempt + 1}/{max_bulk_retries}): {str(e)[:100]}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"Bulk download failed after all retries: {e}, falling back to individual requests")
                    time.sleep(5)
                    for i, ticker in enumerate(tickers):
                        if i > 0:
                            time.sleep(5)
                        result[ticker] = self.get_historical_data(ticker, period, start, end)
                    return result
        
        # If we get here, bulk download succeeded - process the data
        # Process bulk download results
        # yfinance returns multi-level columns: (PriceType, Ticker) or (Ticker, PriceType) for multiple tickers
        # or single-level columns for single ticker
        
        logger.info(f"Bulk download succeeded. DataFrame shape: {df.shape}, columns sample: {df.columns.tolist()[:10]}")
        
        for ticker in tickers:
            try:
                if len(tickers) == 1:
                    # Single ticker: columns are just 'Open', 'High', etc.
                    ticker_data = []
                    for index, row in df.iterrows():
                        ticker_data.append({
                            "date": index.date() if isinstance(index, pd.Timestamp) else index,
                            "open": float(row["Open"]) if pd.notna(row["Open"]) else None,
                            "high": float(row["High"]) if pd.notna(row["High"]) else None,
                            "low": float(row["Low"]) if pd.notna(row["Low"]) else None,
                            "close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                            "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else None,
                            "adj_close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                        })
                    result[ticker] = ticker_data
                else:
                    # Multiple tickers: columns are tuples
                    # Try (Ticker, PriceType) format first, then (PriceType, Ticker) format
                    ticker_data = []
                    column_format = None
                    
                    # Check which format is used
                    if (ticker, "Close") in df.columns:
                        column_format = "ticker_first"  # (Ticker, PriceType)
                    elif ("Close", ticker) in df.columns:
                        column_format = "price_first"  # (PriceType, Ticker)
                    else:
                        logger.warning(f"Ticker {ticker} not found in bulk download results. Available columns: {[c for c in df.columns if isinstance(c, tuple)][:5]}")
                        result[ticker] = self.get_historical_data(ticker, period, start, end)
                        continue
                    
                    # Process data based on column format
                    for index, row in df.iterrows():
                        if column_format == "ticker_first":
                            # Format: (Ticker, PriceType) e.g., ('AAPL', 'Close')
                            ticker_data.append({
                                "date": index.date() if isinstance(index, pd.Timestamp) else index,
                                "open": float(row[(ticker, "Open")]) if pd.notna(row[(ticker, "Open")]) else None,
                                "high": float(row[(ticker, "High")]) if pd.notna(row[(ticker, "High")]) else None,
                                "low": float(row[(ticker, "Low")]) if pd.notna(row[(ticker, "Low")]) else None,
                                "close": float(row[(ticker, "Close")]) if pd.notna(row[(ticker, "Close")]) else None,
                                "volume": int(row[(ticker, "Volume")]) if pd.notna(row[(ticker, "Volume")]) else None,
                                "adj_close": float(row[(ticker, "Adj Close")]) if (ticker, "Adj Close") in df.columns and pd.notna(row[(ticker, "Adj Close")]) else None,
                            })
                        else:
                            # Format: (PriceType, Ticker) e.g., ('Close', 'AAPL')
                            ticker_data.append({
                                "date": index.date() if isinstance(index, pd.Timestamp) else index,
                                "open": float(row[("Open", ticker)]) if pd.notna(row[("Open", ticker)]) else None,
                                "high": float(row[("High", ticker)]) if pd.notna(row[("High", ticker)]) else None,
                                "low": float(row[("Low", ticker)]) if pd.notna(row[("Low", ticker)]) else None,
                                "close": float(row[("Close", ticker)]) if pd.notna(row[("Close", ticker)]) else None,
                                "volume": int(row[("Volume", ticker)]) if pd.notna(row[("Volume", ticker)]) else None,
                                "adj_close": float(row[("Adj Close", ticker)]) if ("Adj Close", ticker) in df.columns and pd.notna(row[("Adj Close", ticker)]) else None,
                            })
                    result[ticker] = ticker_data
            except Exception as e:
                logger.warning(f"Error processing {ticker} from bulk download: {e}, falling back to individual request")
                # Fallback to individual request if processing fails
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
                        # Multiple tickers: columns are tuples
                        # Try (Ticker, PriceType) format first, then (PriceType, Ticker) format
                        if (ticker, "Close") in df.columns:
                            # Format: (Ticker, PriceType) e.g., ('AAPL', 'Close')
                            result[ticker] = {
                                "date": last_date.date() if isinstance(last_date, pd.Timestamp) else last_date,
                                "open": float(last_row[(ticker, "Open")]) if pd.notna(last_row[(ticker, "Open")]) else None,
                                "high": float(last_row[(ticker, "High")]) if pd.notna(last_row[(ticker, "High")]) else None,
                                "low": float(last_row[(ticker, "Low")]) if pd.notna(last_row[(ticker, "Low")]) else None,
                                "close": float(last_row[(ticker, "Close")]) if pd.notna(last_row[(ticker, "Close")]) else None,
                                "volume": int(last_row[(ticker, "Volume")]) if pd.notna(last_row[(ticker, "Volume")]) else None,
                                "adj_close": float(last_row[(ticker, "Adj Close")]) if (ticker, "Adj Close") in df.columns and pd.notna(last_row[(ticker, "Adj Close")]) else None,
                            }
                        elif ("Close", ticker) in df.columns:
                            # Format: (PriceType, Ticker) e.g., ('Close', 'AAPL')
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
                            logger.warning(f"Column for '{ticker}' not found in DataFrame. Available columns: {df.columns.tolist()[:10]}")
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

