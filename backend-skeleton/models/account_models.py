"""
Account-related database models.
Includes Account, Holding, and Transaction models.
"""
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, Text, DateTime,
    ForeignKey, UniqueConstraint, Index, BigInteger
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Account(Base):
    """
    Account model representing a trading account.
    Can be either 'human' or 'ai' type.
    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100))
    account_type = Column(String(10))  # 'human' or 'ai'

    balance = Column(Numeric(15, 2), default=0)
    initial_balance = Column(Numeric(15, 2))
    total_value = Column(Numeric(15, 2))

    model_name = Column(String(50))  # For AI accounts
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    holdings = relationship("Holding", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="account")

    def __repr__(self):
        return f"<Account {self.account_name}>"


class Holding(Base):
    """
    Holding model representing a stock position in an account.
    """
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"))
    ticker = Column(String(10), ForeignKey("stocks.ticker"))

    quantity = Column(Integer, nullable=False)
    avg_cost = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2))
    market_value = Column(Numeric(15, 2))

    first_bought_at = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("account_id", "ticker", name="uix_account_ticker"),
        Index("idx_holdings_account_id", "account_id"),
        Index("idx_holdings_ticker", "ticker"),
    )

    account = relationship("Account", back_populates="holdings")

    def __repr__(self):
        return f"<Holding {self.account_id} - {self.ticker}>"


class Transaction(Base):
    """
    Transaction model representing a buy or sell trade.
    """
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    ticker = Column(String(10), ForeignKey("stocks.ticker"))

    action = Column(String(10), nullable=False)  # 'BUY' or 'SELL'
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)

    rationale = Column(Text, nullable=False)

    executed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="transactions")

    __table_args__ = (
        Index("idx_tx_account_id", "account_id"),
        Index("idx_tx_ticker", "ticker"),
        Index("idx_tx_time", "executed_at"),
    )

    def __repr__(self):
        return f"<Transaction {self.action} {self.ticker} {self.quantity}>"

