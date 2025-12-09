# backend/config.py

from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator
import json


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./stock_arena.db"
    
    # API Keys
    OPENAI_API_KEY: str = ""
    
    # Competition Settings
    DEFAULT_BALANCE: float = 1000000.00
    TRADING_INTERVAL_MINUTES: int = 10  # Auto-trading interval (10 minutes)
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


settings = Settings()
