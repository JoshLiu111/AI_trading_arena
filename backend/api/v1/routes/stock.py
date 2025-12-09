# backend/api/v1/stock.py

"""
Stock API Router
Endpoints for stock prices and data
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models.database import get_db, SessionLocal
from models.crud.stock_price_crud import get_price_history
from services.datasource.stock_price_service import stock_price_service
from config import settings

router = APIRouter(prefix="/api/v1/stocks", tags=["Stocks"])


def _create_missing_stocks_background(missing_tickers: List[str]):
    """Background task to create missing stocks without blocking the request"""
    from models.crud.stock_crud import get_stocks_by_tickers, create_stock
    from services.datasource.data_source_factory import data_source_factory
    
    db = SessionLocal()
    try:
        # Check again which stocks are still missing (may have been created by another request)
        existing_stocks = get_stocks_by_tickers(db, missing_tickers)
        still_missing = [ticker for ticker in missing_tickers if ticker not in existing_stocks]
        
        if still_missing:
            import time
            info_service = data_source_factory.get_info_service()
            for i, ticker in enumerate(still_missing):
                if i > 0:  # Don't delay before first request
                    time.sleep(3)  # Wait 3 seconds between requests to avoid rate limiting
                try:
                    info = info_service.get_company_info(ticker)
                    if info:
                        create_stock(db, **info)
                except Exception:
                    # Log error but don't fail the background task
                    pass
            db.commit()
    finally:
        db.close()


def _update_stock_info_background(tickers: List[str]):
    """Background task to update stock company info for existing stocks that lack it"""
    from models.crud.stock_crud import get_stocks_by_tickers
    from services.datasource.data_source_factory import data_source_factory
    
    db = SessionLocal()
    try:
        stocks = get_stocks_by_tickers(db, tickers)
        
        import time
        info_service = data_source_factory.get_info_service()
        for i, (ticker, stock) in enumerate(stocks.items()):
            # Check if stock needs company info
            if not stock.sector or not stock.sic_description or not stock.homepage_url:
                if i > 0:  # Don't delay before first request
                    time.sleep(3)  # Wait 3 seconds between requests to avoid rate limiting
                try:
                    info = info_service.get_company_info(ticker)
                    if info:
                        # Update only missing fields
                        if not stock.sector and info.get("sector"):
                            stock.sector = info["sector"]
                        if not stock.sic_description and info.get("sic_description"):
                            stock.sic_description = info["sic_description"]
                        if not stock.homepage_url and info.get("homepage_url"):
                            stock.homepage_url = info["homepage_url"]
                        if not stock.description and info.get("description"):
                            stock.description = info["description"]
                except Exception:
                    # Log error but don't fail the background task
                    pass
        
        db.commit()
    finally:
        db.close()


@router.get("/prices")
def get_realtime_prices(
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks
):
    """
    Get real-time prices for all 10 stocks in the pool
    Returns current price, volume, timestamp, name, description, and previous_close
    """
    prices = stock_price_service.get_realtime_prices(db)
    
    # Import CRUD functions and services
    from models.crud.stock_crud import get_stocks_by_tickers
    from models.crud.stock_price_crud import get_price_history_bulk
    
    # Optimize N+1 queries: bulk fetch all stock records
    tickers = [price_data["ticker"] for price_data in prices]
    stocks_dict = get_stocks_by_tickers(db, tickers)
    
    # Bulk fetch historical data for all tickers (only 2 days needed for previous_close)
    history_dict = get_price_history_bulk(db, tickers, days=2)
    
    # Identify missing stocks and schedule background task to create them
    # Don't block the request waiting for external API calls
    missing_tickers = [ticker for ticker in tickers if ticker not in stocks_dict]
    if missing_tickers:
        background_tasks.add_task(_create_missing_stocks_background, missing_tickers)
    
    # Identify stocks that exist but lack company info (sector, industry, homepage_url)
    # These will be updated in background
    stocks_needing_info = []
    for ticker in tickers:
        stock = stocks_dict.get(ticker)
        if stock and (not stock.sector or not stock.sic_description or not stock.homepage_url):
            stocks_needing_info.append(ticker)
    
    if stocks_needing_info:
        background_tasks.add_task(_update_stock_info_background, stocks_needing_info)
    
    # Build enriched stock data (return immediately even if stock info is missing)
    enriched_stocks = []
    for price_data in prices:
        ticker = price_data["ticker"]
        stock = stocks_dict.get(ticker)
        
        # Get previous_close from bulk-fetched history
        history = history_dict.get(ticker, [])
        previous_close = None
        if len(history) >= 2:
            # Second most recent record is previous trading day
            previous_close = float(history[1].close) if history[1].close else None
        elif len(history) == 1:
            # If only one record, use it as previous_close
            previous_close = float(history[0].close) if history[0].close else None
        
        # Ensure updated_at is ISO format string
        updated_at = price_data.get("updated_at")
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()
        elif updated_at is None:
            updated_at = datetime.now().isoformat()
        
        # Build enriched stock data
        # Use ticker as name if stock info is not available yet
        current_price = price_data.get("price")
        enriched_stock = {
            "ticker": ticker,
            "name": stock.name if stock else ticker,
            "price": current_price,  # Keep for backward compatibility
            "current_price": current_price,  # Add explicit current_price field
            "previous_close": previous_close,
            "open": price_data.get("open"),
            "high": price_data.get("high"),
            "low": price_data.get("low"),
            "volume": price_data.get("volume"),
            "updated_at": updated_at,
        }
        
        # Log if price is missing for debugging
        if current_price is None:
            logger.warning(f"Ticker {ticker}: current_price is None. price_data keys: {list(price_data.keys()) if price_data else 'None'}")
        
        # Add company info - return all fields, let frontend decide what to display
        if stock:
            # Always include these fields, even if empty (frontend will handle empty values)
            enriched_stock["description"] = stock.description if stock.description else None
            enriched_stock["sector"] = stock.sector if stock.sector else None
            enriched_stock["industry"] = stock.sic_description if stock.sic_description else None
            enriched_stock["homepage_url"] = stock.homepage_url if stock.homepage_url else None
            enriched_stock["website"] = stock.homepage_url if stock.homepage_url else None  # Alias for frontend convenience
        else:
            # If stock doesn't exist yet, set all company info fields to None
            enriched_stock["description"] = None
            enriched_stock["sector"] = None
            enriched_stock["industry"] = None
            enriched_stock["homepage_url"] = None
            enriched_stock["website"] = None
        
        enriched_stocks.append(enriched_stock)
    
    return {
        "stocks": enriched_stocks,
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
def get_single_price(ticker: str, db: Session = Depends(get_db)):
    """Get current price for a single stock"""
    ticker = ticker.upper()
    if ticker not in settings.STOCK_POOL:
        return {"error": "Stock not in pool", "ticker": ticker}
    
    price = stock_price_service.get_current_price(ticker, db=db)
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
