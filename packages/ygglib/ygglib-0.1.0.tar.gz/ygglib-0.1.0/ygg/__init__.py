"""
YGG Cache Client

High-performance cache client with automatic authentication and multi-tenancy support.

Version 0.1.0 - Single-file architecture to eliminate circular imports.
"""

import os
import json
import time
import requests
from typing import Any, Optional, Dict, List, Union, TYPE_CHECKING
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass, field

# Version information
__version__ = "0.1.0"
__author__ = "YGG Team"

# API base URL - always uses production API
YGG_API_BASE_URL = "https://ygg-api.kluglabs.net"

if TYPE_CHECKING:
    pass


@dataclass
class YGGConfig:
    """Configuration for the YGG cache client."""
    
    api_key: str
    base_url: str = field(default="", init=False)  # Not settable, always uses YGG_API_BASE_URL
    timeout: int = field(default_factory=lambda: int(os.environ.get("YGG_TIMEOUT", "30")))
    max_retries: int = field(default_factory=lambda: int(os.environ.get("YGG_MAX_RETRIES", "3")))
    retry_delay: float = field(default_factory=lambda: float(os.environ.get("YGG_RETRY_DELAY", "1.0")))
    pool_size: int = field(default_factory=lambda: int(os.environ.get("YGG_POOL_SIZE", "10")))
    user_agent: str = field(default="ygg-python/0.1.0")
    
    # Request headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and set default values after initialization."""
        if not self.api_key:
            raise ValueError("YGG_API_KEY is required")
        
        # Always use the production API base URL
        self.base_url = YGG_API_BASE_URL
        
        # Set default headers
        if not self.headers:
            self.headers = {
                "User-Agent": self.user_agent,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "pool_size": self.pool_size,
            "user_agent": self.user_agent,
            "headers": self.headers.copy()
        }
    
    @classmethod
    def from_env(cls) -> "YGGConfig":
        """Create configuration from environment variables."""
        return cls(
            api_key=os.environ["YGG_API_KEY"],
            timeout=int(os.environ.get("YGG_TIMEOUT", "30")),
            max_retries=int(os.environ.get("YGG_MAX_RETRIES", "3")),
            retry_delay=float(os.environ.get("YGG_RETRY_DELAY", "1.0")),
            pool_size=int(os.environ.get("YGG_POOL_SIZE", "10"))
        )


class YGGError(Exception):
    """Base exception for YGG cache client."""
    pass


class YGGConnectionError(YGGError):
    """Exception raised for connection errors."""
    pass


class YGGAuthenticationError(YGGError):
    """Exception raised for authentication errors."""
    pass


class YGGResponseError(YGGError):
    """Exception raised for API response errors."""
    pass


class YGGPipeline:
    """Pipeline for batch cache operations."""
    
    def __init__(self, client: "YGGClient"):
        """Initialize the pipeline.
        
        Args:
            client: The YGG client instance
        """
        self.client = client
        self.commands = []
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> "YGGPipeline":
        """Add SET command to pipeline.
        
        Args:
            key: The key to set
            value: The value to store
            ex: Expiration time in seconds
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("SET", key, value, ex))
        return self
    
    def get(self, key: str) -> "YGGPipeline":
        """Add GET command to pipeline.
        
        Args:
            key: The key to retrieve
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("GET", key))
        return self
    
    def delete(self, key: str) -> "YGGPipeline":
        """Add DELETE command to pipeline.
        
        Args:
            key: The key to delete
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("DEL", key))
        return self
    
    def exists(self, key: str) -> "YGGPipeline":
        """Add EXISTS command to pipeline.
        
        Args:
            key: The key to check
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("EXISTS", key))
        return self
    
    def expire(self, key: str, seconds: int) -> "YGGPipeline":
        """Add EXPIRE command to pipeline.
        
        Args:
            key: The key to set expiration for
            seconds: Expiration time in seconds
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("EXPIRE", key, seconds))
        return self
    
    def ttl(self, key: str) -> "YGGPipeline":
        """Add TTL command to pipeline.
        
        Args:
            key: The key to check
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("TTL", key))
        return self
    
    def cache(self, command: str, *args) -> "YGGPipeline":
        """Add custom cache command to pipeline.
        
        Args:
            command: The cache command to execute
            *args: Arguments for the command
            
        Returns:
            Self for method chaining
        """
        self.commands.append((command.upper(),) + args)
        return self
    
    def execute(self) -> List[Any]:
        """Execute all commands in the pipeline.
        
        Returns:
            List of results for each command
            
        Raises:
            YGGError: If pipeline execution fails
        """
        if not self.commands:
            return []
        
        try:
            # Execute all commands in a single batch request
            data = {
                "commands": [
                    {
                        "command": cmd[0],
                        "args": list(cmd[1:])
                    }
                    for cmd in self.commands
                ]
            }
            
            result = self.client._make_request("POST", "/v1/cache/pipeline", data)
            results = result.get("results", [])
            
            # Clear commands after execution
            self.commands.clear()
            
            return results
            
        except Exception as e:
            # Clear commands on error
            self.commands.clear()
            raise e
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - execute pipeline if not empty."""
        if self.commands:
            self.execute()


class YGGClient:
    """Main client for interacting with YGG cache."""
    
    def __init__(self, config: YGGConfig):
        """Initialize the YGG client.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create and configure the requests session."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            backoff_factor=self.config.retry_delay
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=self.config.pool_size)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_auth_token(self) -> str:
        """Get the API key for authentication."""
        return self.config.api_key
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make an HTTP request to the YGG API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            API response data
            
        Raises:
            YGGConnectionError: For connection issues
            YGGAuthenticationError: For authentication issues
            YGGResponseError: For API errors
        """
        url = f"{self.config.base_url}{endpoint}"
        headers = self.config.headers.copy()
        headers["Authorization"] = f"Bearer {self._get_auth_token()}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 401:
                raise YGGAuthenticationError(f"Authentication failed. Status: {response.status_code}, Response: {response.text}")
            elif response.status_code >= 400:
                raise YGGResponseError(f"API error {response.status_code}: {response.text}")
            
            return response.json() if response.content else None
            
        except requests.exceptions.RequestException as e:
            raise YGGConnectionError(f"Request failed: {e}")
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration.
        
        Args:
            key: The key to set
            value: The value to store
            ex: Expiration time in seconds
            
        Returns:
            True if successful
        """
        data = {"key": key, "value": value}
        if ex is not None:
            data["ex"] = ex
        
        result = self._make_request("POST", "/v1/cache/set", data)
        return result.get("success", False)
    
    def get(self, key: str) -> Optional[str]:
        """Get a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        result = self._make_request("GET", f"/v1/cache/get/{key}")
        return result.get("value")
    
    def delete(self, key: str) -> bool:
        """Delete a key.
        
        Args:
            key: The key to delete
            
        Returns:
            True if key was deleted, False if it didn't exist
        """
        result = self._make_request("DELETE", f"/v1/cache/del/{key}")
        return result.get("deleted", False)
    
    def exists(self, key: str) -> bool:
        """Check if a key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists, False otherwise
        """
        result = self._make_request("GET", f"/v1/cache/exists/{key}")
        return result.get("exists", False)
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key.
        
        Args:
            key: The key to set expiration for
            seconds: Expiration time in seconds
            
        Returns:
            True if expiration was set, False if key doesn't exist
        """
        data = {"key": key, "seconds": seconds}
        result = self._make_request("POST", "/v1/cache/expire", data)
        return result.get("success", False)
    
    def ttl(self, key: str) -> int:
        """Get time to live for a key.
        
        Args:
            key: The key to check
            
        Returns:
            Time to live in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        result = self._make_request("GET", f"/v1/cache/ttl/{key}")
        return result.get("ttl", -2)
    
    def cache(self, command: str, *args) -> Any:
        """Execute any cache command.
        
        Args:
            command: The cache command to execute
            *args: Arguments for the command
            
        Returns:
            The result of the cache command
        """
        data = {
            "command": command.upper(),
            "args": list(args)
        }
        
        result = self._make_request("POST", "/v1/cache/exec", data)
        return result.get("result")
    
    def pipeline(self) -> YGGPipeline:
        """Create a pipeline for batch operations.
        
        Returns:
            A pipeline object for batch operations
        """
        return YGGPipeline(self)
    
    def close(self):
        """Close the connection and cleanup resources."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global client instance
_client = None

def init(api_key, **kwargs):
    """Initialize the YGG client with your API key.
    
    Args:
        api_key (str): Your YGG_API_KEY for authentication
        **kwargs: Additional configuration options (base_url is not settable)
    """
    global _client
    # Remove base_url from kwargs if present - it's always set to production API
    kwargs.pop("base_url", None)
    config = YGGConfig(api_key=api_key, **kwargs)
    _client = YGGClient(config)
    return _client

def get_client():
    """Get the current YGG client instance.
    
    Returns:
        YGGClient: The initialized client instance
        
    Raises:
        RuntimeError: If client is not initialized
    """
    if _client is None:
        raise RuntimeError("YGG client not initialized. Call ygg.init() first.")
    return _client

# Convenience functions that delegate to the global client
def set(key, value, ex=None):
    """Set a key-value pair with optional expiration.
    
    Args:
        key (str): The key to set
        value (str): The value to store
        ex (int, optional): Expiration time in seconds
    """
    return get_client().set(key, value, ex)

def get(key):
    """Get a value by key.
    
    Args:
        key (str): The key to retrieve
        
    Returns:
        str: The stored value, or None if not found
    """
    return get_client().get(key)

def delete(key):
    """Delete a key.
    
    Args:
        key (str): The key to delete
        
    Returns:
        bool: True if key was deleted, False if it didn't exist
    """
    return get_client().delete(key)

def exists(key):
    """Check if a key exists.
    
    Args:
        key (str): The key to check
        
    Returns:
        bool: True if key exists, False otherwise
    """
    return get_client().exists(key)

def expire(key, seconds):
    """Set expiration for a key.
    
    Args:
        key (str): The key to set expiration for
        seconds (int): Expiration time in seconds
        
    Returns:
        bool: True if expiration was set, False if key doesn't exist
    """
    return get_client().expire(key, seconds)

def ttl(key):
    """Get time to live for a key.
    
    Args:
        key (str): The key to check
        
    Returns:
        int: Time to live in seconds, -1 if no expiration, -2 if key doesn't exist
    """
    return get_client().ttl(key)

def cache(command, *args):
    """Execute any cache command.
    
    Args:
        command (str): The cache command to execute
        *args: Arguments for the command
        
    Returns:
        The result of the cache command
    """
    return get_client().cache(command, *args)

def pipeline():
    """Create a pipeline for batch operations.
    
    Returns:
        YGGPipeline: A pipeline object for batch operations
    """
    return get_client().pipeline()

def close():
    """Close the connection."""
    if _client:
        _client.close()

def debug_info():
    """Print debug information about the ygg module."""
    import sys
    print(f"YGG version: {__version__}")
    print(f"Python version: {sys.version}")
    print(f"Module file: {__file__}")
    print(f"Module path: {sys.modules[__name__].__path__}")
    print(f"Available classes: YGGClient, YGGConfig, YGGPipeline")
    print("✅ Single-file architecture - no circular imports possible")

def test_connection(api_key: str):
    """Test the connection to the YGG API."""
    print(f"🔍 Testing connection to: {YGG_API_BASE_URL}")
    print(f"🔍 Using API key: {api_key[:8]}...")
    
    try:
        client = init(api_key)
        print("✅ Client initialized successfully")
        
        # Try a simple operation
        result = client.get("test-connection")
        print(f"✅ Test operation successful: {result}")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()

# Export main classes - these will be available after import
__all__ = [
    'init',
    'get_client',
    'set',
    'get',
    'delete',
    'exists',
    'expire',
    'ttl',
    'cache',
    'pipeline',
    'close',
    'YGGClient',
    'YGGConfig',
    'YGGPipeline',
    'YGGError',
    'YGGConnectionError',
    'YGGAuthenticationError',
    'YGGResponseError',
    'debug_info',
    'test_connection',
    '__version__'
]
