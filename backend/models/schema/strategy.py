# backend/models/schema/strategy.py

"""
Trading Strategy SQLAlchemy Model
"""

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.database import Base


class TradingStrategy(Base):
    """Trading Strategy model for AI-generated strategies"""
    
    __tablename__ = "trading_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    strategy_date = Column(Date, nullable=False)
    strategy_content = Column(Text, nullable=False)  # JSON string with strategy details
    selected_stocks = Column(String, nullable=False)  # Comma-separated stock list
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TradingStrategy(id={self.id}, account_id={self.account_id}, date={self.strategy_date})>"
