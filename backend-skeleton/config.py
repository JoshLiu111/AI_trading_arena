# backend/config.py

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./stock_arena.db"
    
    # API Keys
    OPENAI_API_KEY: str = ""
    
    # Competition Settings
    DEFAULT_BALANCE: float = 1000000.00
    TRADING_INTERVAL_MINUTES: int = 10
    HISTORY_DAYS: int = 7
    
    # Stock Pool (10 stocks)
    STOCK_POOL: List[str] = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "JPM", "V", "WMT"
    ]
    
    class Config:
        env_file = ".env"


settings = Settings()
