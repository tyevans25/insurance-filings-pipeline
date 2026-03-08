"""
Streamlit chat interface for the Reserving Intelligence Assistant
"""
import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add both project root AND src to Python path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
project_root = src_dir.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

try:
    from agents.orchestrator import ReservingAgent
except Exception as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="P&C Reserving Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Source card styling */
    .source-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .source-title {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .source-meta {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .source-text {
        background-color: white;
        padding: 0.75rem;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85rem;
        color: #2c3e50;
    }
    
    /* Example questions styling */
    .example-question {
        background-color: #e8f4f8;
        border-left: 3px solid #3498db;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .example-question:hover {
        background-color: #d4e9f2;
        transform: translateX(5px);
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize agent
@st.cache_resource
def get_agent():
    return ReservingAgent()

try:
    agent = get_agent()
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 P&C Reserving Intelligence Assistant</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Query Settings")
    
    company_filter = st.selectbox(
        "Focus on company:",
        ["All Companies", "AIG", "Travelers", "Chubb"],
        help="Filter results to a specific insurance carrier"
    )
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📈 Database Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">5</div>
            <div class="stat-label">Filings</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">3.2K</div>
            <div class="stat-label">Chunks</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Example questions
    st.markdown("### 💡 Example Questions")
    
    examples = [
        
        "What external risks impacted reserves?",
        "Show me commercial auto reserve trends",
        "Show me financial data from Chubb's latest filing",
    ]
    
    for ex in examples:
        if st.button(f"💬 {ex[:40]}...", key=ex, use_container_width=True):
            st.session_state.example_query = ex
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; font-size: 0.8rem;'>
        <p>Built for MSA 8700</p>
    </div>
    """, unsafe_allow_html=True)

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle example query
if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
    
    # Add to messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get response
    company = None if company_filter == "All Companies" else company_filter
    with st.spinner("🔍 Searching filings and analyzing..."):
        result = agent.answer_query(prompt, company=company)
        st.session_state.messages.append({
            "role": "assistant",
            "content": result['answer'],
            "sources": result['sources']
        })
    st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show sources for assistant messages
        if message["role"] == "assistant" and "sources" in message:
            with st.expander(f"📚 View Sources ({len(message['sources'])} passages)", expanded=False):
                for i, source in enumerate(message["sources"], 1):
                    metadata = source.get('metadata', {})
                    st.markdown(f"""
                    <div class="source-card">
                        <div class="source-title">📄 Source {i}: {metadata.get('company', 'Unknown')} - {metadata.get('section_type', 'Unknown section')}</div>
                        <div class="source-meta">
                            📅 {metadata.get('filing_date', 'Unknown date')} | 
                            🎯 Relevance: {source.get('score', 0):.3f}
                        </div>
                        <div class="source-text">{source.get('text', '')[:300]}...</div>
                    </div>
                    """, unsafe_allow_html=True)

# User input
if prompt := st.chat_input("Ask about insurance reserves...", key="chat_input"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get company filter
    company = None if company_filter == "All Companies" else company_filter
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching filings and analyzing..."):
            try:
                result = agent.answer_query(prompt, company=company)
                response = result['answer']
                st.markdown(response)
                
                # Show sources
                with st.expander(f"📚 Sources ({result['num_sources']} passages used)", expanded=False):
                    for i, source in enumerate(result['sources'], 1):
                        metadata = source.get('metadata', {})
                        st.markdown(f"""
                        <div class="source-card">
                            <div class="source-title">📄 {i}. {metadata.get('company', 'Unknown')} - {metadata.get('section_type', 'Unknown')}</div>
                            <div class="source-meta">
                                📅 {metadata.get('filing_date', 'Unknown')} | 
                                🎯 Relevance: {source.get('score', 0):.3f}
                            </div>
                            <div class="source-text">{source.get('text', '')[:300]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": result['sources']
                })
            except Exception as e:
                st.error(f"Error processing query: {e}")
                import traceback
                st.code(traceback.format_exc())