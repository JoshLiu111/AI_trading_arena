"""
Google Gemini LLM client implementation.
Gemini offers free tier with good rate limits.
"""
import os
import google.generativeai as genai
from .base_client import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """
    Google Gemini API client for trading decisions.
    Free tier available with generous rate limits.
    """

    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Model name to use (default: gemini-2.0-flash-exp)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        self.model_name = model
        
        if not self.api_key:
            raise ValueError("Google API key not configured")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _clean_text(self, text: str) -> str:
        """Remove markdown code blocks from response."""
        if not text:
            return ""
        return text.replace("```json", "").replace("```", "").strip()

    def chat(self, prompt: str) -> str:
        """
        Send prompt to Gemini and return response.
        
        Args:
            prompt: Trading prompt
            
        Returns:
            LLM response text
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 512,
                    "temperature": 0.7,
                }
            )
            
            raw_text = response.text or ""
            return self._clean_text(raw_text)
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")

