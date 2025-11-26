"""
OpenAI LLM client implementation.
Example implementation for OpenAI API.
"""
import os
from openai import OpenAI
from .base_client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """
    OpenAI API client for trading decisions.
    """

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name to use (default: gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def chat(self, prompt: str) -> str:
        """
        Send prompt to OpenAI and return response.
        
        Args:
            prompt: Trading prompt
            
        Returns:
            LLM response text
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a stock trading assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=512,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"OpenAI API error: {str(e)}")

