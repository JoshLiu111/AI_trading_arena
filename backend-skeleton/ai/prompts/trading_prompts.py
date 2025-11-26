"""
Trading prompt templates.
Builds prompts for AI traders based on account status and market data.
"""

def build_trading_prompt(
    account: dict,
    holdings: list,
    market_data: dict,
    style: str = "balanced"
) -> str:
    """
    Build trading prompt with account and market information.
    
    Args:
        account: Account information (balance, total_value, etc.)
        holdings: List of current holdings
        market_data: Dictionary of {ticker: current_price}
        style: Trading style (e.g., "balanced", "aggressive", "conservative")
        
    Returns:
        Formatted trading prompt string
    """
    # Format holdings information
    holdings_str = ""
    if holdings and len(holdings) > 0:
        holdings_str = "\n".join([
            f"  - {h.get('ticker', 'N/A')}: {h.get('quantity', 0)} shares, "
            f"Avg Cost: ${h.get('avg_cost', 0):.2f}, "
            f"Current Price: ${h.get('current_price', 0):.2f}"
            for h in holdings
        ])
    else:
        holdings_str = "  (No holdings)"
    
    # Format market data
    market_data_str = "\n".join([
        f"  {ticker}: ${price:.2f}" 
        for ticker, price in sorted(market_data.items())
    ])
    
    return f"""
You are an AI stock trader with a {style} trading style.

Account Status:
  Cash Balance: ${account.get('balance', 0):,.2f}
  Total Portfolio Value: ${account.get('total_value', account.get('balance', 0)):,.2f}
  Initial Balance: ${account.get('initial_balance', 1000000):,.2f}

Current Holdings:
{holdings_str}

Current Market Prices:
{market_data_str}

Based on the above information, make a trading decision. You can:
- BUY: Purchase stocks if you see opportunities
- SELL: Sell existing holdings if needed
- HOLD: Do nothing if the market conditions are not favorable

Respond with a JSON object in this exact format:
{{
  "action": "BUY" | "SELL" | "HOLD",
  "ticker": "AAPL" (required if action is BUY or SELL),
  "quantity": 10 (required if action is BUY or SELL),
  "rationale": "Your reasoning for this decision"
}}

If action is HOLD, ticker and quantity can be omitted.
"""

