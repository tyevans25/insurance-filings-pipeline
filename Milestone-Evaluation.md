# Milestone Evaluation — msa8700-cu-38-willow

**Evaluated on:** 2026-04-13
**Previous evaluation:** 2026-04-08

## Summary

This project implements a P&C Insurance Reserving Intelligence System that processes SEC filings (10-K/10-Q) from AIG, Travelers, and Chubb. The team has built a functional data pipeline (M02), agentic prototype (M03), and has now made significant progress on the evaluation framework (M04). The system uses PyMuPDF for PDF extraction, sentence-transformers for embeddings, PostgreSQL for structured data, and Qdrant for vector search. The agent layer uses Claude for answer synthesis via a Streamlit chat interface and a CLI batch query interface.

Since the last evaluation (2026-04-08), the primary improvement is the substantial M04 work. The team created a well-designed 75-item evaluation test set (`eval/eval_test_set.json`) covering 10 categories and 3 difficulty levels. They built a proper evaluation pipeline (`eval/run_evaluation.py`, 493 lines) with defined scoring metrics (keyword coverage, source adequacy, completeness, cross-carrier coverage) and composite scoring. The M04_MILESTONE.md document provides thorough error analysis identifying three failure modes (retrieval gap, context truncation, single-carrier dominance) with root causes and specific examples. Three actionable improvement strategies are proposed with clear measurement plans for M05.

However, only 8 of the 75 test items were actually executed against the system — items 9–75 remain marked as "missing" in the baseline results. This significantly limits the evaluation test set execution score. The previously flagged issues (empty utility/test files, documentation path inconsistencies, basic architecture diagrams) remain unaddressed. M05 has no evidence of implementation.

## Evaluation History

| Date | Type | Summary |
|------|------|---------|
| 2026-04-08 | Initial | First evaluation of M02–M04. M02 mostly complete but has empty utility/test files. M03 functional with both interfaces. M04 had no meaningful evaluation framework. |
| 2026-04-13 | Re-evaluation | M04 substantially improved: 75-item test set, evaluation pipeline, quantitative analysis, error analysis, and improvement strategies added. Only 8/75 items executed. M02/M03 unchanged. M05 not yet started. |

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

### M01 — Project Definition

| #   | Criterion                       | Score | Max | Evidence |
|-----|---------------------------------|-------|-----|----------|
| 1.1 | Variation and Corpus Selection | 40 | 40 | README.md:1-9 identifies the variation as P&C insurance reserving analysis. Corpus is clearly specified: AIG, Travelers, and Chubb SEC filings (10-K/10-Q), with 5 PDFs in data/input/. M04_MILESTONE.md:5 provides additional context. Corpus details (document types, sources, scale of ~49MB across 5 filings) are evident from the data/input/ directory and pipeline output statistics. |
| 1.2 | User Persona and Key Use Cases | 40 | 40 | README.md:175-183 provides example queries demonstrating use cases (reserve adequacy analysis, cross-carrier comparison, risk factor analysis, trend analysis). M03_MILESTONE.md documents the actuarial analyst persona implicitly through the dual-interface design (interactive chat for exploratory analysis, batch queries for systematic evaluation). eval/eval_test_set.json defines 10 use case categories spanning reserve adequacy, cross-carrier comparison, line of business, financial metrics, risk factors, trend analysis, reserve methodology, catastrophe, reinsurance, and external factors. |
|     | **M01 Subtotal**               | **80** | **80** | |

### M02 — Data Pipeline, CI/CD Setup

| #   | Criterion                       | Score | Max | Evidence |
|-----|---------------------------------|-------|-----|----------|
| 2.1 | Code Quality                   | 20 | 30 | Pipeline code is modular: pipeline/ingest.py (file scanning), pipeline/extract_text.py (text extraction), pipeline/chunk_text.py (chunking), pipeline/embed.py (embeddings), pipeline/section_filter.py (filtering), pipeline/table_extractor.py (tables), pipeline/run_ingest.py (orchestrator). Uses dataclasses (ingest.py:12-22, chunk_text.py:10-14). However, src/utils/logger.py and src/utils/validators.py are still completely empty files (0 content). tests/test_extraction.py, tests/test_processing.py, tests/test_storage.py are also still empty. config/database_config.yml and config/pipeline_config.yml are empty. Reduce by 10 for empty utility/test/config files representing dead code/stubs. |
| 2.2 | Pipeline Functionality         | 30 | 30 | *Locked — scored at max in previous evaluation.* Pipeline successfully ingests 5 PDFs, extracts text and metadata, generates embeddings, and writes to PostgreSQL and Qdrant. run_ingest.py orchestrates the full flow. 1,799+ chunks and 111 tables stored. |
| 2.3 | Architecture Diagram           | 20 | 30 | README.md:105-110 contains a simple text-based architecture diagram. M03_MILESTONE.md:296-331 has a more detailed ASCII architecture diagram. No new visual diagrams have been added since last evaluation. Still basic text diagrams lacking detail on component interactions and database schema. Reduce by 10. |
| 2.4 | Documentation & Reproducibility | 30 | 30 | *Locked — scored at max in previous evaluation.* README.md provides clear setup instructions including prerequisites, Docker commands, and verification steps. docker-compose.yml properly configures services. |
|     | **M02 Subtotal**               | **100** | **120** | |

### M03 — Agentic Prototype

| #   | Criterion                       | Score | Max | Evidence |
|-----|---------------------------------|-------|-----|----------|
| 3.1 | Multi-Agent Pipeline           | 30 | 40 | src/agents/orchestrator.py:15-135 implements ReservingAgent with tool-use pattern: query analysis, financial table retrieval, semantic search, and Claude-based synthesis. src/agents/tools.py:16-151 provides three tools. Still a single-agent design with tools, not a true multi-agent pipeline with distinct agent roles. Reduce by 10. |
| 3.2 | Document Ingestion & Storage   | 40 | 40 | *Locked — scored at max in previous evaluation.* Data persisted to PostgreSQL and Qdrant, queryable via SQL and vector search. |
| 3.3 | Dual Interface Implementation  | 40 | 40 | *Locked — scored at max in previous evaluation.* Streamlit chat interface and batch query interface both functional. |
| 3.4 | Architecture & Reproducibility | 30 | 40 | M03_MILESTONE.md provides comprehensive documentation with architecture diagram. Repository is well-organized. However, README.md still references paths that don't exist in the actual repo structure (src/main.py at line 147, data/raw/ at lines 38-47, src/ingestion/ at line 148, src/extraction/ at line 149, src/processing/ at line 150). Reduce by 10 for documentation inconsistencies. |
|     | **M03 Subtotal**               | **140** | **160** | |

### M04 — Evaluation Framework Baseline

| #   | Criterion                              | Score | Max | Evidence |
|-----|----------------------------------------|-------|-----|----------|
| 4.1 | Evaluation Test Set Execution          | 20 | 40 | eval/eval_test_set.json contains 75 well-structured items with categories, difficulty levels, expected keywords, and minimum source requirements — meeting the 50–100 item requirement. eval/run_evaluation.py (493 lines) implements the evaluation pipeline with live and score modes. eval/eval_results_baseline.json stores results systematically. However, only 8 of 75 items were actually executed against the agent; items 9–75 are marked as "missing" (M04_MILESTONE.md:84). Reduce by 10 for incomplete outputs (67 of 75 items have no results). Reduce by 10 for the test set not being fully executed against the batch interface. |
| 4.2 | Quantitative Performance Analysis      | 30 | 40 | M04_MILESTONE.md:88-147 presents quantitative analysis with four defined metrics (keyword coverage, source adequacy, answer completeness, cross-carrier coverage) with explicit weighting scheme (lines 94-99). Summary statistics provided: mean 73.2, median 75.5, min 48.9, max 100.0 (lines 116-127). Per-query breakdown with scores and failure modes for all 8 evaluated items (lines 105-114). Category-level breakdown across 8 categories (lines 131-140). Per-query deep-dive for best/worst cases (lines 144-147). run_evaluation.py:31-173 implements all scoring functions. Reduce by 10 because analysis covers only 8 of 75 items, limiting the statistical representativeness. |
| 4.3 | Error Analysis & Failure Identification | 40 | 40 | M04_MILESTONE.md:150-196 provides thorough error analysis with a failure mode taxonomy. Three distinct failure modes identified and categorized: (1) Retrieval Gap with sub-categories of vocabulary mismatch (4 queries) and section-level mismatch (2 queries), with specific examples for Q1, Q5, Q3; (2) Context Truncation (1/8) with Q6 example showing mid-sentence chunk split; (3) Single-Carrier Dominance (2/8) with Q2 example showing Chubb over-representation. Root cause analysis identifies three underlying issues: vocabulary mismatch in all-MiniLM-L6-v2, flat top-K retrieval without section awareness, and single-keyword table search (lines 166-168). Error category summary table at lines 190-195. |
| 4.4 | Improvement Strategy Proposals         | 40 | 40 | M04_MILESTONE.md:199-242 proposes three specific, actionable strategies directly grounded in the error analysis: (1) Query Expansion with Actuarial Synonym Injection targeting vocabulary mismatch retrieval gaps, with target to reduce retrieval_gap from 75% to ≤30% and keyword coverage from 0.72 to ≥0.85; (2) Per-Company Retrieval Balancing targeting single-carrier dominance, with cross-carrier coverage target of ≥0.80; (3) Section-Aware Chunking with MD&A Priority Tagging targeting context truncation and section mismatch, with composite score target of ≥80.0. Each strategy specifies what will be changed, why it is expected to help, and how impact will be measured in M05. |
|     | **M04 Subtotal**                       | **130** | **160** | |

### M05 — Iterative Improvement

| #   | Criterion                              | Score | Max | Evidence |
|-----|----------------------------------------|-------|-----|----------|
| 5.1 | System Refinements Implementation      | 0 | 40 | No system refinements have been implemented. src/agents/orchestrator.py and src/agents/tools.py are unchanged from M03. No query expansion, retrieval balancing, or section-aware chunking has been added. No M05_MILESTONE.md exists. |
| 5.2 | Ablation Study                         | 0 | 40 | No ablation study exists. No comparison of alternative approaches has been conducted. |
| 5.3 | Comparative Results & Impact Assessment | 0 | 40 | No re-evaluation results exist. No comparison against M04 baseline metrics has been produced. |
| 5.4 | Iteration Report                       | 0 | 40 | No iteration report exists. No M05_MILESTONE.md or equivalent documentation of changes, rationale, or measured impact. |
|     | **M05 Subtotal**                       | **0** | **160** | |

### M06 — Final Deliverables

| #   | Criterion                         | Score | Max | Evidence |
|-----|-----------------------------------|-------|-----|----------|
| 6.1 | Deployed DAIS System              | — | 40 | *Not evaluated.* |
| 6.2 | Technical Report                  | — | 40 | *Not evaluated.* |
| 6.3 | Demo Video & In-Class Presentation | — | 40 | *Not evaluated.* |
|     | **M06 Subtotal**                  | **—** | **120** | |

## Score Summary

| Milestone | Score | Max Points | Percentage |
|-----------|-------|------------|------------|
| M01 — Project Definition | 80 | 80 | 100.0% |
| M02 — Data Pipeline, CI/CD Setup | 100 | 120 | 83.3% |
| M03 — Agentic Prototype | 140 | 160 | 87.5% |
| M04 — Evaluation Framework Baseline | 130 | 160 | 81.3% |
| M05 — Iterative Improvement | 0 | 160 | 0.0% |
| M06 — Final Deliverables | — | 120 | N/A |
| **Grand Total (M01–M05)** | **450** | **680** | **66.2%** |

## Recommendations

- **Execute the full 75-item evaluation test set** as the highest-priority task. The test set and pipeline are ready; running `python eval/run_evaluation.py --mode live` would bring M04.1 to full marks and strengthen M04.2 with broader statistical analysis.
- **Begin M05 implementation immediately**: implement the three improvement strategies proposed in M04 (query expansion, per-company retrieval balancing, section-aware chunking), then re-run the full evaluation to produce comparative results, an ablation study, and an iteration report.
- **Remove or implement empty placeholder files**: src/utils/logger.py, src/utils/validators.py, tests/test_extraction.py, test_processing.py, test_storage.py, config/database_config.yml, config/pipeline_config.yml are all 0-byte files that reduce the code quality score.
- **Fix README.md documentation inconsistencies**: update the Project Structure section (lines 136-158) to match the actual repository layout — references to src/main.py, data/raw/, src/ingestion/, src/extraction/, src/processing/ do not exist.
- **Add a more detailed architecture diagram** with visual component boundaries, database schema, and data flow details to improve the M02.3 score.
