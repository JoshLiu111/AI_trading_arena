# backend/config.py

from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator, model_validator
import json


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./stock_arena.db"
    
    # API Keys
    OPENAI_API_KEY: str = ""
    POLYGON_API_KEY: str = ""
    
    # Alpaca Markets API Keys
    # Support both standard and alternative field names
    ALPACA_API_KEY: str = ""
    ALPACA_API_SECRET: str = ""
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"  # Paper trading by default
    ALPACA_DATA_FEED: str = "iex"  # 'iex' (free) or 'sip' (premium)
    
    # Alternative field names (for compatibility with different .env formats)
    ALPACA_SECRET_KEY: str = ""  # Alternative to ALPACA_API_SECRET
    ALPACA_BROKER_URL: str = ""  # Alternative to ALPACA_BASE_URL
    ALPACA_DATA_URL: str = ""  # Alternative to ALPACA_DATA_FEED (not used, but allow it)
    
    @model_validator(mode='after')
    def map_alternative_field_names(self):
        """Map alternative field names to standard names for compatibility"""
        # Map ALPACA_SECRET_KEY to ALPACA_API_SECRET if not set
        if not self.ALPACA_API_SECRET and self.ALPACA_SECRET_KEY:
            self.ALPACA_API_SECRET = self.ALPACA_SECRET_KEY
        
        # Map ALPACA_BROKER_URL to ALPACA_BASE_URL
        # Priority: ALPACA_BROKER_URL > ALPACA_BASE_URL > default
        if self.ALPACA_BROKER_URL:
            self.ALPACA_BASE_URL = self.ALPACA_BROKER_URL
        elif not self.ALPACA_BASE_URL:
            self.ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
        
        return self
    
    # Data Source Configuration
    # Options: "polygon" or "alpaca"
    DATA_SOURCE: str = "alpaca"  # Default to Alpaca for real-time data
    
    # Competition Settings
    DEFAULT_BALANCE: float = 1000000.00
    TRADING_INTERVAL_MINUTES: int = 30  # Auto-trading interval (30 minutes)
    HISTORY_DAYS: int = 7
    
    # Testing Mode (for non-market hours)
    USE_HISTORICAL_AS_REALTIME: bool = False  # If True, use latest historical price as real-time price
    
    # Stock Pool (10 stocks)
    STOCK_POOL: List[str] = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "JPM", "V", "WMT"
    ]
    
    # CORS Settings
    # Supports comma-separated string, JSON array, or single string from environment variable
    # Example: "https://app1.com,https://app2.com" or '["https://app1.com","https://app2.com"]'
    CORS_ORIGINS: Union[str, List[str]] = ["*"]  # Default to allow all for development
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from various formats"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try to parse as JSON array first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            # Parse as comma-separated string
            if ',' in v:
                return [origin.strip() for origin in v.split(',') if origin.strip()]
            # Single string
            return [v] if v else ["*"]
        return ["*"]
    
    class Config:
        env_file = ".env"
        # Ensure environment variables are read (case-sensitive matching)
        case_sensitive = False
        # Allow reading from environment variables
        env_file_encoding = 'utf-8'
        # Allow extra fields in .env (to support alternative field names)
        extra = 'allow'


settings = Settings()
