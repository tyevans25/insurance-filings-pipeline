"""
Analysis Agent - Responsible for processing and analyzing retrieved documents
Part of multi-agent architecture refactor for M06
"""

from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """
    Agent responsible for analyzing retrieved documents and extracting key information.
    Processes both narrative text chunks and structured financial tables.
    """
    
    def __init__(self):
        """Initialize the analysis agent."""
        logger.info("AnalysisAgent initialized")
    
    def analyze(
        self, 
        query: str,
        documents: List[Dict], 
        tables: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze retrieved documents and tables to extract structured information.
        
        Args:
            query: Original user query
            documents: List of text chunks from retrieval
            tables: List of financial tables from retrieval
            
        Returns:
            Structured analysis containing:
            - key_facts: Important information from narrative
            - financial_metrics: Numbers from tables
            - companies_mentioned: List of companies in results
            - relevance_summary: Summary of relevance scores
            - source_metadata: Metadata for citations
        """
        logger.info(f"Analyzing {len(documents)} documents and {len(tables)} tables")
        
        analysis = {
            'query': query,
            'key_facts': self._extract_key_facts(documents),
            'financial_metrics': self._extract_financial_metrics(tables),
            'companies_mentioned': self._extract_companies(documents, tables),
            'relevance_summary': self._calculate_relevance_summary(documents),
            'source_metadata': self._compile_source_metadata(documents, tables),
            'document_count': len(documents),
            'table_count': len(tables)
        }
        
        logger.info(f"Analysis complete: {analysis['companies_mentioned']} companies, "
                   f"{len(analysis['key_facts'])} key facts")
        
        return analysis
    
    def _extract_key_facts(self, documents: List[Dict]) -> List[str]:
        """
        Extract key facts from narrative text chunks.
        
        Args:
            documents: List of text chunks
            
        Returns:
            List of key facts/excerpts
        """
        key_facts = []
        
        for doc in documents[:5]:  # Top 5 most relevant
            text = doc.get('text', '')
            
            # Extract sentences mentioning key actuarial terms
            sentences = text.split('.')
            for sentence in sentences:
                if any(term in sentence.lower() for term in [
                    'reserve', 'loss', 'ibnr', 'development', 'adequacy',
                    'catastrophe', 'cat', 'reinsurance', 'prior year'
                ]):
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 20:  # Ignore very short fragments
                        key_facts.append(clean_sentence)
        
        return key_facts[:10]  # Return top 10 facts
    
    def _extract_financial_metrics(self, tables: List[Dict]) -> List[Dict]:
        """
        Extract financial metrics from structured tables.
        
        Args:
            tables: List of financial tables
            
        Returns:
            List of metrics with context
        """
        metrics = []
        
        for table in tables:
            table_data = table.get('table_data', {})
            table_type = table.get('table_type', 'unknown')
            company = table.get('company', '')
            
            # Extract based on table type
            if 'reserve' in table_type.lower():
                metric = {
                    'company': company,
                    'type': table_type,
                    'data': table_data,
                    'source': f"{company} - {table.get('filing_type', '')} - Page {table.get('page_num', '')}"
                }
                metrics.append(metric)
        
        return metrics
    
    def _extract_companies(
        self, 
        documents: List[Dict], 
        tables: List[Dict]
    ) -> List[str]:
        """
        Extract list of companies mentioned in results.
        
        Args:
            documents: Text chunks
            tables: Financial tables
            
        Returns:
            Unique list of companies
        """
        companies = set()
        
        # From documents
        for doc in documents:
            company = doc.get('company', '')
            if company:
                companies.add(company)
        
        # From tables
        for table in tables:
            company = table.get('company', '')
            if company:
                companies.add(company)
        
        return sorted(list(companies))
    
    def _calculate_relevance_summary(self, documents: List[Dict]) -> Dict[str, Any]:
        """
        Calculate summary statistics for relevance scores.
        
        Args:
            documents: List of text chunks with scores
            
        Returns:
            Relevance statistics
        """
        if not documents:
            return {'avg_score': 0, 'max_score': 0, 'min_score': 0}
        
        scores = [doc.get('score', 0) for doc in documents]
        
        return {
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'total_docs': len(documents)
        }
    
    def _compile_source_metadata(
        self, 
        documents: List[Dict], 
        tables: List[Dict]
    ) -> List[Dict]:
        """
        Compile metadata for all sources (for citations).
        
        Args:
            documents: Text chunks
            tables: Financial tables
            
        Returns:
            List of source metadata
        """
        sources = []
        
        # From documents
        for idx, doc in enumerate(documents):
            source = {
                'source_id': f"doc_{idx}",
                'type': 'narrative',
                'company': doc.get('company', ''),
                'filing_date': doc.get('filing_date', ''),
                'filing_type': doc.get('filing_type', ''),
                'page_num': doc.get('page_num', ''),
                'section_type': doc.get('section_type', ''),
                'score': doc.get('score', 0)
            }
            sources.append(source)
        
        # From tables
        for idx, table in enumerate(tables):
            source = {
                'source_id': f"table_{idx}",
                'type': 'table',
                'company': table.get('company', ''),
                'filing_date': table.get('filing_date', ''),
                'filing_type': table.get('filing_type', ''),
                'page_num': table.get('page_num', ''),
                'table_type': table.get('table_type', '')
            }
            sources.append(source)
        
        return sources
    
    def detect_query_type(self, query: str) -> Dict[str, bool]:
        """
        Detect query characteristics to inform retrieval and synthesis.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary of query characteristics
        """
        query_lower = query.lower()
        
        return {
            'needs_tables': any(term in query_lower for term in [
                'reserve', 'loss', 'ratio', 'premium', 'number', 'amount', '$'
            ]),
            'is_comparison': any(term in query_lower for term in [
                'compare', 'versus', 'vs', 'difference', 'between', 'across'
            ]),
            'is_trend_analysis': any(term in query_lower for term in [
                'trend', 'over time', 'change', 'development', 'historical'
            ]),
            'is_multi_company': any(term in query_lower for term in [
                'all', 'carriers', 'companies', 'industry'
            ]) or 'and' in query_lower
        }