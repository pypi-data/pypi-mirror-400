"""
Text processing utilities for GRKMemory.
"""

import unicodedata
from typing import List, Set, Optional

# Try to import tiktoken for accurate token counting
try:
    import tiktoken
    _HAS_TIKTOKEN = True
except ImportError:
    _HAS_TIKTOKEN = False


# Portuguese stop words
STOP_WORDS = {
    'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'em', 'na', 'no',
    'para', 'com', 'por', 'sobre', 'como', 'que', 'quando', 'onde', 'porque',
    'e', 'ou', 'mas', 'se', 'já', 'mais', 'menos', 'muito', 'pouco',
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that'
}

# Irregular plurals mapping
IRREGULAR_PLURALS = {
    "carros": "carro",
    "automoveis": "automovel",
    "automóveis": "automovel",
    "veiculos": "veiculo",
    "veículos": "veiculo",
}


def normalize_term(term: str) -> str:
    """
    Normalize a term for comparison and search.
    
    Applies:
    - Lowercase conversion
    - Accent removal
    - Irregular plural handling
    - Regular plural reduction
    
    Args:
        term: The term to normalize.
    
    Returns:
        Normalized term string.
    
    Example:
        >>> normalize_term("Automóveis")
        'automovel'
        >>> normalize_term("Carros")
        'carro'
    """
    term = term.strip().lower()
    
    # Remove accents
    term = ''.join(
        c for c in unicodedata.normalize('NFD', term)
        if unicodedata.category(c) != 'Mn'
    )
    
    # Handle irregular plurals
    if term in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[term]
    
    # Handle regular plurals (Portuguese)
    if term.endswith("oes"):
        return term[:-3] + "ao"
    if term.endswith("as") or term.endswith("os"):
        return term[:-1]
    if term.endswith("ns"):
        return term[:-2] + "m"
    
    return term


def normalize_items(items: List[str]) -> Set[str]:
    """
    Normalize a list of items into a set of normalized strings.
    
    Args:
        items: List of strings to normalize.
    
    Returns:
        Set of normalized strings.
    """
    normalized = set()
    for item in items or []:
        if isinstance(item, str) and item.strip():
            normalized.add(normalize_term(item))
    return normalized


def extract_concepts(query: str, min_length: int = 2) -> List[str]:
    """
    Extract meaningful concepts from a query string.
    
    Removes stop words and normalizes terms.
    
    Args:
        query: The query string to process.
        min_length: Minimum character length for a concept.
    
    Returns:
        List of extracted concepts.
    
    Example:
        >>> extract_concepts("What did we discuss about AI projects?")
        ['discuss', 'ai', 'project']
    """
    words = query.lower().split()
    concepts = []
    
    for word in words:
        normalized = normalize_term(word)
        if len(normalized) > min_length and normalized not in STOP_WORDS:
            concepts.append(normalized)
    
    return concepts


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count the number of tokens in a text string.
    
    Uses tiktoken if available, otherwise falls back to approximation.
    
    Args:
        text: The text to count tokens for.
        model: The model to use for tokenization.
    
    Returns:
        Estimated token count.
    """
    if not text:
        return 0
    
    if _HAS_TIKTOKEN:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    
    # Fallback: approximately 1 token per 4 characters
    return max(1, (len(text) // 4) + 1)


def count_messages_tokens(messages: List[dict], model: str = "gpt-4o") -> int:
    """
    Count tokens in a list of chat messages.
    
    Args:
        messages: List of message dictionaries with 'content' key.
        model: The model to use for tokenization.
    
    Returns:
        Total token count.
    """
    total = 0
    for msg in messages or []:
        total += count_tokens(msg.get("content", ""), model)
    return total
