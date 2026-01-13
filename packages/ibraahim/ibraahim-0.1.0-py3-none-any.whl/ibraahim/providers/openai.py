import os
from typing import Any, Dict, Optional
from ibraahim.core.llm import BaseLLM
from ibraahim.core.types import LLMResult, LLMUsage
from ibraahim.core.exceptions import ProviderError

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None # type: ignore

class OpenAIProvider(BaseLLM):
    """
    Adapter for the OpenAI API.
    Requires 'openai' package and OPENAI_API_KEY environment variable.
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None, base_url: Optional[str] = None):
        if OpenAI is None:
            raise ProviderError("OpenAI package is not installed. Please install 'openai'.")
            
        self.model = model
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url
        )
        
    def generate(self, prompt: str, config: Dict[str, Any] | None = None) -> LLMResult:
        merged_config = config or {}
        # Allow overriding model per call if needed
        model = merged_config.get("model", self.model)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **{k: v for k, v in merged_config.items() if k != "model"}
            )
            
            choice = response.choices[0]
            content = choice.message.content or ""
            
            usage = LLMUsage()
            if response.usage:
                usage = LLMUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens
                )
                
            return LLMResult(
                text=content,
                usage=usage,
                raw_response=response.model_dump(),
                provider_name="openai"
            )
            
        except Exception as e:
            raise ProviderError(f"OpenAI API call failed: {str(e)}")
