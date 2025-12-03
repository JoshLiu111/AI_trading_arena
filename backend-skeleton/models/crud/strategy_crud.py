# backend/models/crud/strategy_crud.py

"""
Strategy CRUD operations
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from models.schema.strategy import TradingStrategy


def create_strategy(
    db: Session,
    account_id: int,
    strategy_date: date,
    strategy_content: str,
    selected_stocks: str
) -> TradingStrategy:
    """Create a new trading strategy"""
    strategy = TradingStrategy(
        account_id=account_id,
        strategy_date=strategy_date,
        strategy_content=strategy_content,
        selected_stocks=selected_stocks
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


def get_latest_strategy(
    db: Session,
    account_id: int
) -> Optional[TradingStrategy]:
    """Get the latest strategy for an account"""
    return (
        db.query(TradingStrategy)
        .filter(TradingStrategy.account_id == account_id)
        .order_by(TradingStrategy.created_at.desc())
        .first()
    )


def get_strategies_by_account(
    db: Session,
    account_id: int
) -> List[TradingStrategy]:
    """Get all strategies for an account, ordered by most recent"""
    return (
        db.query(TradingStrategy)
        .filter(TradingStrategy.account_id == account_id)
        .order_by(TradingStrategy.created_at.desc())
        .all()
    )

