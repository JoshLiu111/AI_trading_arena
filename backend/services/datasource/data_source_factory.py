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
        """Get historical data service - Always use Polygon for historical data"""
        api_key = settings.POLYGON_API_KEY
        if not api_key or api_key.strip() == "":
            logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
            raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
        logger.info("Using Polygon.io for historical data")
        return PolygonService()
    
    @staticmethod
    def get_info_service() -> BaseDataSource:
        """Get company info service - Always use Polygon for company info"""
        api_key = settings.POLYGON_API_KEY
        if not api_key or api_key.strip() == "":
            logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
            raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
        logger.info("Using Polygon.io for company info")
        return PolygonService()
    
    @staticmethod
    def get_realtime_service() -> BaseDataSource:
        """Get real-time price service
        Priority: Alpaca (if configured) → Polygon REST API (fallback)
        Note: WebSocket is handled separately, this is for REST API only
        """
        data_source = settings.DATA_SOURCE.lower()
        
        if data_source == "alpaca":
            from services.datasource.alpaca_service import AlpacaService
            api_key = settings.ALPACA_API_KEY
            api_secret = settings.ALPACA_API_SECRET
            if api_key and api_secret and api_key.strip() != "" and api_secret.strip() != "":
                logger.info("Using Alpaca Markets REST API for real-time prices")
                return AlpacaService()
            else:
                logger.warning("Alpaca API credentials not configured! Falling back to Polygon REST API for real-time prices.")
                # Fallback to Polygon REST API
                api_key = settings.POLYGON_API_KEY
                if not api_key or api_key.strip() == "":
                    logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
                    raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
                logger.info("Using Polygon.io REST API for real-time prices (fallback)")
                return PolygonService()
        else:
            # Default to Polygon REST API
            api_key = settings.POLYGON_API_KEY
            if not api_key or api_key.strip() == "":
                logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
                raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
            logger.info("Using Polygon.io REST API for real-time prices")
            return PolygonService()


# Factory instance
data_source_factory = DataSourceFactory()

