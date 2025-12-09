# backend/services/datasource/polygon_service.py

"""
Polygon.io Data Source Service
Provides stock data from Polygon.io API
Returns data in the same format as existing services for compatibility
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


class PolygonService(BaseDataSource):
    """Service for fetching stock data from Polygon.io API"""
    
    BASE_URL = "https://api.polygon.io"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.POLYGON_API_KEY
        if self.api_key:
            logger.info(f"Polygon API key configured (length: {len(self.api_key)})")
        else:
            logger.error("Polygon API key not configured! Check POLYGON_API_KEY environment variable.")
            logger.error(f"Current DATA_SOURCE setting: {settings.DATA_SOURCE}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to Polygon.io API"""
        if not self.api_key:
            raise ValueError("Polygon API key is required")
        
        url = f"{self.BASE_URL}{endpoint}"
        request_params = {"apikey": self.api_key}
        if params:
            request_params.update(params)
        
        try:
            response = requests.get(url, params=request_params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if data.get("status") == "ERROR":
                error_msg = data.get("error", "Unknown error")
                logger.error(f"Polygon API error: {error_msg}")
                raise ValueError(f"Polygon API error: {error_msg}")
            
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
        Returns data in the same format as existing services
        """
        for attempt in range(retries):
            try:
                # Calculate date range
                if start and end:
                    # Use provided dates
                    from_date = start
                    to_date = end
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
                    
                    from_date = start_date.isoformat()
                    to_date = end_date.isoformat()
                
                # Call Polygon API: /v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}
                endpoint = f"/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}"
                logger.debug(f"Fetching historical data for {ticker} from {from_date} to {to_date}")
                data = self._make_request(endpoint)
                
                # Parse response
                if "results" not in data or not data["results"]:
                    logger.warning(f"No historical data found for {ticker}")
                    return []
                
                results = data["results"]
                result = []
                
                # Convert to standard format
                for item in results:
                    try:
                        # Polygon returns Unix timestamp in milliseconds
                        timestamp_ms = item.get("t", 0)
                        price_date = datetime.fromtimestamp(timestamp_ms / 1000).date()
                        
                        # Map Polygon fields to standard format
                        result.append({
                            "date": price_date,
                            "open": float(item.get("o", 0)) if item.get("o") else None,
                            "high": float(item.get("h", 0)) if item.get("h") else None,
                            "low": float(item.get("l", 0)) if item.get("l") else None,
                            "close": float(item.get("c", 0)) if item.get("c") else None,
                            "volume": int(item.get("v", 0)) if item.get("v") else None,
                            "adj_close": float(item.get("c", 0)) if item.get("c") else None,  # Use close as adj_close
                        })
                    except (ValueError, KeyError) as e:
                        logger.debug(f"Error parsing data for {ticker}: {e}")
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
        Polygon doesn't support true bulk download, so we call individually
        """
        result = {}
        total = len(tickers)
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"Downloading {ticker} ({i}/{total})...")
            result[ticker] = self.get_historical_data(ticker, period, start, end)
            if not result[ticker]:
                logger.warning(f"No data received for {ticker}")
            # Small delay to avoid overwhelming the API
            if i < total:
                time.sleep(0.1)  # 100ms delay between requests
        return result
    
    def get_latest_prices_bulk(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get latest price data for multiple tickers
        Uses Polygon snapshot endpoint for bulk fetch
        """
        result = {}
        
        try:
            # Use snapshot endpoint for bulk fetch
            # Format: /v2/snapshot/locale/us/markets/stocks/tickers?tickers=AAPL,MSFT,GOOGL
            tickers_str = ",".join(tickers)
            endpoint = f"/v2/snapshot/locale/us/markets/stocks/tickers"
            params = {"tickers": tickers_str}
            logger.debug(f"Fetching snapshot for tickers: {tickers_str}")
            
            data = self._make_request(endpoint, params)
            
            # Parse response
            if "tickers" not in data:
                logger.warning(f"No tickers data in snapshot response. Response keys: {list(data.keys())}")
                logger.debug(f"Full snapshot response: {data}")
                return {ticker: None for ticker in tickers}
            
            tickers_data = data["tickers"]
            if not tickers_data:
                logger.warning("Empty tickers array in snapshot response")
                return {ticker: None for ticker in tickers}
            
            ticker_dict = {item.get("ticker", ""): item for item in tickers_data if item.get("ticker")}
            logger.debug(f"Snapshot response contains {len(ticker_dict)} tickers: {list(ticker_dict.keys())}")
            
            today = date.today()
            
            for ticker in tickers:
                try:
                    ticker_data = ticker_dict.get(ticker)
                    if not ticker_data:
                        result[ticker] = None
                        continue
                    
                    # Get latest trade data
                    last_trade = ticker_data.get("lastTrade") or {}
                    prev_day = ticker_data.get("prevDay") or {}
                    
                    # Debug logging
                    logger.debug(f"Ticker {ticker} - lastTrade keys: {list(last_trade.keys()) if last_trade else 'None'}, prevDay keys: {list(prev_day.keys()) if prev_day else 'None'}")
                    
                    # Use last trade price as close, or prevDay close if not available
                    close_price = None
                    if last_trade and isinstance(last_trade, dict) and last_trade.get("p"):
                        try:
                            close_price = float(last_trade["p"])
                            logger.debug(f"Using lastTrade price for {ticker}: {close_price}")
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid lastTrade price for {ticker}: {last_trade.get('p')}")
                    elif prev_day and isinstance(prev_day, dict) and prev_day.get("c"):
                        try:
                            close_price = float(prev_day["c"])
                            logger.debug(f"Using prevDay close for {ticker}: {close_price}")
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid prevDay close for {ticker}: {prev_day.get('c')}")
                    
                    if close_price is None:
                        logger.warning(f"No valid price found for {ticker} in snapshot data. lastTrade: {last_trade}, prevDay: {prev_day}")
                    
                    result[ticker] = {
                        "date": today,
                        "open": float(prev_day.get("o", 0)) if prev_day.get("o") else None,
                        "high": float(prev_day.get("h", 0)) if prev_day.get("h") else None,
                        "low": float(prev_day.get("l", 0)) if prev_day.get("l") else None,
                        "close": close_price,
                        "volume": int(prev_day.get("v", 0)) if prev_day.get("v") else None,
                        "adj_close": close_price,  # Use close as adj_close
                    }
                except Exception as e:
                    logger.warning(f"Error processing {ticker} from snapshot: {e}")
                    result[ticker] = None
            
            return result
            
        except Exception as e:
            logger.exception("Error fetching latest prices from snapshot, falling back to individual requests")
            # Fallback to individual requests
            for ticker in tickers:
                try:
                    # Use last trade endpoint: /v2/last/trade/{ticker}
                    endpoint = f"/v2/last/trade/{ticker}"
                    data = self._make_request(endpoint)
                    
                    if "results" not in data or not data["results"]:
                        result[ticker] = None
                        continue
                    
                    last_trade = data["results"]
                    timestamp_ms = last_trade.get("t", 0)
                    trade_date = datetime.fromtimestamp(timestamp_ms / 1000).date()
                    
                    result[ticker] = {
                        "date": trade_date,
                        "open": None,  # Last trade doesn't provide OHLC
                        "high": None,
                        "low": None,
                        "close": float(last_trade.get("p", 0)) if last_trade.get("p") else None,
                        "volume": None,
                        "adj_close": float(last_trade.get("p", 0)) if last_trade.get("p") else None,
                    }
                except Exception as e:
                    logger.warning(f"Error fetching latest price for {ticker}: {e}")
                    result[ticker] = None
        
        return result
    
    def get_company_info(self, ticker: str, retries: int = 3) -> Optional[Dict]:
        """
        Get basic company information
        Returns data in the same format as existing services
        """
        for attempt in range(retries):
            try:
                # Call Polygon API: /v3/reference/tickers/{ticker}
                endpoint = f"/v3/reference/tickers/{ticker}"
                data = self._make_request(endpoint)
                
                # Parse response
                if "results" not in data or not data["results"]:
                    return None
                
                results = data["results"]
                
                # Map Polygon fields to standard format
                # Polygon ticker details response structure
                name = results.get("name", ticker)
                description = results.get("description", "")
                homepage_url = results.get("homepage_url", "") or results.get("url", "")
                
                # Sector mapping - Polygon may use different field names
                sector = results.get("sic_description", "") or results.get("market", "") or results.get("market_cap", "")
                
                # SIC description - industry or type
                sic_description = results.get("sic_description", "") or results.get("type", "") or results.get("primary_exchange", "")
                
                return {
                    "ticker": results.get("ticker", ticker),
                    "name": name,
                    "sector": sector,
                    "description": description,
                    "homepage_url": homepage_url,
                    "sic_description": sic_description,
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
polygon_service = PolygonService()
