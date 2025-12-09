# backend/models/schema/transaction.py

"""
Transaction SQLAlchemy Model
"""

from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from decimal import Decimal
from models.database import Base


class Transaction(Base):
    """Transaction model for trading records"""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    ticker = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # "BUY" or "SELL"
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(15, 4), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    rationale = Column(Text, nullable=True)
    strategy_id = Column(Integer, ForeignKey("trading_strategies.id"), nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, account_id={self.account_id}, ticker={self.ticker}, action={self.action})>"
