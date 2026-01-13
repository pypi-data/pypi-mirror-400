"""
ZeroCarbon SDK Exceptions
"""


class ZeroCarbonError(Exception):
    """Base exception for all SDK errors"""
    pass


class AuthenticationError(ZeroCarbonError):
    """Raised when API key is invalid or missing"""
    pass


class InvalidRequestError(ZeroCarbonError):
    """Raised when request parameters are invalid"""
    pass


class APIError(ZeroCarbonError):
    """Raised when API returns an error"""
    pass
