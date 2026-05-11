"""
Multi-Agent Orchestrator
Coordinates Retrieval → Analysis → Synthesis pipeline
Now supports multiple LLM providers (Claude/Ollama)
"""

from typing import Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.retrieval_agent import RetrievalAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.synthesis_agent import SynthesisAgent


class MultiAgentOrchestrator:
    """
    Orchestrator that coordinates the multi-agent pipeline:
    1. RetrievalAgent: Fetches relevant documents and tables
    2. AnalysisAgent: Processes and structures retrieved data
    3. SynthesisAgent: Generates natural language response
    """
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize orchestrator with all agents
        
        Args:
            llm_provider: 'claude' or 'ollama' (optional, defaults to env var)
        """
        print(f"[Orchestrator] Initializing multi-agent system...")
        
        # Import database clients
        from src.storage.postgres_client import PostgresClient
        from src.storage.qdrant_client import QdrantClient
        
        # Initialize database clients
        postgres_client = PostgresClient()
        qdrant_client = QdrantClient()
        
        # Initialize agents with required dependencies
        self.retrieval_agent = RetrievalAgent(postgres_client, qdrant_client)
        self.analysis_agent = AnalysisAgent()
        self.synthesis_agent = SynthesisAgent(llm_provider=llm_provider)
        
        provider_info = self.synthesis_agent.get_provider_info()
        print(f"[Orchestrator] Ready with LLM provider: {provider_info['provider']} ({provider_info['model']})")
    
    def query(
        self,
        user_query: str,
        company: Optional[str] = None,
        use_balanced_search: bool = True,
        llm_provider: Optional[str] = None
    ) -> dict:
        """
        Process user query through multi-agent pipeline
        
        Args:
            user_query: Natural language query from user
            company: Optional company filter (AIG, Travelers, Chubb, or None for all)
            use_balanced_search: Whether to use balanced multi-company search
            llm_provider: Optional override for LLM provider (dev mode only)
            
        Returns:
            Dictionary containing:
                - answer: Natural language response
                - sources: List of source documents/tables
                - num_sources: Count of sources
                - companies_mentioned: List of companies in results
                - pipeline_stats: Metadata about the query
        """
        print(f"\n[Orchestrator] Processing query: '{user_query[:50]}...'")
        print(f"[Orchestrator] Company filter: {company or 'All'}")
        print(f"[Orchestrator] Balanced search: {use_balanced_search}")
        
        # If llm_provider override provided (dev mode), reinitialize synthesis agent
        if llm_provider and llm_provider != self.synthesis_agent.llm_client.provider:
            print(f"[Orchestrator] Switching LLM provider to: {llm_provider}")
            self.synthesis_agent = SynthesisAgent(llm_provider=llm_provider)
        
        # Step 1: Retrieval Agent - Get relevant documents and tables
        print("[Orchestrator] Step 1/3: Retrieval Agent")
        
        # Retrieve documents
        documents = self.retrieval_agent.retrieve_documents(
            query=user_query,
            company=company,
            limit=5,
            use_balanced=use_balanced_search
        )
        
        # Retrieve financial tables
        tables = self.retrieval_agent.retrieve_financial_tables(
            company=company,
            keyword="reserve"
        )
        
        retrieval_results = {
            'documents': documents,
            'tables': tables
        }
        
        num_docs = len(retrieval_results.get('documents', []))
        num_tables = len(retrieval_results.get('tables', []))
        print(f"[Orchestrator] Retrieved {num_docs} documents, {num_tables} tables")
        
        # Step 2: Analysis Agent - Process and structure data
        print("[Orchestrator] Step 2/3: Analysis Agent")
        analyzed_data = self.analysis_agent.analyze(
            query=user_query,
            documents=retrieval_results.get('documents', []),
            tables=retrieval_results.get('tables', [])
        )
        
        # Step 3: Synthesis Agent - Generate response
        print("[Orchestrator] Step 3/3: Synthesis Agent")
        
        # Build context for synthesis from analyzed data
        synthesis_context = {
            'documents': retrieval_results.get('documents', []),
            'tables': retrieval_results.get('tables', []),
            'key_facts': analyzed_data.get('key_facts', []),
            'metrics': analyzed_data.get('financial_metrics', [])
        }
        
        answer = self.synthesis_agent.synthesize(
            user_query=user_query,
            analyzed_data=synthesis_context,
            company=company
        )
        
        # Combine all sources
        all_sources = (
            retrieval_results.get('documents', []) + 
            retrieval_results.get('tables', [])
        )
        
        # Extract unique companies mentioned
        companies_mentioned = list(set(
            source.get('company') 
            for source in all_sources 
            if source.get('company')
        ))
        
        # Calculate average relevance score
        scores = [s.get('relevance_score', 0) for s in all_sources if s.get('relevance_score')]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Build response
        response = {
            'answer': answer,
            'sources': all_sources,
            'num_sources': len(all_sources),
            'companies_mentioned': companies_mentioned,
            'pipeline_stats': {
                'documents_retrieved': num_docs,
                'tables_retrieved': num_tables,
                'companies_mentioned': companies_mentioned,
                'avg_relevance_score': round(avg_score, 3),
                'llm_provider': self.synthesis_agent.llm_client.provider,
                'llm_model': self.synthesis_agent.llm_client.model
            }
        }
        
        print(f"[Orchestrator] Complete! Generated {len(answer)} character response")
        print(f"[Orchestrator] LLM used: {response['pipeline_stats']['llm_provider']}")
        
        return response


if __name__ == "__main__":
    # Test orchestrator
    orchestrator = MultiAgentOrchestrator()
    
    result = orchestrator.query(
        user_query="What are AIG's catastrophe losses from Hurricane Helene?",
        company="AIG",
        use_balanced_search=False
    )
    
    print("\n=== RESULT ===")
    print(f"Answer: {result['answer'][:200]}...")
    print(f"Sources: {result['num_sources']}")
    print(f"Stats: {result['pipeline_stats']}")