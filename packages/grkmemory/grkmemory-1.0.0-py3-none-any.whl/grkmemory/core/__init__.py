"""Core module for GRKMemory."""

from .config import MemoryConfig
from .grkmemory import GRKMemory
from .agent import KnowledgeAgent

# Alias for backwards compatibility
MonkAI = GRKMemory

__all__ = ["MemoryConfig", "GRKMemory", "MonkAI", "KnowledgeAgent"]
