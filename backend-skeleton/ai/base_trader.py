"""
Base trader class for AI trading.
Provides common functionality for all AI traders including JSON parsing.
"""
import json
import re


class BaseTrader:
    """
    Base class for all AI traders.
    Handles LLM interaction and JSON parsing.
    """

    def __init__(self, llm_client):
        """
        Initialize base trader with an LLM client.
        
        Args:
            llm_client: LLM client instance (e.g., OpenAIClient, AnthropicClient)
        """
        self.llm = llm_client

    def _clean_for_json(self, text: str) -> str:
        """
        Remove markdown and extract JSON from text.
        Handles cases where JSON is embedded in explanatory text.
        
        Args:
            text: Raw text from LLM response
            
        Returns:
            Cleaned JSON string
        """
        if not text:
            return ""
        
        # Remove markdown code blocks
        cleaned = text.replace("```json", "").replace("```", "").strip()
        
        # Try to find JSON object by counting braces
        json_objects = []
        brace_count = 0
        start_idx = -1
        
        for i, char in enumerate(cleaned):
            if char == '{':
                if brace_count == 0:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    json_objects.append(cleaned[start_idx:i+1])
                    start_idx = -1
        
        # Try to parse each potential JSON object
        for json_str in json_objects:
            try:
                json.loads(json_str)
                return json_str.strip()
            except:
                continue
        
        # Fallback: try regex to find JSON
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned)
        if json_match:
            return json_match.group(0)
        
        return cleaned

    def safe_json_load(self, raw_text: str) -> dict:
        """
        Safely parse JSON from LLM response.
        
        Args:
            raw_text: Raw text from LLM
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            ValueError: If JSON cannot be parsed
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Empty response from LLM")
        
        cleaned = self._clean_for_json(raw_text)
        
        if not cleaned or not cleaned.strip():
            raise ValueError("Empty response after cleaning")
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")

    def run(self, prompt: str) -> dict:
        """
        Execute a complete LLM call and parse the response.
        
        Args:
            prompt: Trading prompt to send to LLM
            
        Returns:
            Parsed decision dictionary
        """
        raw = self.llm.chat(prompt)
        data = self.safe_json_load(raw)
        return data

