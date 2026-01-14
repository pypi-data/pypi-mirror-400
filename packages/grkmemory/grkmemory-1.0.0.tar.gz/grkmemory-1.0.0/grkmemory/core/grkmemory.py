"""
GRKMemory - Graph Retrieve Knowledge Memory System.

This is the main entry point for the GRKMemory library.
"""

from typing import Dict, List, Optional

from .config import MemoryConfig
from .agent import KnowledgeAgent
from ..memory.repository import MemoryRepository
from ..graph.semantic_graph import SemanticGraph


class GRKMemory:
    """
    GRKMemory - Graph Retrieve Knowledge Memory System.
    
    A semantic graph-based memory system for AI agents that enables
    intelligent knowledge retrieval and structured conversation analysis.
    
    Example:
        # Basic usage
        from grkmemory import GRKMemory
        
        grk = GRKMemory()
        
        # Search for relevant memories
        results = grk.search("What did we discuss about AI?")
        
        # Chat with memory context
        response = grk.chat("Tell me about our previous discussions")
        
        # Save a conversation
        grk.save_conversation([
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ])
    
    Example with custom config:
        from grkmemory import GRKMemory, MemoryConfig
        
        config = MemoryConfig(
            memory_file="my_memories.json",
            model="gpt-4o",
            enable_embeddings=True,
            background_memory_method="graph"
        )
        
        grk = GRKMemory(config=config)
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        """
        Initialize GRKMemory.
        
        Args:
            config: Optional MemoryConfig instance. If not provided,
                   creates from environment variables.
        """
        self.config = config or MemoryConfig.from_env()
        
        # Initialize components
        self._repository = MemoryRepository(
            memory_file=self.config.memory_file,
            embedding_model=self.config.embedding_model,
            enable_embeddings=self.config.enable_embeddings,
            debug=self.config.debug,
            memory_limit=self.config.background_memory_limit,
            threshold=self.config.background_memory_threshold
        )
        
        self._agent = KnowledgeAgent(
            model=self.config.model,
            name="GRKMemory Knowledge Assistant"
        )
    
    @property
    def repository(self) -> MemoryRepository:
        """Get the memory repository."""
        return self._repository
    
    @property
    def agent(self) -> KnowledgeAgent:
        """Get the knowledge agent."""
        return self._agent
    
    @property
    def graph(self) -> SemanticGraph:
        """Get the semantic graph."""
        return self._repository.semantic_graph
    
    def search(
        self,
        query: str,
        method: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for relevant memories.
        
        Args:
            query: Search query string.
            method: Search method ('graph', 'embedding', 'tags', 'entities').
                   Uses config default if not provided.
            limit: Maximum results to return.
        
        Returns:
            List of search results with 'memoria' and 'similaridade' keys.
        
        Example:
            results = grk.search("AI projects")
            for r in results:
                print(f"{r['memoria']['summary']} - {r['similaridade']:.2f}")
        """
        method = method or self.config.background_memory_method
        return self._repository.search(query, method=method, limit=limit)
    
    def chat(
        self,
        message: str,
        include_memory: bool = True,
        method: Optional[str] = None
    ) -> str:
        """
        Chat with the GRKMemory agent.
        
        Automatically includes relevant memory context if available.
        
        Args:
            message: User message.
            include_memory: Whether to include memory context.
            method: Memory search method.
        
        Returns:
            Agent response text.
        
        Example:
            response = grk.chat("What did we discuss last time?")
            print(response)
        """
        context = None
        
        if include_memory and self.config.background_memory_enabled:
            results = self.search(message, method=method)
            if results:
                context = self._repository.format_background(results)
                if self.config.debug:
                    print(f"🧠 Found {len(results)} relevant memories")
        
        return self._agent.chat(message, context=context)
    
    def chat_with_history(
        self,
        messages: List[Dict],
        include_memory: bool = True,
        method: Optional[str] = None
    ) -> str:
        """
        Continue a conversation with message history.
        
        Args:
            messages: List of message dictionaries.
            include_memory: Whether to include memory context.
            method: Memory search method.
        
        Returns:
            Agent response text.
        """
        if include_memory and self.config.background_memory_enabled and messages:
            # Get last user message for context search
            last_user_msg = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            
            if last_user_msg:
                results = self.search(last_user_msg, method=method)
                if results:
                    context = self._repository.format_background(results)
                    # Add context to last user message
                    messages = [m.copy() for m in messages]
                    for i in range(len(messages) - 1, -1, -1):
                        if messages[i].get("role") == "user":
                            messages[i]["content"] += context
                            break
        
        return self._agent.chat_with_history(messages)
    
    def save_conversation(self, messages: List[Dict]) -> bool:
        """
        Process and save a conversation.
        
        Analyzes the conversation to extract structured information
        and saves it to the memory repository.
        
        Args:
            messages: List of conversation messages.
        
        Returns:
            True if saved successfully.
        
        Example:
            success = grk.save_conversation([
                {"role": "user", "content": "Let's discuss AI"},
                {"role": "assistant", "content": "Sure! What aspect?"}
            ])
        """
        data = self._agent.process_conversation(messages)
        if not data:
            if self.config.debug:
                print("❌ Failed to process conversation")
            return False
        
        return self._repository.save(data)
    
    def save_memory(self, data: Dict) -> bool:
        """
        Save a pre-structured memory directly.
        
        Args:
            data: Dictionary with memory data.
        
        Returns:
            True if saved successfully.
        """
        return self._repository.save(data)
    
    def get_stats(self) -> Dict:
        """
        Get system statistics.
        
        Returns:
            Dictionary with memory and graph statistics.
        """
        return self._repository.get_stats()
    
    def get_graph_stats(self) -> Dict:
        """
        Get semantic graph statistics.
        
        Returns:
            Dictionary with graph statistics.
        """
        return self.graph.get_stats()
    
    def get_top_memories(self, limit: int = 10, by: str = "density") -> List[Dict]:
        """
        Get top memories by density or centrality.
        
        Args:
            limit: Maximum memories to return.
            by: Sort by 'density' or 'centrality'.
        
        Returns:
            List of (summary, score) tuples.
        """
        if by == "centrality":
            return self.graph.get_top_centrality_nodes(limit)
        return self.graph.get_top_density_nodes(limit)
    
    def format_memory_context(self, results: List[Dict]) -> str:
        """
        Format search results as context string.
        
        Args:
            results: Search results from search() method.
        
        Returns:
            Formatted context string.
        """
        return self._repository.format_background(results)
    
    @property
    def memory_count(self) -> int:
        """Get the total number of stored memories."""
        return len(self._repository.memories)
