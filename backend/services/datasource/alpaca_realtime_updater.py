# backend/services/datasource/alpaca_realtime_updater.py

"""
Alpaca Real-Time Data Updater
Scheduled task that fetches latest prices from Alpaca REST API and updates cache
"""

from typing import Dict, List
from datetime import datetime

from config import settings
from services.datasource.data_source_factory import data_source_factory
from services.datasource.price_cache_service import price_cache_service
from core.logging import get_logger

logger = get_logger(__name__)


class AlpacaRealtimeUpdater:
    """Service for updating real-time prices from Alpaca REST API"""
    
    def __init__(self):
        self.stock_pool = settings.STOCK_POOL
        self._alpaca_service = None
    
    def _get_alpaca_service(self):
        """Get Alpaca service instance (lazy initialization)"""
        if self._alpaca_service is None:
            self._alpaca_service = data_source_factory.get_realtime_service()
        return self._alpaca_service
    
    def update_all_prices(self) -> Dict[str, bool]:
        """
        Fetch latest prices for all stocks in pool and update cache
        Returns dict mapping ticker -> success (bool)
        """
        logger.info(f"Starting real-time price update for {len(self.stock_pool)} stocks")
        
        try:
            # Fetch latest prices from Alpaca REST API
            alpaca_service = self._get_alpaca_service()
            prices_dict = alpaca_service.get_latest_prices_bulk(self.stock_pool)
            
            # Prepare cache data
            cache_data = {}
            success_count = 0
            now = datetime.now()
            
            for ticker in self.stock_pool:
                price_data = prices_dict.get(ticker)
                if price_data and price_data.get("close"):
                    cache_data[ticker] = {
                        "price": float(price_data.get("close")),
                        "open": float(price_data.get("open")) if price_data.get("open") else None,
                        "high": float(price_data.get("high")) if price_data.get("high") else None,
                        "low": float(price_data.get("low")) if price_data.get("low") else None,
                        "volume": price_data.get("volume"),
                        "updated_at": now
                    }
                    success_count += 1
                else:
                    logger.warning(f"No price data received for {ticker}")
            
            # Update cache
            if cache_data:
                price_cache_service.update_prices_bulk(cache_data)
                logger.info(f"Updated cache for {success_count}/{len(self.stock_pool)} stocks")
            else:
                logger.warning("No price data to update in cache")
            
            # Return success status for each ticker
            return {ticker: ticker in cache_data for ticker in self.stock_pool}
            
        except Exception as e:
            logger.exception(f"Error updating real-time prices: {e}")
            return {ticker: False for ticker in self.stock_pool}


# Singleton instance
alpaca_realtime_updater = AlpacaRealtimeUpdater()

