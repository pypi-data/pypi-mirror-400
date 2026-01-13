"""
Exception classes for OmniAI SDK
"""


class OmniAIError(Exception):
    """Base exception for OmniAI SDK"""
    pass


class AuthenticationError(OmniAIError):
    """Raised when API key is invalid"""
    pass


class ValidationError(OmniAIError):
    """Raised when request data is invalid"""
    pass


class RateLimitError(OmniAIError):
    """Raised when rate limit is exceeded"""
    pass
