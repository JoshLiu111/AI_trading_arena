# backend/api/v1/competition.py

"""
Competition API Router
Endpoints for competition control
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from models.database import get_db
from services.competition.competition_manage_service import competition_service
from services.competition.generate_metrics_service import metrics_service

router = APIRouter(prefix="/api/v1/competition", tags=["Competition"])


@router.post("/start")
async def start_competition(db: Session = Depends(get_db)):
    """
    Start a new competition:
    - Reset all accounts to initial balance
    - Clear all transactions
    - Refresh 7-day stock data from yfinance
    - Generate AI trading strategies
    """
    result = await competition_service.start_competition(db)
    return result


@router.post("/pause")
def pause_competition():
    """Pause auto-trading (AI will not execute trades)"""
    return competition_service.pause_competition()


@router.post("/resume")
def resume_competition():
    """Resume auto-trading"""
    return competition_service.resume_competition()


@router.get("/status")
def get_competition_status():
    """Get current competition status"""
    return competition_service.get_status()


@router.get("/metrics")
def get_current_metrics(db: Session = Depends(get_db)):
    """Get current stock metrics (used for AI analysis)"""
    metrics = metrics_service.calculate_metrics(db)
    return {
        "metrics": metrics,
        "formatted": metrics_service.format_for_ai(metrics)
    }


@router.post("/execute-trades")
async def execute_ai_trades(db: Session = Depends(get_db)):
    """
    Manually trigger AI trades (for testing)
    In production, this runs automatically every 10 minutes
    """
    trades = await competition_service.execute_ai_trades(db)
    return {
        "trades_executed": len(trades),
        "trades": trades
    }
