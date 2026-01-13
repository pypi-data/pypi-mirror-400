from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class LLMRequest(BaseModel):
    """Encapsulates a request to an LLM."""
    prompt: str
    config: Dict[str, Any] = Field(default_factory=dict)
    
class LLMUsage(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class LLMResult(BaseModel):
    """The result of an LLM generation."""
    text: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    raw_response: Optional[Dict[str, Any]] = None
    provider_name: str
