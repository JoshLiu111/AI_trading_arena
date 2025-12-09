# backend/services/datasource/alpaca_service.py

"""
Alpaca Markets Data Source Service
Provides stock data from Alpaca Markets API
Returns data in the same format as existing services for compatibility
"""

import time
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta

from services.datasource.base_data_source import BaseDataSource
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)

try:
    import alpaca_trade_api as tradeapi
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logger.warning("alpaca-trade-api not installed. Alpaca data source will not be available.")


class AlpacaService(BaseDataSource):
    """Service for fetching stock data from Alpaca Markets API"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, base_url: Optional[str] = None):
        if not ALPACA_AVAILABLE:
            raise ImportError("alpaca-trade-api is not installed. Please install it with: pip install alpaca-trade-api")
        
        self.api_key = api_key or settings.ALPACA_API_KEY
        self.api_secret = api_secret or settings.ALPACA_API_SECRET
        self.base_url = base_url or settings.ALPACA_BASE_URL or "https://paper-api.alpaca.markets"
        
        if not self.api_key or not self.api_secret:
            logger.error("Alpaca API credentials not configured! Check ALPACA_API_KEY and ALPACA_API_SECRET environment variables.")
            raise ValueError("Alpaca API key and secret are required")
        
        # Initialize Alpaca REST API client
        self.api = tradeapi.REST(
            self.api_key,
            self.api_secret,
            self.base_url,
            api_version='v2'
        )
        logger.info(f"Alpaca API client initialized (base_url: {self.base_url})")
    
    def get_historical_data(
        self, 
        ticker: str, 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None,
        retries: int = 3
    ) -> List[Dict]:
        """
        Get historical price data for a single ticker using Alpaca API
        """
        try:
            # Convert period to Alpaca format
            end_date = date.today()
            if end:
                end_date = datetime.strptime(end, "%Y-%m-%d").date()
            
            start_date = end_date - timedelta(days=365)  # Default to 1 year
            if start:
                start_date = datetime.strptime(start, "%Y-%m-%d").date()
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "1mo":
                start_date = end_date - timedelta(days=30)
            
            # Alpaca uses ISO format strings for dates
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            
            # Fetch historical bars
            bars = self.api.get_bars(
                ticker,
                tradeapi.TimeFrame.Day,
                start=start_str,
                end=end_str,
                adjustment='raw'  # Use raw prices (not adjusted)
            ).df
            
            if bars.empty:
                logger.warning(f"No historical data found for {ticker}")
                return []
            
            # Convert to standard format
            result = []
            for idx, row in bars.iterrows():
                result.append({
                    "date": idx.date() if hasattr(idx, 'date') else idx,
                    "open": float(row['open']) if 'open' in row else None,
                    "high": float(row['high']) if 'high' in row else None,
                    "low": float(row['low']) if 'low' in row else None,
                    "close": float(row['close']) if 'close' in row else None,
                    "volume": int(row['volume']) if 'volume' in row else None,
                    "adj_close": float(row['close']) if 'close' in row else None,  # Alpaca doesn't provide adjusted close in free tier
                })
            
            result.sort(key=lambda x: x["date"])
            return result
            
        except Exception as e:
            logger.exception(f"Error fetching historical data for {ticker} from Alpaca: {e}")
            return []
    
    def download_bulk(
        self, 
        tickers: List[str], 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Bulk download historical price data for multiple tickers
        """
        result = {ticker: [] for ticker in tickers}
        total = len(tickers)
        
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"Downloading {ticker} from Alpaca ({i}/{total})...")
            result[ticker] = self.get_historical_data(ticker, period, start, end)
            if not result[ticker]:
                logger.warning(f"No data received for {ticker}")
            # Small delay to avoid rate limiting
            if i < total:
                time.sleep(0.1)  # 100ms delay between requests
        
        return result
    
    def get_latest_prices_bulk(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get latest price data for multiple tickers using Alpaca snapshot endpoint
        """
        result = {}
        
        try:
            # Alpaca provides a snapshot endpoint for multiple tickers
            snapshots = self.api.get_snapshots(tickers)
            
            today = date.today()
            
            for ticker in tickers:
                try:
                    snapshot = snapshots.get(ticker)
                    if not snapshot:
                        result[ticker] = None
                        logger.debug(f"No snapshot data for {ticker}")
                        continue
                    
                    # Get latest trade
                    latest_trade = snapshot.latest_trade if hasattr(snapshot, 'latest_trade') else None
                    latest_quote = snapshot.latest_quote if hasattr(snapshot, 'latest_quote') else None
                    daily_bar = snapshot.daily_bar if hasattr(snapshot, 'daily_bar') else None
                    prev_daily_bar = snapshot.prev_daily_bar if hasattr(snapshot, 'prev_daily_bar') else None
                    
                    # Prioritize latest trade price, fallback to daily bar close
                    close_price = None
                    if latest_trade and hasattr(latest_trade, 'p') and latest_trade.p:
                        close_price = float(latest_trade.p)
                    elif daily_bar and hasattr(daily_bar, 'c') and daily_bar.c:
                        close_price = float(daily_bar.c)
                    elif prev_daily_bar and hasattr(prev_daily_bar, 'c') and prev_daily_bar.c:
                        close_price = float(prev_daily_bar.c)
                    
                    # Get previous close from prev_daily_bar
                    previous_close = None
                    if prev_daily_bar and hasattr(prev_daily_bar, 'c') and prev_daily_bar.c:
                        previous_close = float(prev_daily_bar.c)
                    elif daily_bar and hasattr(daily_bar, 'c') and daily_bar.c:
                        # If no prev_daily_bar, use daily_bar as previous (it's from previous day)
                        previous_close = float(daily_bar.c)
                    
                    result[ticker] = {
                        "date": today,
                        "open": float(daily_bar.o) if daily_bar and hasattr(daily_bar, 'o') and daily_bar.o else None,
                        "high": float(daily_bar.h) if daily_bar and hasattr(daily_bar, 'h') and daily_bar.h else None,
                        "low": float(daily_bar.l) if daily_bar and hasattr(daily_bar, 'l') and daily_bar.l else None,
                        "close": close_price,
                        "volume": int(daily_bar.v) if daily_bar and hasattr(daily_bar, 'v') and daily_bar.v else None,
                        "adj_close": close_price,
                        "previous_close": previous_close,
                    }
                    
                except Exception as e:
                    logger.warning(f"Error processing {ticker} from Alpaca snapshot: {e}")
                    result[ticker] = None
            
            return result
            
        except Exception as e:
            logger.exception("Error fetching latest prices from Alpaca snapshot, falling back to individual requests")
            # Fallback to individual requests
            for ticker in tickers:
                try:
                    # Get latest trade
                    latest_trade = self.api.get_latest_trade(ticker)
                    if latest_trade:
                        result[ticker] = {
                            "date": date.today(),
                            "open": None,
                            "high": None,
                            "low": None,
                            "close": float(latest_trade.p) if hasattr(latest_trade, 'p') and latest_trade.p else None,
                            "volume": None,
                            "adj_close": float(latest_trade.p) if hasattr(latest_trade, 'p') and latest_trade.p else None,
                            "previous_close": None,
                        }
                    else:
                        result[ticker] = None
                except Exception as e:
                    logger.warning(f"Error fetching latest price for {ticker} from Alpaca: {e}")
                    result[ticker] = None
            
            return result
    
    def get_company_info(self, ticker: str, retries: int = 3) -> Optional[Dict]:
        """
        Get basic company information from Alpaca
        Note: Alpaca doesn't provide detailed company info in free tier
        """
        for attempt in range(retries):
            try:
                # Alpaca provides asset information
                asset = self.api.get_asset(ticker)
                if asset:
                    return {
                        "ticker": ticker,
                        "name": asset.name if hasattr(asset, 'name') and asset.name else ticker,
                        "sector": "",  # Alpaca free tier doesn't provide sector
                        "description": "",  # Alpaca free tier doesn't provide description
                        "homepage_url": "",  # Alpaca free tier doesn't provide homepage
                        "sic_description": "",  # Alpaca free tier doesn't provide SIC description
                    }
                return None
            except Exception as e:
                if attempt < retries - 1:
                    wait_time = 5 * (2 ** attempt)
                    logger.warning(f"Error fetching company info for {ticker} (attempt {attempt + 1}/{retries}): {str(e)[:100]}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.exception(f"Error fetching company info for {ticker} after {retries} attempts")
                return None
        return None

