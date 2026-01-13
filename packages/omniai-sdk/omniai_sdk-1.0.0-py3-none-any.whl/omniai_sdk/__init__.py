"""
OmniAI Python SDK
Official Python client for OmniAI API
"""

from .client import Client
from .exceptions import OmniAIError, AuthenticationError, ValidationError, RateLimitError

__version__ = '1.0.0'
__all__ = ['Client', 'OmniAIError', 'AuthenticationError', 'ValidationError', 'RateLimitError']
