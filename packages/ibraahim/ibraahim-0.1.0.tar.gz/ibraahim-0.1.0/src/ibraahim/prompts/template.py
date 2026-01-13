from typing import Any, Dict, List, Set
from ibraahim.core.exceptions import TemplateError
import re

class PromptTemplate:
    """
    A template for creating prompts.
    
    Example:
        template = PromptTemplate("Hello {name}!")
        prompt = template.format(name="World")
    """
    
    def __init__(self, template: str, input_variables: List[str] | None = None):
        self.template = template
        self._input_variables = set(input_variables) if input_variables else self._extract_variables(template)
        
    def _extract_variables(self, template: str) -> Set[str]:
        """Extract variables from generic f-string style template keys."""
        # This is a simple regex for {var_name}. 
        return set(re.findall(r"\{([a-zA-Z0-9_]+)\}", template))

    @property
    def input_variables(self) -> Set[str]:
        return self._input_variables

    def format(self, **kwargs: Any) -> str:
        """
        Format the prompt with the given inputs.
        
        Raises:
            TemplateError: If required variables are missing.
        """
        missing_vars = self.input_variables - set(kwargs.keys())
        if missing_vars:
            raise TemplateError(f"Missing required variables: {missing_vars}")
            
        try:
            # We use format_map which is generally safe for simple string substitution
            # ignoring extra keys is not default behavior of format_map, so we filter first if we wanted strictness.
            # But python's format will just use what it needs. A bigger issue is if extra keys interact with format specs.
            # For simplicity in v1, we use python f-string style formatting.
            return self.template.format(**kwargs)
        except KeyError as e:
            # This handles cases where _extract_variables might have missed something or logical mismatch
            raise TemplateError(f"Formatting failed: {e}")
        except ValueError as e:
            raise TemplateError(f"Formatting failed (Value Error): {e}")

    def __repr__(self) -> str:
        return f"PromptTemplate(input_variables={self.input_variables})"
