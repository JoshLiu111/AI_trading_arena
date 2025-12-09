# backend/services/datasource/data_source_factory.py

"""
Data Source Factory
Creates appropriate data source instances based on configuration
"""

from services.datasource.base_data_source import BaseDataSource
from services.datasource.yahoo_history_price_service import YahooService
from services.datasource.yahoo_info_service import YahooInfoService
from services.datasource.alpha_vantage_service import AlphaVantageService
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class DataSourceFactory:
    """Factory for creating data source instances"""
    
    @staticmethod
    def get_history_service() -> BaseDataSource:
        """Get historical data service based on configuration"""
        if settings.DATA_SOURCE == "alpha_vantage":
            # Check if API key is configured
            api_key = settings.ALPHA_VANTAGE_API_KEY
            if not api_key or api_key.strip() == "":
                logger.error("Alpha Vantage API key not configured! Please set ALPHA_VANTAGE_API_KEY environment variable.")
                logger.error("Cannot proceed without API key. Please configure it in Render dashboard.")
                raise ValueError("Alpha Vantage API key is required but not configured. Please set ALPHA_VANTAGE_API_KEY environment variable.")
            logger.info("Using Alpha Vantage for historical data")
            return AlphaVantageService()
        else:
            logger.info("Using Yahoo Finance for historical data")
            return YahooService()
    
    @staticmethod
    def get_info_service() -> BaseDataSource:
        """Get company info service based on configuration"""
        if settings.DATA_SOURCE == "alpha_vantage":
            # Check if API key is configured
            api_key = settings.ALPHA_VANTAGE_API_KEY
            if not api_key or api_key.strip() == "":
                logger.error("Alpha Vantage API key not configured! Please set ALPHA_VANTAGE_API_KEY environment variable.")
                logger.error("Cannot proceed without API key. Please configure it in Render dashboard.")
                raise ValueError("Alpha Vantage API key is required but not configured. Please set ALPHA_VANTAGE_API_KEY environment variable.")
            logger.info("Using Alpha Vantage for company info")
            return AlphaVantageService()
        else:
            logger.info("Using Yahoo Finance for company info")
            return YahooInfoService()
    
    @staticmethod
    def get_realtime_service() -> BaseDataSource:
        """Get real-time price service based on configuration"""
        if settings.DATA_SOURCE == "alpha_vantage":
            # Check if API key is configured
            api_key = settings.ALPHA_VANTAGE_API_KEY
            if not api_key or api_key.strip() == "":
                logger.error("Alpha Vantage API key not configured! Please set ALPHA_VANTAGE_API_KEY environment variable.")
                logger.error("Cannot proceed without API key. Please configure it in Render dashboard.")
                raise ValueError("Alpha Vantage API key is required but not configured. Please set ALPHA_VANTAGE_API_KEY environment variable.")
            logger.info("Using Alpha Vantage for real-time prices")
            return AlphaVantageService()
        else:
            logger.info("Using Yahoo Finance for real-time prices")
            return YahooService()


# Factory instance
data_source_factory = DataSourceFactory()

