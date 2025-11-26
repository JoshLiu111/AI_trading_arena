"""
Stock-related database models.
Includes Stock and StockDailyData models.
"""
from sqlalchemy import (
    Column, String, Integer, BigInteger, Numeric, Date, Text,
    ForeignKey, Index, DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Stock(Base):
    """
    Stock model representing a company's basic information.
    """
    __tablename__ = "stocks"

    ticker = Column(String(10), primary_key=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    market_cap = Column(BigInteger)
    exchange = Column(String(50))
    currency = Column(String(10))
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    prices = relationship("StockDailyData", back_populates="stock", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Stock {self.ticker} - {self.name}>"


class StockDailyData(Base):
    """
    StockDailyData model representing daily price data for a stock.
    """
    __tablename__ = "stock_daily_data"

    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), primary_key=True)
    date = Column(Date, primary_key=True)

    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    volume = Column(BigInteger)

    data_source = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="prices")

    __table_args__ = (
        Index("idx_daily_date_ticker", "date", "ticker"),
        Index("idx_daily_ticker", "ticker"),
    )

    def __repr__(self):
        return f"<StockDailyData {self.ticker} {self.date}>"

