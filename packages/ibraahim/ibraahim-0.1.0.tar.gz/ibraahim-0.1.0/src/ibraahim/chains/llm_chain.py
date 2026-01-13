from typing import Any, Dict, List, Optional
from ibraahim.chains.base import Chain
from ibraahim.core.llm import BaseLLM
from ibraahim.prompts.template import PromptTemplate

class LLMChain(Chain):
    """
    A chain that runs a PromptTemplate and an LLM.
    """
    
    def __init__(self, prompt: PromptTemplate, llm: BaseLLM, output_key: str = "text"):
        self.prompt = prompt
        self.llm = llm
        self.output_key = output_key
        
    @property
    def input_keys(self) -> List[str]:
        return list(self.prompt.input_variables)
        
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
        
    def call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Format the prompt
        prompt_text = self.prompt.format(**inputs)
        
        # 2. Call the LLM
        result = self.llm.generate(prompt_text)
        
        # 3. Return result
        # We assume for now we just want the text in the output dict
        return {self.output_key: result.text}
