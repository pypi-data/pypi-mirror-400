from typing import Any, Dict, List
from ibraahim.chains.base import Chain
from ibraahim.core.exceptions import ConfigurationError

class SequentialChain(Chain):
    """
    A chain that runs a sequence of chains in order.
    The output of one chain is merged into the inputs for the next chain.
    """
    
    def __init__(self, chains: List[Chain], input_variables: List[str], output_variables: List[str]):
        self.chains = chains
        self._input_variables = input_variables
        self._output_variables = output_variables
        self._validate_chains()
        
    def _validate_chains(self) -> None:
        """
        Validates that the chains can be connected.
        (Simplified validation for v1)
        """
        known_variables = set(self._input_variables)
        for i, chain in enumerate(self.chains):
            missing_vars = set(chain.input_keys) - known_variables
            if missing_vars:
                raise ConfigurationError(
                    f"Chain {i} expects inputs {missing_vars} which are not available. "
                    f"Available: {known_variables}"
                )
            known_variables.update(chain.output_keys)
            
    @property
    def input_keys(self) -> List[str]:
        return self._input_variables
        
    @property
    def output_keys(self) -> List[str]:
        return self._output_variables
        
    def call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Start with the initial inputs
        chain_inputs = inputs.copy()
        
        # Run through each chain
        for chain in self.chains:
            outputs = chain.call(chain_inputs)
            # Update the inputs for the next chain (and the final result)
            chain_inputs.update(outputs)
            
        # Return only the requested output variables
        return {k: chain_inputs[k] for k in self._output_variables}
