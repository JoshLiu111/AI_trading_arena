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
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5  # Initial delay in seconds
    
    async def connect(self):
        """Connect to Polygon WebSocket"""
        if not self.api_key:
            raise ValueError("Polygon API key is required for WebSocket connection")
        
        try:
            # Connect to WebSocket (without API key in URL)
            self.websocket = await websockets.connect(self.WS_URL)
            logger.info("Connected to Polygon.io WebSocket")
            
            # Step 1: Wait for initial "connected" message from server
            connected_response = await self.websocket.recv()
            connected_data = json.loads(connected_response)
            
            # Verify we received the "connected" message
            is_connected = False
            if isinstance(connected_data, list) and len(connected_data) > 0:
                first_event = connected_data[0]
                if first_event.get("ev") == "status" and first_event.get("status") == "connected":
                    is_connected = True
                    logger.info("Received 'connected' status from Polygon WebSocket")
            elif isinstance(connected_data, dict):
                if connected_data.get("ev") == "status" and connected_data.get("status") == "connected":
                    is_connected = True
                    logger.info("Received 'connected' status from Polygon WebSocket")
            
            if not is_connected:
                logger.warning(f"Unexpected initial message: {connected_data}")
            
            # Step 2: Send authentication message
            auth_msg = {
                "action": "auth",
                "params": self.api_key
            }
            await self.websocket.send(json.dumps(auth_msg))
            logger.info("Sent authentication message to Polygon WebSocket")
            
            # Step 3: Wait for "auth_success" message
            auth_response = await self.websocket.recv()
            auth_data = json.loads(auth_response)
            
            # Parse authentication response
            auth_success = False
            if isinstance(auth_data, list) and len(auth_data) > 0:
                first_event = auth_data[0]
                if first_event.get("ev") == "status" and first_event.get("status") == "auth_success":
                    auth_success = True
                    logger.info("Polygon WebSocket authentication successful")
                else:
                    logger.error(f"Polygon WebSocket authentication failed: {first_event}")
            elif isinstance(auth_data, dict):
                if auth_data.get("ev") == "status" and auth_data.get("status") == "auth_success":
                    auth_success = True
                    logger.info("Polygon WebSocket authentication successful")
                else:
                    logger.error(f"Polygon WebSocket authentication failed: {auth_data}")
            else:
                logger.error(f"Unexpected WebSocket auth response format: {auth_data}")
            
            if not auth_success:
                raise ValueError(f"WebSocket authentication failed. Response: {auth_data}")
            
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
        logger.info(f"Subscription message: {json.dumps(subscribe_msg)}")
        
        # Wait a moment to check for subscription errors
        await asyncio.sleep(1.0)
        
        # If we received authorization errors, stop the service
        if not self.running:
            logger.warning("WebSocket service stopped due to subscription errors")
            return
    
    async def _listen(self):
        """Listen for WebSocket messages with auto-reconnect"""
        message_count = 0
        while self.running:
            try:
                async for message in self.websocket:
                    try:
                        data = json.loads(message)
                        message_count += 1
                        
                        # Log first few messages and all trade events for debugging
                        if message_count <= 10:
                            logger.info(f"WebSocket message #{message_count}: {json.dumps(data)[:300]}")
                        
                        # Also log all trade events
                        if isinstance(data, list):
                            for event in data:
                                if event.get("ev") == "T":
                                    logger.info(f"Trade event received: {event.get('sym')} @ ${event.get('p')}")
                        elif isinstance(data, dict) and data.get("ev") == "T":
                            logger.info(f"Trade event received: {data.get('sym')} @ ${data.get('p')}")
                        
                        # Handle array of events
                        if isinstance(data, list):
                            for event in data:
                                await self._handle_event(event)
                        else:
                            await self._handle_event(data)
                        
                        # Reset reconnect attempts on successful message
                        self.reconnect_attempts = 0
                        self.reconnect_delay = 5
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse WebSocket message: {e}")
                    except Exception as e:
                        logger.exception(f"Error handling WebSocket message: {e}")
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                if self.running:
                    # Check if we should stop (due to authorization or connection limit errors)
                    # These errors are handled in _handle_event, which sets self.running = False
                    if self.running:
                        # Attempt to reconnect
                        await self._reconnect()
            except Exception as e:
                logger.exception(f"WebSocket listen error: {e}")
                if self.running:
                    # Attempt to reconnect
                    await self._reconnect()
    
    async def _reconnect(self):
        """Attempt to reconnect to WebSocket with exponential backoff"""
        if not self.running:
            return
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnect attempts ({self.max_reconnect_attempts}) reached. Stopping WebSocket service.")
            logger.warning("WebSocket service disabled. Falling back to REST API for real-time prices.")
            self.running = False
            return
        
        # Don't reconnect if we've been explicitly stopped (e.g., due to authorization errors)
        if not self.running:
            return
        
        self.reconnect_attempts += 1
        delay = min(self.reconnect_delay * (2 ** (self.reconnect_attempts - 1)), 60)  # Max 60 seconds
        logger.info(f"Attempting to reconnect WebSocket (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}) in {delay}s...")
        
        await asyncio.sleep(delay)
        
        if not self.running:
            return
        
        try:
            # Close old connection if exists
            if self.websocket:
                try:
                    if not self.websocket.closed:
                        await self.websocket.close()
                except Exception:
                    pass  # Ignore errors when closing old connection
                self.websocket = None
            
            # Reconnect
            await self.connect()
            
            # Resubscribe to tickers
            if self.subscribed_tickers:
                await self.subscribe(list(self.subscribed_tickers))
            
            logger.info("WebSocket reconnected successfully")
            self.reconnect_attempts = 0
            self.reconnect_delay = 5
            
        except Exception as e:
            logger.error(f"Reconnection attempt {self.reconnect_attempts} failed: {e}")
            # Will retry in next iteration if self.running is still True
    
    async def _handle_event(self, event: Dict):
        """Handle a single WebSocket event"""
        event_type = event.get("ev")
        
        if event_type == "T":  # Trade event
            ticker = event.get("sym", "")
            price = event.get("p")
            if ticker and price:
                # Update price cache
                self.price_cache[ticker] = {
                    "date": date.today(),
                    "open": None,
                    "high": None,
                    "low": None,
                    "close": float(price),
                    "volume": int(event.get("s", 0)) if event.get("s") else None,
                    "adj_close": float(price),
                    "updated_at": datetime.now()
                }
                logger.info(f"WebSocket: Updated {ticker} price to ${price:.2f}")
            elif ticker:
                logger.debug(f"WebSocket: Received trade event for {ticker} but no price data")
        elif event_type == "status":
            status = event.get("status", "")
            message = event.get("message", "")
            if status == "auth_success":
                logger.info("WebSocket authenticated")
            elif status == "auth_failed":
                logger.error(f"WebSocket authentication failed: {message}")
            elif status == "success":
                logger.info(f"WebSocket operation successful: {message}")
            elif status == "subscribed":
                logger.info(f"WebSocket subscription confirmed: {message}")
            elif status == "error" and "not authorized" in message.lower():
                logger.error(f"WebSocket subscription error: {message} - Starter Plan may not support this subscription type")
                # Stop trying to reconnect if we get authorization errors
                if "not authorized" in message.lower():
                    logger.warning("Stopping WebSocket service due to authorization errors. Falling back to REST API.")
                    self.running = False
            elif status == "max_connections":
                logger.error(f"WebSocket max connections reached: {message}")
                logger.warning("Stopping WebSocket service due to connection limit. Falling back to REST API.")
                self.running = False
            else:
                logger.info(f"WebSocket status: {status} - {message}")
    
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
        
        # Cancel listening task
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket connection with error handling
        if self.websocket:
            try:
                # Check if websocket is still open before closing
                if not self.websocket.closed:
                    await self.websocket.close()
                logger.info("Polygon WebSocket connection closed")
            except Exception as e:
                # Ignore errors when closing (socket might already be closed)
                logger.debug(f"Error closing WebSocket (may already be closed): {e}")
            finally:
                self.websocket = None
    
    def get_cached_price(self, ticker: str) -> Optional[Dict]:
        """Get cached price for a ticker"""
        return self.price_cache.get(ticker)
    
    def get_cached_prices_bulk(self, tickers: list) -> Dict[str, Optional[Dict]]:
        """Get cached prices for multiple tickers"""
        return {ticker: self.price_cache.get(ticker) for ticker in tickers}


# Singleton instance
polygon_websocket_service = PolygonWebSocketService()

