# backend/services/datasource/refresh_historical_data_service.py

"""
Refresh Historical Data Service - Refresh and save stock historical data to database
Handles database operations for stock data refresh
"""

from typing import Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session

from config import settings
from models.crud.stock_crud import get_stock, create_stock
from models.crud.stock_price_crud import create_price_data
from services.datasource.yahoo_history_price_service import YahooService
from services.datasource.yahoo_info_service import yahoo_info_service


class RefreshHistoricalDataService:
    """Service for refreshing and saving stock historical data to database"""
    
    def __init__(self):
        self.yahoo = YahooService()
        self.stock_pool = settings.STOCK_POOL
    
    def refresh_historical_data(self, db: Session, days: int = 7) -> int:
        """
        Refresh historical data for all stocks and save to database
        This is business logic, not data fetching
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days + 5)  # Extra days for market closures
        
        # Fetch data from datasource (pure data fetching)
        bulk_data = self.yahoo.download_bulk(
            self.stock_pool,
            start=start_date.isoformat(),
            end=end_date.isoformat()
        )
        
        count = 0
        for ticker, history in bulk_data.items():
            # Ensure stock exists in database
            if not get_stock(db, ticker):
                info = yahoo_info_service.get_company_info(ticker)
                if info:
                    create_stock(db, **info)
            
            # Save price data to database
            for price in history[-days:]:  # Last N days only
                try:
                    create_price_data(
                        db,
                        ticker=ticker,
                        date=price["date"],
                        open=price.get("open"),
                        high=price.get("high"),
                        low=price.get("low"),
                        close=price.get("close"),
                        volume=price.get("volume"),
                        adj_close=price.get("adj_close")
                    )
                    count += 1
                except Exception:
                    pass  # Skip duplicates
        
        db.commit()
        return count


# Singleton instance
refresh_historical_data_service = RefreshHistoricalDataService()

