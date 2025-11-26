"""
Anthropic Claude LLM client implementation.
Claude offers free tier with generous rate limits.
"""
import os
from anthropic import Anthropic
from .base_client import BaseLLMClient


class AnthropicClient(BaseLLMClient):
    """
    Anthropic Claude API client for trading decisions.
    Free tier available with good rate limits.
    """

    def __init__(self, api_key: str = None, model: str = "claude-3-haiku-20240307"):
        """
        Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name to use (default: claude-3-haiku-20240307 - free tier friendly)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def _clean_text(self, text: str) -> str:
        """Remove markdown code blocks from response."""
        if not text:
            return ""
        return text.replace("```json", "").replace("```", "").strip()

    def chat(self, prompt: str) -> str:
        """
        Send prompt to Claude and return response.
        
        Args:
            prompt: Trading prompt
            
        Returns:
            LLM response text
        """
        if not self.client:
            raise ValueError("Anthropic API key not configured")
        
        try:
            # Limit prompt length to avoid token limits
            max_prompt_length = 100000
            if len(prompt) > max_prompt_length:
                prompt = prompt[:max_prompt_length] + "\n\n[Content truncated]"
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            if not response.content or len(response.content) == 0:
                raise ValueError("Empty response from Claude")
            
            raw_text = response.content[0].text
            return self._clean_text(raw_text)
        except Exception as e:
            raise ValueError(f"Anthropic API error: {str(e)}")

