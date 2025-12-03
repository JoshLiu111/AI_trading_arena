# backend/models/crud/stock_crud.py

"""
Stock CRUD operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from models.schema.stock import Stock


def get_stock(db: Session, ticker: str) -> Optional[Stock]:
    """Get stock by ticker"""
    return db.query(Stock).filter(Stock.ticker == ticker).first()


def get_all_stocks(db: Session) -> List[Stock]:
    """Get all stocks"""
    return db.query(Stock).all()


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

