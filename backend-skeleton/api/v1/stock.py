# backend/api/v1/stock.py

"""
Stock API Router
Endpoints for stock prices and data
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models.database import get_db
from models.crud.stock_price_crud import get_price_history
from services.datasource.yahoo_realtime_price_service import stock_price_service
from config import settings

router = APIRouter(prefix="/api/v1/stocks", tags=["Stocks"])


@router.get("/prices")
def get_realtime_prices():
    """
    Get real-time prices for all 10 stocks in the pool
    Returns current price, volume, and timestamp
    """
    prices = stock_price_service.get_realtime_prices()
    return {
        "stocks": prices,
        "updated_at": datetime.now().isoformat(),
        "stock_pool": settings.STOCK_POOL
    }


@router.get("/pool")
def get_stock_pool():
    """Get the list of stocks in the competition pool"""
    return {
        "stocks": settings.STOCK_POOL,
        "count": len(settings.STOCK_POOL)
    }


@router.get("/{ticker}/price")
def get_single_price(ticker: str):
    """Get current price for a single stock"""
    ticker = ticker.upper()
    if ticker not in settings.STOCK_POOL:
        return {"error": "Stock not in pool", "ticker": ticker}
    
    price = stock_price_service.get_current_price(ticker)
    return {
        "ticker": ticker,
        "price": price,
        "updated_at": datetime.now().isoformat()
    }


@router.get("/{ticker}/history")
def get_stock_history(
    ticker: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get historical price data for a stock"""
    ticker = ticker.upper()
    history = get_price_history(db, ticker, days=days)
    
    # Convert ORM objects to dicts
    history_data = []
    for h in history:
        if hasattr(h, 'to_dict'):
            history_data.append(h.to_dict())
        else:
            # Manual conversion if to_dict doesn't exist
            history_data.append({
                "date": h.date.isoformat() if hasattr(h, 'date') and h.date else None,
                "open": float(h.open) if hasattr(h, 'open') and h.open else None,
                "high": float(h.high) if hasattr(h, 'high') and h.high else None,
                "low": float(h.low) if hasattr(h, 'low') and h.low else None,
                "close": float(h.close) if hasattr(h, 'close') and h.close else None,
                "volume": int(h.volume) if hasattr(h, 'volume') and h.volume else None,
                "adj_close": float(h.adj_close) if hasattr(h, 'adj_close') and h.adj_close else None,
            })
    
    return {
        "ticker": ticker,
        "days": days,
        "data": history_data
    }
