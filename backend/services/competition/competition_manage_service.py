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
    create_account, get_all_accounts, update_account, get_account
)
from models.crud.transaction_crud import get_transactions_by_account
from models.crud.strategy_crud import create_strategy, get_latest_strategy, delete_strategies_by_account
from services.datasource.refresh_historical_data_service import refresh_historical_data_service
from services.competition.generate_metrics_service import metrics_service
from services.competition.ai_strategy_report_service import ai_service
from services.competition.trading_service import trading_service
from core.logging import get_logger

logger = get_logger(__name__)


class CompetitionState:
    """Global competition state"""
    is_running: bool = False
    is_paused: bool = False
    started_at: Optional[datetime] = None
    last_trade_at: Optional[datetime] = None


class CompetitionService:
    def __init__(self):
        self.state = CompetitionState()
        # Only keep openai_player account as per requirements
        self.ai_accounts = ["openai_player"]
    
    async def generate_strategy_only(self, db: Session, account_id: Optional[int] = None) -> Dict:
        """
        Generate AI strategy only (without resetting accounts or refreshing data):
        1. Calculate metrics from existing stock data
        2. Generate AI strategies for AI accounts
        Does NOT reset accounts, clear transactions, or refresh stock data
        Does NOT set is_running = True
        """
        # 1. Get 7-day historical data for all stocks
        from services.competition.historical_data_service import historical_data_service
        
        history_data = historical_data_service.get_all_stocks_history(db, days=settings.HISTORY_DAYS)
        
        # Check if we have enough historical data
        stocks_with_data = [ticker for ticker, data in history_data.items() if data]
        if not stocks_with_data:
            return {
                "success": False,
                "message": "No stock historical data available. Please start competition first to refresh stock data.",
                "strategies_created": 0
            }
        
        # Format historical data for AI
        historical_data_text = historical_data_service.format_for_ai(history_data)
        
        # 2. Get AI accounts
        accounts = get_all_accounts(db)
        ai_accounts = [acc for acc in accounts if acc.account_type == "ai"]
        
        if account_id:
            # Generate for specific account only
            ai_accounts = [acc for acc in ai_accounts if acc.id == account_id]
            # Check if account was found
            if not ai_accounts:
                from models.crud.account_crud import get_account
                account = get_account(db, account_id)
                if not account:
                    return {
                        "success": False,
                        "message": f"Account not found: account_id={account_id}",
                        "strategies_created": 0
                    }
                elif account.account_type != "ai":
                    return {
                        "success": False,
                        "message": f"Account {account_id} is not an AI account",
                        "strategies_created": 0
                    }
        
        # Check if any AI accounts exist
        if not ai_accounts:
            return {
                "success": False,
                "message": "No AI accounts found. Please start competition first to create accounts.",
                "strategies_created": 0
            }
        
        # 3. Generate AI strategies
        strategies_created = []
        errors = []
        
        for acc in ai_accounts:
            try:
                strategy = await ai_service.generate_strategy(
                    account_name=acc.account_name,
                    balance=float(acc.balance),
                    historical_data_text=historical_data_text
                )
                
                # Save strategy
                created = create_strategy(
                    db,
                    account_id=acc.id,
                    strategy_date=date.today(),
                    strategy_content=json.dumps(strategy),
                    selected_stocks=json.dumps(strategy.get("selected_stocks", []))
                )
                strategies_created.append(created)
            except Exception as e:
                error_msg = f"Failed to generate strategy for account {acc.account_name}: {str(e)}"
                errors.append(error_msg)
                logger.exception(f"Error generating strategy for {acc.account_name}")
        
        db.commit()
        
        if errors and not strategies_created:
            # All strategies failed
            return {
                "success": False,
                "message": "; ".join(errors),
                "strategies_created": 0
            }
        elif errors:
            # Some succeeded, some failed
            return {
                "success": True,
                "message": f"Strategy generated with warnings: {'; '.join(errors)}",
                "strategies_created": len(strategies_created)
            }
        else:
            # All succeeded
            return {
                "success": True,
                "message": "Strategy generated",
                "strategies_created": len(strategies_created)
            }
    
    async def regenerate_strategy(self, db: Session, account_id: Optional[int] = None) -> Dict:
        """
        Delete existing strategies and regenerate new ones:
        1. Delete all strategies for AI accounts
        2. Generate new AI strategies
        Does NOT reset accounts, clear transactions, or refresh stock data
        Does NOT set is_running = True
        """
        # 1. Get AI accounts
        accounts = get_all_accounts(db)
        ai_accounts = [acc for acc in accounts if acc.account_type == "ai"]
        
        if account_id:
            ai_accounts = [acc for acc in ai_accounts if acc.id == account_id]
            # Check if account was found
            if not ai_accounts:
                from models.crud.account_crud import get_account
                account = get_account(db, account_id)
                if not account:
                    return {
                        "success": False,
                        "message": f"Account not found: account_id={account_id}",
                        "strategies_created": 0
                    }
                elif account.account_type != "ai":
                    return {
                        "success": False,
                        "message": f"Account {account_id} is not an AI account",
                        "strategies_created": 0
                    }
        
        # Check if any AI accounts exist
        if not ai_accounts:
            return {
                "success": False,
                "message": "No AI accounts found. Please start competition first to create accounts.",
                "strategies_created": 0
            }
        
        # 2. Delete existing strategies
        deleted_count = 0
        for acc in ai_accounts:
            count = delete_strategies_by_account(db, acc.id)
            deleted_count += count
        
        # 3. Generate new strategies
        result = await self.generate_strategy_only(db, account_id)
        
        if not result.get("success"):
            return result
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} strategies and {result['message']}",
            "strategies_deleted": deleted_count,
            "strategies_created": result["strategies_created"]
        }
    
    async def start_competition(self, db: Session) -> Dict:
        """
        Start a new competition (full reset):
        1. Reset all accounts
        2. Clear transactions
        3. Refresh stock data
        4. Generate AI strategies
        5. Set is_running = True
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
        
        # 3. Get 7-day historical data for all stocks
        from services.competition.historical_data_service import historical_data_service
        
        history_data = historical_data_service.get_all_stocks_history(db, days=settings.HISTORY_DAYS)
        historical_data_text = historical_data_service.format_for_ai(history_data)
        
        # 4. Generate AI strategies
        for acc in accounts:
            if acc.account_type == "ai":
                strategy = await ai_service.generate_strategy(
                    account_name=acc.account_name,
                    balance=float(acc.balance),
                    historical_data_text=historical_data_text
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
        
        # 5. Update state - Set is_running = True
        self.state.is_running = True
        self.state.is_paused = False
        self.state.started_at = datetime.now()
        
        return {
            "success": True,
            "message": "Competition started",
            "accounts": [self._account_to_dict(a) for a in accounts]
        }
    
    def pause_competition(self) -> Dict:
        """Pause auto-trading (trading loop will skip execution)"""
        if not self.state.is_running:
            return {"success": False, "message": "Competition not running. Cannot pause."}
        
        if self.state.is_paused:
            return {"success": False, "message": "Competition is already paused"}
        
        self.state.is_paused = True
        return {"success": True, "message": "Competition paused"}
    
    def resume_competition(self) -> Dict:
        """Resume auto-trading"""
        if not self.state.is_running:
            return {"success": False, "message": "Competition not running. Cannot resume."}
        
        if not self.state.is_paused:
            return {"success": False, "message": "Competition is not paused"}
        
        self.state.is_paused = False
        return {"success": True, "message": "Competition resumed"}
    
    def stop_competition(self) -> Dict:
        """Stop the competition (set is_running = False)"""
        if not self.state.is_running:
            return {"success": False, "message": "Competition not running"}
        
        self.state.is_running = False
        self.state.is_paused = False
        # Keep started_at and last_trade_at for historical reference
        return {"success": True, "message": "Competition stopped"}
    
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
            logger.debug(f"execute_ai_trades: Competition not running or paused (is_running={self.state.is_running}, is_paused={self.state.is_paused})")
            return []
        
        trades_executed = []
        accounts = get_all_accounts(db)
        ai_accounts = [acc for acc in accounts if acc.account_type == "ai"]
        
        if not ai_accounts:
            logger.warning("execute_ai_trades: No AI accounts found")
            return []
        
        logger.info(f"execute_ai_trades: Processing {len(ai_accounts)} AI account(s)")
        
        for acc in ai_accounts:
            # Get latest strategy
            strategy = get_latest_strategy(db, acc.id)
            if not strategy:
                logger.warning(f"execute_ai_trades: No strategy found for {acc.account_name} (ID: {acc.id})")
                continue
            
            try:
                strategy_data = json.loads(strategy.strategy_content)
                
                # Check format: new AI decision format, trading_plan, trading_rules, or old actions
                selected_stocks = strategy_data.get("selected_stocks", [])
                stock_preferences = strategy_data.get("stock_preferences", [])
                trading_plan = strategy_data.get("trading_plan", [])
                trading_rules = strategy_data.get("trading_rules", [])
                actions = strategy_data.get("actions", [])
                
                # New format: AI makes trading decisions in real-time
                if selected_stocks and len(selected_stocks) > 0:
                    logger.debug(f"execute_ai_trades: {acc.account_name} using AI decision format with {len(selected_stocks)} selected stock(s)")
                    
                    # Get current positions and account balance
                    positions = trading_service.get_positions(db, acc.id)
                    account = get_account(db, acc.id)
                    account_balance = float(account.balance) if account else 0.0
                    
                    # Get historical data for selected stocks
                    from services.competition.historical_data_service import historical_data_service
                    history_data = historical_data_service.get_all_stocks_history(db, days=settings.HISTORY_DAYS)
                    
                    # For each selected stock, ask AI if we should trade
                    for ticker in selected_stocks:
                        # Get stock preference if available
                        stock_pref = None
                        if stock_preferences:
                            for pref in stock_preferences:
                                if pref.get("ticker") == ticker:
                                    stock_pref = pref
                                    break
                        
                        # Get current price
                        from services.datasource.yahoo_realtime_price_service import stock_price_service
                        current_price = stock_price_service.get_current_price(ticker, db=db)
                        
                        if not current_price:
                            logger.warning(f"   Price unavailable for {ticker}, skipping")
                            continue
                        
                        # Get current position
                        current_position = positions.get(ticker)
                        current_quantity = current_position.get("quantity", 0) if current_position else 0
                        avg_price = current_position.get("avg_price", 0.0) if current_position else 0.0
                        
                        # Get last buy date for T+1 rule check
                        last_buy_date = None
                        if current_quantity > 0:
                            from models.crud.transaction_crud import get_transactions_by_account
                            from datetime import date
                            transactions = get_transactions_by_account(db, acc.id, limit=100)
                            # Find the most recent BUY transaction for this ticker
                            for tx in transactions:
                                if tx.ticker == ticker and tx.action == "BUY":
                                    last_buy_date = tx.executed_at.date() if tx.executed_at else None
                                    break
                        
                        # Get historical data for this ticker
                        ticker_history = history_data.get(ticker, [])
                        
                        # Ask AI if we should trade
                        position_dict = None
                        if current_quantity > 0:
                            position_dict = {
                                "quantity": current_quantity,
                                "avg_price": avg_price,
                                "last_buy_date": last_buy_date.isoformat() if last_buy_date else None
                            }
                        
                        decision = await ai_service.should_trade(
                            ticker=ticker,
                            current_price=current_price,
                            account_balance=account_balance,
                            current_position=position_dict,
                            historical_data=ticker_history,
                            stock_preference=stock_pref
                        )
                        
                        if not decision:
                            logger.debug(f"   No decision from AI for {ticker}, skipping")
                            continue
                        
                        if not decision.get("should_trade", False):
                            logger.debug(f"   AI decision: {decision.get('action', 'HOLD')} for {ticker} - {decision.get('rationale', '')}")
                            continue
                        
                        # Execute trade based on AI decision
                        action = decision.get("action", "").upper()
                        quantity = decision.get("quantity", 10)
                        rationale = decision.get("rationale", "AI trading decision")
                        
                        if action == "BUY":
                            if current_quantity > 0:
                                logger.debug(f"   AI suggested BUY but already have position in {ticker}, skipping")
                                continue
                            logger.info(f"   AI BUY decision: {quantity} {ticker} @ ${current_price:.2f} - {rationale}")
                            result = trading_service.execute_trade(
                                db,
                                account_id=acc.id,
                                ticker=ticker,
                                action="BUY",
                                quantity=quantity,
                                rationale=rationale,
                                strategy_id=strategy.id
                            )
                            if result:
                                trades_executed.append(result)
                                logger.info(f"   BUY executed: {quantity} {ticker} @ ${current_price:.2f}")
                            else:
                                logger.warning(f"   BUY failed: {quantity} {ticker} (insufficient balance)")
                        
                        elif action == "SELL":
                            if current_quantity == 0:
                                logger.debug(f"   AI suggested SELL but no position in {ticker}, skipping")
                                continue
                            sell_quantity = min(quantity, current_quantity)
                            logger.info(f"   AI SELL decision: {sell_quantity} {ticker} @ ${current_price:.2f} - {rationale}")
                            result = trading_service.execute_trade(
                                db,
                                account_id=acc.id,
                                ticker=ticker,
                                action="SELL",
                                quantity=sell_quantity,
                                rationale=rationale,
                                strategy_id=strategy.id
                            )
                            if result:
                                trades_executed.append(result)
                                logger.info(f"   SELL executed: {sell_quantity} {ticker} @ ${current_price:.2f}")
                            else:
                                logger.warning(f"   SELL failed: {sell_quantity} {ticker}")
                
                # Legacy format: trading_plan (7-day plan)
                elif trading_plan:
                    # Newest format: 7-day trading plan
                    logger.debug(f"execute_ai_trades: {acc.account_name} has {len(trading_plan)} day(s) trading plan")
                    
                    # Get current date to determine which day of the plan we're on
                    from datetime import date as date_type
                    today = date_type.today()
                    strategy_date = strategy.strategy_date
                    
                    # Calculate which day of the plan (1-7)
                    if strategy_date:
                        days_since_start = (today - strategy_date).days + 1
                        if days_since_start < 1:
                            days_since_start = 1
                        elif days_since_start > 7:
                            days_since_start = 7
                    else:
                        days_since_start = 1  # Default to day 1
                    
                    # Get the plan for today (or closest day)
                    today_plan = None
                    for plan_day in trading_plan:
                        plan_day_num = plan_day.get("day", 0)
                        if plan_day_num == days_since_start:
                            today_plan = plan_day
                            break
                    
                    if not today_plan:
                        logger.debug(f"   No trading plan for day {days_since_start}, skipping")
                        continue
                    
                    # Get current positions
                    positions = trading_service.get_positions(db, acc.id)
                    
                    # Execute actions for today
                    actions_today = today_plan.get("actions", [])
                    logger.debug(f"   Day {days_since_start} of strategy: {len(actions_today)} action(s)")
                    
                    for action in actions_today:
                        ticker = action.get("ticker")
                        action_type = action.get("action", "HOLD").upper()
                        quantity = action.get("quantity", 0)
                        target_price = action.get("target_price")
                        rationale = action.get("rationale", "AI strategy plan")
                        
                        if action_type == "HOLD" or quantity == 0:
                            logger.debug(f"   HOLD: {ticker} (per strategy plan)")
                            continue
                        
                        # Get current real-time price
                        from services.datasource.yahoo_realtime_price_service import stock_price_service
                        current_price = stock_price_service.get_current_price(ticker, db=db)
                        
                        if not current_price:
                            logger.warning(f"   Price unavailable for {ticker}, skipping")
                            continue
                        
                        # Check if target_price matches (if specified)
                        if target_price:
                            # Parse target_price (could be number or range like "150.0-155.0")
                            price_match = False
                            try:
                                if isinstance(target_price, (int, float)):
                                    # Single price - allow small tolerance
                                    if abs(current_price - float(target_price)) / float(target_price) < 0.02:  # 2% tolerance
                                        price_match = True
                                elif isinstance(target_price, str) and "-" in target_price:
                                    # Price range
                                    low, high = map(float, target_price.split("-"))
                                    if low <= current_price <= high:
                                        price_match = True
                                else:
                                    price_match = True  # If can't parse, proceed anyway
                            except:
                                price_match = True  # If error parsing, proceed anyway
                            
                            if not price_match:
                                logger.debug(f"   Price ${current_price:.2f} not in target range {target_price} for {ticker}, waiting")
                                continue
                        
                        # Get current position
                        current_position = positions.get(ticker, {})
                        current_quantity = current_position.get("quantity", 0)
                        
                        # Execute trade
                        if action_type == "BUY":
                            if current_quantity > 0:
                                logger.debug(f"   Already have position in {ticker}, skipping BUY")
                                continue
                            logger.info(f"   BUY: {quantity} {ticker} @ ${current_price:.2f} (target: {target_price})")
                            result = trading_service.execute_trade(
                                db,
                                account_id=acc.id,
                                ticker=ticker,
                                action="BUY",
                                quantity=quantity,
                                rationale=f"{rationale} - Day {days_since_start} of strategy",
                                strategy_id=strategy.id
                            )
                            if result:
                                trades_executed.append(result)
                                logger.info(f"   BUY executed: {quantity} {ticker} @ ${current_price:.2f}")
                            else:
                                logger.warning(f"   BUY failed: {quantity} {ticker} (insufficient balance)")
                        
                        elif action_type == "SELL":
                            if current_quantity == 0:
                                logger.debug(f"   No position in {ticker}, skipping SELL")
                                continue
                            sell_quantity = min(quantity, current_quantity)
                            logger.info(f"   SELL: {sell_quantity} {ticker} @ ${current_price:.2f} (target: {target_price})")
                            result = trading_service.execute_trade(
                                db,
                                account_id=acc.id,
                                ticker=ticker,
                                action="SELL",
                                quantity=sell_quantity,
                                rationale=f"{rationale} - Day {days_since_start} of strategy",
                                strategy_id=strategy.id
                            )
                            if result:
                                trades_executed.append(result)
                                logger.info(f"   SELL executed: {sell_quantity} {ticker} @ ${current_price:.2f}")
                            else:
                                logger.warning(f"   SELL failed: {sell_quantity} {ticker}")
                
                elif trading_rules:
                    # New format: Use trading rules with buy/sell price points
                    logger.debug(f"execute_ai_trades: {acc.account_name} has {len(trading_rules)} trading rule(s)")
                    
                    # Get current positions
                    positions = trading_service.get_positions(db, acc.id)
                    
                    for rule in trading_rules:
                        ticker = rule.get("ticker")
                        buy_price = rule.get("buy_price")
                        sell_price = rule.get("sell_price")
                        quantity = rule.get("quantity", 10)
                        rationale = rule.get("rationale", "AI strategy rule")
                        
                        if not ticker or buy_price is None or sell_price is None:
                            logger.warning(f"   Invalid rule for {ticker}: missing required fields")
                            continue
                        
                        # Get current real-time price
                        from services.datasource.yahoo_realtime_price_service import stock_price_service
                        current_price = stock_price_service.get_current_price(ticker, db=db)
                        
                        if not current_price:
                            logger.warning(f"   Price unavailable for {ticker}, skipping")
                            continue
                        
                        # Get current position for this ticker
                        current_position = positions.get(ticker, {})
                        current_quantity = current_position.get("quantity", 0)
                        
                        # Decision logic: Buy if price below buy_price and no position, Sell if price above sell_price and has position
                        trade_executed = False
                        
                        # BUY condition: price <= buy_price AND no position
                        if current_price <= buy_price and current_quantity == 0:
                            logger.info(f"   BUY signal: {ticker} @ ${current_price:.2f} <= buy_price ${buy_price:.2f} (no position)")
                            result = trading_service.execute_trade(
                                db,
                                account_id=acc.id,
                                ticker=ticker,
                                action="BUY",
                                quantity=quantity,
                                rationale=f"{rationale} - Price ${current_price:.2f} below buy point ${buy_price:.2f}",
                                strategy_id=strategy.id
                            )
                            if result:
                                trades_executed.append(result)
                                trade_executed = True
                                logger.info(f"   BUY executed: {quantity} {ticker} @ ${current_price:.2f}")
                            else:
                                logger.warning(f"   BUY failed: {quantity} {ticker} (insufficient balance)")
                        
                        # SELL condition: price >= sell_price AND has position
                        elif current_price >= sell_price and current_quantity > 0:
                            # Sell all or partial position
                            sell_quantity = min(quantity, current_quantity)  # Don't sell more than owned
                            logger.info(f"   SELL signal: {ticker} @ ${current_price:.2f} >= sell_price ${sell_price:.2f} (position: {current_quantity})")
                            result = trading_service.execute_trade(
                                db,
                                account_id=acc.id,
                                ticker=ticker,
                                action="SELL",
                                quantity=sell_quantity,
                                rationale=f"{rationale} - Price ${current_price:.2f} above sell point ${sell_price:.2f}",
                                strategy_id=strategy.id
                            )
                            if result:
                                trades_executed.append(result)
                                trade_executed = True
                                logger.info(f"   SELL executed: {sell_quantity} {ticker} @ ${current_price:.2f}")
                            else:
                                logger.warning(f"   SELL failed: {sell_quantity} {ticker}")
                        
                        if not trade_executed:
                            if current_quantity > 0:
                                logger.debug(f"   HOLD: {ticker} @ ${current_price:.2f} (has position, price between ${buy_price:.2f}-${sell_price:.2f})")
                            else:
                                logger.debug(f"   WAIT: {ticker} @ ${current_price:.2f} (no position, price above buy_price ${buy_price:.2f})")
                
                elif actions:
                    # Old format: Direct actions (backward compatibility)
                    logger.debug(f"execute_ai_trades: {acc.account_name} has {len(actions)} action(s) in strategy (old format)")
                    
                    for action in actions:
                        logger.debug(f"   Attempting: {action.get('action')} {action.get('quantity')} {action.get('ticker')}")
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
                            logger.info(f"   Trade executed: {result.get('action')} {result.get('quantity')} {result.get('ticker')} @ ${result.get('price')}")
                        else:
                            logger.warning(f"   Trade failed: {action.get('action')} {action.get('quantity')} {action.get('ticker')} (insufficient balance/positions or price unavailable)")
                else:
                    logger.debug(f"execute_ai_trades: No trading rules or actions in strategy for {acc.account_name}")
                    continue
                        
            except Exception as e:
                logger.exception(f"Error executing trades for {acc.account_name}")
        
        self.state.last_trade_at = datetime.now()
        return trades_executed
    
    def _reset_or_create_account(
        self, db: Session, name: str, display: str, acc_type: str
    ):
        """Reset existing account or create new one"""
        from models.schema.account import Account
        from models.schema.transaction import Transaction
        from models.schema.strategy import TradingStrategy
        
        existing = db.query(Account).filter_by(account_name=name).first()
        
        if existing:
            # Reset balance
            existing.balance = Decimal(str(settings.DEFAULT_BALANCE))
            existing.initial_balance = Decimal(str(settings.DEFAULT_BALANCE))
            existing.total_value = Decimal(str(settings.DEFAULT_BALANCE))
            
            # Clear transactions using direct query
            db.query(Transaction).filter(Transaction.account_id == existing.id).delete()
            
            # Clear strategies using direct query
            db.query(TradingStrategy).filter(TradingStrategy.account_id == existing.id).delete()
            
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
