"""
Generate vector embeddings for text chunks
"""
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer

class TextEmbedder:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedder with sentence-transformers model
        
        Args:
            model_name: HuggingFace model name
                       'all-MiniLM-L6-v2' = 384 dimensions, fast
                       'all-mpnet-base-v2' = 768 dimensions, better quality
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for list of texts
        
        Args:
            texts: List of text strings
        
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def embed_chunk(self, chunk: Dict) -> Dict:
        """
        Add embedding to a chunk dict
        
        Args:
            chunk: Dict with 'text' field
        
        Returns:
            chunk dict with added 'embedding' field
        """
        embedding = self.model.encode(chunk['text'], convert_to_numpy=True)
        chunk['embedding'] = embedding.tolist()
        return chunk