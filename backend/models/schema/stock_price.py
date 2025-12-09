# backend/models/schema/stock_price.py

"""
Stock Price SQLAlchemy Model
"""

from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Index
from sqlalchemy.sql import func
from decimal import Decimal
from models.database import Base


class StockPrice(Base):
    """Stock Price model for historical price data"""
    
    __tablename__ = "stock_price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(15, 4), nullable=True)
    high = Column(Numeric(15, 4), nullable=True)
    low = Column(Numeric(15, 4), nullable=True)
    close = Column(Numeric(15, 4), nullable=True)
    volume = Column(Integer, nullable=True)
    adj_close = Column(Numeric(15, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_ticker_date', 'ticker', 'date'),
    )
    
    def __repr__(self):
        return f"<StockPrice(ticker={self.ticker}, date={self.date}, close={self.close})>"


# Alias for backward compatibility with CRUD
StockPriceData = StockPrice
