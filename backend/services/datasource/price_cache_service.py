# backend/services/datasource/price_cache_service.py

"""
In-Memory Price Cache Service
Thread-safe cache for real-time stock prices
"""

import threading
from typing import Dict, Optional
from datetime import datetime

from core.logging import get_logger

logger = get_logger(__name__)


class PriceCacheService:
    """Thread-safe in-memory cache for real-time stock prices"""
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def get_price(self, ticker: str) -> Optional[Dict]:
        """
        Get cached price for a single ticker
        Returns None if not in cache
        """
        with self._lock:
            return self._cache.get(ticker)
    
    def get_prices_bulk(self, tickers: list) -> Dict[str, Optional[Dict]]:
        """
        Get cached prices for multiple tickers
        Returns dict mapping ticker -> price_data or None
        """
        with self._lock:
            return {ticker: self._cache.get(ticker) for ticker in tickers}
    
    def update_price(self, ticker: str, price_data: Dict):
        """
        Update cache for a single ticker
        price_data should contain: price, open, high, low, volume, updated_at, etc.
        """
        with self._lock:
            self._cache[ticker] = {
                **price_data,
                "updated_at": price_data.get("updated_at", datetime.now())
            }
            logger.debug(f"Updated cache for {ticker}")
    
    def update_prices_bulk(self, prices_dict: Dict[str, Dict]):
        """
        Bulk update cache for multiple tickers
        prices_dict: {ticker: {price_data}}
        """
        with self._lock:
            now = datetime.now()
            for ticker, price_data in prices_dict.items():
                self._cache[ticker] = {
                    **price_data,
                    "updated_at": price_data.get("updated_at", now)
                }
            logger.debug(f"Updated cache for {len(prices_dict)} tickers")
    
    def clear(self):
        """Clear all cached prices"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared cache ({count} tickers removed)")
    
    def get_all_tickers(self) -> list:
        """Get list of all tickers in cache"""
        with self._lock:
            return list(self._cache.keys())
    
    def is_cached(self, ticker: str) -> bool:
        """Check if a ticker is in cache"""
        with self._lock:
            return ticker in self._cache


# Singleton instance
price_cache_service = PriceCacheService()

