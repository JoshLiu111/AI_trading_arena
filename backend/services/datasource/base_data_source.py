# backend/services/datasource/base_data_source.py

"""
Base Data Source Interface
Abstract base class for all stock data sources
Ensures consistent interface across different data providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseDataSource(ABC):
    """Abstract base class for stock data sources"""
    
    @abstractmethod
    def get_historical_data(
        self, 
        ticker: str, 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None,
        retries: int = 3
    ) -> List[Dict]:
        """
        Get historical price data for a single ticker
        
        Returns:
            List[Dict]: List of price data dictionaries with keys:
                - date: date object
                - open: float or None
                - high: float or None
                - low: float or None
                - close: float or None
                - volume: int or None
                - adj_close: float or None
        """
        pass
    
    @abstractmethod
    def download_bulk(
        self, 
        tickers: List[str], 
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Bulk download historical price data for multiple tickers
        
        Returns:
            Dict[str, List[Dict]]: Dictionary mapping ticker to list of price data
        """
        pass
    
    @abstractmethod
    def get_latest_prices_bulk(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get latest price data for multiple tickers (bulk fetch)
        
        Returns:
            Dict[str, Optional[Dict]]: Dictionary mapping ticker to price data dict with keys:
                - date: date object
                - open: float or None
                - high: float or None
                - low: float or None
                - close: float or None
                - volume: int or None
                - adj_close: float or None
        """
        pass
    
    @abstractmethod
    def get_company_info(self, ticker: str, retries: int = 3) -> Optional[Dict]:
        """
        Get basic company information
        
        Returns:
            Optional[Dict]: Company info dictionary with keys:
                - ticker: str
                - name: str
                - sector: str
                - description: str
                - homepage_url: str
                - sic_description: str
        """
        pass

