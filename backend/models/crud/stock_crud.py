# backend/models/crud/stock_crud.py

"""
Stock CRUD operations
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from models.schema.stock import Stock


def get_stock(db: Session, ticker: str) -> Optional[Stock]:
    """Get stock by ticker"""
    return db.query(Stock).filter(Stock.ticker == ticker).first()


def get_all_stocks(db: Session) -> List[Stock]:
    """Get all stocks"""
    return db.query(Stock).all()


def get_stocks_by_tickers(db: Session, tickers: List[str]) -> Dict[str, Stock]:
    """Get stocks by tickers in bulk, returns dict mapping ticker -> Stock"""
    stocks = db.query(Stock).filter(Stock.ticker.in_(tickers)).all()
    return {stock.ticker: stock for stock in stocks}


def create_stock(
    db: Session,
    ticker: str,
    name: str,
    sector: str = "",
    description: str = "",
    homepage_url: str = "",
    sic_description: str = ""
) -> Stock:
    """Create a new stock"""
    stock = Stock(
        ticker=ticker,
        name=name,
        sector=sector,
        description=description,
        homepage_url=homepage_url,
        sic_description=sic_description
    )
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


def update_stock(
    db: Session,
    ticker: str,
    name: Optional[str] = None,
    sector: Optional[str] = None,
    description: Optional[str] = None,
    homepage_url: Optional[str] = None,
    sic_description: Optional[str] = None
) -> Optional[Stock]:
    """Update an existing stock"""
    stock = get_stock(db, ticker)
    if not stock:
        return None
    
    if name is not None:
        stock.name = name
    if sector is not None:
        stock.sector = sector
    if description is not None:
        stock.description = description
    if homepage_url is not None:
        stock.homepage_url = homepage_url
    if sic_description is not None:
        stock.sic_description = sic_description
    
    db.commit()
    db.refresh(stock)
    return stock


