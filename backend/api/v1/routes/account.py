# backend/api/v1/account.py

"""
Account API Router
Endpoints for account information and transactions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Set

from models.database import get_db
from models.crud.account_crud import get_account, get_all_accounts
from models.crud.transaction_crud import get_transactions_by_account
from services.competition.trading_service import trading_service
from services.datasource.yahoo_realtime_price_service import stock_price_service
from schemas import AccountResponse, TransactionResponse

router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


@router.get("/", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    """Get all accounts with their balances and updated total_value"""
    accounts = get_all_accounts(db)
    
    # Optimize N+1 queries: collect all unique tickers from all accounts' positions
    all_tickers: Set[str] = set()
    account_positions_map = {}
    
    for account in accounts:
        positions = trading_service.get_positions(db, account.id)
        account_positions_map[account.id] = positions
        all_tickers.update(positions.keys())
    
    # Bulk fetch all prices once
    prices = stock_price_service.get_current_prices_bulk(list(all_tickers), db=db) if all_tickers else {}
    
    # Calculate and update total_value for each account using pre-fetched prices
    for account in accounts:
        account_prices = {ticker: prices.get(ticker) for ticker in account_positions_map.get(account.id, {}).keys()}
        trading_service.calculate_total_value(db, account.id, pre_fetched_prices=account_prices)
        # Refresh the account object to get updated total_value
        db.refresh(account)
    
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
def get_account_detail(account_id: int, db: Session = Depends(get_db)):
    """Get single account details with updated total_value"""
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Calculate and update total_value to ensure AccountDetail displays correct values
    trading_service.calculate_total_value(db, account_id)
    db.refresh(account)
    
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
    
    # Optimize N+1 queries: bulk fetch all prices at once
    tickers = list(positions.keys())
    prices = stock_price_service.get_current_prices_bulk(tickers, db=db) if tickers else {}
    
    # Add current_price for each position
    for ticker in positions:
        positions[ticker]["current_price"] = prices.get(ticker)
    
    # Calculate total_value using pre-fetched prices
    total_value = trading_service.calculate_total_value(db, account_id, pre_fetched_prices=prices)
    
    return {
        "account_id": account_id,
        "balance": float(account.balance),
        "positions": positions,
        "total_value": total_value
    }
