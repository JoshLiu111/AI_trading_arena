"""
Application configuration settings.
Loads environment variables from .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)


class Settings:
    """
    Global configuration settings.
    Automatically loads environment variables from .env file.
    """

    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/trading_arena"
    )
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    # API configuration
    ENVIRONMENT: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # CORS configuration
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Data Source APIs
    # Yahoo Finance - No API key required (uses yfinance library)
    YAHOO_TIMEOUT: int = int(os.getenv("YAHOO_TIMEOUT", "10"))
    YAHOO_RETRY: int = int(os.getenv("YAHOO_RETRY", "3"))

    # Alpaca - For real-time stock prices
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_DATA_URL: str = os.getenv("ALPACA_DATA_URL", "https://data.alpaca.markets/v2")
    ALPACA_FEED: str = os.getenv("ALPACA_FEED", "iex")

    # Polygon.io - Optional backup (can be omitted)
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")
    POLYGON_BASE_URL: str = os.getenv("POLYGON_BASE_URL", "https://api.polygon.io")

    # LLM API Keys (choose one or more)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


# Create singleton instance
settings = Settings()

