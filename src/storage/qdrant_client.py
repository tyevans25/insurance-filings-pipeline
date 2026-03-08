"""
QDrant vector database client for storing embeddings
"""
from qdrant_client import QdrantClient as QdrantSDK
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import os

class QdrantClient:
    def __init__(self, collection_name: str = 'insurance_filings'):
        self.client = QdrantSDK(
            host=os.getenv('QDRANT_HOST', 'localhost'),
            port=int(os.getenv('QDRANT_PORT', '6333'))
        )
        self.collection_name = collection_name
        self.embedding_dim = 384  # for all-MiniLM-L6-v2
        
        self._create_collection()
    
    def _create_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
    
    def insert_embeddings(self, chunks: List[Dict]):
        """
        Insert chunk embeddings into QDrant
        
        Args:
            chunks: List of chunk dicts with 'embedding' field
        """
        points = []
        
        for idx, chunk in enumerate(chunks):
            if 'embedding' not in chunk:
                continue
            
            point = PointStruct(
                id=idx,  # Or use hash of chunk_id
                vector=chunk['embedding'],
                payload={
                    'chunk_id': chunk['chunk_id'],
                    'filing_id': chunk.get('filing_id'),
                    'company': chunk.get('company'),
                    'filing_date': chunk.get('filing_date'),
                    'section_type': chunk.get('section_type'),
                    'text': chunk['text'][:500],  # Store truncated text
                    'page_num': chunk.get('page_num')
                }
            )
            points.append(point)
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
    
    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """
        Search for similar chunks
        
        Args:
            query_vector: Query embedding
            limit: Number of results
        
        Returns:
            List of similar chunks with scores
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return [
            {
                'chunk_id': hit.payload['chunk_id'],
                'text': hit.payload['text'],
                'score': hit.score,
                'metadata': hit.payload
            }
            for hit in results
        ]