"""
Gemini trader implementation.
AI trader using Google's Gemini models.
"""
from ai.base_trader import BaseTrader
from ai.llm_clients.gemini_client import GeminiClient


class GeminiTrader(BaseTrader):
    """
    Gemini-based AI trader.
    Uses Google's Gemini models for trading decisions.
    Free tier available with generous rate limits.
    """

    def __init__(self, account_id: int = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini trader.
        
        Args:
            account_id: Account ID (optional, for logging)
            model: Gemini model name (default: gemini-2.0-flash-exp)
        """
        llm_client = GeminiClient(model=model)
        super().__init__(llm_client)
        self.account_id = account_id

