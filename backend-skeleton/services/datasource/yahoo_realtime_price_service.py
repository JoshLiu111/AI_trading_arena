# backend/services/datasource/yahoo_realtime_price_service.py

"""
Yahoo Realtime Price Service - Pure data fetching from Yahoo Finance
Only handles data retrieval, no database operations
"""

from typing import List, Dict, Optional
from datetime import datetime

from config import settings
from services.datasource.yahoo_history_price_service import YahooService


class StockPriceService:
    """
    Pure data fetching service for stock prices
    No database operations - only fetches data from Yahoo Finance
    """
    
    def __init__(self):
        self.yahoo = YahooService()
        self.stock_pool = settings.STOCK_POOL
    
    def get_realtime_prices(self) -> List[Dict]:
        """Get real-time prices for all stocks in pool (pure data fetch)"""
        result = []
        prices = self.yahoo.get_latest_prices_bulk(self.stock_pool)
        
        for ticker in self.stock_pool:
            price_data = prices.get(ticker)
            if price_data:
                result.append({
                    "ticker": ticker,
                    "price": price_data.get("close"),
                    "open": price_data.get("open"),
                    "high": price_data.get("high"),
                    "low": price_data.get("low"),
                    "volume": price_data.get("volume"),
                    "updated_at": datetime.now()
                })
            else:
                result.append({
                    "ticker": ticker,
                    "price": None,
                    "updated_at": datetime.now()
                })
        
        return result
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current price for a single ticker (pure data fetch)
        Uses bulk fetch and extracts the requested ticker
        """
        prices = self.yahoo.get_latest_prices_bulk(self.stock_pool)
        price_data = prices.get(ticker)
        return price_data.get("close") if price_data else None


# Singleton instance
stock_price_service = StockPriceService()
