# backend/api/v1/competition.py

"""
Competition API Router
Endpoints for competition control
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional

from models.database import get_db
from services.competition.competition_manage_service import competition_service
from services.competition.generate_metrics_service import metrics_service
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/competition", tags=["Competition"])


@router.post("/start")
async def start_competition(db: Session = Depends(get_db)):
    """
    Start a new competition (full reset):
    - Reset all accounts to initial balance
    - Clear all transactions
    - Refresh 7-day stock data from Polygon.io
    - Generate AI trading strategies
    - Set is_running = True
    """
    result = await competition_service.start_competition(db)
    return result


@router.post("/generate-strategy")
async def generate_strategy(
    account_id: Optional[int] = Query(None, description="Optional account ID to generate strategy for"),
    db: Session = Depends(get_db)
):
    """
    Generate AI strategy only (without resetting accounts or refreshing data):
    - Calculate metrics from existing stock data
    - Generate AI trading strategies
    """
    from fastapi import HTTPException
    
    try:
        result = await competition_service.generate_strategy_only(db, account_id)
    
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "not found" in result.get("message", "").lower() else 400,
                detail=result.get("message", "Failed to generate strategy")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in generate_strategy endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/regenerate-strategy")
async def regenerate_strategy(
    account_id: Optional[int] = Query(None, description="Optional account ID to regenerate strategy for"),
    db: Session = Depends(get_db)
):
    """
    Delete existing strategies and regenerate new ones:
    - Delete all strategies for AI accounts
    - Generate new AI strategies
    """
    from fastapi import HTTPException
    
    try:
        result = await competition_service.regenerate_strategy(db, account_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "not found" in result.get("message", "").lower() else 400,
                detail=result.get("message", "Failed to regenerate strategy")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in regenerate_strategy endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/pause")
def pause_competition():
    """Pause auto-trading (AI will not execute trades)"""
    return competition_service.pause_competition()


@router.post("/resume")
def resume_competition():
    """Resume auto-trading"""
    return competition_service.resume_competition()


@router.post("/stop")
def stop_competition():
    """Stop the competition (set is_running = False)"""
    return competition_service.stop_competition()


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
