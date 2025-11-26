"""
Initialize 100 stocks in the database.
Fetches company information from Yahoo Finance and saves to database.

Usage:
    python scripts/init_stocks.py
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from models.database import get_session
from models.stock_models import Stock
from config.stock_list import STOCK_POOL_100


def fetch_stock_info(ticker: str):
    """
    Fetch stock information from Yahoo Finance.
    Returns a dictionary with stock data.
    """
    try:
        import yfinance as yf
        
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        
        if not info:
            return None
        
        # Extract relevant information
        return {
            "ticker": ticker.upper(),
            "name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector") or "Unknown",
            "market_cap": int(info.get("marketCap", 0)) if info.get("marketCap") else None,
            "exchange": info.get("exchange") or "",
            "currency": info.get("currency") or "USD",
            "description": info.get("longBusinessSummary") or "",
            "homepage_url": info.get("website") or "",
        }
    except Exception as e:
        print(f"   ⚠️ Error fetching {ticker}: {e}")
        return None


def main():
    print("=" * 60)
    print("Initializing 100 Stocks")
    print("=" * 60)
    print()
    
    # Check existing stocks
    with get_session() as session:
        existing_tickers = {s.ticker for s in session.query(Stock.ticker).all()}
    
    missing_tickers = [t for t in STOCK_POOL_100 if t.upper() not in existing_tickers]
    
    print(f"📌 Existing stocks: {len(existing_tickers)}")
    print(f"📌 Stocks to add: {len(missing_tickers)}")
    print()
    
    if not missing_tickers:
        print("✅ All stocks already initialized!")
        return
    
    print("Starting to fetch stock information from Yahoo Finance...")
    print()
    
    success_count = 0
    failed_tickers = []
    batch = []
    
    for idx, ticker in enumerate(missing_tickers, 1):
        print(f"[{idx}/{len(missing_tickers)}] Fetching {ticker}...", end=" ")
        
        stock_data = fetch_stock_info(ticker)
        
        if not stock_data:
            print("❌ Failed")
            failed_tickers.append(ticker)
            continue
        
        batch.append(stock_data)
        print("✅")
        
        # Batch insert every 10 stocks
        if len(batch) >= 10:
            with get_session() as session:
                for data in batch:
                    # Check if already exists (race condition protection)
                    existing = session.query(Stock).filter_by(ticker=data["ticker"]).first()
                    if not existing:
                        stock = Stock(**data)
                        session.add(stock)
                session.commit()
            
            success_count += len(batch)
            print(f"   💾 Saved batch of {len(batch)} stocks")
            batch.clear()
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Save remaining stocks
    if batch:
        with get_session() as session:
            for data in batch:
                existing = session.query(Stock).filter_by(ticker=data["ticker"]).first()
                if not existing:
                    stock = Stock(**data)
                    session.add(stock)
            session.commit()
        
        success_count += len(batch)
        print(f"   💾 Saved final batch of {len(batch)} stocks")
    
    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✅ Successfully added: {success_count} stocks")
    if failed_tickers:
        print(f"❌ Failed: {len(failed_tickers)} stocks")
        print(f"   Failed tickers: {', '.join(failed_tickers)}")
    print()
    print("🎉 Stock initialization complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

