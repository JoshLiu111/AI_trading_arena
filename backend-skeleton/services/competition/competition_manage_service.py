# backend/services/competition/competition_manage_service.py

"""
Competition Manage Service - Manage competition state and auto-trading
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from config import settings
from models.crud.account_crud import (
    create_account, get_all_accounts, update_account
)
from models.crud.transaction_crud import get_transactions_by_account
from models.crud.strategy_crud import create_strategy, get_latest_strategy
from services.datasource.refresh_historical_data_service import refresh_historical_data_service
from services.competition.generate_metrics_service import metrics_service
from services.competition.ai_strategy_report_service import ai_service
from services.competition.trading_service import trading_service


class CompetitionState:
    """Global competition state"""
    is_running: bool = False
    is_paused: bool = False
    started_at: Optional[datetime] = None
    last_trade_at: Optional[datetime] = None


class CompetitionService:
    def __init__(self):
        self.state = CompetitionState()
        self.ai_accounts = ["gpt_trader", "deepseek_trader", "gemini_trader", "grok_trader"]
    
    async def start_competition(self, db: Session) -> Dict:
        """
        Start a new competition:
        1. Reset all accounts
        2. Clear transactions
        3. Refresh stock data
        4. Generate AI strategies
        """
        # 1. Reset accounts (create if not exist)
        accounts = []
        
        # Human account
        human = self._reset_or_create_account(db, "human_player", "Human Player", "human")
        accounts.append(human)
        
        # AI accounts
        for ai_name in self.ai_accounts:
            display = ai_name.replace("_", " ").title()
            ai_acc = self._reset_or_create_account(db, ai_name, display, "ai")
            accounts.append(ai_acc)
        
        db.commit()
        
        # 2. Refresh stock historical data
        refresh_historical_data_service.refresh_historical_data(db, days=settings.HISTORY_DAYS)
        
        # 3. Calculate metrics
        metrics = metrics_service.calculate_metrics(db, days=settings.HISTORY_DAYS)
        metrics_text = metrics_service.format_for_ai(metrics)
        
        # 4. Generate AI strategies
        for acc in accounts:
            if acc.account_type == "ai":
                strategy = await ai_service.generate_strategy(
                    account_name=acc.account_name,
                    balance=float(acc.balance),
                    metrics_text=metrics_text
                )
                
                # Save strategy
                create_strategy(
                    db,
                    account_id=acc.id,
                    strategy_date=date.today(),
                    strategy_content=json.dumps(strategy),
                    selected_stocks=json.dumps(strategy.get("selected_stocks", []))
                )
        
        db.commit()
        
        # Update state
        self.state.is_running = True
        self.state.is_paused = False
        self.state.started_at = datetime.now()
        
        return {
            "success": True,
            "message": "Competition started",
            "accounts": [self._account_to_dict(a) for a in accounts]
        }
    
    def pause_competition(self) -> Dict:
        """Pause auto-trading"""
        if not self.state.is_running:
            return {"success": False, "message": "Competition not running"}
        
        self.state.is_paused = True
        return {"success": True, "message": "Competition paused"}
    
    def resume_competition(self) -> Dict:
        """Resume auto-trading"""
        if not self.state.is_running:
            return {"success": False, "message": "Competition not running"}
        
        self.state.is_paused = False
        return {"success": True, "message": "Competition resumed"}
    
    def get_status(self) -> Dict:
        """Get current competition status"""
        return {
            "is_running": self.state.is_running,
            "is_paused": self.state.is_paused,
            "started_at": self.state.started_at.isoformat() if self.state.started_at else None,
            "last_trade_at": self.state.last_trade_at.isoformat() if self.state.last_trade_at else None
        }
    
    async def execute_ai_trades(self, db: Session) -> List[Dict]:
        """Execute trades for all AI accounts based on their strategies"""
        if not self.state.is_running or self.state.is_paused:
            return []
        
        trades_executed = []
        accounts = get_all_accounts(db)
        
        for acc in accounts:
            if acc.account_type != "ai":
                continue
            
            # Get latest strategy
            strategy = get_latest_strategy(db, acc.id)
            if not strategy:
                continue
            
            try:
                strategy_data = json.loads(strategy.strategy_content)
                actions = strategy_data.get("actions", [])
                
                for action in actions:
                    result = trading_service.execute_trade(
                        db,
                        account_id=acc.id,
                        ticker=action["ticker"],
                        action=action["action"],
                        quantity=action["quantity"],
                        rationale=action.get("rationale"),
                        strategy_id=strategy.id
                    )
                    
                    if result:
                        trades_executed.append(result)
                        
            except Exception as e:
                print(f"Error executing trades for {acc.account_name}: {e}")
        
        self.state.last_trade_at = datetime.now()
        return trades_executed
    
    def _reset_or_create_account(
        self, db: Session, name: str, display: str, acc_type: str
    ):
        """Reset existing account or create new one"""
        from models.schema.account import Account
        
        existing = db.query(Account).filter_by(account_name=name).first()
        
        if existing:
            # Reset balance
            existing.balance = Decimal(str(settings.DEFAULT_BALANCE))
            existing.initial_balance = Decimal(str(settings.DEFAULT_BALANCE))
            existing.total_value = Decimal(str(settings.DEFAULT_BALANCE))
            
            # Clear transactions
            for tx in existing.transactions:
                db.delete(tx)
            
            # Clear strategies
            for st in existing.strategies:
                db.delete(st)
            
            return existing
        else:
            return create_account(
                db,
                account_name=name,
                display_name=display,
                account_type=acc_type,
                initial_balance=Decimal(str(settings.DEFAULT_BALANCE))
            )
    
    def _account_to_dict(self, acc) -> Dict:
        return {
            "id": acc.id,
            "account_name": acc.account_name,
            "display_name": acc.display_name,
            "account_type": acc.account_type,
            "balance": float(acc.balance),
            "total_value": float(acc.total_value)
        }


# Singleton instance
competition_service = CompetitionService()
