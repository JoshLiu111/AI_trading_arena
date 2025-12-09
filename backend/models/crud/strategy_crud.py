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


def delete_strategies_by_account(
    db: Session,
    account_id: int
) -> int:
    """
    Delete all strategies for an account.
    Before deleting, sets strategy_id to NULL in all transactions that reference these strategies.
    """
    # First, get all strategy IDs for this account
    strategies = (
        db.query(TradingStrategy)
        .filter(TradingStrategy.account_id == account_id)
        .all()
    )
    
    if not strategies:
        return 0
    
    strategy_ids = [s.id for s in strategies]
    
    # Update all transactions that reference these strategies to set strategy_id = NULL
    from models.schema.transaction import Transaction
    updated_count = (
        db.query(Transaction)
        .filter(Transaction.strategy_id.in_(strategy_ids))
        .update({Transaction.strategy_id: None}, synchronize_session=False)
    )
    
    if updated_count > 0:
        print(f"   Updated {updated_count} transaction(s) to remove strategy references")
    
    # Now delete the strategies
    count = (
        db.query(TradingStrategy)
        .filter(TradingStrategy.account_id == account_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return count


