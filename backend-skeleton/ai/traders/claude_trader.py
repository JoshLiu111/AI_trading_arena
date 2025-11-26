"""
Claude trader implementation.
AI trader using Anthropic's Claude models.
"""
from ai.base_trader import BaseTrader
from ai.llm_clients.anthropic_client import AnthropicClient


class ClaudeTrader(BaseTrader):
    """
    Claude-based AI trader.
    Uses Anthropic's Claude models for trading decisions.
    Free tier available with good rate limits.
    """

    def __init__(self, account_id: int = None, model: str = "claude-3-haiku-20240307"):
        """
        Initialize Claude trader.
        
        Args:
            account_id: Account ID (optional, for logging)
            model: Claude model name (default: claude-3-haiku-20240307 - free tier friendly)
        """
        llm_client = AnthropicClient(model=model)
        super().__init__(llm_client)
        self.account_id = account_id

