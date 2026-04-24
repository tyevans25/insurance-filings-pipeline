# Milestone Evaluation — msa8700-cu-38-willow

**Evaluated on:** 2026-04-24
**Previous evaluation:** 2026-04-13

## Summary

This project implements a P&C Insurance Reserving Intelligence System that processes SEC filings (10-K/10-Q) from AIG, Travelers, and Chubb. The team has built a functional data pipeline (M02), agentic prototype (M03), evaluation framework (M04), and has now completed substantial iterative improvement work (M05).

Since the last evaluation (2026-04-13), the team has made major progress. The most significant advancement is the complete M05 implementation: two improvement strategies from M04 (query expansion with actuarial synonyms and balanced multi-company retrieval) were implemented, and a rigorous ablation study was conducted across 4 variants using the full 75-query test set. The combined variant (V4) achieved the best composite score of 87.1 (+1.4 from baseline), with notable gains in catastrophe reserves (+28.2 points) and financial metrics (+13.8 points). The ablation study is well-documented in M05_MILESTONE.md with detailed comparative analysis, key insights about synergistic effects, and clear rationale for selecting V4 as the production system.

Additionally, several M04 issues have been resolved: the full 75-item evaluation test set has been executed against the system (previously only 8/75), and the previously empty utility files (logger.py, validators.py), test files, and config files now contain actual implementations. The README.md project structure still does not fully reflect the M05 additions (iterations/ directory, query_expansion.py), and the architecture diagrams remain text-based.

## Evaluation History

| Date | Type | Summary |
|------|------|---------|
| 2026-04-08 | Initial | First evaluation of M02–M04. M02 mostly complete but has empty utility/test files. M03 functional with both interfaces. M04 had no meaningful evaluation framework. |
| 2026-04-13 | Re-evaluation | M04 substantially improved: 75-item test set, evaluation pipeline, quantitative analysis, error analysis, and improvement strategies added. Only 8/75 items executed. M02/M03 unchanged. M05 not yet started. |
| 2026-04-24 | Re-evaluation | M05 fully implemented: ablation study with 4 variants, Combined (V4) achieves 87.1 score. Full 75-item test set executed. Empty utility/test/config files now populated. M04.1 and M04.2 improved to full marks. |

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
| 1.1 | Variation and Corpus Selection | 40 | 40 | *Locked — scored at max in previous evaluation.* README.md:1-9 identifies variation as P&C insurance reserving analysis with AIG, Travelers, Chubb SEC filings. |
| 1.2 | User Persona and Key Use Cases | 40 | 40 | *Locked — scored at max in previous evaluation.* README.md:175-183 provides example queries; eval/eval_test_set.json defines 10 use case categories. |
|     | **M01 Subtotal**               | **80** | **80** | |

### M02 — Data Pipeline, CI/CD Setup

| #   | Criterion                       | Score | Max | Evidence |
|-----|---------------------------------|-------|-----|----------|
| 2.1 | Code Quality                   | 30 | 30 | Previously deducted 10 for empty utility/test/config files. Now resolved: src/utils/logger.py (16 lines, setup_logger function), src/utils/validators.py (12 lines, validate_chunk/validate_filing), tests/test_extraction.py (14 lines), tests/test_processing.py (18 lines), tests/test_storage.py (18 lines), config/database_config.yml and config/pipeline_config.yml all contain real implementations. Pipeline code remains well-structured and modular. |
| 2.2 | Pipeline Functionality         | 30 | 30 | *Locked — scored at max in previous evaluation.* |
| 2.3 | Architecture Diagram           | 20 | 30 | No change from previous evaluation. README.md:105-110 and M03_MILESTONE.md:296-331 still contain only text-based ASCII diagrams. No visual diagrams with component boundaries, database schema, or detailed data flow have been added. Reduce by 10. |
| 2.4 | Documentation & Reproducibility | 30 | 30 | *Locked — scored at max in previous evaluation.* |
|     | **M02 Subtotal**               | **110** | **120** | |

### M03 — Agentic Prototype

| #   | Criterion                       | Score | Max | Evidence |
|-----|---------------------------------|-------|-----|----------|
| 3.1 | Multi-Agent Pipeline           | 30 | 40 | No change in fundamental architecture. src/agents/orchestrator.py implements ReservingAgent with tool-use pattern (now 4 tools including balanced_search). Still a single-agent design with tools rather than a true multi-agent pipeline with distinct agent roles. Reduce by 10. |
| 3.2 | Document Ingestion & Storage   | 40 | 40 | *Locked — scored at max in previous evaluation.* |
| 3.3 | Dual Interface Implementation  | 40 | 40 | *Locked — scored at max in previous evaluation.* |
| 3.4 | Architecture & Reproducibility | 30 | 40 | README.md:136-168 project structure still does not reflect the actual repository layout. Missing: src/agents/query_expansion.py, src/agents/iterations/ directory (8 files), and M05 eval results files. Reduce by 10 for documentation inconsistencies. |
|     | **M03 Subtotal**               | **140** | **160** | |

### M04 — Evaluation Framework Baseline

| #   | Criterion                              | Score | Max | Evidence |
|-----|----------------------------------------|-------|-----|----------|
| 4.1 | Evaluation Test Set Execution          | 40 | 40 | Previously deducted 20 for only 8/75 items executed. Now fully resolved: eval/eval_results_baseline.json contains all 75 items executed against the system (timestamp 2026-04-23T18:29:32), with 75/75 success rate. Results systematically organized with scores, failure modes, and processing times. |
| 4.2 | Quantitative Performance Analysis      | 40 | 40 | Previously deducted 10 for limited statistical representativeness (8 items). Now resolved: M05_MILESTONE.md:14-34 presents full baseline analysis across all 75 queries with composite score 85.7, keyword coverage 92.2%, source adequacy 100%, completeness 71.9%. Category-level and per-query breakdowns available. eval/run_evaluation.py:31-173 implements all scoring functions. |
| 4.3 | Error Analysis & Failure Identification | 40 | 40 | *Locked — scored at max in previous evaluation.* |
| 4.4 | Improvement Strategy Proposals         | 40 | 40 | *Locked — scored at max in previous evaluation.* |
|     | **M04 Subtotal**                       | **160** | **160** | |

### M05 — Iterative Improvement

| #   | Criterion                              | Score | Max | Evidence |
|-----|----------------------------------------|-------|-----|----------|
| 5.1 | System Refinements Implementation      | 40 | 40 | Two improvements implemented, both directly linked to M04 strategies: (1) Query expansion with actuarial synonyms in src/agents/query_expansion.py (25 lines, 7 domain-specific synonym mappings) integrated into src/agents/tools.py:41 via expand_query(); (2) Balanced multi-company retrieval in src/agents/tools.py:81-104 (balanced_search method ensuring representation from AIG, Travelers, Chubb). Production orchestrator (src/agents/orchestrator.py:85-93) routes multi-company queries through balanced_search and single-company queries through semantic_search. Both modifications are functional. |
| 5.2 | Ablation Study                         | 40 | 40 | Structured ablation study with 4 variants in src/agents/iterations/ (8 files): V1 Baseline (no improvements), V2 Query Expansion Only, V3 Balanced Retrieval Only, V4 Combined. All measured against M04 baseline using same 75-query test set and evaluation pipeline. Results stored in eval/eval_results_baseline.json, eval/results_query_exp_only.json, eval/results_balanced_only.json, eval/results_combined.json. M05_MILESTONE.md:70-87 documents study design with clear methodology. |
| 5.3 | Comparative Results & Impact Assessment | 40 | 40 | M05_MILESTONE.md:289-313 presents comprehensive comparison table with all 4 variants across 8 metrics. Category-level comparisons at lines 166-176 and 221-234 show per-category changes. Analysis identifies trade-offs (keyword coverage slight decrease in V3/V4, risk factors -2.8 in V4) and regressions (V2 created 4 null answers). Synergistic effect discovery documented at lines 236-285. Difficulty-level analysis at lines 304-312. |
| 5.4 | Iteration Report                       | 40 | 40 | M05_MILESTONE.md (405 lines) is a comprehensive iteration report documenting: what was changed (two improvements, lines 38-67), rationale grounded in M04 error analysis (lines 40-45), measured impact with quantitative results for all 4 variants (lines 90-285), key insights and takeaways (lines 316-367), and final deployment decision with rationale (lines 371-383). Report is well-organized with clear sections and demonstrates how DAIS performance improved from 85.7 to 87.1 composite score. |
|     | **M05 Subtotal**                       | **160** | **160** | |

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
| M02 — Data Pipeline, CI/CD Setup | 110 | 120 | 91.7% |
| M03 — Agentic Prototype | 140 | 160 | 87.5% |
| M04 — Evaluation Framework Baseline | 160 | 160 | 100.0% |
| M05 — Iterative Improvement | 160 | 160 | 100.0% |
| M06 — Final Deliverables | — | 120 | N/A |
| **Grand Total (M01–M05)** | **650** | **680** | **95.6%** |

## Recommendations

- **Update README.md project structure** (lines 136-168) to reflect the current repository layout, including src/agents/query_expansion.py, src/agents/iterations/ directory, and the M05 evaluation result files in eval/.
- **Add a visual architecture diagram** (e.g., PNG/SVG) with component boundaries, database schema, data flow details, and the M05 improvements (query expansion and balanced retrieval paths) to achieve full marks on M02.3.
- **Consider evolving to a true multi-agent architecture** for M06 — the current single-agent-with-tools design works well but distinct agent roles (e.g., retrieval agent, analysis agent, synthesis agent) would better demonstrate multi-agent pipeline design (M03.1).
