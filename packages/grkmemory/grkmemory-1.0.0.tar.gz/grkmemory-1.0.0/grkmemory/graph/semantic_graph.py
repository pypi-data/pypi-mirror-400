"""
Semantic Graph for GRKMemory.

This module provides a graph-based structure for analyzing relationships
between conversation sessions based on shared concepts, entities, and embeddings.
"""

from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field

from ..utils.text import normalize_items
from ..utils.embeddings import cosine_similarity


@dataclass
class GraphNode:
    """Represents a node in the semantic graph."""
    session_id: str
    summary: str
    created_at: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    entities: Set[str] = field(default_factory=set)
    key_points: Set[str] = field(default_factory=set)
    embedding: List[float] = field(default_factory=list)
    memoria: Dict = field(default_factory=dict)
    density: float = 0.0
    centrality: float = 0.0
    neighbors: Dict[str, Dict] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Represents an edge between two nodes."""
    shared_tags: int = 0
    shared_entities: int = 0
    shared_key_points: int = 0
    embedding_similarity: float = 0.0
    weight: float = 0.0


class SemanticGraph:
    """
    Semantic graph for analyzing density and relationships between sessions.
    
    The graph connects conversation sessions based on:
    - Shared tags
    - Shared entities
    - Shared key points
    - Embedding similarity
    
    Example:
        graph = SemanticGraph()
        graph.add_conversation(memory_dict)
        graph.calculate_densities()
        top_nodes = graph.get_top_density_nodes(limit=10)
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.75,
        tag_weight: float = 1.0,
        entity_weight: float = 1.2,
        key_point_weight: float = 1.1,
        embedding_weight: float = 2.5
    ):
        """
        Initialize the semantic graph.
        
        Args:
            similarity_threshold: Minimum embedding similarity to create edge.
            tag_weight: Weight for shared tags in edge calculation.
            entity_weight: Weight for shared entities.
            key_point_weight: Weight for shared key points.
            embedding_weight: Weight for embedding similarity.
        """
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[Tuple[str, str], GraphEdge] = {}
        self.total_conversations = 0
        self.last_rebuild = None
        
        self.similarity_threshold = similarity_threshold
        self.tag_weight = tag_weight
        self.entity_weight = entity_weight
        self.key_point_weight = key_point_weight
        self.embedding_weight = embedding_weight
    
    def _ensure_node(self, memoria: Dict) -> GraphNode:
        """Get or create a node for a memory."""
        session_id = memoria["id"]
        
        if session_id not in self.nodes:
            self.nodes[session_id] = GraphNode(
                session_id=session_id,
                summary=memoria.get("summary", ""),
                created_at=memoria.get("created_at"),
                tags=normalize_items(memoria.get("tags", [])),
                entities=normalize_items(memoria.get("entities", [])),
                key_points=normalize_items(memoria.get("key_points", [])),
                embedding=memoria.get("embedding", []),
                memoria=memoria,
            )
        
        return self.nodes[session_id]
    
    def _update_edge(
        self,
        session_a: str,
        session_b: str,
        shared_tags: int,
        shared_entities: int,
        shared_key_points: int,
        embedding_similarity: float
    ):
        """Update or create an edge between two nodes."""
        if session_a == session_b:
            return
        
        key = tuple(sorted([session_a, session_b]))
        
        current = self.edges.get(key, GraphEdge())
        current.shared_tags = shared_tags
        current.shared_entities = shared_entities
        current.shared_key_points = shared_key_points
        current.embedding_similarity = max(current.embedding_similarity, embedding_similarity)
        
        # Calculate weight
        weight = (
            shared_tags * self.tag_weight +
            shared_entities * self.entity_weight +
            shared_key_points * self.key_point_weight
        )
        
        if embedding_similarity >= self.similarity_threshold:
            weight += embedding_similarity * self.embedding_weight
        
        current.weight = weight
        
        if weight > 0:
            self.edges[key] = current
            edge_dict = {
                "shared_tags": current.shared_tags,
                "shared_entities": current.shared_entities,
                "shared_key_points": current.shared_key_points,
                "embedding_similarity": current.embedding_similarity,
                "weight": current.weight,
            }
            self.nodes[session_a].neighbors[session_b] = edge_dict
            self.nodes[session_b].neighbors[session_a] = edge_dict
        else:
            self.edges.pop(key, None)
            self.nodes[session_a].neighbors.pop(session_b, None)
            self.nodes[session_b].neighbors.pop(session_a, None)
    
    def add_conversation(self, memoria: Dict) -> GraphNode:
        """
        Add a conversation session to the semantic graph.
        
        Args:
            memoria: Dictionary containing conversation data with keys:
                - id: Unique session identifier
                - summary: Text summary of conversation
                - tags: List of tags
                - entities: List of entities mentioned
                - key_points: List of key points
                - embedding: Optional embedding vector
        
        Returns:
            The created or updated GraphNode.
        """
        session_node = self._ensure_node(memoria)
        self.total_conversations = len(self.nodes)
        
        # Update edges with existing sessions
        for other_id, other_node in self.nodes.items():
            if other_id == session_node.session_id:
                continue
            
            shared_tags = len(session_node.tags & other_node.tags)
            shared_entities = len(session_node.entities & other_node.entities)
            shared_key_points = len(session_node.key_points & other_node.key_points)
            embedding_sim = cosine_similarity(session_node.embedding, other_node.embedding)
            
            self._update_edge(
                session_node.session_id,
                other_id,
                shared_tags,
                shared_entities,
                shared_key_points,
                embedding_sim
            )
        
        return session_node
    
    def calculate_densities(self):
        """Calculate density for each session node."""
        for node in self.nodes.values():
            neighbor_weights = [
                edge_data["weight"] 
                for edge_data in node.neighbors.values()
            ]
            
            if neighbor_weights:
                node.density = sum(neighbor_weights) / len(neighbor_weights)
            else:
                node.density = 0.0
    
    def calculate_centralities(self):
        """Calculate centrality (connection degree) for each node."""
        for node in self.nodes.values():
            degree = len(node.neighbors)
            weighted = sum(edge["weight"] for edge in node.neighbors.values())
            node.centrality = (degree * 0.4 + weighted * 0.6) / max(1, self.total_conversations)
    
    def get_top_density_nodes(self, limit: int = 20) -> List[Tuple[str, float]]:
        """
        Get sessions with highest density.
        
        Args:
            limit: Maximum number of nodes to return.
        
        Returns:
            List of (summary, density) tuples.
        """
        self.calculate_densities()
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda x: x.density,
            reverse=True
        )
        return [(node.summary, node.density) for node in sorted_nodes[:limit]]
    
    def get_top_centrality_nodes(self, limit: int = 20) -> List[Tuple[str, float]]:
        """
        Get sessions with highest centrality.
        
        Args:
            limit: Maximum number of nodes to return.
        
        Returns:
            List of (summary, centrality) tuples.
        """
        self.calculate_centralities()
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda x: x.centrality,
            reverse=True
        )
        return [(node.summary, node.centrality) for node in sorted_nodes[:limit]]
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the semantic graph.
        
        Returns:
            Dictionary with graph statistics.
        """
        self.calculate_densities()
        self.calculate_centralities()
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "total_conversations": self.total_conversations,
            "avg_density": sum(n.density for n in self.nodes.values()) / max(1, len(self.nodes)),
            "avg_centrality": sum(n.centrality for n in self.nodes.values()) / max(1, len(self.nodes)),
            "top_density": self.get_top_density_nodes(10),
            "top_centrality": self.get_top_centrality_nodes(10),
        }
    
    def clear(self):
        """Clear all nodes and edges from the graph."""
        self.nodes.clear()
        self.edges.clear()
        self.total_conversations = 0
