# backend/services/datasource/yahoo_info_service.py

"""
Yahoo Info Service - Company information from Yahoo Finance
"""

import yfinance as yf
from typing import Optional, Dict


class YahooInfoService:
    """Service for fetching company information from Yahoo Finance"""

    def get_company_info(self, ticker: str, retries: int = 3) -> Optional[Dict]:
        """Get basic company information with retry logic"""
        import time
        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                if not info or "shortName" not in info:
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
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
            except Exception as e:
                from core.logging import get_logger
                logger = get_logger(__name__)
                error_str = str(e).lower()
                # Check if it's a rate limit error (429)
                is_rate_limit = "429" in error_str or "too many requests" in error_str or "rate limit" in error_str
                
                if attempt < retries - 1:
                    # Longer wait for rate limit errors
                    wait_time = (2 ** attempt) * (5 if is_rate_limit else 1)  # 5s, 10s, 20s for rate limits
                    logger.warning(f"Error fetching company info for {ticker} (attempt {attempt + 1}/{retries}): {str(e)[:100]}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.exception(f"Error fetching company info for {ticker} after {retries} attempts")
                return None
        
        return None


# Singleton instance
yahoo_info_service = YahooInfoService()

