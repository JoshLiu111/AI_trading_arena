# backend/services/competition/trading_service.py

"""
Trading Service - Execute trades and manage positions
"""

from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from models.crud.account_crud import get_account, update_account
from models.crud.transaction_crud import (
    create_transaction, get_transactions_by_account
)
from services.datasource.yahoo_realtime_price_service import stock_price_service
from schemas import TransactionResponse


class TradingService:
    def execute_trade(
        self,
        db: Session,
        account_id: int,
        ticker: str,
        action: str,
        quantity: int,
        rationale: str = None,
        strategy_id: int = None
    ) -> Optional[Dict]:
        """
        Execute a trade (BUY or SELL)
        
        Returns transaction dict or None if failed
        """
        account = get_account(db, account_id)
        if not account:
            return None
        
        # Get current price
        price = stock_price_service.get_current_price(ticker)
        if not price:
            return None
        
        total_amount = price * quantity
        
        if action.upper() == "BUY":
            # Check balance
            if float(account.balance) < total_amount:
                return None
            
            # Update balance
            new_balance = float(account.balance) - total_amount
            update_account(db, account_id, balance=Decimal(str(new_balance)))
            
        elif action.upper() == "SELL":
            # Check if has enough shares (simplified - just check transactions)
            positions = self.get_positions(db, account_id)
            if ticker not in positions or positions[ticker]["quantity"] < quantity:
                return None
            
            # Update balance
            new_balance = float(account.balance) + total_amount
            update_account(db, account_id, balance=Decimal(str(new_balance)))
        else:
            return None
        
        # Create transaction
        transaction = create_transaction(
            db,
            account_id=account_id,
            ticker=ticker,
            action=action.upper(),
            quantity=quantity,
            price=price,
            rationale=rationale,
            strategy_id=strategy_id
        )
        
        db.commit()
        
        # Convert to dict using Pydantic schema
        if transaction:
            return TransactionResponse.model_validate(transaction).model_dump()
        return None
    
    def get_positions(self, db: Session, account_id: int) -> Dict[str, Dict]:
        """
        Calculate current positions from transactions
        
        Returns: {ticker: {"quantity": int, "avg_price": float, "total_cost": float}}
        """
        transactions = get_transactions_by_account(db, account_id)
        positions = {}
        
        for tx in transactions:
            ticker = tx.ticker
            if ticker not in positions:
                positions[ticker] = {"quantity": 0, "total_cost": 0.0}
            
            if tx.action == "BUY":
                positions[ticker]["quantity"] += tx.quantity
                positions[ticker]["total_cost"] += float(tx.total_amount)
            elif tx.action == "SELL":
                positions[ticker]["quantity"] -= tx.quantity
                positions[ticker]["total_cost"] -= float(tx.total_amount)
        
        # Calculate average price and filter zero positions
        result = {}
        for ticker, data in positions.items():
            if data["quantity"] > 0:
                result[ticker] = {
                    "quantity": data["quantity"],
                    "total_cost": data["total_cost"],
                    "avg_price": round(data["total_cost"] / data["quantity"], 2)
                }
        
        return result
    
    def calculate_total_value(self, db: Session, account_id: int) -> float:
        """Calculate total portfolio value (balance + positions)"""
        account = get_account(db, account_id)
        if not account:
            return 0.0
        
        total = float(account.balance)
        positions = self.get_positions(db, account_id)
        
        for ticker, data in positions.items():
            price = stock_price_service.get_current_price(ticker)
            if price:
                total += price * data["quantity"]
        
        # Update account total_value
        update_account(db, account_id, total_value=Decimal(str(total)))
        db.commit()
        
        return total


# Singleton instance
trading_service = TradingService()
