# backend/services/datasource/alpha_vantage_service.py

"""
Alpha Vantage Data Source Service
Provides stock data from Alpha Vantage API
Returns data in the same format as Yahoo Finance service for compatibility
"""

import requests
import time
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from requests.exceptions import HTTPError

from services.datasource.base_data_source import BaseDataSource
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class AlphaVantageService(BaseDataSource):
    """Service for fetching stock data from Alpha Vantage API"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    RATE_LIMIT_DELAY = 12  # 12 seconds between requests (5 requests per minute)
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ALPHA_VANTAGE_API_KEY
        # Debug: Log API key status (without exposing the key)
        if self.api_key:
            logger.info(f"Alpha Vantage API key configured (length: {len(self.api_key)})")
        else:
            logger.error("Alpha Vantage API key not configured! Check ALPHA_VANTAGE_API_KEY environment variable.")
            logger.error(f"Current DATA_SOURCE setting: {settings.DATA_SOURCE}")
            logger.error(f"ALPHA_VANTAGE_API_KEY from settings: {'SET' if settings.ALPHA_VANTAGE_API_KEY else 'NOT SET'}")
    
    def _make_request(self, function: str, symbol: str, **params) -> Dict:
        """Make a request to Alpha Vantage API with rate limiting"""
        if not self.api_key:
            raise ValueError("Alpha Vantage API key is required")
        
        params.update({
            "function": function,
            "symbol": symbol,
            "apikey": self.api_key
        })
        
        # Rate limiting: wait before each request
        time.sleep(self.RATE_LIMIT_DELAY)
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
            if "Note" in data:
                # Rate limit message
                raise ValueError(f"Alpha Vantage rate limit: {data['Note']}")
            
            return data
        except HTTPError as e:
            if e.response.status_code == 429:
                raise ValueError("Rate limit exceeded")
            raise
    
    def get_historical_data(
        self, 
        ticker: str, 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None,
        retries: int = 3
    ) -> List[Dict]:
        """
        Get historical price data for a single ticker
        Returns data in the same format as Yahoo Finance service
        """
        for attempt in range(retries):
            try:
                # Calculate date range
                if start and end:
                    # Use provided dates
                    pass
                else:
                    # Calculate from period
                    end_date = date.today()
                    if period == "1y":
                        start_date = end_date - timedelta(days=365)
                    elif period == "6mo":
                        start_date = end_date - timedelta(days=180)
                    elif period == "3mo":
                        start_date = end_date - timedelta(days=90)
                    elif period == "1mo":
                        start_date = end_date - timedelta(days=30)
                    else:
                        start_date = end_date - timedelta(days=365)
                    
                    start = start_date.isoformat()
                    end = end_date.isoformat()
                
                # Call Alpha Vantage API
                data = self._make_request("TIME_SERIES_DAILY_ADJUSTED", ticker, outputsize="full")
                
                # Parse response
                time_series_key = "Time Series (Daily)"
                if time_series_key not in data:
                    logger.warning(f"No time series data found for {ticker}")
                    return []
                
                time_series = data[time_series_key]
                result = []
                
                # Convert to standard format
                for date_str, values in time_series.items():
                    try:
                        # Parse date string "YYYY-MM-DD" to date object
                        price_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        
                        # Check if date is in range
                        if start and end:
                            start_date_obj = datetime.strptime(start, "%Y-%m-%d").date()
                            end_date_obj = datetime.strptime(end, "%Y-%m-%d").date()
                            if not (start_date_obj <= price_date <= end_date_obj):
                                continue
                        
                        # Map Alpha Vantage fields to standard format
                        result.append({
                            "date": price_date,
                            "open": float(values.get("1. open", 0)) if values.get("1. open") else None,
                            "high": float(values.get("2. high", 0)) if values.get("2. high") else None,
                            "low": float(values.get("3. low", 0)) if values.get("3. low") else None,
                            "close": float(values.get("4. close", 0)) if values.get("4. close") else None,
                            "volume": int(values.get("6. volume", 0)) if values.get("6. volume") else None,
                            "adj_close": float(values.get("5. adjusted close", 0)) if values.get("5. adjusted close") else None,
                        })
                    except (ValueError, KeyError) as e:
                        logger.debug(f"Error parsing date {date_str} for {ticker}: {e}")
                        continue
                
                # Sort by date (ascending)
                result.sort(key=lambda x: x["date"])
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = "rate limit" in error_str or "429" in error_str
                
                if attempt < retries - 1:
                    wait_time = 10 * (2 ** attempt) if is_rate_limit else 3 * (2 ** attempt)
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
        Note: Alpha Vantage doesn't support true bulk download, so we call individually
        with rate limiting (12 seconds between requests)
        """
        result = {}
        for ticker in tickers:
            result[ticker] = self.get_historical_data(ticker, period, start, end)
        return result
    
    def get_latest_prices_bulk(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get latest price data for multiple tickers
        Returns data in the same format as Yahoo Finance service
        """
        result = {}
        for ticker in tickers:
            try:
                # Call Alpha Vantage GLOBAL_QUOTE API
                data = self._make_request("GLOBAL_QUOTE", ticker)
                
                # Parse response
                quote_key = "Global Quote"
                if quote_key not in data or not data[quote_key]:
                    result[ticker] = None
                    continue
                
                quote = data[quote_key]
                today = date.today()
                
                # Map Alpha Vantage fields to standard format
                result[ticker] = {
                    "date": today,
                    "open": float(quote.get("02. open", 0)) if quote.get("02. open") else None,
                    "high": float(quote.get("03. high", 0)) if quote.get("03. high") else None,
                    "low": float(quote.get("04. low", 0)) if quote.get("04. low") else None,
                    "close": float(quote.get("05. price", 0)) if quote.get("05. price") else None,
                    "volume": int(quote.get("06. volume", 0)) if quote.get("06. volume") else None,
                    "adj_close": float(quote.get("05. price", 0)) if quote.get("05. price") else None,  # Use price as adj_close
                }
            except Exception as e:
                logger.warning(f"Error fetching latest price for {ticker}: {e}")
                result[ticker] = None
        
        return result
    
    def get_company_info(self, ticker: str, retries: int = 3) -> Optional[Dict]:
        """
        Get basic company information
        Returns data in the same format as Yahoo Finance service
        """
        for attempt in range(retries):
            try:
                # Call Alpha Vantage OVERVIEW API
                data = self._make_request("OVERVIEW", ticker)
                
                # Check if we got valid data
                if not data or "Symbol" not in data:
                    return None
                
                # Map Alpha Vantage fields to standard format
                return {
                    "ticker": data.get("Symbol", ticker),
                    "name": data.get("Name", ticker),
                    "sector": data.get("Sector", ""),
                    "description": data.get("Description", ""),
                    "homepage_url": data.get("Website", ""),
                    "sic_description": data.get("Industry", ""),
                }
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = "rate limit" in error_str or "429" in error_str
                
                if attempt < retries - 1:
                    wait_time = 10 * (2 ** attempt) if is_rate_limit else 3 * (2 ** attempt)
                    logger.warning(f"Error fetching company info for {ticker} (attempt {attempt + 1}/{retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.exception(f"Error fetching company info for {ticker} after {retries} attempts")
                return None
        
        return None


# Singleton instance
alpha_vantage_service = AlphaVantageService()

