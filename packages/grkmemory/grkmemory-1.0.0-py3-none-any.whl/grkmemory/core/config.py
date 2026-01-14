"""
Configuration module for GRKMemory.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MemoryConfig:
    """
    Configuration for GRKMemory memory system.
    
    Attributes:
        api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        model: OpenAI model to use for processing.
        embedding_model: Model for generating embeddings.
        memory_file: Path to the JSON file storing memories.
        enable_embeddings: Whether to generate embeddings for semantic search.
        debug: Enable debug logging.
        background_memory_enabled: Enable background memory retrieval.
        background_memory_limit: Maximum number of memories to retrieve.
        background_memory_method: Search method ('graph', 'embedding', 'tags', 'entities').
        background_memory_threshold: Minimum similarity threshold for retrieval.
    
    Example:
        config = MemoryConfig(
            model="gpt-4o",
            memory_file="my_memories.json",
            enable_embeddings=True
        )
    """
    
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    memory_file: str = "graph_retrieve_knowledge_memory.json"
    enable_embeddings: bool = True
    debug: bool = False
    background_memory_enabled: bool = True
    background_memory_limit: int = 5
    background_memory_method: str = "graph"
    background_memory_threshold: float = 0.3
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key to MemoryConfig."
            )
        
        valid_methods = {"graph", "embedding", "tags", "entities"}
        if self.background_memory_method not in valid_methods:
            raise ValueError(
                f"Invalid background_memory_method: {self.background_memory_method}. "
                f"Must be one of: {valid_methods}"
            )
        
        # Set API key in environment for OpenAI client
        os.environ["OPENAI_API_KEY"] = self.api_key
    
    @classmethod
    def from_env(cls) -> "MemoryConfig":
        """
        Create configuration from environment variables.
        
        Environment variables:
            OPENAI_API_KEY: Required API key
            OPENAI_MODEL: Model name (default: gpt-4o)
            OPENAI_EMBEDDING_MODEL: Embedding model (default: text-embedding-3-small)
            MEMORY_FILE: Memory file path
            ENABLE_EMBEDDINGS: true/false
            DEBUG: true/false
            BACKGROUND_MEMORY_ENABLED: true/false
            BACKGROUND_MEMORY_LIMIT: integer
            BACKGROUND_MEMORY_METHOD: graph/embedding/tags/entities
            BACKGROUND_MEMORY_THRESHOLD: float
        """
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            memory_file=os.getenv("MEMORY_FILE", "graph_retrieve_knowledge_memory.json"),
            enable_embeddings=os.getenv("ENABLE_EMBEDDINGS", "true").lower() == "true",
            debug=os.getenv("DEBUG", "false").lower() == "true",
            background_memory_enabled=os.getenv("BACKGROUND_MEMORY_ENABLED", "true").lower() == "true",
            background_memory_limit=int(os.getenv("BACKGROUND_MEMORY_LIMIT", "5")),
            background_memory_method=os.getenv("BACKGROUND_MEMORY_METHOD", "graph"),
            background_memory_threshold=float(os.getenv("BACKGROUND_MEMORY_THRESHOLD", "0.3")),
        )
