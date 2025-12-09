# backend/services/datasource/yahoo_info_service.py

"""
Yahoo Info Service - Company information from Yahoo Finance
"""

import yfinance as yf
from typing import Optional, Dict, List
import json

from services.datasource.base_data_source import BaseDataSource


class YahooInfoService(BaseDataSource):
    """Service for fetching company information from Yahoo Finance"""

    def get_company_info(self, ticker: str, retries: int = 3) -> Optional[Dict]:
        """Get basic company information with retry logic"""
        import time
        from requests.exceptions import HTTPError
        
        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                if not info or "shortName" not in info:
                    if attempt < retries - 1:
                        time.sleep(3 * (2 ** attempt))  # Exponential backoff: 3s, 6s, 12s
                        continue
                    return None
                
                return {
                    "ticker": ticker,
                    "name": info.get("shortName") or info.get("longName") or "Unknown",
                    "sector": info.get("sector") or "",
                    "description": info.get("longBusinessSummary") or "",
                    "homepage_url": info.get("website") or "",
                    "sic_description": info.get("industry") or "",
                }
            except (json.JSONDecodeError, ValueError) as e:
                # JSONDecodeError usually means 429 rate limit (non-JSON response)
                from core.logging import get_logger
                logger = get_logger(__name__)
                if attempt < retries - 1:
                    wait_time = 10 * (2 ** attempt)  # 10s, 20s, 40s for JSON errors (likely rate limit)
                    logger.warning(f"JSON decode error for {ticker} (likely rate limit, attempt {attempt + 1}/{retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"JSON decode error for {ticker} after {retries} attempts: {e}")
                return None
            except HTTPError as e:
                from core.logging import get_logger
                logger = get_logger(__name__)
                is_rate_limit = e.response.status_code == 429
                if attempt < retries - 1:
                    wait_time = 10 * (2 ** attempt) if is_rate_limit else 3 * (2 ** attempt)
                    logger.warning(f"HTTP error for {ticker} (status {e.response.status_code}, attempt {attempt + 1}/{retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"HTTP error for {ticker} after {retries} attempts: {e}")
                return None
            except Exception as e:
                from core.logging import get_logger
                logger = get_logger(__name__)
                error_str = str(e).lower()
                # Check if it's a rate limit error (429)
                is_rate_limit = "429" in error_str or "too many requests" in error_str or "rate limit" in error_str
                
                if attempt < retries - 1:
                    # Longer wait for rate limit errors
                    wait_time = 10 * (2 ** attempt) if is_rate_limit else 3 * (2 ** attempt)
                    logger.warning(f"Error fetching company info for {ticker} (attempt {attempt + 1}/{retries}): {str(e)[:100]}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.exception(f"Error fetching company info for {ticker} after {retries} attempts")
                return None
        
        return None
    
    def get_historical_data(
        self, 
        ticker: str, 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None,
        retries: int = 3
    ) -> List[Dict]:
        """
        Get historical data - not implemented in YahooInfoService
        Use YahooService for historical data
        """
        from services.datasource.yahoo_history_price_service import YahooService
        yahoo_service = YahooService()
        return yahoo_service.get_historical_data(ticker, period, start, end, retries)
    
    def download_bulk(
        self, 
        tickers: List[str], 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Bulk download - not implemented in YahooInfoService
        Use YahooService for bulk download
        """
        from services.datasource.yahoo_history_price_service import YahooService
        yahoo_service = YahooService()
        return yahoo_service.download_bulk(tickers, period, start, end)
    
    def get_latest_prices_bulk(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get latest prices - not implemented in YahooInfoService
        Use YahooService for latest prices
        """
        from services.datasource.yahoo_history_price_service import YahooService
        yahoo_service = YahooService()
        return yahoo_service.get_latest_prices_bulk(tickers)


# Singleton instance
yahoo_info_service = YahooInfoService()

