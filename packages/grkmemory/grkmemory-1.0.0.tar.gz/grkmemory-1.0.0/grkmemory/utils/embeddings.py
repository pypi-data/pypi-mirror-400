"""
Embedding utilities for GRKMemory.
"""

import math
from typing import List, Optional
from openai import OpenAI


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embedding vectors.
    
    Args:
        embedding1: First embedding vector.
        embedding2: Second embedding vector.
    
    Returns:
        Similarity score between 0 and 1.
    
    Example:
        >>> vec1 = [1.0, 0.0, 0.0]
        >>> vec2 = [1.0, 0.0, 0.0]
        >>> cosine_similarity(vec1, vec2)
        1.0
    """
    if not embedding1 or not embedding2 or len(embedding1) != len(embedding2):
        return 0.0
    
    dot = sum(a * b for a, b in zip(embedding1, embedding2))
    norm1 = math.sqrt(sum(a * a for a in embedding1))
    norm2 = math.sqrt(sum(b * b for b in embedding2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot / (norm1 * norm2)


class EmbeddingGenerator:
    """
    Generator for text embeddings using OpenAI API.
    
    Example:
        generator = EmbeddingGenerator(model="text-embedding-3-small")
        embedding = generator.generate("Hello world")
    """
    
    def __init__(self, model: str = "text-embedding-3-small", client: Optional[OpenAI] = None):
        """
        Initialize the embedding generator.
        
        Args:
            model: The embedding model to use.
            client: Optional OpenAI client. If not provided, creates a new one.
        """
        self.model = model
        self.client = client or OpenAI()
    
    def generate(self, text: str) -> List[float]:
        """
        Generate embedding for a text string.
        
        Args:
            text: The text to embed.
        
        Returns:
            List of floats representing the embedding vector.
        """
        if not text or not text.strip():
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"⚠️ Error generating embedding: {e}")
            return []
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed.
        
        Returns:
            List of embedding vectors.
        """
        if not texts:
            return []
        
        # Filter empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return [[] for _ in texts]
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            
            # Map back to original indices
            embeddings = [[] for _ in texts]
            valid_idx = 0
            for i, text in enumerate(texts):
                if text and text.strip():
                    embeddings[i] = response.data[valid_idx].embedding
                    valid_idx += 1
            
            return embeddings
        except Exception as e:
            print(f"⚠️ Error generating batch embeddings: {e}")
            return [[] for _ in texts]
