"""
Main agent orchestrator - decides which tools to use and synthesizes answers
"""
from typing import Dict, List
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from agents.tools import AgentTools
import json

# Load environment variables from .env
load_dotenv()


class ReservingAgent:
    def __init__(self):
        self.tools = AgentTools()
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        self.system_prompt = """You are an expert P&C insurance reserving analyst with deep knowledge of actuarial science and loss reserving.

You have access to SEC filings (10-K, 10-Q) from major insurance carriers: AIG, Travelers, and Chubb.

Available Tools:
1. semantic_search(query, limit, company) - Search narrative text from filings
2. get_filing_metadata(company, filing_type) - Get filing information
3. get_financial_tables(company, keyword) - Query structured financial tables and data

When answering questions about reserves, loss development, or financial metrics:
1. First use get_financial_tables() to find relevant structured data
2. Then use semantic_search() for narrative context
3. Combine both sources in your answer
4. Always cite specific companies, filing types, and dates
5. Distinguish between narrative text and tabular data

Acknowledge any limitations in the available data and suggest what additional information would be helpful."""
    
    def answer_query(self, query: str, company: str = None) -> Dict:
        """
        Answer a user query using available tools
        
        Args:
            query: User's natural language question
            company: Optional company to focus on
        
        Returns:
            Dict with answer and sources
        """
        print(f"\n🔍 Processing query: {query}")
        if company:
            print(f"   Focusing on: {company}")
        
        # Check if query needs financial tables
        financial_keywords = ['reserve', 'loss', 'ratio', 'premium', 'metric', 'amount', 'billion', 'million', 'data', 'number']
        needs_tables = any(kw in query.lower() for kw in financial_keywords)
        
        context_parts = []
        
        # Get table data if query seems financial
        if needs_tables:
            print("   Querying financial tables...")
            tables = self.tools.get_financial_tables(company=company, keyword='reserve')
            if tables:
                table_summary = f"\n=== Financial Tables ({len(tables)} found) ===\n"
                for i, table in enumerate(tables[:5], 1):  # Top 5 tables
                    title = table.get('metadata', {}).get('title', 'Untitled')
                    company_name = table.get('company', 'Unknown')
                    filing_type = table.get('filing_type', 'Unknown')
                    page = table.get('page_num', 0)
                    
                    table_summary += f"\n[Table {i}] {company_name} {filing_type} - Page {page}\n"
                    table_summary += f"Title: {title}\n"
                    
                    # Include sample data
                    if table.get('table_data'):
                        data_str = str(table['table_data'])[:300]
                        table_summary += f"Data: {data_str}...\n"
                
                context_parts.append(table_summary)
                print(f"   Found {len(tables)} financial tables")
        
        # Get semantic search results
        print("   Searching narrative text...")
        search_results = self.tools.semantic_search(query, limit=5, company=company)
        
        if search_results:
            narrative_context = "\n=== Narrative Context from Filings ===\n"
            for i, result in enumerate(search_results, 1):
                metadata = result.get('metadata', {})
                narrative_context += f"\n[Passage {i}] {metadata.get('company')} - {metadata.get('filing_type')}\n"
                narrative_context += f"{result['text'][:400]}...\n"
            context_parts.append(narrative_context)
            print(f"   Found {len(search_results)} relevant passages")
        
        # Combine contexts
        full_context = "\n".join(context_parts) if context_parts else "No relevant information found."
        
        # Generate answer
        print("   Generating answer with Claude...")
        answer = self._synthesize_answer(query, full_context)
        
        return {
            'query': query,
            'answer': answer,
            'sources': search_results,
            'num_sources': len(search_results),
            'num_tables': len(tables) if needs_tables and tables else 0
        }
    
    def _synthesize_answer(self, query: str, context: str) -> str:
        """Use Claude to synthesize final answer from context"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on the following information from SEC filings:

{context}

Please answer this question: {query}

Provide a clear, concise answer that:
- Cites specific companies and filing dates
- References both tabular data and narrative context when available
- Highlights key findings
- Notes any important caveats or limitations
- Is written for an actuarial audience"""
                }
            ]
        )
        
        return response.content[0].text