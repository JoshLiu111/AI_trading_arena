# backend/cleanup_accounts.py

"""
Cleanup script to remove all accounts except human_player and openai_player
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from models.schema.account import Account

def cleanup_accounts():
    """Delete all accounts except human_player and openai_player"""
    db = SessionLocal()
    
    try:
        # Get all accounts
        all_accounts = db.query(Account).all()
        
        # Accounts to keep
        keep_accounts = ["human_player", "openai_player"]
        
        deleted_count = 0
        kept_count = 0
        
        for account in all_accounts:
            if account.account_name in keep_accounts:
                kept_count += 1
                print(f"✅ Keeping: {account.account_name} ({account.display_name})")
            else:
                # Delete related transactions
                from models.schema.transaction import Transaction
                from models.schema.strategy import TradingStrategy
                
                tx_count = db.query(Transaction).filter(Transaction.account_id == account.id).count()
                st_count = db.query(TradingStrategy).filter(TradingStrategy.account_id == account.id).count()
                
                db.query(Transaction).filter(Transaction.account_id == account.id).delete()
                db.query(TradingStrategy).filter(TradingStrategy.account_id == account.id).delete()
                db.delete(account)
                
                deleted_count += 1
                print(f"❌ Deleted: {account.account_name} ({account.display_name}) - {tx_count} transactions, {st_count} strategies")
        
        db.commit()
        
        print(f"\n📊 Summary:")
        print(f"   Kept: {kept_count} accounts")
        print(f"   Deleted: {deleted_count} accounts")
        
        # Show remaining accounts
        remaining = db.query(Account).all()
        print(f"\n📋 Remaining accounts:")
        for acc in remaining:
            print(f"   - {acc.account_name} ({acc.display_name}) - {acc.account_type}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Cleaning up accounts...\n")
    cleanup_accounts()
    print("\n✅ Cleanup complete!")

