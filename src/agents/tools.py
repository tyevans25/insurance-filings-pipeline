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
from processing.embedder import TextEmbedder

class AgentTools:
    def __init__(self):
        self.postgres = PostgresClient()
        self.qdrant = QdrantClient()
        self.embedder = TextEmbedder()
    
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
        query_embedding = self.embedder.model.encode(query).tolist()
        
        # Search QDrant
        results = self.qdrant.search(query_embedding, limit=limit * 2)
        
        # Filter by company if specified
        if company:
            results = [r for r in results if r.get('metadata', {}).get('company') == company]
        
        return results[:limit]
    
    def get_filing_metadata(self, company: str = None, filing_type: str = None) -> List[Dict]:
        """
        Get filing metadata from PostgreSQL
        
        Args:
            company: Filter by company name
            filing_type: Filter by filing type
        
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