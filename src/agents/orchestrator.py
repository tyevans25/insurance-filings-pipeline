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

Your capabilities:
- semantic_search: Find relevant text passages about specific topics using vector similarity
- get_filing_metadata: Get basic filing information (dates, types, companies)
- get_chunks_by_section: Get text from specific sections (Risk Factors, MD&A, etc.)

When answering questions:
1. Use semantic_search to find the most relevant information
2. Cite specific companies, filing types, and dates in your answers
3. Be precise about financial metrics and technical terms
4. If information is from multiple sources, synthesize clearly
5. Acknowledge uncertainty if the data doesn't fully answer the question

Your user is a Senior Reserving Actuary preparing quarterly reserve reviews."""
    
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
        
        # Step 1: Semantic search for relevant context
        print("   Searching for relevant passages...")
        search_results = self.tools.semantic_search(query, limit=5, company=company)
        
        # Step 2: Build context from search results
        context = self._build_context(search_results)
        
        # Step 3: Generate answer with Claude
        print("   Generating answer...")
        answer = self._synthesize_answer(query, context)
        
        return {
            'query': query,
            'answer': answer,
            'sources': search_results,
            'num_sources': len(search_results)
        }
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """Build context string from search results"""
        if not search_results:
            return "No relevant information found in the filings."
        
        context_parts = ["=== Relevant Passages from SEC Filings ===\n"]
        
        for i, result in enumerate(search_results, 1):
            metadata = result.get('metadata', {})
            company = metadata.get('company', 'Unknown')
            filing_date = metadata.get('filing_date', 'Unknown date')
            section = metadata.get('section_type', 'Unknown section')
            text = result.get('text', '')
            score = result.get('score', 0)
            
            context_parts.append(f"\n[{i}] {company} - {filing_date} ({section})")
            context_parts.append(f"Relevance: {score:.3f}")
            context_parts.append(f"{text[:500]}...")
            context_parts.append("-" * 80)
        
        return "\n".join(context_parts)
    
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
- Highlights key findings from the passages
- Notes any important caveats or limitations
- Is written for an actuarial audience"""
                }
            ]
        )
        
        return response.content[0].text