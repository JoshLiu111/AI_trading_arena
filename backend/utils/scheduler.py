# backend/utils/scheduler.py

"""
Background Scheduler for auto-trading
Runs AI trades every 1 minute when competition is active
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from config import settings
from models.database import SessionLocal
from services.competition.competition_manage_service import competition_service
from core.logging import get_logger

logger = get_logger(__name__)


class TradingScheduler:
    def __init__(self):
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the background trading loop"""
        self.running = True
        self.task = asyncio.create_task(self._trading_loop())
        logger.info("Trading scheduler started")
    
    async def stop(self):
        """Stop the background trading loop"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Trading scheduler stopped")
    
    async def _trading_loop(self):
        """Main trading loop - runs every TRADING_INTERVAL_MINUTES"""
        interval = settings.TRADING_INTERVAL_MINUTES * 60  # Convert to seconds
        
        while self.running:
            try:
                await asyncio.sleep(interval)
                
                if not competition_service.state.is_running:
                    logger.debug("Trading loop: Competition not running, skipping...")
                    continue
                
                if competition_service.state.is_paused:
                    logger.debug("Trading loop: Competition paused, skipping...")
                    continue
                
                logger.info(f"Trading loop: Executing AI trades at {datetime.now()}")
                
                # Execute trades
                db = SessionLocal()
                try:
                    trades = await competition_service.execute_ai_trades(db)
                    db.commit()  # Ensure all changes are committed
                    if trades:
                        logger.info(f"Executed {len(trades)} trades at {datetime.now()}")
                        for trade in trades:
                            logger.debug(f"   - {trade.get('action')} {trade.get('quantity')} {trade.get('ticker')} @ ${trade.get('price')}")
                    else:
                        logger.debug("No trades executed (no strategy actions or insufficient balance/positions)")
                except Exception as e:
                    db.rollback()  # Rollback on error
                    logger.exception("Error in trading execution")
                finally:
                    db.close()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Trading loop error")


# Singleton instance
scheduler = TradingScheduler()


@asynccontextmanager
async def lifespan(app):
    """FastAPI lifespan manager for scheduler and database initialization"""
    # Initialize database on startup
    from models.database import init_db
    init_db()
    logger.info("Stock Trading Arena API started")
    
    # Debug: Log configuration status
    logger.info(f"DATA_SOURCE: {settings.DATA_SOURCE}")
    data_source = settings.DATA_SOURCE.lower()
    
    if data_source == "alpaca":
        api_key = settings.ALPACA_API_KEY
        api_secret = settings.ALPACA_API_SECRET
        if api_key and api_key.strip() and api_secret and api_secret.strip():
            logger.info(f"ALPACA_API_KEY: Configured (length: {len(api_key)})")
            logger.info(f"ALPACA_API_SECRET: Configured (length: {len(api_secret)})")
        else:
            logger.error("ALPACA_API_KEY or ALPACA_API_SECRET: NOT CONFIGURED!")
            logger.error("Please set ALPACA_API_KEY and ALPACA_API_SECRET environment variables in Render dashboard")
    else:
        # Default to Polygon
        api_key = settings.POLYGON_API_KEY
        if api_key and api_key.strip():
            logger.info(f"POLYGON_API_KEY: Configured (length: {len(api_key)})")
        else:
            logger.error("POLYGON_API_KEY: NOT CONFIGURED!")
            logger.error("Please set POLYGON_API_KEY environment variable in Render dashboard")
    
    # Start trading scheduler
    await scheduler.start()
    
    # Start WebSocket service based on configured data source (optional - will fallback to REST API if fails)
    try:
        if data_source == "alpaca":
            from services.datasource.alpaca_websocket_service import get_alpaca_websocket_service
            alpaca_ws = get_alpaca_websocket_service()
            if alpaca_ws:
                await alpaca_ws.start(settings.STOCK_POOL)
                logger.info("Alpaca WebSocket service started")
            else:
                logger.warning("Alpaca WebSocket service not available")
        else:
            # Default to Polygon
            from services.datasource.polygon_websocket_service import polygon_websocket_service
            await polygon_websocket_service.start(settings.STOCK_POOL)
            logger.info("Polygon WebSocket service started")
    except Exception as e:
        logger.warning(f"Failed to start WebSocket service ({data_source}): {e}")
        logger.info("Will use REST API for real-time prices (WebSocket unavailable)")
    
    yield
    
    # Stop trading scheduler on shutdown
    await scheduler.stop()
    
    # Stop WebSocket service on shutdown
    try:
        if data_source == "alpaca":
            from services.datasource.alpaca_websocket_service import get_alpaca_websocket_service
            alpaca_ws = get_alpaca_websocket_service()
            if alpaca_ws:
                await alpaca_ws.stop()
        else:
            # Default to Polygon
            from services.datasource.polygon_websocket_service import polygon_websocket_service
            await polygon_websocket_service.stop()
    except Exception as e:
        logger.warning(f"Failed to stop WebSocket service ({data_source}): {e}")
