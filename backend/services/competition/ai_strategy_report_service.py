# backend/services/competition/ai_strategy_report_service.py

"""
AI Strategy Report Service - Generate trading strategies using LLM
"""

import json
from typing import Dict, List, Optional
from datetime import date
import httpx

from config import settings


class AIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o-mini"  # Cost-effective model
    
    async def generate_strategy(
        self, 
        account_name: str,
        balance: float,
        historical_data_text: str,
        existing_positions: List[Dict] = None
    ) -> Dict:
        """
        Generate a 7-day trading strategy based on historical data
        Returns strategy with selected stocks and trading metrics for buy/sell decisions
        
        Returns:
        {
            "summary": "Strategy summary explaining analysis and stock selection",
            "selected_stocks": ["AAPL", "META", "TSLA"],  # AI free choice, recommend 3-5 stocks
            "trading_strategies": [
                {
                    "ticker": "AAPL",
                    "buy_metrics": {
                        "description": "Text description: Buy when price is below 7-day average and RSI < 30",
                        "condition": "price < 7_day_avg AND rsi < 30"
                    },
                    "sell_metrics": {
                        "description": "Text description: Sell when price is above 7-day average and RSI > 70",
                        "condition": "price > 7_day_avg AND rsi > 70"
                    },
                    "quantity": 10,
                    "rationale": "Reason for selecting this stock"
                },
                ...
            ]
        }
        """
        prompt = f"""You are participating in a 7-day stock trading competition. You need to select stocks you want to trade from the following stocks, and create a 7-day trading strategy for each selected stock to guide buy and sell points. Please determine the buy/sell metrics based on the 7-day historical data.

Here is the 7-day historical data for 10 stocks:
{historical_data_text}

Return a JSON format strategy report that includes a summary and for each selected stock, specify under what metrics to buy and under what metrics to sell.

Respond in JSON format:
{{
    "summary": "2-3 sentence summary explaining your analysis and why these stocks were selected",
    "selected_stocks": ["SYMBOL1", "SYMBOL2", "SYMBOL3"],
    "trading_strategies": [
        {{
            "ticker": "SYMBOL1",
            "buy_metrics": {{
                "description": "Text description: Under what metrics to buy (e.g., buy when price is below 7-day average and RSI < 30)",
                "condition": "price < 7_day_avg AND rsi < 30"
            }},
            "sell_metrics": {{
                "description": "Text description: Under what metrics to sell (e.g., sell when price is above 7-day average and RSI > 70)",
                "condition": "price > 7_day_avg AND rsi > 70"
            }},
            "quantity": NUMBER,
            "rationale": "Reason for selecting this stock"
        }},
        {{
            "ticker": "SYMBOL2",
            "buy_metrics": {{
                "description": "...",
                "condition": "..."
            }},
            "sell_metrics": {{
                "description": "...",
                "condition": "..."
            }},
            "quantity": NUMBER,
            "rationale": "..."
        }}
    ]
}}

Rules:
- Analyze the 7-day historical data and select 3-5 stocks with trading opportunities (recommend 3-5, do not exceed 10)
- Create buy and sell metrics for each stock based on price trends, volatility, volume, etc. from the 7-day historical data
- Both buy_metrics and sell_metrics must include description (text description) and condition (structured condition)
- quantity is the suggested number of shares per trade (consider account balance, suggest 10-50 shares)
- Buy/sell metrics should be clear and specific, able to guide 7-day trading decisions
"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 2000  # Increased for 7-day trading plan with detailed actions
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "choices" not in response_data or not response_data["choices"]:
                        return self._fallback_strategy()
                    
                    content = response_data["choices"][0]["message"]["content"]
                    # Parse JSON from response
                    content = content.strip()
                    if content.startswith("```"):
                        # Remove markdown code blocks
                        parts = content.split("```")
                        if len(parts) > 1:
                            content = parts[1]
                            if content.startswith("json"):
                                content = content[4:].strip()
                    
                    try:
                        strategy = json.loads(content)
                        # Validate strategy format
                        if not isinstance(strategy, dict):
                            raise ValueError("Strategy is not a dictionary")
                        if "selected_stocks" not in strategy:
                            raise ValueError("Strategy missing 'selected_stocks' field")
                        selected_stocks = strategy.get("selected_stocks", [])
                        if not isinstance(selected_stocks, list):
                            raise ValueError("selected_stocks must be a list")
                        if len(selected_stocks) < 1 or len(selected_stocks) > 10:
                            from core.logging import get_logger
                            logger = get_logger(__name__)
                            logger.warning(f"Strategy selected {len(selected_stocks)} stocks, expected 1-10")
                        
                        # Validate trading_strategies (new format)
                        if "trading_strategies" in strategy:
                            strategies = strategy.get("trading_strategies", [])
                            if not isinstance(strategies, list):
                                raise ValueError("trading_strategies must be a list")
                            if len(strategies) != len(selected_stocks):
                                raise ValueError(f"trading_strategies count ({len(strategies)}) must match selected_stocks count ({len(selected_stocks)})")
                            
                            for i, strat in enumerate(strategies):
                                if not isinstance(strat, dict):
                                    raise ValueError(f"Trading strategy {i+1} is not a dictionary")
                                if "ticker" not in strat:
                                    raise ValueError(f"Trading strategy {i+1} missing 'ticker' field")
                                if "buy_metrics" not in strat:
                                    raise ValueError(f"Trading strategy {i+1} missing 'buy_metrics' field")
                                if "sell_metrics" not in strat:
                                    raise ValueError(f"Trading strategy {i+1} missing 'sell_metrics' field")
                                
                                # Validate buy_metrics
                                buy_metrics = strat.get("buy_metrics", {})
                                if not isinstance(buy_metrics, dict):
                                    raise ValueError(f"Trading strategy {i+1} buy_metrics must be a dictionary")
                                if "description" not in buy_metrics:
                                    raise ValueError(f"Trading strategy {i+1} buy_metrics missing 'description' field")
                                if "condition" not in buy_metrics:
                                    raise ValueError(f"Trading strategy {i+1} buy_metrics missing 'condition' field")
                                
                                # Validate sell_metrics
                                sell_metrics = strat.get("sell_metrics", {})
                                if not isinstance(sell_metrics, dict):
                                    raise ValueError(f"Trading strategy {i+1} sell_metrics must be a dictionary")
                                if "description" not in sell_metrics:
                                    raise ValueError(f"Trading strategy {i+1} sell_metrics missing 'description' field")
                                if "condition" not in sell_metrics:
                                    raise ValueError(f"Trading strategy {i+1} sell_metrics missing 'condition' field")
                        
                        # Validate stock_preferences (old format, for backward compatibility)
                        if "stock_preferences" in strategy:
                            prefs = strategy.get("stock_preferences", [])
                            if not isinstance(prefs, list):
                                raise ValueError("stock_preferences must be a list")
                            for i, pref in enumerate(prefs):
                                if not isinstance(pref, dict):
                                    raise ValueError(f"Stock preference {i+1} is not a dictionary")
                                if "ticker" not in pref:
                                    raise ValueError(f"Stock preference {i+1} missing 'ticker' field")
                        
                        return strategy
                    except json.JSONDecodeError as e:
                        from core.logging import get_logger
                        logger = get_logger(__name__)
                        logger.error(f"AI JSON parse error: {e}")
                        logger.debug(f"   Content preview: {content[:500]}")
                        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
                    except ValueError as e:
                        from core.logging import get_logger
                        logger = get_logger(__name__)
                        logger.exception("AI strategy validation error")
                        raise
                else:
                    from core.logging import get_logger
                    logger = get_logger(__name__)
                    error_text = response.text[:500] if hasattr(response, 'text') else str(response)
                    logger.error(f"AI API error: {response.status_code} - {error_text}")
                    raise ValueError(f"OpenAI API returned status {response.status_code}: {error_text}")
                    
        except ValueError as e:
            # Re-raise validation errors
            raise
        except httpx.TimeoutException as e:
            from core.logging import get_logger
            logger = get_logger(__name__)
            logger.exception("AI API timeout")
            raise ValueError(f"OpenAI API request timed out: {str(e)}")
        except httpx.RequestError as e:
            from core.logging import get_logger
            logger = get_logger(__name__)
            logger.exception("AI API request error")
            raise ValueError(f"OpenAI API request failed: {str(e)}")
        except Exception as e:
            from core.logging import get_logger
            logger = get_logger(__name__)
            logger.exception("AI Error")
            raise ValueError(f"Unexpected error generating strategy: {str(e)}")
    
    async def should_trade(
        self,
        ticker: str,
        current_price: float,
        account_balance: float,
        current_position: Optional[Dict] = None,
        historical_data: Optional[List[Dict]] = None,
        stock_preference: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Ask AI to decide if we should trade this stock right now
        
        Returns:
        {
            "should_trade": true/false,
            "action": "BUY" | "SELL" | "HOLD",
            "quantity": NUMBER (if should_trade is true),
            "rationale": "Brief explanation"
        }
        or None if error
        """
        position_text = ""
        if current_position:
            quantity = current_position.get('quantity', 0)
            avg_price = current_position.get('avg_price', 0.0)
            last_buy_date = current_position.get('last_buy_date')
            from datetime import date
            today = date.today()
            
            position_text = f"\nCurrent Position: {quantity} shares @ avg ${avg_price:.2f}"
            if last_buy_date:
                buy_date = date.fromisoformat(last_buy_date) if isinstance(last_buy_date, str) else last_buy_date
                if buy_date == today:
                    position_text += "\nWARNING: This position was bought TODAY. T+1 rule applies - cannot sell until next trading day."
                else:
                    position_text += f"\nPosition bought on: {buy_date.isoformat()} (can sell today)"
            else:
                position_text += "\nNote: Buy date unknown - assume T+1 rule may apply if bought today"
        else:
            position_text = "\nCurrent Position: None"
        
        history_text = ""
        if historical_data:
            import json
            history_text = f"\n\n7-Day Historical Data:\n{json.dumps(historical_data, indent=2)}"
        
        preference_text = ""
        if stock_preference:
            preference_text = f"\n\nStock Preference: {stock_preference.get('rationale', 'No specific preference')}"
        
        prompt = f"""You are a trading AI making a trading decision.

Stock: {ticker}
Current Price: ${current_price:.2f}
Account Balance: ${account_balance:,.2f}
{position_text}{history_text}{preference_text}

Based on the current price, historical data, and your position, decide if you should trade NOW.

IMPORTANT: T+1 Trading Rule - Stocks bought today cannot be sold until the next trading day. If you bought this stock today, you must wait until tomorrow to sell it.

Respond in JSON format:
{{
    "should_trade": true/false,
    "action": "BUY" | "SELL" | "HOLD",
    "quantity": NUMBER (only if should_trade is true, suggest 10-50 shares),
    "rationale": "Brief 1-sentence explanation of your decision"
}}

Rules:
- T+1 Trading Rule: Stocks purchased today cannot be sold on the same day. You must wait until the next trading day to sell stocks you bought today.
- BUY only if: no current position AND price looks good based on historical data
- SELL only if: have position AND the stock was NOT bought today AND it's a good time to take profit
- HOLD if: have position but not a good time to sell, OR no position but not a good time to buy, OR have position but stock was bought today (must wait for T+1)
- Consider the 7-day price trend and current price relative to historical range
- Be conservative with quantities
- Only trade if there's a clear opportunity
"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.5,  # Lower temperature for more consistent decisions
                        "max_tokens": 300
                    },
                    timeout=15.0  # Shorter timeout for faster decisions
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "choices" not in response_data or not response_data["choices"]:
                        return None
                    
                    content = response_data["choices"][0]["message"]["content"]
                    content = content.strip()
                    if content.startswith("```"):
                        parts = content.split("```")
                        if len(parts) > 1:
                            content = parts[1]
                            if content.startswith("json"):
                                content = content[4:].strip()
                    
                    try:
                        decision = json.loads(content)
                        # Validate decision format
                        if not isinstance(decision, dict):
                            return None
                        if "should_trade" not in decision or "action" not in decision:
                            return None
                        if decision.get("should_trade") and "quantity" not in decision:
                            return None
                        return decision
                    except json.JSONDecodeError:
                        from core.logging import get_logger
                        logger = get_logger(__name__)
                        logger.warning(f"Failed to parse trade decision JSON for {ticker}")
                        return None
                else:
                    from core.logging import get_logger
                    logger = get_logger(__name__)
                    logger.error(f"AI API error in should_trade: {response.status_code}")
                    return None
        except Exception as e:
            from core.logging import get_logger
            logger = get_logger(__name__)
            logger.exception(f"Error in should_trade for {ticker}")
            return None
    
    def _fallback_strategy(self) -> Dict:
        """Fallback strategy when AI fails"""
        return {
            "summary": "Hold current positions. Market conditions unclear.",
            "selected_stocks": [],
            "trading_rules": []
        }


# Singleton instance
ai_service = AIService()
