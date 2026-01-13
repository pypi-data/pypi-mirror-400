"""
ZeroCarbon SDK for Python
Official Python client for ZeroCarbon.codes API
"""

__version__ = "2.0.0"
__author__ = "ZeroCarbon.codes"

from .client import ZeroCarbon
from .exceptions import (
    ZeroCarbonError,
    AuthenticationError,
    InvalidRequestError,
    APIError
)

__all__ = [
    "ZeroCarbon",
    "ZeroCarbonError",
    "AuthenticationError",
    "InvalidRequestError",
    "APIError"
]
