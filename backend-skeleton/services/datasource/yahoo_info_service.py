# backend/services/datasource/yahoo_info_service.py

"""
Yahoo Info Service - Company information from Yahoo Finance
"""

import yfinance as yf
from typing import Optional, Dict


class YahooInfoService:
    """Service for fetching company information from Yahoo Finance"""

    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """Get basic company information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or "shortName" not in info:
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
            print(f"Error fetching company info for {ticker}: {e}")
            return None


# Singleton instance
yahoo_info_service = YahooInfoService()

