"""
Prediction Markets API Client

A Python client library for accessing the Prediction Markets API.

Usage:
    from predictmarket import Client

    client = Client(api_key="pk_live_your_key_here")
    markets = client.get_markets(venue="kalshi", limit=50)
"""

from .client import Client
from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

__version__ = "0.2.1"
__all__ = [
    "Client",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
]
