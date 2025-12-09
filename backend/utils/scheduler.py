# backend/utils/scheduler.py

"""
Background Scheduler for auto-trading and data refresh
- Runs AI trades every 30 minutes when competition is active
- Refreshes historical data twice daily (9:00 AM and 4:00 PM ET)
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta
import pytz

from config import settings
from models.database import SessionLocal
from services.competition.competition_manage_service import competition_service
from services.datasource.refresh_historical_data_service import refresh_historical_data_service
from core.logging import get_logger

logger = get_logger(__name__)


class TradingScheduler:
    def __init__(self):
        self.running = False
        self.trading_task = None
        self.historical_data_task = None
        self.realtime_data_task = None
    
    async def start(self):
        """Start the background trading loop, historical data refresh, and real-time data update"""
        self.running = True
        self.trading_task = asyncio.create_task(self._trading_loop())
        self.historical_data_task = asyncio.create_task(self._historical_data_refresh_loop())
        self.realtime_data_task = asyncio.create_task(self._realtime_data_update_loop())
        logger.info("Trading scheduler started (trading + historical data refresh + real-time data update)")
    
    async def stop(self):
        """Stop the background trading loop"""
        self.running = False
        if self.trading_task:
            self.trading_task.cancel()
            try:
                await self.trading_task
            except asyncio.CancelledError:
                pass
        if self.historical_data_task:
            self.historical_data_task.cancel()
            try:
                await self.historical_data_task
            except asyncio.CancelledError:
                pass
        if self.realtime_data_task:
            self.realtime_data_task.cancel()
            try:
                await self.realtime_data_task
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
    
    async def _historical_data_refresh_loop(self):
        """Historical data refresh loop - runs twice daily (08:00 UTC and 20:00 UTC)"""
        # Set refresh times (08:00 UTC and 20:00 UTC)
        utc_tz = pytz.timezone('UTC')
        refresh_times = [time(8, 0), time(20, 0)]  # 8 AM and 8 PM UTC
        
        while self.running:
            try:
                # Get current time in UTC
                now_utc = datetime.now(utc_tz)
                current_time = now_utc.time()
                
                # Find next refresh time
                next_refresh = None
                for refresh_time in refresh_times:
                    # If current time is before this refresh time today, use it
                    if current_time < refresh_time:
                        next_refresh = datetime.combine(now_utc.date(), refresh_time)
                        next_refresh = utc_tz.localize(next_refresh)
                        break
                
                # If no refresh time found today, use first one tomorrow
                if next_refresh is None:
                    tomorrow = now_utc.date() + timedelta(days=1)
                    next_refresh = datetime.combine(tomorrow, refresh_times[0])
                    next_refresh = utc_tz.localize(next_refresh)
                
                # Calculate seconds until next refresh
                wait_seconds = (next_refresh - now_utc).total_seconds()
                
                if wait_seconds > 0:
                    logger.info(f"Historical data refresh scheduled for {next_refresh.strftime('%Y-%m-%d %H:%M:%S %Z')} (in {wait_seconds/3600:.1f} hours)")
                    await asyncio.sleep(wait_seconds)
                
                # Refresh historical data
                logger.info(f"Starting historical data refresh at {datetime.now()}")
                db = SessionLocal()
                try:
                    count = refresh_historical_data_service.refresh_historical_data(db, days=settings.HISTORY_DAYS)
                    db.commit()
                    logger.info(f"Historical data refresh completed: {count} price records updated")
                except Exception as e:
                    db.rollback()
                    logger.exception("Error refreshing historical data")
                finally:
                    db.close()
                
                # Wait a bit before checking next refresh time
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Historical data refresh loop error")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying on error
    
    async def _realtime_data_update_loop(self):
        """Real-time data update loop - runs every 30 minutes"""
        from services.datasource.alpaca_realtime_updater import alpaca_realtime_updater
        
        interval = 30 * 60  # 30 minutes in seconds
        
        while self.running:
            try:
                await asyncio.sleep(interval)
                
                logger.info(f"Starting real-time price update at {datetime.now()}")
                try:
                    results = alpaca_realtime_updater.update_all_prices()
                    success_count = sum(1 for success in results.values() if success)
                    logger.info(f"Real-time price update completed: {success_count}/{len(results)} stocks updated")
                except Exception as e:
                    logger.exception("Error updating real-time prices")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Real-time data update loop error")
                await asyncio.sleep(60)  # Wait 1 minute before retrying on error


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
            logger.info(f"ALPACA_BASE_URL: {settings.ALPACA_BASE_URL}")
        else:
            logger.error("ALPACA_API_KEY or ALPACA_API_SECRET: NOT CONFIGURED!")
            logger.error("Please set the following environment variables in Render dashboard:")
            logger.error("  - ALPACA_API_KEY (or use ALPACA_API_KEY)")
            logger.error("  - ALPACA_SECRET_KEY (or ALPACA_API_SECRET)")
            logger.error("  - ALPACA_BROKER_URL (optional, defaults to paper-api.alpaca.markets)")
            logger.error("  - DATA_SOURCE=alpaca")
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
    
    # WebSocket is disabled - using REST API with caching instead
    # Real-time data is updated every 30 minutes via scheduler
    # Historical data is updated twice daily (08:00 UTC, 20:00 UTC)
    logger.info("Using REST API with caching (WebSocket disabled for stability)")
    
    # Trigger initial real-time data update (non-blocking, runs in background thread)
    try:
        from services.datasource.alpaca_realtime_updater import alpaca_realtime_updater
        import threading
        def run_initial_update():
            try:
                alpaca_realtime_updater.update_all_prices()
            except Exception as e:
                logger.warning(f"Error in initial real-time price update: {e}")
        
        update_thread = threading.Thread(target=run_initial_update, daemon=True)
        update_thread.start()
        logger.info("Initial real-time price update triggered (background thread)")
    except Exception as e:
        logger.warning(f"Failed to trigger initial real-time price update: {e}")
    
    yield
    
    # Stop trading scheduler on shutdown
    await scheduler.stop()
