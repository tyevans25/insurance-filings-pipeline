# P&C Insurance Reserving Intelligence System

Automated agentic AI system for analyzing P&C insurance 10-K/10-Q filings from AIG, Travelers, and Chubb.

## System Overview

**M02 - Data Pipeline:** Ingests SEC filings, extracts text/tables, generates embeddings, stores in vector database  
**M03 - AI Agent:** Interactive chat interface and batch query system for actuarial Q&A  
**M04 - Evaluation:** Comprehensive testing framework with 75 actuarial queries (baseline: 85.7/100)  
**M05 - Improvements:** Ablation study with query expansion + balanced retrieval (final: 87.1/100)

## Features

### Data Pipeline (M02)
- ✅ PDF ingestion and validation
- ✅ Metadata extraction (company, filing date, type)
- ✅ Text extraction with section detection
- ✅ Financial table extraction
- ✅ Semantic chunking with overlap
- ✅ Vector embeddings (sentence-transformers)
- ✅ Multi-database storage (PostgreSQL + QDrant)

### AI Agent (M03)
- ✅ Semantic search across filings
- ✅ Natural language Q&A interface
- ✅ Company-specific filtering
- ✅ Source attribution and citations
- ✅ Batch query evaluation system

### Evaluation Framework (M04)
- ✅ 75-query test set across 10 actuarial categories
- ✅ Multi-metric scoring (keyword, source, completeness)
- ✅ Baseline performance: 85.7/100 composite score
- ✅ Failure mode analysis
- ✅ Category-level performance tracking

### Iterative Improvements (M05)
- ✅ Query expansion with actuarial synonyms
- ✅ Balanced multi-company retrieval
- ✅ Ablation study (4 variants tested)
- ✅ Performance: 87.1/100 composite score (+1.4 from baseline)
- ✅ Completeness: 75.5% (+3.6% from baseline)
- ✅ Catastrophe category breakthrough: 99.2/100 (+28.2 points)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Anthropic API key for chat interface

### 1. Setup Input Data

Place PDF files in the following structure:
data/raw/
├── AIG/
│   └── 2024/
│       └── aig_10q_2024q3.pdf
├── Travelers/
│   └── 2024/
│       └── travelers_10k_2024.pdf
└── Chubb/
└── 2024/
└── chubb_10q_2024q2.pdf

### 2. Start Data Pipeline (M02)
```bash
# Start all services
docker-compose up -d

# Monitor processing
docker-compose logs -f pipeline

# Verify data loaded
docker-compose exec postgres psql -U postgres -d insurance_filings -c "SELECT company, COUNT(*) FROM text_chunks GROUP BY company;"
```

**Expected Output:**
- 5 filings processed
- ~3,224 text chunks
- ~700 financial tables

### 3. Run AI Agent (M03)

#### Option A: View Pre-Generated Results (No API Key Required)
```bash
# See batch query results from 8 test questions
cat data/results.json | python3 -m json.tool
```

#### Option B: Interactive Chat Demo (Requires API Key)

**Get Free API Key:**
1. Sign up at https://console.anthropic.com/ (free $5 credit)
2. Create API key
3. Add to `.env` file:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

**Run Chat Interface:**
```bash
# Install dependencies (local - not in Docker)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start chat interface
streamlit run src/interfaces/streamlit_app.py
```

**Run Batch Queries:**
```bash
# Using Docker (recommended)
docker-compose run --rm pipeline python /app/src/interfaces/batch_query.py --input /data/eval_queries.json --output /data/results.json

# Results saved to data/results.json
```

### 4. Run Evaluation (M04)

```bash
# Run full evaluation on 75 queries
python eval/run_evaluation.py --mode live \
  --input eval/eval_test_set.json \
  --output eval/eval_results.json

# View results
python eval/run_evaluation.py --mode score \
  --input eval/eval_results.json
```

### 5. Test M05 Improvements

```bash
# The production system uses V4 (Combined) improvements
# To test individual variants, use the iteration files

# Example: Test baseline
cp src/agents/iterations/tools_baseline.py src/agents/tools.py
cp src/agents/iterations/orchestrator_baseline.py src/agents/orchestrator.py
python eval/run_evaluation.py --mode live \
  --input eval/eval_test_set.json \
  --output eval/results_baseline.json

# Restore production (V4 Combined)
cp src/agents/iterations/tools_combined.py src/agents/tools.py
cp src/agents/iterations/orchestrator_combined.py src/agents/orchestrator.py
```

## Architecture
Input PDFs → Ingestion → Extraction → Chunking → Embedding → Storage → AI Agent
↓          ↓            ↓           ↓          ↓         ↓         ↓
5 files   Metadata    Text/Tables   1000-char  384-dim   PostgreSQL Query
parsing                   chunks     vectors   + QDrant   Answer
↓
M05: Query Expansion
+ Balanced Retrieval

## Database Access

**PostgreSQL:**
```bash
docker-compose exec postgres psql -U postgres -d insurance_filings

# Example queries
SELECT company, filing_type, page_count FROM filings;
SELECT COUNT(*) FROM text_chunks;
```

**QDrant Dashboard:**
http://localhost:6333/dashboard

**Neo4j Browser (Optional):**
http://localhost:7474
Username: neo4j
Password: password123

## Project Structure
insurance-filings-pipeline/
├── data/
│   ├── raw/                # PDF SEC filings
│   ├── output/             # Processing artifacts
│   ├── test_queries.json   # M03 batch queries
│   └── batch_results.json  # M03 batch results
├── eval/                   # M04 evaluation + M05 ablation
│   ├── eval_test_set.json
│   ├── eval_results_baseline.json      # V1: 85.7
│   ├── results_query_exp_only.json     # V2: 79.6
│   ├── results_balanced_only.json      # V3: 86.1
│   ├── results_combined.json           # V4: 87.1 (WINNER)
│   └── run_evaluation.py
├── src/
│   ├── pipeline/          # M02 data pipeline
│   │   ├── ingest.py
│   │   ├── extract_text.py
│   │   ├── section_filter.py
│   │   ├── table_extractor.py
│   │   ├── chunk_text.py
│   │   ├── embed.py
│   │   └── run_ingest.py
│   ├── agents/            # M03 agent + M05 improvements
│   │   ├── tools.py              # Production (V4 Combined)
│   │   ├── orchestrator.py       # Production (V4 Combined)
│   │   ├── query_expansion.py    # M05: Synonym expansion
│   │   └── iterations/           # M05: Ablation variants
│   │       ├── tools_baseline.py
│   │       ├── orchestrator_baseline.py
│   │       ├── tools_query_exp_only.py
│   │       ├── orchestrator_query_exp_only.py
│   │       ├── tools_balanced_only.py
│   │       ├── orchestrator_balanced_only.py
│   │       ├── tools_combined.py
│   │       └── orchestrator_combined.py
│   ├── storage/
│   │   ├── postgres_client.py
│   │   └── qdrant_client.py
│   ├── interfaces/
│   │   ├── streamlit_app.py
│   │   └── batch_query.py
│   └── utils/
│       ├── logger.py
│       └── validators.py
├── config/
│   ├── database_config.yml
│   └── pipeline_config.yml
├── tests/
│   ├── test_pipeline.py
│   ├── test_extraction.py
│   ├── test_processing.py
│   └── test_storage.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── docker-compose.yml
├── requirements.txt
├── .env
├── README.md
├── M02_MILESTONE.md
├── M03_MILESTONE.md
├── M04_MILESTONE.md
└── M05_MILESTONE.md

## System Statistics

**Data Processed (M02):**
- 5 SEC filings (2 × 10-K, 3 × 10-Q)
- 3,224 text chunks
- ~700 financial tables
- 3,224 vector embeddings

**Agent Performance (M03-M05):**
- Baseline (M04): 85.7/100 composite score
- Final (M05): 87.1/100 composite score
- Improvement: +1.4 points, +3.6% completeness
- Best category: Catastrophe reserves (99.2/100, +28.2 from baseline)
- Test coverage: 75 queries across 10 actuarial categories

**M05 Ablation Study Results:**

| Variant | Composite | Keyword | Source | Complete | Verdict |
|---------|-----------|---------|--------|----------|---------|
| V1: Baseline | 85.7 | 92.2% | 100.0% | 71.9% | Strong baseline |
| V2: Query Exp Only | 79.6 | 85.9% | 94.7% | 65.1% | Failed (-6.1) |
| V3: Balanced Only | 86.1 | 90.6% | 100.0% | 70.7% | Modest gain (+0.4) |
| V4: Combined | **87.1** | 90.8% | 100.0% | **75.5%** | **Winner (+1.4)** |

## Example Queries
```python
# Try these in the chat interface:
"What did AIG say about reserve adequacy in their latest filing?"
"Compare loss development across all carriers"
"What external risks impacted reserves?"
"Show me commercial auto reserve trends"
"How are carriers addressing social inflation?"
"What catastrophe events most impacted Chubb's reserves in 2024?"
"Compare the reserve sensitivity analyses across AIG, Travelers, and Chubb"
```

## Monitoring & Debugging

**Check pipeline progress:**
```bash
docker-compose logs -f pipeline
```

**Database statistics:**
```sql
-- Chunks per company
SELECT f.company, COUNT(c.chunk_id) as chunks
FROM filings f
LEFT JOIN text_chunks c ON f.filing_id = c.filing_id
GROUP BY f.company;

-- QDrant collection info
curl http://localhost:6333/collections/insurance_filings | python3 -m json.tool
```

**Common Issues:**

| Issue | Solution |
|-------|----------|
| PDF extraction fails | Verify PDFs not corrupted: `pdfinfo file.pdf` |
| Out of memory | Reduce batch size in `embedder.py` |
| Database connection errors | Check services: `docker-compose ps` |
| Chat interface slow | First load takes ~30s to load embedding model |
| API authentication error | Verify `.env` has `ANTHROPIC_API_KEY` |
| Evaluation takes long | Normal - 75 queries × 15s = ~20 min per variant |

## Performance Notes

**M02 Pipeline:**
- Processing time: ~5-10 minutes for 5 PDFs
- Memory usage: ~2GB peak

**M03 Chat Interface:**
- Initial load: ~30-60 seconds (loading embedding model)
- Query response time: 3-5 seconds average
- API cost: ~$0.01-0.02 per query (with Claude)

**M04/M05 Evaluation:**
- Full evaluation: ~18-20 minutes (75 queries)
- Per-query time: ~14-15 seconds average
- Ablation study total: ~80 minutes (4 variants)

## Deliverables

### M02 ✅
- [x] Multi-stage data pipeline
- [x] PDF text extraction (pdfplumber)
- [x] Vector embeddings (sentence-transformers)
- [x] PostgreSQL + QDrant storage
- [x] 3,224 chunks processed

### M03 ✅
- [x] Agent orchestrator with semantic search
- [x] Streamlit chat interface
- [x] Batch query evaluation system
- [x] Pre-generated results (`data/results.json`)

### M04 ✅
- [x] Evaluation framework (75 queries, 10 categories)
- [x] Baseline performance: 85.7/100
- [x] Comprehensive metrics (keyword, source, completeness)
- [x] Failure mode analysis

### M05 ✅
- [x] Query expansion with actuarial synonyms
- [x] Balanced multi-company retrieval
- [x] Ablation study (4 variants)
- [x] Final system: 87.1/100 (+1.4 improvement)
- [x] Completeness breakthrough: 75.5% (+3.6%)
- [x] Catastrophe category: 99.2/100 (+28.2 points)

## Tech Stack

**M02 Pipeline:**
- Python 3.9
- pdfplumber (PDF extraction)
- sentence-transformers (embeddings)
- PostgreSQL 15 (structured data)
- QDrant (vector search)

**M03 Agent:**
- Anthropic Claude API (LLM)
- Streamlit (chat UI)
- Custom orchestration (tool calling)

**M04/M05 Evaluation:**
- Custom scoring framework
- JSON-based test sets
- Automated batch evaluation

## Configuration

Environment variables (`.env`):
```env
# Database connections (M02)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=insurance_filings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
QDRANT_HOST=qdrant
QDRANT_PORT=6333
INPUT_DIR=/data/raw

# AI Agent (M03)
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional - for chat demo
```

## Key Findings (M05)

### Synergistic Effects
Query expansion alone failed (-6.1 points), but when combined with balanced retrieval, created a synergistic effect (+1.4 points). This demonstrates that complementary improvements can compensate for each other's weaknesses.

### Domain Customization Matters
The catastrophe category improved by +28.2 points (40% relative improvement) through domain-specific synonyms ("CAT", "natural disaster") combined with multi-company coverage.

### Completeness Breakthrough
The combined system improved answer completeness from 71.9% to 75.5% (+3.6%), addressing the weakest baseline metric through targeted improvements.

## Future Work

**Potential Enhancements:**
- Expand to 15 carriers (original M01 scope)
- Add historical coverage (2020-2024)
- Implement hybrid search (BM25 + semantic)
- Add multi-turn conversation memory
- Deploy production API endpoint
- Advanced reranking strategies
