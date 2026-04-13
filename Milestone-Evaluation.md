# Milestone Evaluation — msa8700-cu-38-willow

**Evaluated on:** 2026-04-08
**Previous evaluation:** N/A

## Summary

This project implements a P&C Insurance Reserving Intelligence System that processes SEC filings (10-K/10-Q) from AIG, Travelers, and Chubb. The team has built a functional data pipeline (M02) and agentic prototype (M03) with clear documentation and a working Dockerized deployment. The system uses PyMuPDF for PDF extraction, sentence-transformers for embeddings, PostgreSQL for structured data, and Qdrant for vector search. The agent layer uses Claude for answer synthesis via a Streamlit chat interface and a CLI batch query interface.

Strengths include a well-structured pipeline with modular components, working dual-database architecture (PostgreSQL + Qdrant), clear README documentation with deployment instructions, and pre-generated batch query results demonstrating working end-to-end functionality. The M03 milestone documentation (M03_MILESTONE.md) is comprehensive with architecture diagrams and detailed usage instructions.

## Evaluation History

| Date | Type | Summary |
|------|------|---------|
| 2026-04-08 | Initial | First evaluation of M02–M04. M02 mostly complete but has empty utility/test files. M03 functional with both interfaces. M04 has no meaningful evaluation framework. |

## Major Frameworks and Libraries

| Library / Framework | Purpose |
|---|---|
| PyMuPDF (fitz) | PDF text and metadata extraction |
| sentence-transformers (all-MiniLM-L6-v2) | 384-dim text embedding generation |
| pdfplumber | PDF extraction (listed in requirements, secondary to PyMuPDF) |
| scikit-learn | Stopword removal for text cleaning |
| psycopg2 | PostgreSQL database client |
| qdrant-client | Qdrant vector database client |
| Anthropic (Claude) | LLM for answer synthesis |
| Streamlit | Web-based chat interface |
| pandas | Data analysis |
| matplotlib / seaborn | Visualization in notebook |
| Docker / Docker Compose | Containerized deployment |

## Detailed Evaluation

### M02 — Data Pipeline, CI/CD Setup

| #   | Criterion                       | Score | Max | Evidence |
|-----|---------------------------------|-------|-----|----------|
| 2.1 | Code Quality                   | 20 | 30 | Pipeline code is modular: pipeline/ingest.py (file scanning), pipeline/extract_text.py (text extraction), pipeline/chunk_text.py (chunking), pipeline/embed.py (embeddings), pipeline/section_filter.py (filtering), pipeline/table_extractor.py (tables), pipeline/run_ingest.py (orchestrator). Uses dataclasses (ingest.py:12-22, chunk_text.py:10-14). However, src/utils/logger.py and src/utils/validators.py are completely empty files (0 content). tests/test_extraction.py, tests/test_processing.py, tests/test_storage.py are also empty. requirements.txt has duplicate entries (pdfplumber listed twice, lines 4 and 22). Reduce by 10 for empty utility/test files representing dead code/stubs. |
| 2.2 | Pipeline Functionality         | 30 | 30 | Pipeline successfully ingests 5 PDFs, extracts text and metadata (extract_text.py:30-72), generates embeddings (embed.py:20-23), and writes to PostgreSQL (postgres_client.py:82-103, 105-131) and Qdrant (qdrant_client.py:36-82). run_ingest.py:109-327 orchestrates the full flow. Notebook output confirms 1,799 chunks and 111 tables stored. Financial table extraction (table_extractor.py) and narrative filtering (section_filter.py) add value. |
| 2.3 | Architecture Diagram           | 20 | 30 | README.md:105-110 contains a simple text-based architecture diagram showing the pipeline flow. M03_MILESTONE.md:296-331 has a more detailed ASCII architecture diagram showing components and data flow. However, these are basic text diagrams, not comprehensive visual diagrams with clear component boundaries. Reduce by 10 for lacking detail on component interactions and database schema. |
| 2.4 | Documentation & Reproducibility | 30 | 30 | README.md:28-102 provides clear setup instructions including prerequisites, Docker commands, and verification steps. docker-compose.yml properly configures PostgreSQL, Qdrant, and pipeline services. Dockerfile is well-structured. .env.example provides template. M02_MILESTONE.md provides additional resubmission documentation with testing evidence. |
|     | **M02 Subtotal**               | **100** | **120** | |

### M03 — Agentic Prototype

| #   | Criterion                       | Score | Max | Evidence |
|-----|---------------------------------|-------|-----|----------|
| 3.1 | Multi-Agent Pipeline           | 30 | 40 | src/agents/orchestrator.py:15-135 implements ReservingAgent with tool-use pattern: query analysis (line 54), financial table retrieval, semantic search, and Claude-based synthesis. src/agents/tools.py:16-151 provides three tools: semantic_search(), get_filing_metadata(), get_financial_tables(). However, this is a single-agent design with tools, not a true multi-agent pipeline with distinct agent roles. Reduce by 10 for single-agent rather than multi-agent architecture. |
| 3.2 | Document Ingestion & Storage   | 40 | 40 | Data is persisted to PostgreSQL (filings, text_chunks, financial_tables tables — postgres_client.py:23-76) and Qdrant (vector embeddings — qdrant_client.py:22-34). Data is queryable via SQL (tools.py:86-104, 106-151) and vector search (tools.py:25-73). Notebook confirms 1,799 chunks and 111 tables successfully stored and queryable. |
| 3.3 | Dual Interface Implementation  | 40 | 40 | Streamlit chat interface (src/interfaces/streamlit_app.py, 300 lines) with company filter, example questions, source citations, and conversational history. Batch query interface (src/interfaces/batch_query.py, 112 lines) with JSON input/output, timing metrics, and error handling. Both route through ReservingAgent.answer_query(). Pre-generated results in data/results.json (8 queries, all successful) demonstrate working functionality. |
| 3.4 | Architecture & Reproducibility | 30 | 40 | M03_MILESTONE.md provides comprehensive documentation including architecture diagram (lines 296-331), pipeline description, interface instructions, and dependency list. Repository is well-organized with clear separation (pipeline/, src/agents/, src/interfaces/, src/storage/). Docker deployment works. However, some referenced paths in README don't match actual structure (e.g., README mentions src/main.py, data/raw/ which don't exist). Reduce by 10 for inconsistencies between documentation and actual repo structure. |
|     | **M03 Subtotal**               | **140** | **160** | |

### M04 — Evaluation Framework Baseline

| #   | Criterion                              | Score | Max | Evidence |
|-----|----------------------------------------|-------|-----|----------|
| 4.1 | Evaluation Test Set Execution          | 0 | 40 | eval_queries.json contains only 8 queries (well below the 50–100 required). While results.json and data/results.json show these 8 queries were executed with successful responses, there is no test set of 50–100 items. No systematic collection or organization of results beyond the 8 pre-generated outputs. Reduce by 10 for test set below 50 items; reduce by 10 for incomplete outputs; reduce by 10 for results not systematically organized; reduce by 10 for insufficient scale. |
| 4.2 | Quantitative Performance Analysis      | 0 | 40 | No quantitative performance analysis exists. No metrics are defined (accuracy, relevance, completeness). No summary statistics or per-query breakdowns. The results.json files contain raw outputs with processing times but no evaluation against expected results. No scoring rubric or evaluation methodology. Reduce by 40 for complete absence. |
| 4.3 | Error Analysis & Failure Identification | 0 | 40 | No error analysis or failure identification exists. While some batch results acknowledge limitations (e.g., "I cannot provide a substantive answer" in data/results.json query 1), these are agent self-assessments, not systematic error categorization or root cause analysis. No document analyzing retrieval gaps, prompt failures, or schema mismatches. Reduce by 40 for complete absence. |
| 4.4 | Improvement Strategy Proposals         | 0 | 40 | M03_MILESTONE.md:389-394 briefly mentions "Planned M04/M05 Improvements" including expanding evaluation test set, hybrid retrieval, query rewriting, and ablation studies. However, these are one-liners without grounding in error analysis, without explaining what will change or why, and without measurement plans. No dedicated M04 document exists. Reduce by 40 for complete absence of substantive improvement strategies. |
|     | **M04 Subtotal**                       | **0** | **160** | |

## Score Summary

| Milestone | Score | Max Points | Percentage |
|-----------|-------|------------|------------|
| M02 — Data Pipeline, CI/CD Setup | 100 | 120 | 83.3% |
| M03 — Agentic Prototype | 140 | 160 | 87.5% |
| M04 — Evaluation Framework Baseline | 0 | 160 | 0.0% |
| M05 — Iterative Improvement | — | 160 | N/A |
| M06 — Final Deliverables | — | 120 | N/A |
| **Grand Total (M02–M04)** | **240** | **440** | **54.5%** |

## Recommendations

- **Implement the M04 Evaluation Framework** as the highest-priority gap: create a test set of 50–100 queries with expected answers, define evaluation metrics, run the batch interface, and produce quantitative analysis with per-query breakdowns.
- **Complete empty placeholder files**: src/utils/logger.py, src/utils/validators.py, and all test files (tests/test_extraction.py, test_processing.py, test_storage.py) are empty. Either implement real functionality or remove them to avoid the appearance of stub code.
- **Fix documentation inconsistencies**: README.md references paths that don't exist (src/main.py, data/raw/, src/ingestion/, src/extraction/, src/processing/). Update to match the actual repository structure.
- **Clean up requirements.txt**: Remove duplicate pdfplumber entry (lines 4 and 22) and contradictory comments. Resolve version conflicts between pinned and minimum versions for shared libraries (e.g., pandas listed twice with different version specs).
