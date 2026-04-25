"""
Synthesis Agent - Generates natural language responses using LLM
Now supports both Claude and Ollama via abstraction layer
"""

from typing import Optional
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.llm_client import LLMClient


class SynthesisAgent:
    """
    Agent responsible for synthesizing responses from analyzed data
    Uses LLM (Claude or Ollama) to generate natural language answers
    """
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize synthesis agent
        
        Args:
            llm_provider: 'claude' or 'ollama' (optional, defaults to env var)
        """
        self.llm_client = LLMClient(provider=llm_provider)
        print(f"[SynthesisAgent] Initialized with provider: {self.llm_client.provider}")
    
    def synthesize(
        self,
        user_query: str,
        analyzed_data: dict,
        company: Optional[str] = None
    ) -> str:
        """
        Synthesize natural language response from analyzed data
        
        Args:
            user_query: Original user query
            analyzed_data: Structured data from AnalysisAgent
            company: Optional company filter
            
        Returns:
            Natural language response string
        """
        # Build context from analyzed data
        context = self.build_context(analyzed_data)
        
        # Create system prompt
        system_prompt = self._create_system_prompt()
        
        # Create user prompt with context
        user_prompt = self._create_user_prompt(user_query, context, company)
        
        # Generate response using LLM
        try:
            response = self.llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=4000,
                temperature=0.0
            )
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for LLM"""
        return """You are an expert insurance analyst specializing in Property & Casualty (P&C) insurance reserves, loss development, and financial analysis of SEC filings.

Your role is to:
1. Analyze insurance company financial data from 10-K and 10-Q filings
2. Provide clear, accurate insights about reserves, loss development, catastrophe events, and financial metrics
3. Cite specific sources and page numbers when available
4. Acknowledge limitations in the data when information is incomplete
5. Use professional insurance and actuarial terminology appropriately
6. Format responses with clear structure using markdown headers (##) and bullet points (*)

Always base your analysis strictly on the provided source documents. If information is not available in the sources, clearly state this limitation."""
    
    def _create_user_prompt(
        self,
        user_query: str,
        context: str,
        company: Optional[str]
    ) -> str:
        """Create user prompt with query and context"""
        company_context = f" focusing on {company}" if company else ""
        
        return f"""Based on the following SEC filing data{company_context}, please answer this query:

Query: {user_query}

Available Information:
{context}

Please provide a comprehensive answer based on the available data. Use markdown formatting with ## for major sections and ### for subsections. Bold important figures and company names with **text**. Use bullet points (*) for lists. If citing sources, use italic format like *Source: Company Filing*.

Structure your response clearly with headers and organized sections."""
    
    def build_context(self, analyzed_data: dict) -> str:
        """
        Build context string from analyzed data
        
        Args:
            analyzed_data: Dictionary from AnalysisAgent containing:
                - documents: List of document chunks
                - tables: List of financial tables
                - key_facts: Extracted facts
                - metrics: Extracted metrics
                
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add document context
        if analyzed_data.get('documents'):
            context_parts.append("=== DOCUMENT EXCERPTS ===")
            for i, doc in enumerate(analyzed_data['documents'], 1):
                source_info = f"{doc.get('company', 'Unknown')} {doc.get('filing_type', '')} {doc.get('filing_date', '')} (Page {doc.get('page_num', 'N/A')})"
                context_parts.append(f"\n[Document {i}] {source_info}")
                context_parts.append(f"Section: {doc.get('section_type', 'General')}")
                context_parts.append(f"Content: {doc.get('text', '')}")
        
        # Add table context
        if analyzed_data.get('tables'):
            context_parts.append("\n=== FINANCIAL TABLES ===")
            for i, table in enumerate(analyzed_data['tables'], 1):
                source_info = f"{table.get('company', 'Unknown')} {table.get('filing_type', '')} (Page {table.get('page_num', 'N/A')})"
                context_parts.append(f"\n[Table {i}] {source_info}")
                context_parts.append(f"Type: {table.get('table_type', 'Financial Data')}")
                context_parts.append(f"Data:\n{table.get('extracted_data', '')}")
        
        # Add key facts if available
        if analyzed_data.get('key_facts'):
            context_parts.append("\n=== KEY FACTS ===")
            for fact in analyzed_data['key_facts']:
                context_parts.append(f"- {fact}")
        
        # Add metrics if available
        if analyzed_data.get('metrics'):
            context_parts.append("\n=== EXTRACTED METRICS ===")
            for metric in analyzed_data['metrics']:
                if isinstance(metric, dict):
                    company = metric.get('company', '')
                    metric_type = metric.get('type', '')
                    context_parts.append(f"- {company} {metric_type}: {metric.get('data', '')}")
                else:
                    context_parts.append(f"- {metric}")
        
        return "\n".join(context_parts)
    
    def format_sources(self, sources: list) -> str:
        """
        Format source citations
        
        Args:
            sources: List of source documents/tables
            
        Returns:
            Formatted source string
        """
        if not sources:
            return "No sources available"
        
        formatted = []
        for i, source in enumerate(sources, 1):
            company = source.get('company', 'Unknown')
            filing_type = source.get('filing_type', '')
            date = source.get('filing_date', '')
            page = source.get('page_num', 'N/A')
            
            formatted.append(f"{i}. {company} {filing_type} ({date}) - Page {page}")
        
        return "\n".join(formatted)
    
    def get_provider_info(self) -> dict:
        """Get information about current LLM provider"""
        return self.llm_client.get_provider_info()


if __name__ == "__main__":
    # Test the synthesis agent
    agent = SynthesisAgent()
    
    # Test data
    test_data = {
        'documents': [
            {
                'company': 'AIG',
                'filing_type': '10-K',
                'filing_date': '2024-02-15',
                'page_num': '42',
                'section_type': 'Reserves',
                'text': 'Total loss reserves increased by $500M primarily due to catastrophe events.'
            }
        ],
        'tables': [],
        'key_facts': ['Reserve adequacy maintained', 'CAT losses from Hurricane Helene'],
        'metrics': {'Total Reserves': '$10.5B', 'Prior Year Development': '+$250M'}
    }
    
    response = agent.synthesize(
        user_query="What are AIG's reserve trends?",
        analyzed_data=test_data,
        company="AIG"
    )
    
    print("\n=== RESPONSE ===")
    print(response)
    print("\n=== PROVIDER INFO ===")
    print(agent.get_provider_info())