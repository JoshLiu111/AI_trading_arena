"""
OpenAI trader implementation.
Example AI trader using OpenAI's GPT models.
"""
from ai.base_trader import BaseTrader
from ai.llm_clients.openai_client import OpenAIClient


class OpenAITrader(BaseTrader):
    """
    OpenAI-based AI trader.
    Uses GPT models to make trading decisions.
    """

    def __init__(self, account_id: int = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI trader.
        
        Args:
            account_id: Account ID (optional, for logging)
            model: OpenAI model name
        """
        llm_client = OpenAIClient(model=model)
        super().__init__(llm_client)
        self.account_id = account_id

