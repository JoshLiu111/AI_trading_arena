"""
Groq trader implementation.
AI trader using Groq's fast inference with open-source models.
"""
from ai.base_trader import BaseTrader
from ai.llm_clients.groq_client import GroqClient


class GroqTrader(BaseTrader):
    """
    Groq-based AI trader.
    Uses Groq's fast inference with open-source models (e.g., Llama).
    Free tier available with very fast response times.
    """

    def __init__(self, account_id: int = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq trader.
        
        Args:
            account_id: Account ID (optional, for logging)
            model: Groq model name (default: llama-3.3-70b-versatile)
        """
        llm_client = GroqClient(model=model)
        super().__init__(llm_client)
        self.account_id = account_id

