"""
Streamlit Chat Interface - Professional Insurance Analytics Design
Multi-Agent Document AI for SEC Filing Analysis (M06)
"""

import streamlit as st
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import multi-agent orchestrator
from src.agents import MultiAgentOrchestrator

# Page config
st.set_page_config(
    page_title="P&C Reserving Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Insurance/Finance Aesthetic CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #0a1929 0%, #1a2332 50%, #0f1419 100%);
        color: #e3e8ef;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a1929 0%, #1a2332 50%, #0f1419 100%);
    }
    
    /* Fix white header bar */
    header[data-testid="stHeader"] {
        background: #0a1929 !important;
    }
    
    /* Fix toolbar */
    [data-testid="stToolbar"] {
        background: #0a1929 !important;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Crimson Pro', serif;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    p, div, span {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(120deg, #1e3a5f 0%, #2a5298 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            repeating-linear-gradient(
                90deg,
                rgba(255,255,255,0.03) 0px,
                rgba(255,255,255,0.03) 1px,
                transparent 1px,
                transparent 40px
            ),
            repeating-linear-gradient(
                0deg,
                rgba(255,255,255,0.03) 0px,
                rgba(255,255,255,0.03) 1px,
                transparent 1px,
                transparent 40px
            );
        pointer-events: none;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        position: relative;
        z-index: 1;
    }
    
    .main-header .subtitle {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.7);
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        position: relative;
        z-index: 1;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1923 0%, #1a2332 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #b8c5d6;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #22c55e;
        padding: 0.5rem 1rem;
        border-radius: 2px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        margin: 1rem 0;
    }
    
    /* Architecture Info Box */
    .architecture-box {
        background: rgba(30, 58, 95, 0.3);
        border-left: 3px solid #2a5298;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 2px;
    }
    
    .architecture-box h4 {
        color: #6b9bd1;
        font-size: 0.85rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .architecture-box .step {
        margin: 0.75rem 0;
        padding-left: 1.5rem;
        position: relative;
        color: #c5d1de;
        font-size: 0.85rem;
    }
    
    .architecture-box .step::before {
        content: '→';
        position: absolute;
        left: 0;
        color: #2a5298;
        font-weight: bold;
    }
    
    /* Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 2px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: 600;
        color: #6b9bd1;
        font-family: 'Crimson Pro', serif;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #b8c5d6;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        padding: 1.5rem !important;
        margin-bottom: 1rem;
    }
    
    /* Source Cards */
    .source-card {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.2) 0%, rgba(26, 35, 50, 0.3) 100%);
        border-left: 2px solid #2a5298;
        padding: 1.25rem;
        margin: 1rem 0;
        border-radius: 2px;
        transition: all 0.2s ease;
    }
    
    .source-card:hover {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.3) 0%, rgba(26, 35, 50, 0.4) 100%);
        border-left-width: 3px;
    }
    
    .source-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .source-title {
        font-family: 'Crimson Pro', serif;
        font-size: 1rem;
        font-weight: 600;
        color: #e3e8ef;
    }
    
    .source-score {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: #22c55e;
        background: rgba(34, 197, 94, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 2px;
    }
    
    .source-meta {
        font-size: 0.75rem;
        color: #b8c5d6;
        margin-bottom: 0.75rem;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .source-text {
        background: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: 2px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        line-height: 1.6;
        color: #c5d1de;
        border-left: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Input - AGGRESSIVE FIX FOR WHITE BOX */
    [data-testid="stChatInputContainer"],
    [data-testid="stChatInputContainer"] > div,
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div {
        background: #0a1929 !important;
        background-color: #0a1929 !important;
    }
    
    [data-testid="stChatInputContainer"] {
        border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    .stChatInput {
        background: #0a1929 !important;
    }
    
    .stChatInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #e3e8ef !important;
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stChatInput input:focus {
        border-color: #2a5298 !important;
        box-shadow: 0 0 0 1px #2a5298 !important;
    }
    
    .stChatInput input::placeholder {
        color: #8b95a5 !important;
    }
    
    /* Buttons */
    .stButton button {
        background: rgba(42, 82, 152, 0.1);
        border: 1px solid rgba(42, 82, 152, 0.3);
        color: #6b9bd1;
        border-radius: 2px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        background: rgba(42, 82, 152, 0.2);
        border-color: rgba(42, 82, 152, 0.5);
        transform: translateY(-1px);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 2px;
        color: #b8c5d6 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important;
    }
    
    /* Selectbox */
    [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 2px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(107, 155, 209, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(107, 155, 209, 0.5);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #2a5298 transparent transparent transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    """Initialize and cache the multi-agent orchestrator"""
    return MultiAgentOrchestrator()

try:
    orchestrator = get_orchestrator()
    status_html = '<div class="status-badge">✓ MULTI-AGENT SYSTEM READY</div>'
    st.markdown(status_html, unsafe_allow_html=True)
except Exception as e:
    st.error(f"❌ System initialization failed: {str(e)}")
    st.stop()

# Header
st.markdown("""
<div class="main-header">
    <h1>Property & Casualty Reserving Intelligence</h1>
    <div class="subtitle">Document AI System • Multi-Agent Architecture • SEC Filing Analysis</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ QUERY CONFIGURATION")
    
    # Company filter
    company = st.selectbox(
        "Target Company",
        ["All Companies", "AIG", "Travelers", "Chubb"],
        help="Filter results by specific insurance carrier"
    )
    
    # Balanced search toggle
    use_balanced = st.checkbox(
        "Enable Balanced Multi-Company Search",
        value=True,
        help="M05 Enhancement: Ensures equal representation from all carriers"
    )
    
    st.divider()
    
    # Architecture info
    st.markdown("""
    <div class="architecture-box">
        <h4>Pipeline Architecture</h4>
        <div class="step">RetrievalAgent<br/>Semantic search + table queries</div>
        <div class="step">AnalysisAgent<br/>Data processing + structuring</div>
        <div class="step">SynthesisAgent<br/>Answer generation via Claude 4</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # System metrics
    st.markdown("### 📊 SYSTEM METRICS")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">3,224</div>
            <div class="metric-label">Chunks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">700+</div>
            <div class="metric-label">Tables</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">87.1/100</div>
        <div class="metric-label">M05 Performance</div>
    </div>
    """, unsafe_allow_html=True)

# Main chat interface
st.markdown("## 💬 Query Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle example query clicks
if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Determine company filter
    company_filter = None if company == "All Companies" else company
    
    # Query orchestrator
    try:
        response = orchestrator.query(
            user_query=prompt,
            company=company_filter,
            use_balanced_search=use_balanced
        )
        
        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response['answer']
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Error: {str(e)}"
        })
    
    st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Query: insurance reserves, loss development, catastrophe events..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("⚙️ Processing through multi-agent pipeline..."):
            try:
                # Determine company filter
                company_filter = None if company == "All Companies" else company
                
                # Query orchestrator
                response = orchestrator.query(
                    user_query=prompt,
                    company=company_filter,
                    use_balanced_search=use_balanced
                )
                
                # Display answer
                st.markdown(response['answer'])
                
                # Display sources
                if response.get('sources'):
                    with st.expander(f"📚 SOURCES ({response['num_sources']} DOCUMENTS)", expanded=False):
                        for idx, source in enumerate(response['sources'][:5], 1):
                            if source['type'] == 'narrative':
                                st.markdown(f"""
                                <div class="source-card">
                                    <div class="source-header">
                                        <div class="source-title">Document {idx}: {source['company']}</div>
                                        <div class="source-score">Relevance: {source['relevance_score']:.3f}</div>
                                    </div>
                                    <div class="source-meta">
                                        {source['filing_type']} • {source['filing_date']} • Page {source['page_num']} • {source.get('section_type', 'N/A')}
                                    </div>
                                    <div class="source-text">{source['excerpt']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="source-card">
                                    <div class="source-header">
                                        <div class="source-title">Table {idx}: {source['company']}</div>
                                    </div>
                                    <div class="source-meta">
                                        {source['filing_type']} • Page {source['page_num']} • {source.get('table_type', 'Financial Table')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                
                # Display pipeline stats
                if response.get('pipeline_stats'):
                    stats = response['pipeline_stats']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Documents Retrieved", stats['documents_retrieved'])
                    with col2:
                        st.metric("Tables Retrieved", stats['tables_retrieved'])
                    with col3:
                        st.metric("Companies", len(stats['companies_mentioned']))
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response['answer']
                })
                
            except Exception as e:
                st.error(f"❌ Pipeline Error: {str(e)}")
                st.exception(e)

# Example queries with YOUR custom questions
with st.expander("💡 EXAMPLE QUERIES"):
    st.markdown('<p style="color: #e3e8ef; font-weight: 600; margin-bottom: 0.5rem;">Reserve Adequacy Analysis:</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("What does Travelers say about reserve adequacy and prior year?", key="ex1", use_container_width=True):
            st.session_state.example_query = "What does Travelers say about reserve adequacy and prior year?"
            st.rerun()
    with col2:
        if st.button("How do carriers reserve for asbestos and environmental exposures?", key="ex2", use_container_width=True):
            st.session_state.example_query = "How do carriers reserve for asbestos and environmental exposures?"
            st.rerun()
    
    st.markdown('<p style="color: #e3e8ef; font-weight: 600; margin: 1rem 0 0.5rem 0;">Catastrophe Impact:</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("AIG catastrophe events in 2024", key="ex3", use_container_width=True):
            st.session_state.example_query = "What catastrophe events impacted AIG's reserves in 2024?"
            st.rerun()
    with col2:
        if st.button("Tell me about catastrophe loss reserves", key="ex4", use_container_width=True):
            st.session_state.example_query = "Tell me about catastrophe loss reserves across all companies"
            st.rerun()
    
    st.markdown('<p style="color: #e3e8ef; font-weight: 600; margin: 1rem 0 0.5rem 0;">Financial Metrics:</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Travelers total loss reserves", key="ex5", use_container_width=True):
            st.session_state.example_query = "What are Travelers' total loss reserves by line of business?"
            st.rerun()
    with col2:
        if st.button("Compare combined ratios", key="ex6", use_container_width=True):
            st.session_state.example_query = "Compare combined ratios and loss development across all companies"
            st.rerun()
    
    st.markdown('<p style="color: #e3e8ef; font-weight: 600; margin: 1rem 0 0.5rem 0;">Cross-Carrier Comparative:</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("IBNR estimation approaches", key="ex7", use_container_width=True):
            st.session_state.example_query = "How do all three carriers approach IBNR estimation?"
            st.rerun()
    with col2:
        if st.button("External economic risks", key="ex8", use_container_width=True):
            st.session_state.example_query = "What external economic risks are mentioned across multiple carriers?"
            st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #b8c5d6; font-size: 0.75rem; font-family: "IBM Plex Mono", monospace; letter-spacing: 0.05em;'>
MSA 8700 • M06 FINAL PROJECT • MULTI-AGENT DOCUMENT AI SYSTEM
</div>
""", unsafe_allow_html=True)