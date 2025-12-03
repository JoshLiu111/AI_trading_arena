# backend/models/schema/account.py

"""
Account SQLAlchemy Model
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from decimal import Decimal

from models.database import Base


class Account(Base):
    """Account model for trading accounts"""
    
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)  # "human" or "ai"
    balance = Column(Numeric(15, 2), nullable=False, default=0)
    initial_balance = Column(Numeric(15, 2), nullable=False, default=0)
    total_value = Column(Numeric(15, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Account(id={self.id}, name={self.account_name}, balance={self.balance})>"

