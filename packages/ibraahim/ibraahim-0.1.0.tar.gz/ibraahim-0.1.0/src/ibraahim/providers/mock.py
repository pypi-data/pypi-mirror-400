from typing import Any, Dict, Optional
from ibraahim.core.llm import BaseLLM
from ibraahim.core.types import LLMResult, LLMUsage

class MockLLM(BaseLLM):
    """
    A mock LLM that returns pre-determined responses.
    Useful for testing.
    """
    
    def __init__(self, response: str = "Mock response"):
        self.response = response
        
    def generate(self, prompt: str, config: Dict[str, Any] | None = None) -> LLMResult:
        # Simulate basic usage stats
        tokens = len(prompt.split()) + len(self.response.split())
        
        return LLMResult(
            text=self.response,
            usage=LLMUsage(total_tokens=tokens),
            provider_name="mock"
        )
