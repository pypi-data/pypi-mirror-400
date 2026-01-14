"""
HerecoBot - SDK for HuggingFace Space AI models

Usage:
    from herecobot import Hereco
    
    client = Hereco()
    response = client.chat.create("Tell me a joke")
    print(response.output_text)
    
    # Or simpler:
    print(client.ask("What is 2+2?"))
"""

__version__ = "0.2.0"

from .client import Hereco, HerecoBot, ChatResponse, Message, KeyValidation
from .exceptions import (
    HerecoBotError,
    ConnectionError,
    TimeoutError,
    RateLimitError,
    InvalidResponseError,
)

__all__ = [
    "Hereco",
    "HerecoBot",  # backwards compat
    "ChatResponse",
    "Message",
    "KeyValidation",
    "HerecoBotError",
    "ConnectionError", 
    "TimeoutError",
    "RateLimitError",
    "InvalidResponseError",
    "__version__",
]
