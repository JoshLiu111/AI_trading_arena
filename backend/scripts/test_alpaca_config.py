# backend/scripts/test_alpaca_config.py

"""
Test script to verify Alpaca API configuration
Run this script to check if your Alpaca credentials are correctly configured
"""

import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


def test_alpaca_config():
    """Test Alpaca API configuration"""
    print("=" * 60)
    print("Testing Alpaca API Configuration")
    print("=" * 60)
    
    # Check DATA_SOURCE
    print(f"\n1. DATA_SOURCE: {settings.DATA_SOURCE}")
    if settings.DATA_SOURCE.lower() != "alpaca":
        print("   ⚠️  WARNING: DATA_SOURCE is not set to 'alpaca'")
        print("   💡 Set DATA_SOURCE=alpaca in your .env file")
    else:
        print("   ✅ DATA_SOURCE is correctly set to 'alpaca'")
    
    # Check ALPACA_API_KEY
    print(f"\n2. ALPACA_API_KEY: ", end="")
    if settings.ALPACA_API_KEY and settings.ALPACA_API_KEY.strip():
        print(f"✅ Configured (length: {len(settings.ALPACA_API_KEY)})")
        print(f"   First 10 chars: {settings.ALPACA_API_KEY[:10]}...")
    else:
        print("❌ NOT CONFIGURED!")
        print("   💡 Add ALPACA_API_KEY=your_key_here to your .env file")
    
    # Check ALPACA_API_SECRET
    print(f"\n3. ALPACA_API_SECRET: ", end="")
    if settings.ALPACA_API_SECRET and settings.ALPACA_API_SECRET.strip():
        print(f"✅ Configured (length: {len(settings.ALPACA_API_SECRET)})")
        print(f"   First 10 chars: {settings.ALPACA_API_SECRET[:10]}...")
    else:
        print("❌ NOT CONFIGURED!")
        print("   💡 Add ALPACA_API_SECRET=your_secret_here to your .env file")
    
    # Check ALPACA_BASE_URL
    print(f"\n4. ALPACA_BASE_URL: {settings.ALPACA_BASE_URL}")
    if "paper-api" in settings.ALPACA_BASE_URL:
        print("   ✅ Using Paper Trading (recommended for testing)")
    elif "api.alpaca.markets" in settings.ALPACA_BASE_URL:
        print("   ⚠️  Using Live Trading API (be careful!)")
    else:
        print("   ⚠️  Unexpected base URL")
    
    # Check ALPACA_DATA_FEED
    print(f"\n5. ALPACA_DATA_FEED: {settings.ALPACA_DATA_FEED}")
    if settings.ALPACA_DATA_FEED.lower() == "iex":
        print("   ✅ Using IEX data feed (free)")
    elif settings.ALPACA_DATA_FEED.lower() == "sip":
        print("   ℹ️  Using SIP data feed (premium)")
    else:
        print("   ⚠️  Unknown data feed")
    
    # Test API connection
    print("\n" + "=" * 60)
    print("Testing Alpaca API Connection...")
    print("=" * 60)
    
    if not settings.ALPACA_API_KEY or not settings.ALPACA_API_SECRET:
        print("\n❌ Cannot test connection: API credentials missing")
        return False
    
    try:
        import alpaca_trade_api as tradeapi
        
        api = tradeapi.REST(
            settings.ALPACA_API_KEY,
            settings.ALPACA_API_SECRET,
            settings.ALPACA_BASE_URL,
            api_version='v2'
        )
        
        # Test connection by getting account info
        account = api.get_account()
        print(f"\n✅ Successfully connected to Alpaca API!")
        print(f"   Account Status: {account.status}")
        print(f"   Trading Blocked: {account.trading_blocked}")
        print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
        
        # Test getting a stock snapshot
        print("\n" + "=" * 60)
        print("Testing Stock Data Fetch...")
        print("=" * 60)
        
        try:
            snapshot = api.get_snapshot("AAPL")
            if snapshot:
                print(f"\n✅ Successfully fetched AAPL snapshot")
                if hasattr(snapshot, 'latest_trade') and snapshot.latest_trade:
                    print(f"   Latest Trade Price: ${snapshot.latest_trade.p}")
                if hasattr(snapshot, 'daily_bar') and snapshot.daily_bar:
                    print(f"   Daily Bar Close: ${snapshot.daily_bar.c}")
            else:
                print("\n⚠️  Snapshot returned None (may be outside market hours)")
        except Exception as e:
            print(f"\n⚠️  Error fetching snapshot: {e}")
            print("   This is normal if market is closed")
        
        return True
        
    except ImportError:
        print("\n❌ alpaca-trade-api is not installed")
        print("   💡 Install it with: pip install alpaca-trade-api")
        return False
    except Exception as e:
        print(f"\n❌ Error connecting to Alpaca API: {e}")
        print("\n   Possible issues:")
        print("   1. Invalid API credentials")
        print("   2. Network connection problem")
        print("   3. API endpoint incorrect")
        return False


if __name__ == "__main__":
    success = test_alpaca_config()
    print("\n" + "=" * 60)
    if success:
        print("✅ Configuration test completed successfully!")
    else:
        print("❌ Configuration test failed. Please check the errors above.")
    print("=" * 60)
    sys.exit(0 if success else 1)

