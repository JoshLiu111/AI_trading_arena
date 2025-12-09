# backend/api/v1/trading.py

"""
Trading API Router
Endpoints for trading operations and strategies
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import json

from models.database import get_db
from models.crud.account_crud import get_account
from models.crud.strategy_crud import get_latest_strategy, get_strategies_by_account
from services.competition.trading_service import trading_service
from schemas import TransactionCreate

router = APIRouter(prefix="/api/v1/trading", tags=["Trading"])


@router.post("/execute")
def execute_trade(trade: TransactionCreate, db: Session = Depends(get_db)):
    """
    Execute a trade (for human player or testing)
    """
    account = get_account(db, trade.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    result = trading_service.execute_trade(
        db,
        account_id=trade.account_id,
        ticker=trade.ticker,
        action=trade.action,
        quantity=trade.quantity,
        rationale=trade.rationale
    )
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Trade failed. Check balance/positions and try again."
        )
    
    return result


@router.get("/strategy/{account_id}")
def get_current_strategy(account_id: int, db: Session = Depends(get_db)):
    """Get the latest trading strategy for an account"""
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    strategy = get_latest_strategy(db, account_id)
    if not strategy:
        return {"account_id": account_id, "strategy": None}
    
    return {
        "account_id": account_id,
        "strategy_id": strategy.id,
        "strategy_date": strategy.strategy_date.isoformat(),
        "content": json.loads(strategy.strategy_content),
        "selected_stocks": json.loads(strategy.selected_stocks) if strategy.selected_stocks else [],
        "created_at": strategy.created_at.isoformat()
    }


@router.get("/strategies/{account_id}")
def get_strategy_history(
    account_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get strategy history for an account"""
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    strategies = get_strategies_by_account(db, account_id)[:limit]
    
    return {
        "account_id": account_id,
        "strategies": [
            {
                "id": s.id,
                "date": s.strategy_date.isoformat(),
                "content": json.loads(s.strategy_content),
                "created_at": s.created_at.isoformat()
            }
            for s in strategies
        ]
    }
