"""
Retrieval Agent - Responsible for finding relevant documents and tables
Part of multi-agent architecture refactor for M06
"""

from typing import List, Dict, Optional
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class RetrievalAgent:
    """
    Agent responsible for retrieving relevant documents from the knowledge base.
    Handles semantic search, balanced multi-company search, and financial table queries.
    """
    
    def __init__(self, postgres_client, qdrant_client):
        """
        Initialize the retrieval agent with database clients.
        
        Args:
            postgres_client: PostgreSQL client for structured data
            qdrant_client: QDrant client for vector search
        """
        self.postgres = postgres_client
        self.qdrant = qdrant_client
        # Initialize embedding model for query encoding
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        logger.info("RetrievalAgent initialized with embedding model")
    
    def retrieve_documents(
        self, 
        query: str, 
        company: Optional[str] = None, 
        limit: int = 5,
        use_balanced: bool = False
    ) -> List[Dict]:
        """
        Retrieve relevant documents using semantic search.
        
        Args:
            query: User query string
            company: Optional company filter (AIG, Travelers, Chubb)
            limit: Number of results to return
            use_balanced: Whether to use balanced multi-company search
            
        Returns:
            List of document chunks with metadata and relevance scores
        """
        logger.info(f"Retrieving documents for query: {query[:50]}...")
        
        if use_balanced and company is None:
            # Use balanced multi-company search (M05 improvement)
            return self._balanced_search(query, limit)
        else:
            # Use standard semantic search
            return self._semantic_search(query, company, limit)
    
    def retrieve_financial_tables(
        self, 
        company: Optional[str] = None, 
        keyword: str = "reserve"
    ) -> List[Dict]:
        """
        Retrieve structured financial tables from PostgreSQL.
        
        Args:
            company: Optional company filter
            keyword: Keyword to filter tables (default: "reserve")
            
        Returns:
            List of financial tables with metadata
        """
        logger.info(f"Retrieving financial tables for company: {company}, keyword: {keyword}")
        
        query = """
            SELECT 
                ft.table_id,
                ft.table_type,
                ft.table_data,
                ft.metadata,
                ft.page_num,
                f.company,
                f.filing_date,
                f.filing_type
            FROM financial_tables ft
            JOIN filings f ON ft.filing_id = f.filing_id
            WHERE 1=1
        """
        
        params = []
        
        if company:
            query += " AND f.company = %s"
            params.append(company)
        
        if keyword:
            query += " AND (ft.table_type ILIKE %s OR ft.metadata::text ILIKE %s)"
            params.append(f"%{keyword}%")
            params.append(f"%{keyword}%")
        
        query += " ORDER BY f.filing_date DESC LIMIT 10"
        
        results = self.postgres.query(query, tuple(params) if params else None)
        
        logger.info(f"Retrieved {len(results)} financial tables")
        return results
    
    def _semantic_search(
        self, 
        query: str, 
        company: Optional[str], 
        limit: int
    ) -> List[Dict]:
        """
        Standard semantic search using QDrant vector database.
        
        Args:
            query: Query string
            company: Optional company filter
            limit: Number of results
            
        Returns:
            List of relevant chunks
        """
        # Encode query to vector
        query_vector = self.embedding_model.encode(query).tolist()
        
        # Search with higher limit if filtering by company
        search_limit = limit * 3 if company else limit
        
        # Search QDrant
        search_results = self.qdrant.search(
            query_vector=query_vector,
            limit=search_limit
        )
        
        # Format and filter results
        documents = []
        for result in search_results:
            metadata = result.get('metadata', {})
            
            # Filter by company if specified
            if company and metadata.get('company') != company:
                continue
            
            documents.append({
                "text": result.get('text', ''),
                "company": metadata.get('company', ''),
                "filing_date": metadata.get('filing_date', ''),
                "filing_type": metadata.get('filing_type', ''),
                "page_num": metadata.get('page_num', ''),
                "section_type": metadata.get('section_type', ''),
                "score": result.get('score', 0)
            })
            
            # Stop when we have enough
            if len(documents) >= limit:
                break
        
        return documents
    
    def _balanced_search(self, query: str, limit: int) -> List[Dict]:
        """
        Balanced multi-company search (M05 improvement).
        Ensures equal representation from all carriers in results.
        
        Args:
            query: Query string
            limit: Total number of results to return
            
        Returns:
            Balanced list of chunks from all companies
        """
        companies = ["AIG", "Travelers", "Chubb"]
        per_company = (limit // 3) + 1
        
        all_results = []
        
        # Retrieve from each company
        for company in companies:
            company_results = self._semantic_search(query, company, per_company)
            all_results.extend(company_results)
        
        # Sort by relevance score and take top limit
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        return all_results[:limit]
    
    def get_filing_metadata(
        self, 
        company: Optional[str] = None, 
        filing_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve filing metadata from PostgreSQL.
        
        Args:
            company: Optional company filter
            filing_type: Optional filing type filter (10-K, 10-Q)
            
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
        
        results = self.postgres.query(query, tuple(params) if params else None)
        
        return results