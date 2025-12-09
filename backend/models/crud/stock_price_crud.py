# backend/models/crud/stock_price_crud.py

"""
Stock Price CRUD operations
"""

from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from models.schema.stock_price import StockPriceData


def create_price_data(
    db: Session,
    ticker: str,
    date: date,
    open: Optional[float] = None,
    high: Optional[float] = None,
    low: Optional[float] = None,
    close: Optional[float] = None,
    volume: Optional[int] = None,
    adj_close: Optional[float] = None
) -> StockPriceData:
    """Create a new stock price data entry (or update if exists)"""
    # Check if entry already exists
    existing = (
        db.query(StockPriceData)
        .filter(StockPriceData.ticker == ticker, StockPriceData.date == date)
        .first()
    )
    
    if existing:
        # Update existing entry
        existing.open = Decimal(str(open)) if open is not None else existing.open
        existing.high = Decimal(str(high)) if high is not None else existing.high
        existing.low = Decimal(str(low)) if low is not None else existing.low
        existing.close = Decimal(str(close)) if close is not None else existing.close
        existing.volume = volume if volume is not None else existing.volume
        existing.adj_close = Decimal(str(adj_close)) if adj_close is not None else existing.adj_close
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new entry
        price_data = StockPriceData(
            ticker=ticker,
            date=date,
            open=Decimal(str(open)) if open is not None else None,
            high=Decimal(str(high)) if high is not None else None,
            low=Decimal(str(low)) if low is not None else None,
            close=Decimal(str(close)) if close is not None else None,
            volume=volume,
            adj_close=Decimal(str(adj_close)) if adj_close is not None else None
        )
        db.add(price_data)
        db.commit()
        db.refresh(price_data)
        return price_data


def get_latest_price_data(
    db: Session,
    ticker: str
) -> Optional[StockPriceData]:
    """Get the latest price data for a ticker"""
    return (
        db.query(StockPriceData)
        .filter(StockPriceData.ticker == ticker)
        .order_by(StockPriceData.date.desc())
        .first()
    )


def get_price_history(
    db: Session,
    ticker: str,
    days: int = 7
) -> List[StockPriceData]:
    """Get price history for a ticker, ordered by most recent"""
    return (
        db.query(StockPriceData)
        .filter(StockPriceData.ticker == ticker)
        .order_by(StockPriceData.date.desc())
        .limit(days)
        .all()
    )


def get_price_history_bulk(
    db: Session,
    tickers: List[str],
    days: int = 7
) -> Dict[str, List[StockPriceData]]:
    """
    Get price history for multiple tickers in bulk, returns dict mapping ticker -> List[StockPriceData]
    Optimized: queries each ticker separately with LIMIT to avoid loading all data into memory
    """
    if not tickers:
        return {}
    
    result = {}
    
    # Query each ticker separately with LIMIT for efficiency
    # This avoids loading all historical data into memory
    for ticker in tickers:
        history = (
            db.query(StockPriceData)
            .filter(StockPriceData.ticker == ticker)
            .order_by(StockPriceData.date.desc())
            .limit(days)
            .all()
        )
        result[ticker] = history
    
    return result


