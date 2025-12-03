# backend/schemas/__init__.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ============================================================
# Account Schemas
# ============================================================
class AccountBase(BaseModel):
    account_name: str
    display_name: str
    account_type: str  # human / ai


class AccountCreate(AccountBase):
    initial_balance: float = 1000000.00


class AccountResponse(AccountBase):
    id: int
    balance: float
    initial_balance: float
    total_value: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class AccountWithTransactions(AccountResponse):
    transactions: List["TransactionResponse"] = []


# ============================================================
# Stock Schemas

class StockPrice(BaseModel):
    ticker: str
    name: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    updated_at: Optional[datetime] = None


class StockPriceList(BaseModel):
    stocks: List[StockPrice]
    updated_at: datetime


# ============================================================
# Strategy Schemas
# ============================================================
class StrategyResponse(BaseModel):
    id: int
    account_id: int
    strategy_date: date
    strategy_content: str
    selected_stocks: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# Transaction Schemas
# ============================================================
class TransactionCreate(BaseModel):
    account_id: int
    ticker: str
    action: str  # BUY / SELL
    quantity: int
    # Note: price is fetched automatically from stock_service, not from user input
    rationale: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    ticker: str
    action: str
    quantity: int
    price: float
    total_amount: float
    rationale: Optional[str] = None
    executed_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# Competition Schemas
# ============================================================
class CompetitionStatus(BaseModel):
    is_running: bool
    is_paused: bool
    started_at: Optional[datetime] = None
    last_trade_at: Optional[datetime] = None
    next_trade_at: Optional[datetime] = None


class CompetitionStartResponse(BaseModel):
    success: bool
    message: str
    accounts: List[AccountResponse]


# ============================================================
# Metrics Schema (for AI)
# ============================================================
class StockMetrics(BaseModel):
    ticker: str
    current_price: float
    price_7d_ago: float
    change_7d_percent: float
    avg_volume_7d: int
    volatility_7d: float  # Standard deviation
    trend: str  # UP / DOWN / SIDEWAYS


class MetricsReport(BaseModel):
    date: date
    stocks: List[StockMetrics]


# Update forward references
AccountWithTransactions.model_rebuild()
