# P&C Insurance Reserving Intelligence System

AI-powered multi-agent system for analyzing P&C insurance 10-K/10-Q filings from AIG, Travelers, and Chubb.

## 🎯 System Overview

**M02 - Data Pipeline:** Ingests SEC filings, extracts text/tables, generates embeddings, stores in vector database  
**M03 - AI Agent:** Interactive chat interface and batch query system for actuarial Q&A  
**M04 - Evaluation:** Systematic testing and baseline performance measurement  
**M05 - Improvements:** Query expansion and balanced multi-company retrieval (87.1/100 score)  
**M06 - Production System:** Multi-agent architecture + React frontend + LLM provider abstraction

---

## ✨ Latest Features (M06)

### Multi-Agent Architecture
- **RetrievalAgent:** Specialized database queries and semantic search
- **AnalysisAgent:** Data processing and structuring
- **SynthesisAgent:** Response generation with LLM abstraction
- **MultiAgentOrchestrator:** Coordinates the agent pipeline

### Production React Frontend
- Professional dashboard interface built with Next.js + TypeScript
- Real-time query processing with loading states
- Source attribution with interactive citations
- Company, year, quarter, and filing type filters
- Balanced search toggle for multi-company analysis

### LLM Provider Abstraction
- **Claude (Anthropic):** High-quality responses for development/demo
- **Ollama (GSU Server):** Cost-free deployment option
- Environment variable configuration for easy switching
- Dev mode toggle for provider selection

### Preserved M05 Improvements
- Query expansion with actuarial synonym mapping (50+ terms)
- Balanced multi-company retrieval
- Validated 87.1/100 performance score

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm
- Docker & Docker Compose
- Anthropic API key (for Claude provider)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd insurance-filings-pipeline

# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

Create `.env` file in project root:

```bash
# Database connections
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=insurance_filings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
QDRANT_HOST=localhost
QDRANT_PORT=6333

# LLM Provider (choose one)
LLM_PROVIDER=claude  # or "ollama"
ANTHROPIC_API_KEY=sk-ant-your-key-here

# For Ollama deployment
OLLAMA_API_KEY=your-gsu-key
OLLAMA_BASE_URL=https://gpu-01.insight.gsu.edu:11443
OLLAMA_MODEL=llama3.1

# Development mode (shows LLM provider toggle)
NODE_ENV=development  # or "production"
```

### 3. Start Data Pipeline (M02)

```bash
# Start databases
docker-compose up -d

# Verify data loaded
docker-compose exec postgres psql -U postgres -d insurance_filings -c "SELECT company, COUNT(*) FROM text_chunks GROUP BY company;"
```

**Expected:**
- 5 filings processed
- ~3,224 text chunks
- ~700 financial tables

### 4. Run the Application (M06)

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
uvicorn src.api.main:app --reload
# Runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

**Access the app:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/

---

## 🏗️ Architecture

### System Overview (M06)

```
┌─────────────────────────────────────────┐
│   React Frontend (Next.js + TypeScript) │
│   - Professional dashboard UI           │
│   - Real-time query interface           │
│   - Source attribution & citations      │
│   - LLM provider toggle (dev mode)      │
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│      FastAPI Backend (Python)           │
│   ┌─────────────────────────────────┐   │
│   │  MultiAgentOrchestrator         │   │
│   │  ├─ RetrievalAgent              │   │
│   │  ├─ AnalysisAgent               │   │
│   │  └─ SynthesisAgent              │   │
│   └─────────────────────────────────┘   │
│                                          │
│   ┌─────────────────────────────────┐   │
│   │  LLM Abstraction Layer          │   │
│   │  ├─ Claude (Anthropic)          │   │
│   │  └─ Ollama (GSU Server)         │   │
│   └─────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
┌────────▼─────┐  ┌────────▼────────┐
│ PostgreSQL   │  │ QDrant Vector   │
│ (Metadata,   │  │ (Semantic       │
│  Tables)     │  │  Embeddings)    │
└──────────────┘  └─────────────────┘
```

### Multi-Agent Pipeline

1. **User Query** → Frontend sends to FastAPI
2. **RetrievalAgent** → Semantic search + table queries (PostgreSQL + QDrant)
3. **AnalysisAgent** → Extract key facts, metrics, companies mentioned
4. **SynthesisAgent** → Generate response using LLM (Claude or Ollama)
5. **Response** → Frontend displays with source citations

### LLM Provider Flexibility

**Development/Demo:**
```bash
LLM_PROVIDER=claude
NODE_ENV=development
```
- Uses Claude for high-quality responses
- Shows dev mode toggle in UI
- Can switch providers on-the-fly

**Production Deployment:**
```bash
LLM_PROVIDER=ollama
NODE_ENV=production
```
- Uses GSU Ollama endpoint
- No external API costs
- Dev toggle hidden in UI

---

## 📁 Project Structure

```
insurance-filings-pipeline/
├── frontend/                        # M06: React Frontend
│   ├── app/
│   │   ├── page.tsx                # Main page
│   │   ├── layout.tsx              # App layout
│   │   ├── globals.css             # Global styles
│   │   └── api/
│   │       └── orchestrator.ts     # API client
│   ├── components/
│   │   ├── ChatInterface.tsx       # Main chat UI
│   │   ├── SourceCard.tsx          # Source citations
│   │   └── FormattedText.tsx       # Markdown renderer
│   ├── package.json
│   └── next.config.js
│
├── src/
│   ├── agents/                      # M06: Multi-Agent Architecture
│   │   ├── retrieval_agent.py      # Database retrieval
│   │   ├── analysis_agent.py       # Data processing
│   │   ├── synthesis_agent.py      # Response generation
│   │   ├── orchestrator.py         # Agent coordination
│   │   └── iterations/             # M05: Ablation variants
│   │
│   ├── api/                         # M06: FastAPI Backend
│   │   └── main.py                 # API endpoints
│   │
│   ├── utils/                       # M06: LLM Abstraction
│   │   └── llm_client.py           # Claude/Ollama client
│   │
│   └── storage/
│       ├── postgres_client.py
│       └── qdrant_client.py
│
├── pipeline/                        # M02: Data Pipeline
│   ├── ingest.py
│   ├── extract_text.py
│   ├── chunk_text.py
│   ├── embed.py
│   └── table_extractor.py
│
├── eval/                            # M04-M05: Evaluation
│   ├── eval_test_set.json
│   ├── results_baseline.json       # 85.7/100
│   ├── results_combined.json       # 87.1/100 ⭐
│   └── iterations/
│
├── diagrams/
│   ├── architecture_diagram_m05.svg
│   ├── database_schema.svg
│   └── dataflow_diagram_m05.svg
│
├── scripts/                         # Utility scripts
│   ├── resync_qdrant_v2.py
│   └── backfill_qdrant.py
│
├── .env                             # Environment config
├── .env.example
├── docker-compose.yml
├── requirements.txt
├── M02_MILESTONE.md
├── M03_MILESTONE.md
├── M04_MILESTONE.md
├── M05_MILESTONE.md
├── M06_MILESTONE.md                # Latest milestone
└── README.md
```

---

## 💻 Usage Examples

### Example Queries

Try these in the chat interface:

**Reserve Adequacy:**
- "What did AIG say about reserve adequacy in their latest filing?"
- "Compare reserve trends across all carriers"

**Loss Development:**
- "Analyze prior year development for Travelers"
- "What caused reserve strengthening in Q3 2024?"

**Catastrophe Impact:**
- "How did Hurricane Helene impact reserves?"
- "Compare CAT losses across companies"

**External Risks:**
- "What external factors impacted reserves this quarter?"
- "How are carriers addressing social inflation?"

### API Usage

**Query Endpoint:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are AIG reserves?",
    "company": "AIG",
    "use_balanced_search": true
  }'
```

**Health Check:**
```bash
curl http://localhost:8000/
```

**Available Providers:**
```bash
curl http://localhost:8000/providers
```

---

## 🎨 Frontend Features

### Sophisticated Dashboard UI
- Dark gradient theme with clean aesthetics
- Card-based layouts with subtle borders
- Smooth animations with Framer Motion
- Professional analytics platform feel

### Query Interface
- Real-time search with loading states
- 3-step pipeline visualization (Retrieval → Analysis → Synthesis)
- Search suggestions after 2+ characters
- Recent queries (clickable history)

### Filters & Controls
- **Company:** All, AIG, Travelers, Chubb
- **Year:** 2024, 2023, 2022, 2021
- **Quarter:** Q1, Q2, Q3, Q4, All
- **Filing Type:** 10-K, 10-Q, All
- **Balanced Search:** Toggle for multi-company analysis
- **LLM Provider:** Claude vs Ollama (dev mode only)

### Source Attribution
- Interactive source cards with hover previews
- Company, filing type, date, page numbers
- Relevance scores
- Direct quotes with citations

---

## 🔧 Configuration

### Environment Variables

**Database:**
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=insurance_filings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

**LLM Providers:**
```env
# Claude (Anthropic)
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Ollama (GSU Server)
LLM_PROVIDER=ollama
OLLAMA_API_KEY=your-gsu-key
OLLAMA_BASE_URL=https://gpu-01.insight.gsu.edu:11443
OLLAMA_MODEL=llama3.1
```

**Development:**
```env
NODE_ENV=development  # Shows LLM provider toggle
```

**Production:**
```env
NODE_ENV=production  # Hides dev features
```

### Frontend Configuration

For network/mobile access, create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://your-ip:8000
```

---

## 📊 Performance Metrics

### Data Processing (M02)
- 5 SEC filings processed
- 3,224 text chunks generated
- 700+ financial tables extracted
- Processing time: 5-10 minutes

### Query Performance (M06)
- **Frontend Load:** 1-2 seconds initial
- **Query Response (Claude):** 3-5 seconds
- **Query Response (Ollama):** 5-8 seconds
- **Database Query:** <100ms

### Evaluation Results (M05)
- **Baseline:** 85.7/100
- **Query Expansion Only:** 79.6/100
- **Balanced Search Only:** 86.1/100
- **Combined (Final):** 87.1/100 ⭐

---

## 🛠️ Tech Stack

### Frontend (M06)
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v3
- **Animation:** Framer Motion
- **Icons:** Lucide React

### Backend (M06)
- **API:** FastAPI (Python 3.9)
- **LLM Providers:**
  - Claude Sonnet 4 (Anthropic)
  - Llama 3.1 (Ollama/GSU)
- **Architecture:** Multi-agent pipeline

### Data Layer (M02)
- **Vector DB:** QDrant
- **Structured DB:** PostgreSQL 15
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **PDF Processing:** pdfplumber

---

## 🔍 Database Access

**PostgreSQL:**
```bash
docker-compose exec postgres psql -U postgres -d insurance_filings

# Example queries
SELECT company, filing_type, filing_date FROM filings;
SELECT COUNT(*) FROM text_chunks;
SELECT COUNT(*) FROM financial_tables;
```

**QDrant Dashboard:**
```
http://localhost:6333/dashboard
```

**API Documentation:**
```
http://localhost:8000/docs
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Frontend won't start | Check Node.js version (18+), run `npm install` |
| Backend 404 errors | Verify uvicorn running with `--host 0.0.0.0` |
| CORS errors | Check `allowedDevOrigins` in `next.config.js` |
| LLM provider errors | Verify API keys in `.env` |
| Database connection fails | Run `docker-compose ps`, restart if needed |
| Port already in use | Change port in uvicorn/npm command |

### Debugging Commands

```bash
# Check backend health
curl http://localhost:8000/

# Check available providers
curl http://localhost:8000/providers

# View backend logs
# (check terminal running uvicorn)

# View frontend logs
# (check terminal running npm dev)

# Check database
docker-compose exec postgres psql -U postgres -d insurance_filings
```

---

## 📈 Evaluation & Testing

### M04-M05 Ablation Study

The system was systematically evaluated using 8 test queries across different configurations:

| Variant | Features | Score |
|---------|----------|-------|
| V1: Baseline | Standard semantic search | 85.7 |
| V2: Query Expansion | Synonym mapping only | 79.6 |
| V3: Balanced Search | Multi-company sampling | 86.1 |
| V4: Combined | Both improvements | **87.1** ⭐ |

All evaluation results and code variants are preserved in `eval/` and `src/agents/iterations/`.

---

## 🚀 Deployment

### Local Development
```bash
# Backend
uvicorn src.api.main:app --reload

# Frontend
cd frontend && npm run dev
```

### Production Deployment

**For GSU/Ollama:**
```bash
# Update .env
LLM_PROVIDER=ollama
NODE_ENV=production

# Start backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Build frontend
cd frontend
npm run build
npm start
```

**For Cloud Deployment:**
- Backend: Railway, Render, Fly.io, AWS
- Frontend: Vercel, Netlify
- Update `NEXT_PUBLIC_API_URL` to deployed backend URL

---

## 📝 Milestones

- **M02:** ✅ Data pipeline with PDF ingestion, embeddings, vector storage
- **M03:** ✅ AI agent with semantic search and chat interface
- **M04:** ✅ Systematic evaluation and baseline measurement
- **M05:** ✅ Query expansion + balanced retrieval (87.1/100 score)
- **M06:** ✅ Multi-agent architecture + React frontend + LLM abstraction

---

## 📚 Documentation

- **M02_MILESTONE.md:** Data pipeline architecture
- **M03_MILESTONE.md:** AI agent design
- **M04_MILESTONE.md:** Evaluation methodology
- **M05_MILESTONE.md:** Ablation study results
- **M06_MILESTONE.md:** Multi-agent architecture + frontend (latest)

---
