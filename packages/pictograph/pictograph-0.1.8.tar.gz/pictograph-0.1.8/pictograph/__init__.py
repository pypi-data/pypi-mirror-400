"""
Pictograph Python SDK

Official Python client for the Pictograph annotation platform API.
"""

from .client import Client
from .exceptions import (
    PictographError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError
)

__version__ = "0.1.8"
__all__ = [
    "Client",
    "PictographError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError"
]
