"""
Multi-Agent Architecture for DAIS
M06 Refactor - Distinct agent roles for retrieval, analysis, and synthesis
"""

from .retrieval_agent import RetrievalAgent
from .analysis_agent import AnalysisAgent
from .synthesis_agent import SynthesisAgent
from .orchestrator import MultiAgentOrchestrator

__all__ = [
    'RetrievalAgent',
    'AnalysisAgent',
    'SynthesisAgent',
    'MultiAgentOrchestrator',
]