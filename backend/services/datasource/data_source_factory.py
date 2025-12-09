# backend/services/datasource/data_source_factory.py

"""
Data Source Factory
Creates data source instances based on configuration (Polygon.io or Alpaca Markets)
"""

from services.datasource.base_data_source import BaseDataSource
from services.datasource.polygon_service import PolygonService
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class DataSourceFactory:
    """Factory for creating data source instances"""
    
    @staticmethod
    def get_history_service() -> BaseDataSource:
        """Get historical data service"""
        data_source = settings.DATA_SOURCE.lower()
        
        if data_source == "alpaca":
            from services.datasource.alpaca_service import AlpacaService
            api_key = settings.ALPACA_API_KEY
            api_secret = settings.ALPACA_API_SECRET
            if not api_key or not api_secret or api_key.strip() == "" or api_secret.strip() == "":
                logger.error("Alpaca API credentials not configured! Please set ALPACA_API_KEY and ALPACA_API_SECRET environment variables.")
                raise ValueError("Alpaca API credentials are required but not configured.")
            logger.info("Using Alpaca Markets for historical data")
            return AlpacaService()
        else:
            # Default to Polygon
            api_key = settings.POLYGON_API_KEY
            if not api_key or api_key.strip() == "":
                logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
                raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
            logger.info("Using Polygon.io for historical data")
            return PolygonService()
    
    @staticmethod
    def get_info_service() -> BaseDataSource:
        """Get company info service"""
        data_source = settings.DATA_SOURCE.lower()
        
        if data_source == "alpaca":
            from services.datasource.alpaca_service import AlpacaService
            api_key = settings.ALPACA_API_KEY
            api_secret = settings.ALPACA_API_SECRET
            if not api_key or not api_secret or api_key.strip() == "" or api_secret.strip() == "":
                logger.error("Alpaca API credentials not configured! Please set ALPACA_API_KEY and ALPACA_API_SECRET environment variables.")
                raise ValueError("Alpaca API credentials are required but not configured.")
            logger.info("Using Alpaca Markets for company info")
            return AlpacaService()
        else:
            # Default to Polygon
            api_key = settings.POLYGON_API_KEY
            if not api_key or api_key.strip() == "":
                logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
                raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
            logger.info("Using Polygon.io for company info")
            return PolygonService()
    
    @staticmethod
    def get_realtime_service() -> BaseDataSource:
        """Get real-time price service"""
        data_source = settings.DATA_SOURCE.lower()
        
        if data_source == "alpaca":
            from services.datasource.alpaca_service import AlpacaService
            api_key = settings.ALPACA_API_KEY
            api_secret = settings.ALPACA_API_SECRET
            if not api_key or not api_secret or api_key.strip() == "" or api_secret.strip() == "":
                logger.error("Alpaca API credentials not configured! Please set ALPACA_API_KEY and ALPACA_API_SECRET environment variables.")
                raise ValueError("Alpaca API credentials are required but not configured.")
            logger.info("Using Alpaca Markets for real-time prices")
            return AlpacaService()
        else:
            # Default to Polygon
            api_key = settings.POLYGON_API_KEY
            if not api_key or api_key.strip() == "":
                logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
                raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
            logger.info("Using Polygon.io for real-time prices")
            return PolygonService()


# Factory instance
data_source_factory = DataSourceFactory()

