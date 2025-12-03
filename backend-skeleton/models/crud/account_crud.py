# backend/models/crud/account_crud.py

"""
Account CRUD operations
"""

from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from models.schema.account import Account


def get_account(db: Session, account_id: int) -> Optional[Account]:
    """Get account by ID"""
    return db.query(Account).filter(Account.id == account_id).first()


def get_all_accounts(db: Session) -> List[Account]:
    """Get all accounts"""
    return db.query(Account).all()


def create_account(
    db: Session,
    account_name: str,
    display_name: str,
    account_type: str,
    initial_balance: Decimal
) -> Account:
    """Create a new account"""
    account = Account(
        account_name=account_name,
        display_name=display_name,
        account_type=account_type,
        balance=initial_balance,
        initial_balance=initial_balance,
        total_value=initial_balance
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_account(
    db: Session,
    account_id: int,
    balance: Optional[Decimal] = None,
    total_value: Optional[Decimal] = None
) -> Optional[Account]:
    """Update account balance or total value"""
    account = get_account(db, account_id)
    if not account:
        return None
    
    if balance is not None:
        account.balance = balance
    if total_value is not None:
        account.total_value = total_value
    
    db.commit()
    db.refresh(account)
    return account

