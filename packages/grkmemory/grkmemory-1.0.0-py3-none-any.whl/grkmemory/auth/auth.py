"""
Authentication utilities for GRKMemory.

Provides authentication decorator and GRKMemory auth integration.
"""

import os
import functools
from typing import Optional, Callable, Any, List

from .token_manager import TokenManager, Token


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class PermissionError(Exception):
    """Raised when permission check fails."""
    pass


class GRKAuth:
    """
    Authentication handler for GRKMemory.
    
    Provides token validation and permission checking for GRKMemory operations.
    
    Example:
        # Initialize auth
        auth = GRKAuth()
        
        # Create a token
        api_key = auth.create_api_key("My App")
        
        # Authenticate
        if auth.authenticate(api_key):
            print("Authenticated!")
        
        # Use with GRKMemory
        from grkmemory import GRKMemory
        grk = GRKMemory()
        auth.protect(grk, api_key)
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, tokens_file: str = "grkmemory_tokens.json"):
        """Singleton pattern for shared token manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, tokens_file: str = "grkmemory_tokens.json"):
        """
        Initialize authentication handler.
        
        Args:
            tokens_file: Path to tokens storage file.
        """
        if not self._initialized:
            self.token_manager = TokenManager(tokens_file)
            self.current_token: Optional[Token] = None
            self._initialized = True
    
    def create_api_key(
        self,
        name: str,
        permissions: Optional[List[str]] = None,
        expires_days: Optional[int] = None,
        rate_limit: int = 0
    ) -> str:
        """
        Create a new API key.
        
        Args:
            name: Name for the token.
            permissions: List of permissions.
            expires_days: Days until expiration.
            rate_limit: Requests per minute limit.
        
        Returns:
            The new API key (save it, won't be shown again!).
        """
        api_key, token = self.token_manager.create_token(
            name=name,
            permissions=permissions,
            expires_days=expires_days,
            rate_limit=rate_limit
        )
        return api_key
    
    def authenticate(self, api_key: str) -> bool:
        """
        Authenticate with an API key.
        
        Args:
            api_key: The API key to authenticate.
        
        Returns:
            True if authenticated, False otherwise.
        """
        token = self.token_manager.validate_token(api_key)
        if token:
            self.current_token = token
            return True
        self.current_token = None
        return False
    
    def authenticate_or_raise(self, api_key: str) -> Token:
        """
        Authenticate and raise exception if invalid.
        
        Args:
            api_key: The API key to authenticate.
        
        Returns:
            The validated Token.
        
        Raises:
            AuthenticationError: If authentication fails.
        """
        token = self.token_manager.validate_token(api_key)
        if not token:
            raise AuthenticationError("Invalid or expired API key")
        self.current_token = token
        return token
    
    def check_permission(self, permission: str) -> bool:
        """
        Check if current token has a permission.
        
        Args:
            permission: Permission to check.
        
        Returns:
            True if permitted, False otherwise.
        """
        if not self.current_token:
            return False
        return self.current_token.has_permission(permission)
    
    def require_permission(self, permission: str):
        """
        Require a permission or raise exception.
        
        Args:
            permission: Required permission.
        
        Raises:
            PermissionError: If permission not granted.
        """
        if not self.check_permission(permission):
            raise PermissionError(f"Permission '{permission}' required")
    
    def revoke_key(self, token_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            token_id: Token ID to revoke.
        
        Returns:
            True if revoked.
        """
        return self.token_manager.revoke_token(token_id)
    
    def list_keys(self) -> List[Token]:
        """
        List all active API keys (tokens).
        
        Returns:
            List of active tokens.
        """
        return self.token_manager.list_tokens()
    
    def get_current_token(self) -> Optional[Token]:
        """Get the currently authenticated token."""
        return self.current_token
    
    def logout(self):
        """Clear current authentication."""
        self.current_token = None
    
    @classmethod
    def from_env(cls, env_var: str = "GRKMEMORY_API_KEY") -> "GRKAuth":
        """
        Create and authenticate from environment variable.
        
        Args:
            env_var: Environment variable name containing API key.
        
        Returns:
            Authenticated GRKAuth instance.
        
        Raises:
            AuthenticationError: If key not found or invalid.
        """
        auth = cls()
        api_key = os.environ.get(env_var)
        
        if not api_key:
            raise AuthenticationError(
                f"API key not found in environment variable '{env_var}'"
            )
        
        if not auth.authenticate(api_key):
            raise AuthenticationError("Invalid API key")
        
        return auth


def require_auth(
    permission: Optional[str] = None,
    api_key_param: str = "api_key"
) -> Callable:
    """
    Decorator to require authentication for a function.
    
    Args:
        permission: Optional permission to require.
        api_key_param: Parameter name for API key.
    
    Example:
        @require_auth(permission="write")
        def save_data(api_key: str, data: dict):
            # Only called if authenticated with 'write' permission
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get API key from kwargs
            api_key = kwargs.get(api_key_param)
            
            if not api_key:
                raise AuthenticationError(
                    f"API key required (parameter: {api_key_param})"
                )
            
            # Authenticate
            auth = GRKAuth()
            token = auth.authenticate_or_raise(api_key)
            
            # Check permission if required
            if permission:
                auth.require_permission(permission)
            
            # Call function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class AuthenticatedGRK:
    """
    Wrapper for GRKMemory with authentication.
    
    Example:
        from grkmemory import GRKMemory
        from grkmemory.auth import AuthenticatedGRK
        
        grk = GRKMemory()
        auth_grk = AuthenticatedGRK(grk, api_key="grk_...")
        
        # All operations require valid API key
        auth_grk.chat("Hello!")
    """
    
    def __init__(self, grkmemory, api_key: str):
        """
        Initialize authenticated wrapper.
        
        Args:
            grkmemory: GRKMemory instance to wrap.
            api_key: API key for authentication.
        """
        self.grkmemory = grkmemory
        self.auth = GRKAuth()
        self.token = self.auth.authenticate_or_raise(api_key)
    
    def _check_permission(self, permission: str):
        """Check permission and raise if not granted."""
        if not self.token.has_permission(permission):
            raise PermissionError(f"Permission '{permission}' required")
    
    def search(self, *args, **kwargs):
        """Search with authentication (requires 'read' permission)."""
        self._check_permission("read")
        return self.grkmemory.search(*args, **kwargs)
    
    def chat(self, *args, **kwargs):
        """Chat with authentication (requires 'read' permission)."""
        self._check_permission("read")
        return self.grkmemory.chat(*args, **kwargs)
    
    def save_conversation(self, *args, **kwargs):
        """Save conversation with authentication (requires 'write' permission)."""
        self._check_permission("write")
        return self.grkmemory.save_conversation(*args, **kwargs)
    
    def save_memory(self, *args, **kwargs):
        """Save memory with authentication (requires 'write' permission)."""
        self._check_permission("write")
        return self.grkmemory.save_memory(*args, **kwargs)
    
    def get_stats(self, *args, **kwargs):
        """Get stats with authentication (requires 'read' permission)."""
        self._check_permission("read")
        return self.grkmemory.get_stats(*args, **kwargs)
    
    def get_graph_stats(self, *args, **kwargs):
        """Get graph stats with authentication (requires 'read' permission)."""
        self._check_permission("read")
        return self.grkmemory.get_graph_stats(*args, **kwargs)
    
    @property
    def memory_count(self):
        """Get memory count (requires 'read' permission)."""
        self._check_permission("read")
        return self.grkmemory.memory_count
