"""
FastAPI Backend for Multi-Agent Insurance Reserving Intelligence
Supports both Claude and Ollama LLM providers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from src.agents import MultiAgentOrchestrator

app = FastAPI(
    title="P&C Reserving Intelligence API",
    description="Multi-Agent Document AI System for SEC Filing Analysis",
    version="2.0.0"
)

# CORS middleware - allows React app to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative port
        "https://*.vercel.app",   # Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator once at startup
# Uses LLM_PROVIDER from environment variable (defaults to 'claude')
orchestrator = MultiAgentOrchestrator()


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str
    company: Optional[str] = None
    use_balanced_search: bool = True
    llm_provider: Optional[str] = None  # Dev mode only - allows switching providers


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    answer: str
    sources: list
    num_sources: int
    companies_mentioned: list
    pipeline_stats: dict


@app.get("/")
async def root():
    """Health check endpoint"""
    provider_info = orchestrator.synthesis_agent.get_provider_info()
    return {
        "status": "healthy",
        "service": "P&C Reserving Intelligence API",
        "architecture": "multi-agent",
        "llm_provider": provider_info['provider'],
        "llm_model": provider_info['model']
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    provider_info = orchestrator.synthesis_agent.get_provider_info()
    return {
        "status": "healthy",
        "orchestrator": "initialized",
        "agents": ["RetrievalAgent", "AnalysisAgent", "SynthesisAgent"],
        "llm_provider": provider_info['provider'],
        "llm_model": provider_info['model'],
        "base_url": provider_info['base_url']
    }


@app.get("/providers")
async def get_providers():
    """
    Get available LLM providers
    Only accessible in development mode
    """
    is_dev = os.getenv('NODE_ENV', 'production') == 'development'
    
    if not is_dev:
        return {
            "available": False,
            "message": "Provider selection only available in development mode"
        }
    
    current_provider = orchestrator.synthesis_agent.get_provider_info()
    
    return {
        "available": True,
        "current_provider": current_provider['provider'],
        "providers": [
            {
                "id": "claude",
                "name": "Claude (Anthropic)",
                "model": "claude-sonnet-4-20250514",
                "recommended": True
            },
            {
                "id": "ollama",
                "name": "Ollama (GSU Server)",
                "model": os.getenv('OLLAMA_MODEL', 'llama3'),
                "recommended": False
            }
        ]
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process a user query through the multi-agent pipeline.
    
    Args:
        request: QueryRequest with query text, optional company filter, search settings, and optional LLM provider
        
    Returns:
        QueryResponse with answer, sources, and metadata
    """
    try:
        # Only allow llm_provider override in development mode
        llm_provider = None
        if request.llm_provider:
            is_dev = os.getenv('NODE_ENV', 'production') == 'development'
            if is_dev:
                llm_provider = request.llm_provider
            else:
                print("[API] Ignoring llm_provider in production mode")
        
        response = orchestrator.query(
            user_query=request.query,
            company=request.company,
            use_balanced_search=request.use_balanced_search,
            llm_provider=llm_provider
        )
        
        return response
        
    except Exception as e:
        return {
            "answer": f"Error processing query: {str(e)}",
            "sources": [],
            "num_sources": 0,
            "companies_mentioned": [],
            "pipeline_stats": {
                "error": str(e)
            }
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)