class IbraahimError(Exception):
    """Base exception for all Ibraahim errors."""
    pass

class ProviderError(IbraahimError):
    """Raised when an LLM provider fails."""
    pass

class TemplateError(IbraahimError):
    """Raised when there is an issue with prompt templating."""
    pass

class ConfigurationError(IbraahimError):
    """Raised when configuration is invalid."""
    pass
