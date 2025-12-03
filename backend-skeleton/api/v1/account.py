# backend/api/v1/account.py

"""
Account API Router
Endpoints for account information and transactions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models.database import get_db
from models.crud.account_crud import get_account, get_all_accounts
from models.crud.transaction_crud import get_transactions_by_account
from services.competition.trading_service import trading_service
from schemas import AccountResponse, TransactionResponse

router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


@router.get("/", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    """Get all accounts with their balances"""
    accounts = get_all_accounts(db)
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
def get_account_detail(account_id: int, db: Session = Depends(get_db)):
    """Get single account details"""
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.get("/{account_id}/transactions", response_model=List[TransactionResponse])
def get_account_transactions(
    account_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get transactions for an account"""
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transactions = get_transactions_by_account(db, account_id, limit=limit)
    return transactions


@router.get("/{account_id}/positions")
def get_account_positions(account_id: int, db: Session = Depends(get_db)):
    """Get current stock positions for an account"""
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    positions = trading_service.get_positions(db, account_id)
    total_value = trading_service.calculate_total_value(db, account_id)
    
    return {
        "account_id": account_id,
        "balance": float(account.balance),
        "positions": positions,
        "total_value": total_value
    }
