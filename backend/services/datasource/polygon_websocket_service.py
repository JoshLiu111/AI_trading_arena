# backend/services/datasource/polygon_websocket_service.py

"""
Polygon.io WebSocket Service
Maintains WebSocket connection to Polygon.io for real-time stock data
"""

import asyncio
import json
import websockets
from typing import Dict, Optional, Set
from datetime import date, datetime
from collections import defaultdict

from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class PolygonWebSocketService:
    """WebSocket service for real-time stock data from Polygon.io"""
    
    WS_URL = "wss://socket.polygon.io/stocks"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.POLYGON_API_KEY
        self.price_cache: Dict[str, Dict] = {}
        self.websocket = None
        self.running = False
        self.task = None
        self.subscribed_tickers: Set[str] = set()
    
    async def connect(self):
        """Connect to Polygon WebSocket"""
        if not self.api_key:
            raise ValueError("Polygon API key is required for WebSocket connection")
        
        try:
            # Connect with authentication
            uri = f"{self.WS_URL}?apiKey={self.api_key}"
            self.websocket = await websockets.connect(uri)
            logger.info("Connected to Polygon.io WebSocket")
            
            # Wait for authentication confirmation
            auth_response = await self.websocket.recv()
            auth_data = json.loads(auth_response)
            
            # Polygon WebSocket returns array of events
            if isinstance(auth_data, list) and len(auth_data) > 0:
                first_event = auth_data[0]
                if first_event.get("ev") == "status" and first_event.get("status") == "auth_success":
                    logger.info("Polygon WebSocket authentication successful")
                else:
                    logger.error(f"Polygon WebSocket authentication failed: {first_event}")
                    raise ValueError("WebSocket authentication failed")
            elif isinstance(auth_data, dict):
                if auth_data.get("ev") == "status" and auth_data.get("status") == "auth_success":
                    logger.info("Polygon WebSocket authentication successful")
                else:
                    logger.error(f"Polygon WebSocket authentication failed: {auth_data}")
                    raise ValueError("WebSocket authentication failed")
            else:
                logger.error(f"Unexpected WebSocket auth response format: {auth_data}")
                raise ValueError("WebSocket authentication failed - unexpected response format")
            
            self.running = True
        except Exception as e:
            logger.exception(f"Error connecting to Polygon WebSocket: {e}")
            raise
    
    async def subscribe(self, tickers: list):
        """Subscribe to tickers"""
        if not self.websocket or not self.running:
            await self.connect()
        
        # Subscribe to trades for each ticker
        # Format: {"action":"subscribe","params":"T.AAPL,T.MSFT"}
        # Polygon WebSocket format: T.{ticker} for trades, Q.{ticker} for quotes, A.{ticker} for aggregates
        ticker_params = ",".join([f"T.{ticker}" for ticker in tickers])
        subscribe_msg = {
            "action": "subscribe",
            "params": ticker_params
        }
        
        await self.websocket.send(json.dumps(subscribe_msg))
        self.subscribed_tickers.update(tickers)
        logger.info(f"Subscribed to {len(tickers)} tickers via WebSocket: {tickers}")
    
    async def _listen(self):
        """Listen for WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    
                    # Handle array of events
                    if isinstance(data, list):
                        for event in data:
                            await self._handle_event(event)
                    else:
                        await self._handle_event(data)
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse WebSocket message: {e}")
                except Exception as e:
                    logger.exception(f"Error handling WebSocket message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.running = False
        except Exception as e:
            logger.exception(f"WebSocket listen error: {e}")
            self.running = False
    
    async def _handle_event(self, event: Dict):
        """Handle a single WebSocket event"""
        event_type = event.get("ev")
        
        if event_type == "T":  # Trade event
            ticker = event.get("sym", "")
            if ticker:
                # Update price cache
                self.price_cache[ticker] = {
                    "date": date.today(),
                    "open": None,
                    "high": None,
                    "low": None,
                    "close": float(event.get("p", 0)) if event.get("p") else None,
                    "volume": int(event.get("s", 0)) if event.get("s") else None,
                    "adj_close": float(event.get("p", 0)) if event.get("p") else None,
                    "updated_at": datetime.now()
                }
        elif event_type == "status":
            status = event.get("status", "")
            message = event.get("message", "")
            if status == "auth_success":
                logger.info("WebSocket authenticated")
            elif status == "auth_failed":
                logger.error(f"WebSocket authentication failed: {message}")
            elif status == "success":
                logger.debug(f"WebSocket operation successful: {message}")
            else:
                logger.debug(f"WebSocket status: {status} - {message}")
    
    async def start(self, tickers: list):
        """Start WebSocket connection and subscribe to tickers"""
        if self.running:
            logger.warning("WebSocket service already running")
            return
        
        await self.connect()
        await self.subscribe(tickers)
        
        # Start listening in background
        self.task = asyncio.create_task(self._listen())
        logger.info("Polygon WebSocket service started")
    
    async def stop(self):
        """Stop WebSocket connection"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            await self.websocket.close()
            logger.info("Polygon WebSocket connection closed")
    
    def get_cached_price(self, ticker: str) -> Optional[Dict]:
        """Get cached price for a ticker"""
        return self.price_cache.get(ticker)
    
    def get_cached_prices_bulk(self, tickers: list) -> Dict[str, Optional[Dict]]:
        """Get cached prices for multiple tickers"""
        return {ticker: self.price_cache.get(ticker) for ticker in tickers}


# Singleton instance
polygon_websocket_service = PolygonWebSocketService()

