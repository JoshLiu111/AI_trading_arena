"""
Groq LLM client implementation.
Groq offers free tier with very fast inference using open-source models.
"""
import os
from groq import Groq
from .base_client import BaseLLMClient


class GroqClient(BaseLLMClient):
    """
    Groq API client for trading decisions.
    Free tier available with fast inference speeds.
    Uses open-source models like Llama.
    """

    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model name to use (default: llama-3.3-70b-versatile)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def _clean_text(self, text: str) -> str:
        """Remove markdown code blocks from response."""
        if not text:
            return ""
        return text.replace("```json", "").replace("```", "").strip()

    def chat(self, prompt: str) -> str:
        """
        Send prompt to Groq and return response.
        
        Args:
            prompt: Trading prompt
            
        Returns:
            LLM response text
        """
        if not self.client:
            raise ValueError("Groq API key not configured")
        
        try:
            # Limit prompt length to manage token usage
            max_prompt_length = 50000
            if len(prompt) > max_prompt_length:
                prompt = prompt[:max_prompt_length] + "\n\n[Content truncated]"
            
            # Try primary model first, fallback to smaller model if rate limited
            models_to_try = [
                self.model,
                "llama-3.1-8b-instant",  # Smaller model as fallback
            ]
            
            last_error = None
            for model_to_use in models_to_try:
                try:
                    response = self.client.chat.completions.create(
                        model=model_to_use,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=512,
                        temperature=0.7,
                    )
                    
                    if not response.choices or len(response.choices) == 0:
                        raise ValueError("Empty response from Groq")
                    
                    raw_text = response.choices[0].message.content
                    return self._clean_text(raw_text)
                except Exception as e:
                    last_error = e
                    if "rate limit" not in str(e).lower():
                        raise
                    # If rate limited, try next model
                    continue
            
            # If all models failed, raise the last error
            raise last_error
        except Exception as e:
            raise ValueError(f"Groq API error: {str(e)}")

