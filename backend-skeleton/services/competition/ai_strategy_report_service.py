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
        metrics_text: str,
        existing_positions: List[Dict] = None
    ) -> Dict:
        """
        Generate a trading strategy based on market metrics
        
        Returns:
        {
            "summary": "Brief strategy summary",
            "actions": [
                {"ticker": "AAPL", "action": "BUY", "quantity": 10, "rationale": "..."},
                ...
            ],
            "selected_stocks": ["AAPL", "MSFT", ...]
        }
        """
        positions_text = ""
        if existing_positions:
            positions_text = "\n\nCurrent Positions:\n" + "\n".join(
                f"- {p['ticker']}: {p['quantity']} shares @ ${p['avg_price']}"
                for p in existing_positions
            )
        
        prompt = f"""You are a trading AI for account "{account_name}".
Available Balance: ${balance:,.2f}
{positions_text}

{metrics_text}

Based on the above metrics, generate a brief trading strategy.
Respond in JSON format:
{{
    "summary": "2-3 sentence strategy summary",
    "actions": [
        {{"ticker": "SYMBOL", "action": "BUY|SELL", "quantity": NUMBER, "rationale": "brief reason"}}
    ],
    "selected_stocks": ["SYMBOL1", "SYMBOL2"]
}}

Rules:
- Maximum 3 trades per strategy
- BUY only if you have enough balance
- SELL only if you have the position
- Be conservative with quantities
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
                        "max_tokens": 500
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
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"AI JSON parse error: {e}, content: {content[:200]}")
                        return self._fallback_strategy()
                else:
                    print(f"AI API error: {response.status_code} - {response.text}")
                    return self._fallback_strategy()
                    
        except json.JSONDecodeError as e:
            print(f"AI JSON decode error: {e}")
            return self._fallback_strategy()
        except Exception as e:
            print(f"AI Error: {e}")
            return self._fallback_strategy()
    
    def _fallback_strategy(self) -> Dict:
        """Fallback strategy when AI fails"""
        return {
            "summary": "Hold current positions. Market conditions unclear.",
            "actions": [],
            "selected_stocks": []
        }


# Singleton instance
ai_service = AIService()
