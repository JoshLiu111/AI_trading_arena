"""
Base LLM client interface.
All LLM clients should implement this interface.
"""
from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """
    Base class for all LLM clients.
    Defines the interface that all LLM clients must implement.
    """

    @abstractmethod
    def chat(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return the response.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Raw text response from the LLM
        """
        pass

