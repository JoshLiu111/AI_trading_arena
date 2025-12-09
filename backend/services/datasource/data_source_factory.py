# backend/services/datasource/data_source_factory.py

"""
Data Source Factory
Creates Polygon.io data source instances
"""

from services.datasource.base_data_source import BaseDataSource
from services.datasource.polygon_service import PolygonService
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class DataSourceFactory:
    """Factory for creating Polygon.io data source instances"""
    
    @staticmethod
    def get_history_service() -> BaseDataSource:
        """Get historical data service - Polygon.io"""
        api_key = settings.POLYGON_API_KEY
        if not api_key or api_key.strip() == "":
            logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
            raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
        logger.info("Using Polygon.io for historical data")
        return PolygonService()
    
    @staticmethod
    def get_info_service() -> BaseDataSource:
        """Get company info service - Polygon.io"""
        api_key = settings.POLYGON_API_KEY
        if not api_key or api_key.strip() == "":
            logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
            raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
        logger.info("Using Polygon.io for company info")
        return PolygonService()
    
    @staticmethod
    def get_realtime_service() -> BaseDataSource:
        """Get real-time price service - Polygon.io"""
        api_key = settings.POLYGON_API_KEY
        if not api_key or api_key.strip() == "":
            logger.error("Polygon API key not configured! Please set POLYGON_API_KEY environment variable.")
            raise ValueError("Polygon API key is required but not configured. Please set POLYGON_API_KEY environment variable.")
        logger.info("Using Polygon.io for real-time prices")
        return PolygonService()


# Factory instance
data_source_factory = DataSourceFactory()

