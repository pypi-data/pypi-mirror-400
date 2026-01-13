from abc import ABC, abstractmethod
from typing import Any, Dict, List

class Chain(ABC):
    """
    Abstract base class for all chains.
    A Chain is a unit of work that takes dictionary inputs and produces dictionary outputs.
    """
    
    @property
    @abstractmethod
    def input_keys(self) -> List[str]:
        """Keys expected in the input dictionary."""
        pass
        
    @property
    @abstractmethod
    def output_keys(self) -> List[str]:
        """Keys produced in the output dictionary."""
        pass
        
    @abstractmethod
    def call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the chain logic.
        
        Args:
            inputs: Dictionary of inputs.
            
        Returns:
            Dictionary of outputs.
        """
        pass
        
    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Allows calling the instance directly."""
        return self.call(inputs)
