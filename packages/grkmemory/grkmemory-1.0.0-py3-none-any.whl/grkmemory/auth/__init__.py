"""
Authentication module for GRKMemory.

Provides token-based authentication for API access.
"""

from .token_manager import TokenManager, Token
from .auth import GRKAuth, AuthenticatedGRK, require_auth

# Alias for backwards compatibility
MonkAIAuth = GRKAuth
AuthenticatedMonkAI = AuthenticatedGRK

__all__ = ["TokenManager", "Token", "GRKAuth", "MonkAIAuth", "AuthenticatedGRK", "AuthenticatedMonkAI", "require_auth"]
