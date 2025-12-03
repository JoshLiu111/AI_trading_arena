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
        end: Optional[str] = None
    ) -> List[Dict]:
        """Get historical price data for a single ticker"""
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
            print(f"Error fetching historical data for {ticker}: {e}")
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
        """
        result = {}
        for ticker in tickers:
            result[ticker] = self.get_historical_data(ticker, period, start, end)
        return result

    def get_latest_prices_bulk(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get latest price data for multiple tickers (bulk fetch)
        Uses yfinance batch download - simplest approach for 5-10 stocks
        """
        try:
            # Use yfinance batch download - one API call for all tickers
            df = yf.download(tickers, period="1d", progress=False, threads=True)
            
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
                        # Multiple tickers: columns are tuples like ('AAPL', 'Open')
                        if (ticker, "Close") in df.columns:
                            result[ticker] = {
                                "date": last_date.date() if isinstance(last_date, pd.Timestamp) else last_date,
                                "open": float(last_row[(ticker, "Open")]) if pd.notna(last_row[(ticker, "Open")]) else None,
                                "high": float(last_row[(ticker, "High")]) if pd.notna(last_row[(ticker, "High")]) else None,
                                "low": float(last_row[(ticker, "Low")]) if pd.notna(last_row[(ticker, "Low")]) else None,
                                "close": float(last_row[(ticker, "Close")]) if pd.notna(last_row[(ticker, "Close")]) else None,
                                "volume": int(last_row[(ticker, "Volume")]) if pd.notna(last_row[(ticker, "Volume")]) else None,
                                "adj_close": float(last_row[(ticker, "Close")]) if pd.notna(last_row[(ticker, "Close")]) else None,
                            }
                        else:
                            result[ticker] = None
                except Exception as e:
                    print(f"Error processing {ticker}: {e}")
                    result[ticker] = None
            
            return result
            
        except Exception as e:
            print(f"Error fetching latest prices: {e}")
            return {ticker: None for ticker in tickers}

