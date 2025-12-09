# backend/refresh_stock_data.py

"""
Script to refresh historical stock data for all stocks in the pool
With rate limiting and retry mechanism
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from config import settings
from services.datasource.data_source_factory import data_source_factory
from models.crud.stock_crud import get_stock, create_stock
from models.crud.stock_price_crud import create_price_data
from datetime import date, timedelta

def refresh_all_stocks():
    """Refresh historical data for all stocks in the pool with rate limiting"""
    db = SessionLocal()
    data_source = data_source_factory.get_history_service()
    info_service = data_source_factory.get_info_service()
    
    try:
        print(f"🔄 Refreshing historical data for {len(settings.STOCK_POOL)} stocks...")
        print(f"📊 Stocks: {', '.join(settings.STOCK_POOL)}")
        print(f"📅 Days: {settings.HISTORY_DAYS}")
        print()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=settings.HISTORY_DAYS + 5)
        
        total_count = 0
        
        # Process each stock individually with delays to avoid rate limiting
        for i, ticker in enumerate(settings.STOCK_POOL, 1):
            print(f"[{i}/{len(settings.STOCK_POOL)}] Processing {ticker}...", end=" ", flush=True)
            
            try:
                # Add delay between requests (except first one)
                if i > 1:
                    time.sleep(2)  # 2 second delay between requests
                
                # Fetch historical data for this ticker
                history = data_source.get_historical_data(
                    ticker,
                    start=start_date.isoformat(),
                    end=end_date.isoformat()
                )
                
                if not history:
                    print("⚠️  No data")
                    continue
                
                # Ensure stock exists in database
                if not get_stock(db, ticker):
                    print("(creating stock record...)", end=" ", flush=True)
                    info = info_service.get_company_info(ticker)
                    if info:
                        create_stock(db, **info)
                    else:
                        # Create stock with minimal info if API fails
                        create_stock(
                            db,
                            ticker=ticker,
                            name=ticker,
                            sector="",
                            description="",
                            homepage_url="",
                            sic_description=""
                        )
                
                # Save price data
                saved = 0
                for price in history[-settings.HISTORY_DAYS:]:
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
                        saved += 1
                    except Exception:
                        pass  # Skip duplicates
                
                db.commit()
                total_count += saved
                print(f"✅ {saved} records saved")
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                db.rollback()
                # Wait longer if we hit rate limit
                if "429" in str(e) or "Too Many Requests" in str(e):
                    print(f"   ⏳ Rate limited, waiting 10 seconds...")
                    time.sleep(10)
        
        print(f"\n✅ Successfully saved {total_count} price records to database")
        
        # Verify data was saved
        from models.schema.stock_price import StockPrice
        total_records = db.query(StockPrice).count()
        print(f"📊 Total price records in database: {total_records}")
        
        # Show records per ticker
        print("\n📈 Records per ticker:")
        for ticker in settings.STOCK_POOL:
            ticker_count = db.query(StockPrice).filter(StockPrice.ticker == ticker).count()
            if ticker_count > 0:
                print(f"   ✅ {ticker}: {ticker_count} records")
            else:
                print(f"   ⚠️  {ticker}: 0 records")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting stock data refresh...\n")
    refresh_all_stocks()
    print("\n✅ Refresh complete!")

