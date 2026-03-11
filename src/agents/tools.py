"""
Agent tools for querying the insurance filings data
"""
from typing import List, Dict
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.postgres_client import PostgresClient
from storage.qdrant_client import QdrantClient


class AgentTools:
    def __init__(self):
        self.postgres = PostgresClient()
        self.qdrant = QdrantClient()
        
        # Use the new embedder from pipeline
        from pipeline.embed import embed_texts
        self.embed_fn = embed_texts
    
    def semantic_search(self, query: str, limit: int = 5, company: str = None) -> List[Dict]:
        """
        Search for relevant chunks using semantic similarity
        
        Args:
            query: Natural language query
            limit: Number of results
            company: Optional company filter
        
        Returns:
            List of relevant chunks with metadata
        """
        # Generate embedding for query
        query_vectors = self.embed_fn([query])
        query_vector = query_vectors[0]
        
        # Search QDrant
        from qdrant_client.models import SearchRequest
        
        search_result = self.qdrant.client.search(
            collection_name="insurance_filings",
            query_vector=query_vector,
            limit=limit * 3  # Get more for filtering
        )
        
        # Convert to your format
        results = []
        for hit in search_result:
            payload = hit.payload or {}
            
            # Filter by company if specified
            if company:
                hit_company = payload.get('company', '')
                if company.lower() not in hit_company.lower():
                    continue
            
            results.append({
                'text': payload.get('text', ''),
                'score': hit.score,
                'metadata': {
                    'company': payload.get('company', 'Unknown'),
                    'filing_date': payload.get('filing_date'),
                    'section_type': payload.get('section_type', 'document'),
                    'filename': payload.get('filename', ''),
                    'filing_type': payload.get('filing_type', 'Unknown')
                }
            })
        
        return results[:limit]
    
    def get_filing_metadata(self, company: str = None, filing_type: str = None) -> List[Dict]:
        """
        Get filing metadata from PostgreSQL
        
        Args:
            company: Filter by company name (AIG, Travelers, Chubb)
            filing_type: Filter by filing type (10-K, 10-Q)
        
        Returns:
            List of filing records
        """
        query = "SELECT * FROM filings WHERE 1=1"
        params = []
        
        if company:
            query += " AND company = %s"
            params.append(company)
        
        if filing_type:
            query += " AND filing_type = %s"
            params.append(filing_type)
        
        query += " ORDER BY filing_date DESC"
        
        with self.postgres.conn.cursor() as cur:
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return results