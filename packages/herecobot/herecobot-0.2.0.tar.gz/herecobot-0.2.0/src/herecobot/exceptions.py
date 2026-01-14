"""
HerecoBot Exceptions
"""


class HerecoBotError(Exception):
    """Base exception for HerecoBot"""
    pass


class ConnectionError(HerecoBotError):
    """Failed to connect to HF Space"""
    pass


class TimeoutError(HerecoBotError):
    """Request timed out"""
    pass


class RateLimitError(HerecoBotError):
    """Rate limited by HF Space"""
    pass


class InvalidResponseError(HerecoBotError):
    """Unexpected response format"""
    pass
