# backend/models/crud/transaction_crud.py

"""
Transaction CRUD operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from models.schema.transaction import Transaction


def create_transaction(
    db: Session,
    account_id: int,
    ticker: str,
    action: str,
    quantity: int,
    price: float,
    rationale: Optional[str] = None,
    strategy_id: Optional[int] = None
) -> Transaction:
    """Create a new transaction"""
    from decimal import Decimal
    
    total_amount = Decimal(str(price * quantity))
    
    transaction = Transaction(
        account_id=account_id,
        ticker=ticker,
        action=action.upper(),
        quantity=quantity,
        price=Decimal(str(price)),
        total_amount=total_amount,
        rationale=rationale,
        strategy_id=strategy_id
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transactions_by_account(
    db: Session,
    account_id: int,
    limit: int = 50
) -> List[Transaction]:
    """Get transactions for an account, ordered by most recent"""
    return (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .order_by(Transaction.executed_at.desc())
        .limit(limit)
        .all()
    )


