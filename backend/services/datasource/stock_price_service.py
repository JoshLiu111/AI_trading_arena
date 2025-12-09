# backend/services/datasource/stock_price_service.py

"""
Stock Price Service - Reads from cache and database
Never calls external APIs - all data comes from cache or database
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from config import settings
from services.datasource.price_cache_service import price_cache_service
from core.logging import get_logger

logger = get_logger(__name__)


class StockPriceService:
    """
    Stock price service - reads from cache and database
    Never calls external APIs - all data comes from cache or database
    """
    
    def __init__(self):
        self.stock_pool = settings.STOCK_POOL
        self._test_mode_logged = False  # Flag to log test mode message only once
    
    def get_realtime_prices(self, db: Session = None) -> List[Dict]:
        """
        Get real-time prices for all stocks in pool
        Reads from cache first, falls back to database (latest historical)
        Never calls external APIs
        """
        result = []
        
        # Test mode: use historical data as real-time
        if settings.USE_HISTORICAL_AS_REALTIME and db:
            from models.crud.stock_price_crud import get_latest_price_data
            if not self._test_mode_logged:
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
            # Normal mode: read from cache, fallback to database
            from models.crud.stock_price_crud import get_latest_price_data
            
            # Get prices from cache
            cached_prices = price_cache_service.get_prices_bulk(self.stock_pool)
            
            for ticker in self.stock_pool:
                cached_data = cached_prices.get(ticker)
                
                if cached_data and cached_data.get("price"):
                    # Use cached price
                    result.append({
                        "ticker": ticker,
                        "price": cached_data.get("price"),
                        "open": cached_data.get("open"),
                        "high": cached_data.get("high"),
                        "low": cached_data.get("low"),
                        "volume": cached_data.get("volume"),
                        "updated_at": cached_data.get("updated_at", datetime.now())
                    })
                elif db:
                    # Fallback to database (latest historical)
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
                    result.append({
                        "ticker": ticker,
                        "price": None,
                        "updated_at": datetime.now()
                    })
        
        return result
    
    def get_current_price(self, ticker: str, db: Session = None) -> Optional[float]:
        """
        Get current price for a single ticker
        Reads from cache first, falls back to database
        Never calls external APIs
        """
        # Test mode: use historical data as real-time
        if settings.USE_HISTORICAL_AS_REALTIME and db:
            from models.crud.stock_price_crud import get_latest_price_data
            latest = get_latest_price_data(db, ticker)
            if latest and latest.close:
                return float(latest.close)
            return None
        else:
            # Normal mode: read from cache, fallback to database
            cached_data = price_cache_service.get_price(ticker)
            
            if cached_data and cached_data.get("price"):
                return float(cached_data.get("price"))
            elif db:
                # Fallback to database
                from models.crud.stock_price_crud import get_latest_price_data
                latest = get_latest_price_data(db, ticker)
                if latest and latest.close:
                    return float(latest.close)
            
            return None
    
    def get_current_prices_bulk(self, tickers: List[str], db: Session = None) -> Dict[str, Optional[float]]:
        """
        Get current prices for multiple tickers in bulk
        Reads from cache first, falls back to database
        Never calls external APIs
        """
        result = {}
        
        # Test mode: use historical data as real-time
        if settings.USE_HISTORICAL_AS_REALTIME and db:
            from models.crud.stock_price_crud import get_latest_price_data
            for ticker in tickers:
                latest = get_latest_price_data(db, ticker)
                result[ticker] = float(latest.close) if latest and latest.close else None
        else:
            # Normal mode: read from cache, fallback to database
            cached_prices = price_cache_service.get_prices_bulk(tickers)
            
            for ticker in tickers:
                cached_data = cached_prices.get(ticker)
                if cached_data and cached_data.get("price"):
                    result[ticker] = float(cached_data.get("price"))
                elif db:
                    # Fallback to database
                    from models.crud.stock_price_crud import get_latest_price_data
                    latest = get_latest_price_data(db, ticker)
                    result[ticker] = float(latest.close) if latest and latest.close else None
                else:
                    result[ticker] = None
        
        return result


# Singleton instance
stock_price_service = StockPriceService()
