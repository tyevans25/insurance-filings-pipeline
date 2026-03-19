"""
Filter narrative sections from SEC filings
"""
import re
from typing import List


def is_narrative_text(text: str, min_word_ratio: float = 0.6) -> bool:
    """
    Determine if text chunk is narrative (vs table/numbers)
    
    Args:
        text: Text chunk to evaluate
        min_word_ratio: Minimum ratio of words to numbers
    
    Returns:
        True if narrative, False if table/numeric
    """
    if len(text.strip()) < 50:
        return False
    
    # Count words (3+ letters)
    words = len(re.findall(r'\b[A-Za-z]{3,}\b', text))
    
    # Count numbers
    numbers = len(re.findall(r'\b\d+\b', text))
    
    # If too many numbers relative to words, it's a table
    if numbers > 0:
        word_to_number_ratio = words / numbers
        if word_to_number_ratio < min_word_ratio:
            return False
    
    # Check for table indicators
    table_indicators = [
        r'\$\s*\d+',  # Dollar amounts
        r'\d+\.\d+\s*%',  # Percentages
        r'\|\s*\|',  # Table separators
        r'^\s*\d+\s+\d+\s+\d+',  # Multiple numbers in a row
    ]
    
    table_score = sum(1 for pattern in table_indicators if re.search(pattern, text))
    if table_score >= 2:
        return False
    
    return True


def filter_chunks_for_narrative(chunks: List) -> List[int]:
    """
    Filter chunk list to keep only narrative chunks
    
    Args:
        chunks: List of ChunkRecord objects with chunk_text attribute
    
    Returns:
        List of indices of narrative chunks
    """
    narrative_indices = []
    
    for i, chunk in enumerate(chunks):
        # Access chunk_text attribute from ChunkRecord
        chunk_text = chunk.chunk_text if hasattr(chunk, 'chunk_text') else str(chunk)
        
        if is_narrative_text(chunk_text):
            narrative_indices.append(i)
    
    return narrative_indices