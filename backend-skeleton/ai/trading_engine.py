"""
Trading engine for executing AI trading decisions.
Handles trade execution, account updates, and holding management.
"""
from decimal import Decimal
from typing import Dict, Optional
from sqlalchemy.orm import Session

from models.account_models import Account, Holding, Transaction
from models.stock_models import StockDailyData


class TradingEngine:
    """
    Trading engine for executing trades and managing account state.
    """

    def __init__(self):
        """Initialize trading engine."""
        pass

    def execute_trade(
        self,
        session: Session,
        account_id: int,
        action: str,
        ticker: str,
        quantity: int,
        price: Decimal,
        rationale: str,
        market_data: Optional[Dict[str, float]] = None
    ) -> Transaction:
        """
        Execute a trade (BUY or SELL) and update account/holdings.
        
        Args:
            session: Database session
            account_id: Account ID
            action: 'BUY' or 'SELL'
            ticker: Stock ticker symbol
            quantity: Number of shares
            price: Price per share
            rationale: Trading rationale
            market_data: Optional dict of {ticker: current_price} for updating holdings
            
        Returns:
            Created Transaction object
            
        Raises:
            ValueError: If trade cannot be executed (insufficient funds/holdings)
        """
        # Get account
        account = session.query(Account).filter_by(id=account_id).first()
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Calculate total amount
        total_amount = Decimal(str(price)) * quantity

        # Validate trade
        if action.upper() == "BUY":
            if account.balance < total_amount:
                raise ValueError(f"Insufficient balance. Required: ${total_amount}, Available: ${account.balance}")
        elif action.upper() == "SELL":
            holding = session.query(Holding).filter_by(
                account_id=account_id,
                ticker=ticker.upper()
            ).first()
            if not holding or holding.quantity < quantity:
                raise ValueError(f"Insufficient holdings. Available: {holding.quantity if holding else 0}, Requested: {quantity}")
        else:
            raise ValueError(f"Invalid action: {action}")

        # Create transaction record
        transaction = Transaction(
            account_id=account_id,
            ticker=ticker.upper(),
            action=action.upper(),
            quantity=quantity,
            price=price,
            total_amount=total_amount,
            rationale=rationale,
        )
        session.add(transaction)
        session.flush()

        # Update account balance
        if action.upper() == "BUY":
            account.balance -= total_amount
        else:  # SELL
            account.balance += total_amount

        # Update or create holding
        holding = session.query(Holding).filter_by(
            account_id=account_id,
            ticker=ticker.upper()
        ).first()

        if action.upper() == "BUY":
            if holding:
                # Update existing holding (calculate new average cost)
                total_cost = (holding.avg_cost * holding.quantity) + total_amount
                holding.quantity += quantity
                holding.avg_cost = total_cost / holding.quantity
            else:
                # Create new holding
                holding = Holding(
                    account_id=account_id,
                    ticker=ticker.upper(),
                    quantity=quantity,
                    avg_cost=price,
                )
                session.add(holding)
        else:  # SELL
            if holding:
                holding.quantity -= quantity
                if holding.quantity <= 0:
                    session.delete(holding)
                    holding = None

        # Update holding market value if market_data provided
        if holding and market_data:
            current_price = market_data.get(ticker.upper())
            if current_price:
                holding.current_price = Decimal(str(current_price))
                holding.market_value = holding.current_price * holding.quantity

        # Update account total value
        self._recalc_account_total_value(session, account_id)

        session.flush()
        return transaction

    def _recalc_account_total_value(self, session: Session, account_id: int):
        """
        Recalculate account total value based on balance and holdings.
        
        Args:
            session: Database session
            account_id: Account ID
        """
        account = session.query(Account).filter_by(id=account_id).first()
        if not account:
            return

        # Start with cash balance
        total_value = account.balance

        # Add market value of all holdings
        holdings = session.query(Holding).filter_by(account_id=account_id).all()
        for holding in holdings:
            if holding.market_value:
                total_value += holding.market_value
            elif holding.current_price:
                total_value += holding.current_price * holding.quantity

        account.total_value = total_value

    def run_trader(
        self,
        session: Session,
        trader,
        account_id: int,
        market_data: Dict[str, float]
    ) -> dict:
        """
        Run an AI trader and execute its decision.
        
        Args:
            session: Database session
            trader: Trader instance (must have run() method)
            account_id: Account ID
            market_data: Dictionary of {ticker: current_price}
            
        Returns:
            Dictionary with decision and execution result
        """
        # Load account information
        account = session.query(Account).filter_by(id=account_id).first()
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Load holdings
        holdings = session.query(Holding).filter_by(account_id=account_id).all()
        holdings_list = []
        for h in holdings:
            holdings_list.append({
                "ticker": h.ticker,
                "quantity": h.quantity,
                "avg_cost": float(h.avg_cost) if h.avg_cost else 0,
                "current_price": float(h.current_price) if h.current_price else 0,
            })

        # Build account info
        account_data = {
            "balance": float(account.balance),
            "total_value": float(account.total_value) if account.total_value else float(account.balance),
            "initial_balance": float(account.initial_balance) if account.initial_balance else 1000000.0,
        }

        # Build prompt
        from ai.prompts.trading_prompts import build_trading_prompt
        prompt = build_trading_prompt(
            account=account_data,
            holdings=holdings_list,
            market_data=market_data,
            style="balanced"
        )

        # Get AI decision
        try:
            decision = trader.run(prompt)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "decision": None
            }

        # Execute trade if not HOLD
        if decision.get("action", "").upper() == "HOLD":
            return {
                "success": True,
                "decision": decision,
                "transaction_id": None
            }

        # Execute trade
        try:
            ticker = decision.get("ticker", "").upper()
            quantity = int(decision.get("quantity", 0))
            rationale = decision.get("rationale", "AI trading decision")

            # Get current price from market_data or database
            if ticker in market_data:
                price = Decimal(str(market_data[ticker]))
            else:
                # Fallback: get latest price from database
                latest = session.query(StockDailyData).filter_by(
                    ticker=ticker
                ).order_by(StockDailyData.date.desc()).first()
                if not latest or not latest.close:
                    raise ValueError(f"Price data not found for {ticker}")
                price = Decimal(str(latest.close))

            transaction = self.execute_trade(
                session=session,
                account_id=account_id,
                action=decision.get("action", "BUY"),
                ticker=ticker,
                quantity=quantity,
                price=price,
                rationale=rationale,
                market_data=market_data
            )

            return {
                "success": True,
                "decision": decision,
                "transaction_id": transaction.id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "decision": decision
            }

