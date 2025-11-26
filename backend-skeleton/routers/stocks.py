"""
Stock API endpoints.
Provides CRUD operations for stocks and price data.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from models.deps import get_db
from models.stock_models import Stock, StockDailyData

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])


# Request/Response Models
class StockCreate(BaseModel):
    ticker: str
    name: str
    sector: str = None
    market_cap: int = None
    exchange: str = None
    currency: str = "USD"
    description: str = None


class StockResponse(BaseModel):
    ticker: str
    name: str
    sector: str = None
    market_cap: int = None
    exchange: str = None
    currency: str = None
    description: str = None

    class Config:
        from_attributes = True


# -----------------------------------------------------
# Stock Endpoints
# -----------------------------------------------------

@router.get("/", response_model=List[StockResponse])
def get_all_stocks(db: Session = Depends(get_db)):
    """
    Get all stocks.
    Returns a list of all stocks in the system.
    """
    stocks = db.query(Stock).all()
    return stocks


@router.get("/{ticker}", response_model=StockResponse)
def get_stock(ticker: str, db: Session = Depends(get_db)):
    """
    Get stock by ticker symbol.
    Returns stock details or 404 if not found.
    """
    stock = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")
    return stock


@router.post("/", response_model=StockResponse)
def create_stock(stock_data: StockCreate, db: Session = Depends(get_db)):
    """
    Create a new stock.
    Creates a stock record with the provided information.
    """
    # Check if stock already exists
    existing = db.query(Stock).filter(Stock.ticker == stock_data.ticker.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stock already exists")

    # Create new stock
    stock = Stock(
        ticker=stock_data.ticker.upper(),
        name=stock_data.name,
        sector=stock_data.sector,
        market_cap=stock_data.market_cap,
        exchange=stock_data.exchange,
        currency=stock_data.currency,
        description=stock_data.description,
    )
    
    db.add(stock)
    db.commit()
    db.refresh(stock)
    
    return stock


# -----------------------------------------------------
# Price History Endpoints
# -----------------------------------------------------

@router.get("/{ticker}/history")
def get_stock_history(
    ticker: str,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get stock price history.
    Returns the most recent price data, limited by the limit parameter.
    """
    stock = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")

    history = (
        db.query(StockDailyData)
        .filter(StockDailyData.ticker == ticker.upper())
        .order_by(StockDailyData.date.desc())
        .limit(limit)
        .all()
    )

    result = []
    for h in history:
        result.append({
            "date": str(h.date),
            "open": float(h.open) if h.open else None,
            "high": float(h.high) if h.high else None,
            "low": float(h.low) if h.low else None,
            "close": float(h.close) if h.close else None,
            "volume": int(h.volume) if h.volume else None,
        })

    # Reverse to show oldest first
    result.reverse()
    return result

