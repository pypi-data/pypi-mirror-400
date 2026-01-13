from abc import ABC, abstractmethod
from typing import Any, Dict

from ibraahim.core.types import LLMResult

class BaseLLM(ABC):
    """Abstract base class for all LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, config: Dict[str, Any] | None = None) -> LLMResult:
        """
        Generate text from the LLM.
        
        Args:
            prompt: The input text.
            config: Optional provider-specific overrides (e.g. temperature).
            
        Returns:
            LLMResult containing the generated text and metadata.
        """
        pass
    
    def __call__(self, prompt: str, config: Dict[str, Any] | None = None) -> LLMResult:
        """Allows calling the instance directly like a function."""
        return self.generate(prompt, config)
