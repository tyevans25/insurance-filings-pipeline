# M03 Milestone - Functional DAIS Prototype

## Overview

This milestone delivers a functional Document AI System (DAIS) for P&C insurance reserve analysis, including:
- Multi-agent document processing pipeline (M02)
- Interactive chat interface for human queries
- Batch query interface for automated evaluation

---

## Document Pipeline

### Pipeline Description

**Input Documents:**
- **Type**: PDF SEC filings (10-K, 10-Q) from insurance companies
- **Sources**: AIG, Travelers, Chubb quarterly and annual reports
- **Location**: `data/input/` directory

**Processing Steps:**
1. **Text Extraction** (`pipeline/extract_text.py`)
   - Uses PyMuPDF to extract text and metadata (author, title, dates, page count)
   - Supports both PDF and TXT files

2. **Narrative Filtering** (`pipeline/section_filter.py`)
   - Filters out purely numeric/tabular chunks
   - Retains narrative text (MD&A, Risk Factors, etc.)
   - Result: 1,799 narrative chunks from 5 filings

3. **Financial Table Extraction** (`pipeline/table_extractor.py`)
   - Detects and extracts structured financial tables
   - Stores reserve data, metrics, and financial statements separately
   - Result: 111 financial tables extracted

4. **Chunking** (`pipeline/chunk_text.py`)
   - Token-based chunking: 200 tokens per chunk, 50 token overlap
   - Uses sklearn stopword removal and tokenization
   - Optimized for embedding model input

5. **Embedding Generation** (`pipeline/embed.py`)
   - Model: sentence-transformers/all-MiniLM-L6-v2
   - Generates 384-dimensional vectors for semantic search
   - Batch processing for efficiency

6. **Storage** (`src/storage/`)
   - **PostgreSQL**: Stores filings, text chunks, financial tables (structured data)
   - **QDrant**: Stores vector embeddings for semantic search (1,799 vectors)

**Output Format:**
- PostgreSQL: Relational tables (filings, text_chunks, financial_tables)
- QDrant: Vector collection ("insurance_filings")
- Local artifacts: JSON summaries in `data/output/` (optional)

### How to Run the Pipeline

**Prerequisites:**
```bash
# Install Docker Desktop
# Clone repository
git clone git@git.insight.gsu.edu:msa8700-spring2026/msa8700-cu-38-willow.git
cd insurance-filings-pipeline
```

**Execution (Docker):**
```bash
# Start databases and run pipeline
docker-compose up --build

# Expected output:
# - Files processed: 5
# - Total narrative chunks: 1,799
# - Total tables extracted: 111
# - PostgreSQL: ✅ 1,799 chunks, 111 tables
# - QDrant: ✅ 1,799 vectors
```

**Execution (Local - Development):**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with credentials
cat > .env << 'ENVEOF'
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=insurance_filings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
QDRANT_HOST=localhost
QDRANT_PORT=6333
ANTHROPIC_API_KEY=your-key-here
ENVEOF

# Start databases only
docker-compose up -d postgres qdrant

# Run pipeline
python pipeline/run_ingest.py
```

**Verification:**
```bash
# Check PostgreSQL data
docker-compose exec postgres psql -U postgres -d insurance_filings -c "SELECT COUNT(*) FROM text_chunks;"
# Expected: 1799

# Check QDrant data
curl http://localhost:6333/collections/insurance_filings | grep points_count
# Expected: "points_count": 1799
```

---

## Chat Interface

### Interface Description

**Type**: Web-based chat interface using Streamlit

**Features:**
- Natural language query input
- Company filter dropdown (AIG, Travelers, Chubb, or All)
- Real-time responses from Claude API
- Source citations with company, filing type, and relevance scores
- Conversational history display

**Agent Architecture** (`src/agents/orchestrator.py`):
1. **Query Analysis**: Detects if query needs financial tables or narrative context
2. **Tool Selection**:
   - `get_financial_tables()`: Queries structured data from PostgreSQL
   - `semantic_search()`: Queries narrative text via QDrant vector search
3. **Context Building**: Combines table data and narrative passages
4. **Answer Synthesis**: Uses Claude Sonnet 4 to generate comprehensive answer

**Available Tools** (`src/agents/tools.py`):
- `semantic_search(query, limit, company)`: Vector similarity search
- `get_filing_metadata(company, filing_type)`: Retrieve filing information
- `get_financial_tables(company, keyword)`: Query structured financial tables

### How to Run the Chat Interface

**Prerequisites:**
```bash
# Ensure pipeline has been run (data must exist in databases)
# Set ANTHROPIC_API_KEY in .env file
```

**Execution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Start Streamlit app
streamlit run src/interfaces/streamlit_app.py

# Interface opens at: http://localhost:8501
```

**Usage Examples:**
```
Query: "What companies are in the database?"
Query: "What are AIG's loss reserves for 2024?"
Query: "Compare reserve adequacy across all companies"
Query: "What external risks impact insurance reserves?"
```

**Sample Output:**
```
Query: "What are AIG's loss reserves?"

Answer: Based on the financial tables and narrative context from AIG's 
10-Q filing (Q3 2024), AIG reported loss and loss adjustment expense 
reserves of $X billion. The filing indicates [narrative context about 
reserve adequacy, development patterns, etc.]...

Sources:
1. AIG - 10-Q (2024-09-30) - Page 47 [Table]
   Relevance: 0.892
2. AIG - 10-Q (2024-09-30) - Narrative
   Relevance: 0.856
```

---

## Batch Query Interface

### Batch Processing Description

**Type**: Command-line Python script for automated evaluation

**Input Format**: JSON file with array of queries
```json
{
  "queries": [
    {
      "id": 1,
      "query": "What companies are in the database?",
      "company": null
    },
    {
      "id": 2,
      "query": "What are AIG's total loss reserves?",
      "company": "AIG"
    }
  ]
}
```

**Processing Flow**:
1. Loads queries from JSON file
2. Processes each query sequentially using the same agent
3. Tracks execution time and token usage per query
4. Saves results to JSON output file

**Output Format**: JSON file with detailed results
```json
{
  "metadata": {
    "total_queries": 10,
    "successful": 10,
    "failed": 0,
    "total_time_seconds": 45.2,
    "timestamp": "2026-03-23T10:30:00Z"
  },
  "results": [
    {
      "id": 1,
      "query": "What companies are in the database?",
      "answer": "The database contains SEC filings from three major P&C insurance companies...",
      "sources": [...],
      "execution_time_seconds": 2.3,
      "timestamp": "2026-03-23T10:30:00Z"
    }
  ]
}
```

**Storage Location**: `data/batch_results.json`

### How to Run Batch Queries

**Prerequisites:**
```bash
# Ensure pipeline has been run
# Set ANTHROPIC_API_KEY in .env
# Prepare input queries file
```

**Execution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Run batch evaluation with default queries
python src/interfaces/batch_query.py

# Or specify custom query file
python src/interfaces/batch_query.py --input data/custom_queries.json --output data/custom_results.json
```

**Example Input File** (`data/test_queries.json`):
```json
{
  "queries": [
    {"id": 1, "query": "What companies are in the database?", "company": null},
    {"id": 2, "query": "What are AIG's loss reserves?", "company": "AIG"},
    {"id": 3, "query": "Compare combined ratios across companies", "company": null},
    {"id": 4, "query": "What risks does Travelers mention?", "company": "Travelers"}
  ]
}
```

**Viewing Results:**
```bash
# Pretty-print results
cat data/batch_results.json | python -m json.tool | less

# Extract just answers
jq '.results[] | {id, query, answer}' data/batch_results.json
```

**Performance Metrics:**
- Average response time: ~3-5 seconds per query
- Token usage: ~1,500-3,000 tokens per query (varies by complexity)
- Success rate: 100% (with valid queries)

---

## System Architecture Summary
```
┌─────────────────┐
│  PDF Documents  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Processing Pipeline (M02)      │
│  • Extract text + metadata      │
│  • Filter narrative chunks       │
│  • Extract financial tables      │
│  • Generate embeddings           │
└────────┬────────────────────────┘
         │
         ▼
┌──────────────────┬───────────────┐
│   PostgreSQL     │    QDrant     │
│  • Filings       │  • Vectors    │
│  • Chunks        │  • Metadata   │
│  • Tables        │               │
└────────┬─────────┴───────┬───────┘
         │                 │
         ▼                 ▼
┌─────────────────────────────────┐
│  Agent + Tools (M03)            │
│  • semantic_search()            │
│  • get_financial_tables()       │
│  • Claude API synthesis         │
└────────┬────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌───────┐
│Streamlit│ │ Batch │
│  Chat   │ │Query  │
└─────────┘ └───────┘
```

---

## Key Features Delivered

### M02 Pipeline Enhancements:
✅ Narrative text filtering (1,799 quality chunks)
✅ Financial table extraction (111 tables)
✅ Dual storage: PostgreSQL (structured) + QDrant (vectors)
✅ Full metadata extraction (author, title, dates, pages)

### M03 Agent Capabilities:
✅ Hybrid retrieval (narrative + tables)
✅ Multi-tool orchestration
✅ Context-aware query routing
✅ Source citation with relevance scores

### Interfaces:
✅ Web chat (Streamlit) - Interactive Q&A
✅ Batch query (CLI) - Automated evaluation
✅ Both use same underlying agent

---

## Testing Evidence

**Pipeline Execution:**
```bash
docker-compose up --build
# ✅ 5 filings processed
# ✅ 1,799 chunks stored
# ✅ 111 tables extracted
```

**Chat Interface:**
```bash
streamlit run src/interfaces/streamlit_app.py
# Test: "What are AIG's loss reserves?"
# ✅ Returns answer with table data + narrative context
```

**Batch Query:**
```bash
python src/interfaces/batch_query.py
# ✅ 10/10 queries successful
# ✅ Results saved to data/batch_results.json
```

---

## Known Limitations & Future Work

**Current Limitations:**
- Limited to 5 SEC filings (can scale with more documents)
- Table extraction focuses on reserve tables (can expand to other metrics)
- No real-time filing updates (manual ingestion required)

**Planned M04/M05 Improvements:**
- Expand evaluation test set (50-100 queries)
- Implement hybrid retrieval (vector + keyword)
- Add query rewriting and expansion
- Conduct ablation studies (chunking strategies, retrieval methods)

---

## Dependencies

**Core Libraries:**
- PyMuPDF (fitz) 1.23.8 - PDF processing
- sentence-transformers 2.3.0 - Embeddings
- qdrant-client 1.16.0 - Vector database
- psycopg2 2.9.9 - PostgreSQL
- anthropic 0.39.0 - Claude API
- streamlit 1.40.0 - Chat interface

**System Requirements:**
- Docker Desktop (for databases)
- Python 3.9+
- 8GB RAM minimum
- Anthropic API key

---

## Repository Structure
```
insurance-filings-pipeline/
├── data/
│   ├── input/              # PDF filings
│   ├── output/             # Pipeline artifacts
│   ├── test_queries.json   # Batch query input
│   └── batch_results.json  # Batch query output
├── pipeline/
│   ├── ingest.py           # File scanner
│   ├── extract_text.py     # Text + metadata extraction
│   ├── section_filter.py   # Narrative filtering
│   ├── table_extractor.py  # Table extraction
│   ├── chunk_text.py       # Tokenization + chunking
│   ├── embed.py            # Embedding generation
│   └── run_ingest.py       # Pipeline orchestrator
├── src/
│   ├── agents/
│   │   ├── tools.py        # Search, tables, metadata tools
│   │   └── orchestrator.py # Agent logic
│   ├── storage/
│   │   ├── postgres_client.py
│   │   └── qdrant_client.py
│   └── interfaces/
│       ├── streamlit_app.py    # Chat UI
│       └── batch_query.py      # Batch processor
├── config/
│   ├── database_config.yml
│   └── pipeline_config.yml
├── tests/
│   └── test_pipeline.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── docker-compose.yml
├── requirements.txt
├── M02_MILESTONE.md
└── M03_MILESTONE.md
```

---

## Conclusion

M03 delivers a complete, functional DAIS prototype with:
- Robust document processing pipeline
- Dual storage for structured and unstructured data
- Interactive chat interface for human queries
- Batch evaluation interface for automated testing
- Foundation for M04 evaluation and M05 iterative improvements

All components are tested, documented, and ready for evaluation.
