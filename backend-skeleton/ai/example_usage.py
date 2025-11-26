"""
Example usage of the AI trading system.
This script demonstrates how to use different AI traders and trading engine.

Supports multiple LLM providers:
- Claude (FREE tier available)
- Gemini (FREE tier available)
- Groq (FREE tier available, very fast)
- OpenAI (paid)
"""
from models.database import get_session
from ai.trading_engine import TradingEngine
from models.account_models import Account

# Import traders (choose one based on your API key)
# from ai.traders.claude_trader import ClaudeTrader      # FREE tier
# from ai.traders.gemini_trader import GeminiTrader       # FREE tier
# from ai.traders.groq_trader import GroqTrader          # FREE tier, very fast
# from ai.traders.openai_trader import OpenAITrader      # Paid


def example_ai_trading(trader_type: str = "claude"):
    """
    Example: Run an AI trader for an account.
    
    Args:
        trader_type: Type of trader to use ('claude', 'gemini', 'groq', or 'openai')
    """
    # Initialize trader based on type
    if trader_type == "claude":
        from ai.traders.claude_trader import ClaudeTrader
        trader = ClaudeTrader(account_id=1)
        print("Using Claude trader (FREE tier)")
    elif trader_type == "gemini":
        from ai.traders.gemini_trader import GeminiTrader
        trader = GeminiTrader(account_id=1)
        print("Using Gemini trader (FREE tier)")
    elif trader_type == "groq":
        from ai.traders.groq_trader import GroqTrader
        trader = GroqTrader(account_id=1)
        print("Using Groq trader (FREE tier, very fast)")
    elif trader_type == "openai":
        from ai.traders.openai_trader import OpenAITrader
        trader = OpenAITrader(account_id=1, model="gpt-4o-mini")
        print("Using OpenAI trader (paid)")
    else:
        raise ValueError(f"Unknown trader type: {trader_type}")
    
    # Initialize trading engine
    engine = TradingEngine()
    
    # Market data (current prices)
    market_data = {
        "AAPL": 150.0,
        "MSFT": 350.0,
        "GOOGL": 140.0,
    }
    
    # Run trader
    with get_session() as session:
        # Check if account exists
        account = session.query(Account).filter_by(id=1).first()
        if not account:
            print("❌ Account not found. Please create an account first.")
            return
        
        print(f"Running AI trader for account: {account.display_name}")
        print(f"Current balance: ${account.balance:,.2f}")
        print(f"Market data: {market_data}")
        print("-" * 50)
        
        # Execute AI trading decision
        result = engine.run_trader(
            session=session,
            trader=trader,
            account_id=1,
            market_data=market_data
        )
        
        if result["success"]:
            print("✅ Trading decision executed successfully!")
            print(f"Decision: {result['decision']}")
            if result.get("transaction_id"):
                print(f"Transaction ID: {result['transaction_id']}")
        else:
            print(f"❌ Trading failed: {result.get('error', 'Unknown error')}")
            if result.get("decision"):
                print(f"Decision was: {result['decision']}")


if __name__ == "__main__":
    print("AI Trading Example")
    print("=" * 50)
    print("Available traders:")
    print("  - claude  (FREE tier) - Requires ANTHROPIC_API_KEY")
    print("  - gemini  (FREE tier) - Requires GOOGLE_API_KEY")
    print("  - groq    (FREE tier) - Requires GROQ_API_KEY")
    print("  - openai  (paid)      - Requires OPENAI_API_KEY")
    print("=" * 50)
    
    # Change this to test different traders
    TRADER_TYPE = "claude"  # Options: "claude", "gemini", "groq", "openai"
    
    try:
        example_ai_trading(TRADER_TYPE)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Set the appropriate API key in .env")
        print("  2. Installed the required package (e.g., pip install anthropic)")
        print("  3. Created an account in the database")
        import traceback
        traceback.print_exc()

