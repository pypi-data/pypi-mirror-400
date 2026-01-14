"""
GRKMemory - Graph Retrieve Knowledge Memory
============================================

GRKMemory = Graph Retrieve Knowledge Memory

A semantic graph-based memory system for AI agents that enables
intelligent knowledge retrieval and structured conversation analysis.

Developed by MonkAI team (https://www.monkai.com.br)

Example usage:
    from grkmemory import GRKMemory, MemoryConfig
    
    # Initialize with default config
    grk = GRKMemory()
    
    # Or with custom configuration
    config = MemoryConfig(
        memory_file="my_memories.json",
        model="gpt-4o",
        enable_embeddings=True
    )
    grk = GRKMemory(config=config)
    
    # Search memories
    results = grk.search("What did we discuss about AI?")
    
    # Save a conversation
    grk.save_conversation(messages)

Authentication Example:
    from grkmemory import GRKMemory, GRKAuth, AuthenticatedGRK
    
    # Create an API key
    auth = GRKAuth()
    api_key = auth.create_api_key("My App", permissions=["read", "write"])
    print(f"Your API key: {api_key}")
    
    # Use authenticated GRKMemory
    grk = GRKMemory()
    secure_grk = AuthenticatedGRK(grk, api_key)
    secure_grk.chat("Hello!")

Author: Arthur Vaz
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Arthur Vaz"

from .core.grkmemory import GRKMemory
from .core.config import MemoryConfig
from .memory.repository import MemoryRepository
from .graph.semantic_graph import SemanticGraph
from .core.agent import KnowledgeAgent
from .auth.token_manager import TokenManager, Token
from .auth.auth import GRKAuth, AuthenticatedGRK, require_auth

# Aliases for backwards compatibility
MonkAI = GRKMemory
MonkAIAuth = GRKAuth
AuthenticatedMonkAI = AuthenticatedGRK

__all__ = [
    # Core
    "GRKMemory",
    "MonkAI",  # alias
    "MemoryConfig", 
    "MemoryRepository",
    "SemanticGraph",
    "KnowledgeAgent",
    # Auth
    "TokenManager",
    "Token",
    "GRKAuth",
    "MonkAIAuth",  # alias
    "AuthenticatedGRK",
    "AuthenticatedMonkAI",  # alias
    "require_auth",
    # Meta
    "__version__",
]
