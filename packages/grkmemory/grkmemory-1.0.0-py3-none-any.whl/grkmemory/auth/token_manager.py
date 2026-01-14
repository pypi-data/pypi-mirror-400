"""
Token Manager for GRKMemory.

Handles creation, validation, and management of API tokens.
"""

import os
import json
import hashlib
import secrets
import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Token:
    """
    Represents an API token.
    
    Attributes:
        token_id: Unique identifier for the token.
        name: Human-readable name/description.
        hashed_key: SHA-256 hash of the actual API key.
        created_at: When the token was created.
        expires_at: When the token expires (None = never).
        last_used: When the token was last used.
        permissions: List of permissions (e.g., ['read', 'write', 'admin']).
        rate_limit: Maximum requests per minute (0 = unlimited).
        is_active: Whether the token is currently active.
        metadata: Additional metadata.
    """
    token_id: str
    name: str
    hashed_key: str
    created_at: str
    expires_at: Optional[str] = None
    last_used: Optional[str] = None
    permissions: List[str] = field(default_factory=lambda: ["read", "write"])
    rate_limit: int = 0
    is_active: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if token has expired."""
        if self.expires_at is None:
            return False
        expires = datetime.datetime.fromisoformat(self.expires_at)
        return datetime.datetime.now() > expires
    
    def has_permission(self, permission: str) -> bool:
        """Check if token has a specific permission."""
        return permission in self.permissions or "admin" in self.permissions
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Token":
        """Create Token from dictionary."""
        return cls(**data)


class TokenManager:
    """
    Manages API tokens for GRKMemory.
    
    Tokens are stored in a JSON file and validated using SHA-256 hashes.
    The actual API keys are never stored - only their hashes.
    
    Example:
        manager = TokenManager()
        
        # Create a new token
        api_key, token = manager.create_token(
            name="My App",
            permissions=["read", "write"],
            expires_days=30
        )
        print(f"Your API key: {api_key}")  # Save this! It won't be shown again.
        
        # Validate a token
        token = manager.validate_token(api_key)
        if token:
            print(f"Valid token: {token.name}")
        
        # Revoke a token
        manager.revoke_token(token_id)
    """
    
    # Token prefix for easy identification
    TOKEN_PREFIX = "grk_"
    
    def __init__(self, tokens_file: str = "grkmemory_tokens.json"):
        """
        Initialize the token manager.
        
        Args:
            tokens_file: Path to the JSON file storing token data.
        """
        self.tokens_file = Path(tokens_file)
        self.tokens: Dict[str, Token] = {}
        self._load_tokens()
    
    def _load_tokens(self):
        """Load tokens from file."""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tokens = {
                        k: Token.from_dict(v) for k, v in data.items()
                    }
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️ Error loading tokens: {e}")
                self.tokens = {}
        else:
            self.tokens = {}
    
    def _save_tokens(self):
        """Save tokens to file."""
        try:
            data = {k: v.to_dict() for k, v in self.tokens.items()}
            with open(self.tokens_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving tokens: {e}")
    
    def _hash_key(self, api_key: str) -> str:
        """Generate SHA-256 hash of API key."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _generate_key(self) -> str:
        """Generate a new API key."""
        random_bytes = secrets.token_bytes(32)
        key_part = secrets.token_urlsafe(32)
        return f"{self.TOKEN_PREFIX}{key_part}"
    
    def _generate_token_id(self) -> str:
        """Generate a unique token ID."""
        return f"tok_{secrets.token_hex(8)}"
    
    def create_token(
        self,
        name: str,
        permissions: Optional[List[str]] = None,
        expires_days: Optional[int] = None,
        rate_limit: int = 0,
        metadata: Optional[Dict] = None
    ) -> tuple[str, Token]:
        """
        Create a new API token.
        
        Args:
            name: Human-readable name for the token.
            permissions: List of permissions (default: ['read', 'write']).
            expires_days: Number of days until expiration (None = never).
            rate_limit: Max requests per minute (0 = unlimited).
            metadata: Additional metadata to store.
        
        Returns:
            Tuple of (api_key, Token). The api_key is shown only once!
        
        Example:
            api_key, token = manager.create_token(
                name="Production App",
                permissions=["read", "write"],
                expires_days=365
            )
        """
        # Generate unique key and ID
        api_key = self._generate_key()
        token_id = self._generate_token_id()
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = (
                datetime.datetime.now() + 
                datetime.timedelta(days=expires_days)
            ).isoformat()
        
        # Create token
        token = Token(
            token_id=token_id,
            name=name,
            hashed_key=self._hash_key(api_key),
            created_at=datetime.datetime.now().isoformat(),
            expires_at=expires_at,
            permissions=permissions or ["read", "write"],
            rate_limit=rate_limit,
            is_active=True,
            metadata=metadata or {}
        )
        
        # Save
        self.tokens[token_id] = token
        self._save_tokens()
        
        return api_key, token
    
    def validate_token(self, api_key: str) -> Optional[Token]:
        """
        Validate an API key and return the associated token.
        
        Args:
            api_key: The API key to validate.
        
        Returns:
            Token if valid, None if invalid.
        """
        if not api_key or not api_key.startswith(self.TOKEN_PREFIX):
            return None
        
        hashed = self._hash_key(api_key)
        
        for token in self.tokens.values():
            if token.hashed_key == hashed:
                # Check if active
                if not token.is_active:
                    return None
                
                # Check if expired
                if token.is_expired():
                    return None
                
                # Update last used
                token.last_used = datetime.datetime.now().isoformat()
                self._save_tokens()
                
                return token
        
        return None
    
    def revoke_token(self, token_id: str) -> bool:
        """
        Revoke a token (deactivate it).
        
        Args:
            token_id: The token ID to revoke.
        
        Returns:
            True if revoked, False if not found.
        """
        if token_id in self.tokens:
            self.tokens[token_id].is_active = False
            self._save_tokens()
            return True
        return False
    
    def delete_token(self, token_id: str) -> bool:
        """
        Permanently delete a token.
        
        Args:
            token_id: The token ID to delete.
        
        Returns:
            True if deleted, False if not found.
        """
        if token_id in self.tokens:
            del self.tokens[token_id]
            self._save_tokens()
            return True
        return False
    
    def list_tokens(self, include_inactive: bool = False) -> List[Token]:
        """
        List all tokens.
        
        Args:
            include_inactive: Whether to include revoked tokens.
        
        Returns:
            List of Token objects.
        """
        tokens = list(self.tokens.values())
        if not include_inactive:
            tokens = [t for t in tokens if t.is_active]
        return tokens
    
    def get_token(self, token_id: str) -> Optional[Token]:
        """
        Get a token by ID.
        
        Args:
            token_id: The token ID.
        
        Returns:
            Token if found, None otherwise.
        """
        return self.tokens.get(token_id)
    
    def update_token(
        self,
        token_id: str,
        name: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        rate_limit: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Token]:
        """
        Update token properties.
        
        Args:
            token_id: The token ID to update.
            name: New name (optional).
            permissions: New permissions (optional).
            rate_limit: New rate limit (optional).
            metadata: New metadata (optional).
        
        Returns:
            Updated Token if found, None otherwise.
        """
        if token_id not in self.tokens:
            return None
        
        token = self.tokens[token_id]
        
        if name is not None:
            token.name = name
        if permissions is not None:
            token.permissions = permissions
        if rate_limit is not None:
            token.rate_limit = rate_limit
        if metadata is not None:
            token.metadata.update(metadata)
        
        self._save_tokens()
        return token
    
    def regenerate_key(self, token_id: str) -> Optional[str]:
        """
        Regenerate the API key for a token.
        
        Args:
            token_id: The token ID.
        
        Returns:
            New API key if successful, None otherwise.
        """
        if token_id not in self.tokens:
            return None
        
        new_key = self._generate_key()
        self.tokens[token_id].hashed_key = self._hash_key(new_key)
        self._save_tokens()
        
        return new_key
