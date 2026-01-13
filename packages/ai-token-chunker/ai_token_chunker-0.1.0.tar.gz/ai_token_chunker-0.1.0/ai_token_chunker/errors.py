"""Custom exception classes for ai_token_chunker."""


class ChunkerError(Exception):
    """Base exception for all chunker errors."""
    
    def __init__(self, message: str, provider: str = None, model: str = None, code: str = None):
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.code = code or self.__class__.__name__


class ProviderNotSupportedError(ChunkerError):
    """Raised when a provider is not supported."""
    
    def __init__(self, provider: str):
        super().__init__(
            f"Provider '{provider}' is not supported",
            provider=provider,
            code="PROVIDER_NOT_SUPPORTED"
        )


class LimitExceededError(ChunkerError):
    """Raised when a limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        provider: str,
        model: str = None,
        limit_name: str = None,
        actual: int = None,
        allowed: int = None
    ):
        super().__init__(message, provider=provider, model=model, code="LIMIT_EXCEEDED")
        self.limit_name = limit_name
        self.actual = actual
        self.allowed = allowed


class ImageLimitError(ChunkerError):
    """Raised when image limits are exceeded."""
    
    def __init__(
        self,
        message: str,
        provider: str,
        model: str = None,
        limit_name: str = None,
        actual: int = None,
        allowed: int = None
    ):
        super().__init__(message, provider=provider, model=model, code="IMAGE_LIMIT_ERROR")
        self.limit_name = limit_name
        self.actual = actual
        self.allowed = allowed


class InvalidInputError(ChunkerError):
    """Raised when input is invalid."""
    
    def __init__(self, message: str, provider: str = None, model: str = None):
        super().__init__(message, provider=provider, model=model, code="INVALID_INPUT")

