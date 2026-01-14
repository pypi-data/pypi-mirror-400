"""
HerecoBot Client - SDK-style interface for HuggingFace Space AI models
"""

import os
import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class ChatResponse:
    """Response from chat completion"""
    output_text: str
    model: str
    usage: Dict[str, int]
    
    def __str__(self) -> str:
        return self.output_text


@dataclass  
class Message:
    """Chat message"""
    role: str  # 'user', 'assistant', 'system'
    content: str


class Chat:
    """Chat completions interface"""
    
    def __init__(self, client: 'Hereco'):
        self._client = client
    
    def create(
        self,
        message: str,
        *,
        model: str = "default",
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> ChatResponse:
        """
        Create a chat completion.
        
        Args:
            message: User message to send
            model: Model name (for compatibility, uses space's model)
            system: Optional system prompt
            temperature: Response randomness (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            ChatResponse with output_text
        """
        return self._client._chat_sync(message, model, system, temperature, max_tokens)
    
    async def create_async(
        self,
        message: str,
        *,
        model: str = "default",
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> ChatResponse:
        """Async version of create()"""
        return await self._client._chat_async(message, model, system, temperature, max_tokens)


@dataclass
class KeyValidation:
    """API key validation result"""
    valid: bool
    key_id: Optional[str] = None
    permissions: Optional[List[str]] = None
    rate_limit: Optional[int] = None
    remaining: Optional[int] = None
    error: Optional[str] = None


class Hereco:
    """
    Hereco AI Client - OpenAI-style SDK interface.
    
    Example:
        >>> from herecobot import Hereco
        >>> client = Hereco()
        >>> response = client.chat.create("Tell me a joke")
        >>> print(response.output_text)
        
        # Or simpler:
        >>> from herecobot import Hereco
        >>> client = Hereco()
        >>> print(client.ask("What is 2+2?"))
        
        # Test API key:
        >>> result = client.test_key()
        >>> print(f"Valid: {result.valid}, Permissions: {result.permissions}")
    """
    
    # Default API base URL for key validation
    DEFAULT_API_BASE = "https://hereco.xyz"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        space_url: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initialize Hereco client.
        
        Args:
            api_key: API key (or set HERECO_API_KEY env var)
            space_url: HuggingFace Space URL (or set HERECO_SPACE env var)
            api_base: API base URL for key validation (default: https://hereco.xyz)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts on failure
        """
        self.api_key = api_key or os.environ.get("HERECO_API_KEY")
        self.api_base = (api_base or os.environ.get("HERECO_API_BASE") or self.DEFAULT_API_BASE).rstrip("/")
        self.space_url = (
            space_url 
            or os.environ.get("HERECO_SPACE") 
            or os.environ.get("HERECOBOT_SPACE")
        )
        
        # Space URL only required for chat, not for key testing
        if self.space_url:
            self.space_url = self.space_url.rstrip("/")
        
        self.timeout = timeout
        self.max_retries = max_retries
        self._gradio_client = None
        
        # SDK-style interface
        self.chat = Chat(self)
    
    @property
    def _client(self):
        """Lazy-load Gradio client"""
        if self._gradio_client is None:
            if not self.space_url:
                raise ValueError(
                    "HuggingFace Space URL is required for chat. "
                    "Set HERECO_SPACE environment variable or pass space_url parameter."
                )
            try:
                from gradio_client import Client
                self._gradio_client = Client(self.space_url)
            except Exception as e:
                raise ConnectionError(f"Failed to connect to {self.space_url}: {e}")
        return self._gradio_client
    
    def test_key(self, api_key: Optional[str] = None) -> KeyValidation:
        """
        Test if an API key is valid.
        
        Args:
            api_key: API key to test (uses self.api_key if not provided)
            
        Returns:
            KeyValidation with valid status and details
            
        Example:
            >>> client = Hereco(api_key="hrc_xxx...")
            >>> result = client.test_key()
            >>> if result.valid:
            ...     print(f"Key works! Permissions: {result.permissions}")
            ... else:
            ...     print(f"Invalid: {result.error}")
        """
        key = api_key or self.api_key
        
        if not key:
            return KeyValidation(valid=False, error="No API key provided")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.api_base}/api/v1/validate",
                    headers={"Authorization": f"Bearer {key}"}
                )
                
                data = response.json()
                
                if response.status_code == 200 and data.get("valid"):
                    return KeyValidation(
                        valid=True,
                        key_id=data.get("keyId"),
                        permissions=data.get("permissions", []),
                        rate_limit=data.get("rateLimit", {}).get("limit"),
                        remaining=data.get("rateLimit", {}).get("remaining"),
                    )
                elif response.status_code == 429:
                    return KeyValidation(
                        valid=True,  # Key is valid but rate limited
                        error="Rate limit exceeded",
                        key_id=data.get("keyId"),
                    )
                else:
                    return KeyValidation(
                        valid=False,
                        error=data.get("error", f"HTTP {response.status_code}")
                    )
                    
        except httpx.TimeoutException:
            return KeyValidation(valid=False, error="Request timed out")
        except Exception as e:
            return KeyValidation(valid=False, error=str(e))
    
    async def test_key_async(self, api_key: Optional[str] = None) -> KeyValidation:
        """Async version of test_key()"""
        key = api_key or self.api_key
        
        if not key:
            return KeyValidation(valid=False, error="No API key provided")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/api/v1/validate",
                    headers={"Authorization": f"Bearer {key}"}
                )
                
                data = response.json()
                
                if response.status_code == 200 and data.get("valid"):
                    return KeyValidation(
                        valid=True,
                        key_id=data.get("keyId"),
                        permissions=data.get("permissions", []),
                        rate_limit=data.get("rateLimit", {}).get("limit"),
                        remaining=data.get("rateLimit", {}).get("remaining"),
                    )
                else:
                    return KeyValidation(
                        valid=False,
                        error=data.get("error", f"HTTP {response.status_code}")
                    )
                    
        except Exception as e:
            return KeyValidation(valid=False, error=str(e))
    
    def _chat_sync(
        self,
        message: str,
        model: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> ChatResponse:
        """Internal sync chat implementation"""
        for attempt in range(self.max_retries):
            try:
                result = self._client.predict(
                    message,
                    api_name="/chat"
                )
                
                # Handle different response formats
                if isinstance(result, str):
                    output = result
                elif isinstance(result, (list, tuple)) and len(result) > 0:
                    output = str(result[-1])
                else:
                    output = str(result)
                
                return ChatResponse(
                    output_text=output,
                    model=model,
                    usage={"prompt_tokens": len(message), "completion_tokens": len(output)}
                )
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Chat failed after {self.max_retries} attempts: {e}")
        
        raise RuntimeError("Unexpected error in chat")
    
    async def _chat_async(
        self,
        message: str,
        model: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> ChatResponse:
        """Internal async chat implementation"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.space_url}/api/predict",
                    json={"data": [message]},
                )
                response.raise_for_status()
                data = response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    output = data["data"][0]
                    return ChatResponse(
                        output_text=output,
                        model=model,
                        usage={"prompt_tokens": len(message), "completion_tokens": len(output)}
                    )
                
                raise RuntimeError(f"Unexpected response format: {data}")
                
            except httpx.TimeoutException:
                raise TimeoutError(f"Request timed out after {self.timeout}s")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise RuntimeError("Rate limited by HF Space")
                raise RuntimeError(f"HTTP error: {e}")
    
    def ask(self, message: str, **kwargs) -> str:
        """
        Simple one-liner to ask a question.
        
        Args:
            message: Question to ask
            **kwargs: Additional args passed to chat.create()
            
        Returns:
            Response text as string
        """
        return self.chat.create(message, **kwargs).output_text
    
    async def ask_async(self, message: str, **kwargs) -> str:
        """Async version of ask()"""
        response = await self.chat.create_async(message, **kwargs)
        return response.output_text
    
    def ping(self) -> bool:
        """Check if the HF Space is alive"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.space_url)
                return response.status_code == 200
        except Exception:
            return False
    
    async def ping_async(self) -> bool:
        """Async version of ping()"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.space_url)
                return response.status_code == 200
        except Exception:
            return False


# Backwards compatibility alias
HerecoBot = Hereco
