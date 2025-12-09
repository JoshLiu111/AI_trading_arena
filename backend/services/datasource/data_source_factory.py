# backend/services/datasource/data_source_factory.py

"""
Data Source Factory
Creates appropriate data source instances based on configuration
Only supports Alpha Vantage (yfinance has been removed)
"""

from services.datasource.base_data_source import BaseDataSource
from services.datasource.alpha_vantage_service import AlphaVantageService
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class DataSourceFactory:
    """Factory for creating data source instances - Alpha Vantage only"""
    
    @staticmethod
    def get_history_service() -> BaseDataSource:
        """Get historical data service - Alpha Vantage only"""
        # Check if API key is configured
        api_key = settings.ALPHA_VANTAGE_API_KEY
        if not api_key or api_key.strip() == "":
            logger.error("Alpha Vantage API key not configured! Please set ALPHA_VANTAGE_API_KEY environment variable.")
            logger.error("Cannot proceed without API key. Please configure it in Render dashboard.")
            raise ValueError("Alpha Vantage API key is required but not configured. Please set ALPHA_VANTAGE_API_KEY environment variable.")
        logger.info("Using Alpha Vantage for historical data")
        return AlphaVantageService()
    
    @staticmethod
    def get_info_service() -> BaseDataSource:
        """Get company info service - Alpha Vantage only"""
        # Check if API key is configured
        api_key = settings.ALPHA_VANTAGE_API_KEY
        if not api_key or api_key.strip() == "":
            logger.error("Alpha Vantage API key not configured! Please set ALPHA_VANTAGE_API_KEY environment variable.")
            logger.error("Cannot proceed without API key. Please configure it in Render dashboard.")
            raise ValueError("Alpha Vantage API key is required but not configured. Please set ALPHA_VANTAGE_API_KEY environment variable.")
        logger.info("Using Alpha Vantage for company info")
        return AlphaVantageService()
    
    @staticmethod
    def get_realtime_service() -> BaseDataSource:
        """Get real-time price service - Alpha Vantage only"""
        # Check if API key is configured
        api_key = settings.ALPHA_VANTAGE_API_KEY
        if not api_key or api_key.strip() == "":
            logger.error("Alpha Vantage API key not configured! Please set ALPHA_VANTAGE_API_KEY environment variable.")
            logger.error("Cannot proceed without API key. Please configure it in Render dashboard.")
            raise ValueError("Alpha Vantage API key is required but not configured. Please set ALPHA_VANTAGE_API_KEY environment variable.")
        logger.info("Using Alpha Vantage for real-time prices")
        return AlphaVantageService()


# Factory instance
data_source_factory = DataSourceFactory()

