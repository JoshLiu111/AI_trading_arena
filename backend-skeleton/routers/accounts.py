"""
Account API endpoints.
Provides CRUD operations for accounts, holdings, and transactions.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from models.deps import get_db
from models.account_models import Account, Holding, Transaction

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


# Request/Response Models
class AccountCreate(BaseModel):
    account_name: str
    display_name: str
    account_type: str  # 'human' or 'ai'
    initial_balance: float = 1000000.0
    model_name: str = None


class AccountResponse(BaseModel):
    id: int
    account_name: str
    display_name: str
    account_type: str
    balance: float
    total_value: float = None
    model_name: str = None

    class Config:
        from_attributes = True


# -----------------------------------------------------
# Account Endpoints
# -----------------------------------------------------

@router.get("/", response_model=List[AccountResponse])
def get_all_accounts(db: Session = Depends(get_db)):
    """
    Get all accounts.
    Returns a list of all accounts in the system.
    """
    accounts = db.query(Account).all()
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """
    Get account by ID.
    Returns account details or 404 if not found.
    """
    account = db.query(Account).filter_by(id=account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/", response_model=AccountResponse)
def create_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    """
    Create a new account.
    Creates an account with the specified initial balance.
    """
    # Check if account name already exists
    existing = db.query(Account).filter_by(account_name=account_data.account_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account name already exists")

    # Create new account
    account = Account(
        account_name=account_data.account_name,
        display_name=account_data.display_name,
        account_type=account_data.account_type,
        balance=account_data.initial_balance,
        initial_balance=account_data.initial_balance,
        total_value=account_data.initial_balance,
        model_name=account_data.model_name,
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


# -----------------------------------------------------
# Holdings Endpoints
# -----------------------------------------------------

@router.get("/{account_id}/holdings")
def get_account_holdings(account_id: int, db: Session = Depends(get_db)):
    """
    Get all holdings for an account.
    Returns a list of all stock positions for the account.
    """
    account = db.query(Account).filter_by(id=account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    holdings = db.query(Holding).filter(
        Holding.account_id == account_id,
        Holding.quantity > 0
    ).all()

    result = []
    for h in holdings:
        result.append({
            "ticker": h.ticker,
            "quantity": h.quantity,
            "avg_cost": float(h.avg_cost) if h.avg_cost else None,
            "current_price": float(h.current_price) if h.current_price else None,
            "market_value": float(h.market_value) if h.market_value else None,
        })

    return result


# -----------------------------------------------------
# Transactions Endpoints
# -----------------------------------------------------

@router.get("/{account_id}/transactions")
def get_account_transactions(account_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Get transaction history for an account.
    Returns the most recent transactions, limited by the limit parameter.
    """
    account = db.query(Account).filter_by(id=account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .order_by(Transaction.executed_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for tx in transactions:
        result.append({
            "id": tx.id,
            "ticker": tx.ticker,
            "action": tx.action,
            "quantity": tx.quantity,
            "price": float(tx.price),
            "total_amount": float(tx.total_amount),
            "rationale": tx.rationale,
            "executed_at": tx.executed_at.isoformat() if tx.executed_at else None,
        })

    return result

