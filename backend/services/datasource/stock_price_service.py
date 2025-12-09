# backend/services/datasource/stock_price_service.py

"""
Stock Price Service - Pure data fetching from configured data source
Only handles data retrieval, no database operations
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from config import settings
from services.datasource.data_source_factory import data_source_factory
from core.logging import get_logger

logger = get_logger(__name__)


class StockPriceService:
    """
    Pure data fetching service for stock prices
    No database operations - only fetches data from configured data source
    """
    
    def __init__(self):
        self._data_source = None  # Lazy initialization
        self.stock_pool = settings.STOCK_POOL
        self._websocket_service = None
        self._websocket_initialized = False
    
    def _get_data_source(self):
        """Get data source instance (lazy initialization)"""
        if self._data_source is None:
            self._data_source = data_source_factory.get_realtime_service()
        return self._data_source
    
    def get_realtime_prices(self, db: Session = None) -> List[Dict]:
        """
        Get real-time prices for all stocks in pool (pure data fetch)
        If USE_HISTORICAL_AS_REALTIME is True, uses latest historical price from database
        """
        result = []
        
        # Test mode: use historical data as real-time
        if settings.USE_HISTORICAL_AS_REALTIME and db:
            from models.crud.stock_price_crud import get_latest_price_data
            if not hasattr(self, '_test_mode_logged'):
                logger.info("TEST MODE: Using historical data as real-time prices (non-market hours testing)")
                self._test_mode_logged = True
            for ticker in self.stock_pool:
                latest = get_latest_price_data(db, ticker)
                if latest:
                    result.append({
                        "ticker": ticker,
                        "price": float(latest.close) if latest.close else None,
                        "open": float(latest.open) if latest.open else None,
                        "high": float(latest.high) if latest.high else None,
                        "low": float(latest.low) if latest.low else None,
                        "volume": latest.volume,
                        "updated_at": datetime.now()
                    })
                else:
                    result.append({
                        "ticker": ticker,
                        "price": None,
                        "updated_at": datetime.now()
                    })
        else:
            # Normal mode: fetch from configured data source
            # Try WebSocket first if using Polygon and WebSocket is running, fallback to REST API
            ws_service = self._get_websocket_service()
            if settings.DATA_SOURCE == "polygon" and ws_service and ws_service.running:
                # Try to get from WebSocket cache first
                ws_prices = ws_service.get_cached_prices_bulk(self.stock_pool)
                # Use WebSocket data if available, otherwise fallback to REST
                if any(ws_prices.values()):
                    logger.debug("Using WebSocket cached prices for real-time data")
                    prices = ws_prices
                else:
                    logger.debug("WebSocket cache empty, fetching from Polygon REST API")
                    prices = self._get_data_source().get_latest_prices_bulk(self.stock_pool)
            else:
                logger.debug("Fetching real-time prices from Polygon REST API")
                prices = self._get_data_source().get_latest_prices_bulk(self.stock_pool)
            
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
    
    def get_current_price(self, ticker: str, db: Session = None) -> Optional[float]:
        """
        Get current price for a single ticker (pure data fetch)
        If USE_HISTORICAL_AS_REALTIME is True, uses latest historical price from database
        Otherwise, prioritizes WebSocket real-time data, falls back to REST API
        """
        # Test mode: use historical data as real-time
        if settings.USE_HISTORICAL_AS_REALTIME and db:
            from models.crud.stock_price_crud import get_latest_price_data
            latest = get_latest_price_data(db, ticker)
            if latest and latest.close:
                return float(latest.close)
            return None
        else:
            # Normal mode: fetch from configured data source
            # Try WebSocket first if using Polygon and WebSocket is running, fallback to REST API
            ws_service = self._get_websocket_service()
            if settings.DATA_SOURCE == "polygon" and ws_service and ws_service.running:
                ws_price = ws_service.get_cached_price(ticker)
                if ws_price and ws_price.get("close"):
                    logger.debug(f"Using WebSocket cached price for {ticker}")
                    return float(ws_price.get("close"))
                else:
                    logger.debug(f"WebSocket cache empty for {ticker}, fetching from REST API")
                    prices = self._get_data_source().get_latest_prices_bulk([ticker])
                    price_data = prices.get(ticker)
                    return price_data.get("close") if price_data else None
            else:
                logger.debug(f"Fetching real-time price for {ticker} from Polygon REST API")
                prices = self._get_data_source().get_latest_prices_bulk([ticker])
                price_data = prices.get(ticker)
                return price_data.get("close") if price_data else None
    
    def get_current_prices_bulk(self, tickers: List[str], db: Session = None) -> Dict[str, Optional[float]]:
        """
        Get current prices for multiple tickers in bulk (optimized for N+1 query prevention)
        Returns a dict mapping ticker -> price
        """
        result = {}
        
        # Test mode: use historical data as real-time
        if settings.USE_HISTORICAL_AS_REALTIME and db:
            from models.crud.stock_price_crud import get_latest_price_data
            for ticker in tickers:
                latest = get_latest_price_data(db, ticker)
                result[ticker] = float(latest.close) if latest and latest.close else None
        else:
            # Normal mode: fetch from configured data source (already bulk)
            # Try WebSocket first if using Polygon and WebSocket is running, fallback to REST API
            ws_service = self._get_websocket_service()
            if settings.DATA_SOURCE == "polygon" and ws_service and ws_service.running:
                ws_prices = ws_service.get_cached_prices_bulk(tickers)
                if any(ws_prices.values()):
                    logger.debug("Using WebSocket cached prices for bulk real-time data")
                    prices = ws_prices
                else:
                    logger.debug("WebSocket cache empty, fetching from Polygon REST API for bulk prices")
                    prices = self._get_data_source().get_latest_prices_bulk(tickers)
            else:
                logger.debug("Fetching bulk real-time prices from Polygon REST API")
                prices = self._get_data_source().get_latest_prices_bulk(tickers)
            for ticker in tickers:
                price_data = prices.get(ticker)
                result[ticker] = price_data.get("close") if price_data else None
        
        return result
    
    def _get_websocket_service(self):
        """Get WebSocket service instance (lazy initialization)"""
        if not self._websocket_initialized:
            try:
                from services.datasource.polygon_websocket_service import polygon_websocket_service
                self._websocket_service = polygon_websocket_service
                self._websocket_initialized = True
            except Exception as e:
                logger.debug(f"WebSocket service not available: {e}")
                self._websocket_service = None
                self._websocket_initialized = True
        return self._websocket_service


# Singleton instance
stock_price_service = StockPriceService()

