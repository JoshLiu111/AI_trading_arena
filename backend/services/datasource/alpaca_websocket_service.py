# backend/services/datasource/alpaca_websocket_service.py

"""
Alpaca Markets WebSocket Service
Maintains WebSocket connection to Alpaca Markets for real-time stock data
"""

import asyncio
import threading
from typing import Dict, Optional, Set
from datetime import date, datetime

from config import settings
from core.logging import get_logger

logger = get_logger(__name__)

try:
    from alpaca_trade_api.stream import Stream
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logger.warning("alpaca-trade-api not installed. Alpaca WebSocket will not be available.")


class AlpacaWebSocketService:
    """WebSocket service for real-time stock data from Alpaca Markets"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, base_url: Optional[str] = None):
        if not ALPACA_AVAILABLE:
            raise ImportError("alpaca-trade-api is not installed. Please install it with: pip install alpaca-trade-api")
        
        self.api_key = api_key or settings.ALPACA_API_KEY
        self.api_secret = api_secret or settings.ALPACA_API_SECRET
        self.base_url = base_url or settings.ALPACA_BASE_URL or "https://paper-api.alpaca.markets"
        
        if not self.api_key or not self.api_secret:
            logger.error("Alpaca API credentials not configured! Check ALPACA_API_KEY and ALPACA_API_SECRET environment variables.")
            raise ValueError("Alpaca API key and secret are required")
        
        self.price_cache: Dict[str, Dict] = {}
        self.stream = None
        self.running = False
        self.task = None
        self.subscribed_tickers: Set[str] = set()
        
        # Initialize Alpaca Stream
        # Use 'iex' data feed (free tier) or 'sip' (premium)
        self.data_feed = getattr(settings, 'ALPACA_DATA_FEED', 'iex')
        self.stream = Stream(
            self.api_key,
            self.api_secret,
            base_url=self.base_url,
            data_feed=self.data_feed
        )
        logger.info(f"Alpaca WebSocket service initialized (base_url: {self.base_url}, data_feed: {self.data_feed})")
    
    async def on_trade(self, trade):
        """Handle trade events from Alpaca WebSocket"""
        try:
            ticker = trade.symbol
            price = float(trade.price) if hasattr(trade, 'price') and trade.price else None
            size = int(trade.size) if hasattr(trade, 'size') and trade.size else None
            
            if ticker and price:
                logger.debug(f"Alpaca WebSocket: Received trade for {ticker} @ ${price:.2f}")
                # Update price cache
                self.price_cache[ticker] = {
                    "date": date.today(),
                    "open": None,
                    "high": None,
                    "low": None,
                    "close": price,
                    "volume": size,
                    "adj_close": price,
                    "updated_at": datetime.now()
                }
        except Exception as e:
            logger.warning(f"Error handling Alpaca trade event: {e}")
    
    async def on_quote(self, quote):
        """Handle quote events from Alpaca WebSocket"""
        try:
            ticker = quote.symbol
            # Use bid/ask midpoint or last price
            bid = float(quote.bid_price) if hasattr(quote, 'bid_price') and quote.bid_price else None
            ask = float(quote.ask_price) if hasattr(quote, 'ask_price') and quote.ask_price else None
            
            if ticker and bid and ask:
                price = (bid + ask) / 2  # Use midpoint
                logger.debug(f"Alpaca WebSocket: Received quote for {ticker} @ ${price:.2f}")
                # Update price cache
                self.price_cache[ticker] = {
                    "date": date.today(),
                    "open": None,
                    "high": None,
                    "low": None,
                    "close": price,
                    "volume": None,
                    "adj_close": price,
                    "updated_at": datetime.now()
                }
        except Exception as e:
            logger.warning(f"Error handling Alpaca quote event: {e}")
    
    async def subscribe(self, tickers: list):
        """Subscribe to tickers"""
        if not self.stream:
            raise ValueError("Alpaca Stream not initialized")
        
        # Subscribe to trades for each ticker
        for ticker in tickers:
            try:
                self.stream.subscribe_trades(self.on_trade, ticker)
                self.subscribed_tickers.add(ticker)
                logger.info(f"Subscribed to {ticker} trades via Alpaca WebSocket")
            except Exception as e:
                logger.error(f"Error subscribing to {ticker}: {e}")
    
    async def start(self, tickers: list):
        """Start WebSocket connection and subscribe to tickers"""
        if self.running:
            logger.warning("Alpaca WebSocket service already running")
            return
        
        if not self.stream:
            raise ValueError("Alpaca Stream not initialized")
        
        try:
            # Subscribe to tickers
            await self.subscribe(tickers)
            
            # Start the stream in a background task
            self.running = True
            self.task = asyncio.create_task(self._run_stream())
            logger.info("Alpaca WebSocket service started")
            
        except Exception as e:
            logger.exception(f"Error starting Alpaca WebSocket: {e}")
            self.running = False
            raise
    
    async def _run_stream(self):
        """Run the Alpaca stream in background"""
        try:
            # Alpaca stream.run() is blocking, so we need to run it in a thread
            import threading
            def run_stream():
                try:
                    self.stream.run()
                except Exception as e:
                    logger.exception(f"Error in Alpaca stream thread: {e}")
                    self.running = False
            
            stream_thread = threading.Thread(target=run_stream, daemon=True)
            stream_thread.start()
            logger.info("Alpaca WebSocket stream thread started")
            
            # Keep the async task alive while stream is running
            while self.running:
                await asyncio.sleep(1)
        except Exception as e:
            logger.exception(f"Error running Alpaca stream: {e}")
            self.running = False
    
    async def stop(self):
        """Stop WebSocket connection"""
        self.running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        if self.stream:
            try:
                # Alpaca stream doesn't have a direct stop method, but we can unsubscribe
                for ticker in list(self.subscribed_tickers):
                    try:
                        self.stream.unsubscribe_trades(ticker)
                    except Exception as e:
                        logger.warning(f"Error unsubscribing from {ticker}: {e}")
                self.subscribed_tickers.clear()
                logger.info("Alpaca WebSocket connection closed")
            except Exception as e:
                logger.warning(f"Error closing Alpaca WebSocket: {e}")
    
    def get_cached_price(self, ticker: str) -> Optional[Dict]:
        """Get cached price for a ticker"""
        return self.price_cache.get(ticker)
    
    def get_cached_prices_bulk(self, tickers: list) -> Dict[str, Optional[Dict]]:
        """Get cached prices for multiple tickers"""
        return {ticker: self.price_cache.get(ticker) for ticker in tickers}


# Singleton instance (lazy initialization)
_alpaca_websocket_service = None

def get_alpaca_websocket_service() -> Optional[AlpacaWebSocketService]:
    """Get or create Alpaca WebSocket service instance"""
    global _alpaca_websocket_service
    
    if _alpaca_websocket_service is None:
        try:
            _alpaca_websocket_service = AlpacaWebSocketService()
        except Exception as e:
            logger.warning(f"Failed to initialize Alpaca WebSocket service: {e}")
            return None
    
    return _alpaca_websocket_service

