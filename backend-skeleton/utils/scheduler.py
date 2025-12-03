# backend/utils/scheduler.py

"""
Background Scheduler for auto-trading
Runs AI trades every 10 minutes when competition is active
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from config import settings
from models.database import SessionLocal
from services.competition.competition_manage_service import competition_service


class TradingScheduler:
    def __init__(self):
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the background trading loop"""
        self.running = True
        self.task = asyncio.create_task(self._trading_loop())
        print("📈 Trading scheduler started")
    
    async def stop(self):
        """Stop the background trading loop"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("📉 Trading scheduler stopped")
    
    async def _trading_loop(self):
        """Main trading loop - runs every TRADING_INTERVAL_MINUTES"""
        interval = settings.TRADING_INTERVAL_MINUTES * 60  # Convert to seconds
        
        while self.running:
            try:
                await asyncio.sleep(interval)
                
                if not competition_service.state.is_running:
                    continue
                
                if competition_service.state.is_paused:
                    continue
                
                # Execute trades
                db = SessionLocal()
                try:
                    trades = await competition_service.execute_ai_trades(db)
                    db.commit()  # Ensure all changes are committed
                    if trades:
                        print(f"⚡ Executed {len(trades)} trades at {datetime.now()}")
                except Exception as e:
                    db.rollback()  # Rollback on error
                    print(f"❌ Error in trading execution: {e}")
                finally:
                    db.close()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Trading loop error: {e}")


# Singleton instance
scheduler = TradingScheduler()


@asynccontextmanager
async def lifespan(app):
    """FastAPI lifespan manager for scheduler"""
    await scheduler.start()
    yield
    await scheduler.stop()
