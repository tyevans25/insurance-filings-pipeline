# M04 Milestone – Evaluation & Performance Analysis

## Project: P&C Insurance Reserving Intelligence System

**System:** RAG-based Document AI for analyzing AIG, Travelers, and Chubb SEC filings (10-K/10-Q)  
**Evaluation Date:** April 2026  
**Evaluated By:** msa8700-cu-38-willow  

---

## 1. Evaluation Test Set Execution

### Test Set Description

The evaluation test set (`eval/eval_test_set.json`) contains **75 items** designed to comprehensively cover the system's expected use cases in actuarial reserve analysis.

**Coverage design:**

| Dimension | Breakdown |
|-----------|-----------|
| **Category** | reserve_adequacy (10), cross_carrier_comparison (8), line_of_business (10), financial_metrics (10), risk_factors (7), trend_analysis (6), reserve_methodology (7), catastrophe (7), reinsurance (5), external_factors (5) |
| **Difficulty** | easy (14), medium (43), hard (18) |
| **Company scope** | AIG-specific (12), Travelers-specific (12), Chubb-specific (13), Cross-carrier / All (38) |
| **Format** | JSON; each item has `id`, `category`, `difficulty`, `company` (nullable), `query`, `expected_keywords`, `expected_min_sources`, `notes` |

Items 1–8 reuse the original queries from M03 for continuity; items 9–75 are new, spanning the full breadth of actuarial reserve topics (IBNR methodology, catastrophe loss trends, A&E reserves, social inflation, reinsurance structure, etc.).

### How to Run the Evaluation Pipeline

The pipeline is implemented in `eval/run_evaluation.py`.

**Prerequisites:**
```bash
# Activate virtual environment and install dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Ensure databases are running and ingested (M02/M03 prerequisite)
docker-compose up -d postgres qdrant

# Set your API key
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

**Option A – Live mode (runs all 75 queries against the agent):**
```bash
python eval/run_evaluation.py \
  --mode live \
  --input eval/eval_test_set.json \
  --output eval/eval_results.json
```

**Option B – Score mode (scores pre-existing results without running the agent):**
```bash
python eval/run_evaluation.py \
  --mode score \
  --input eval/eval_test_set.json \
  --results data/results.json \
  --output eval/eval_results_baseline.json
```

**Option C – Quick test (first 10 items only):**
```bash
python eval/run_evaluation.py \
  --mode live \
  --input eval/eval_test_set.json \
  --output eval/eval_results_quick.json \
  --limit 10
```

**Output format** (`eval/eval_results_baseline.json`):
```json
{
  "metadata": { "timestamp": "...", "total_test_items": 75, "results_evaluated": 8 },
  "summary": {
    "composite_score": { "mean": 73.2, "min": 48.9, "max": 100.0 },
    "failure_modes": { "retrieval_gap": 6, "context_truncation": 1, "none": 1 },
    "by_category": { "line_of_business": 100.0, "reserve_methodology": 82.0 }
  },
  "scored_results": [ ... ]
}
```

The baseline results file (`data/results.json`, 8 queries) was produced during M03 development using the live agent against the full pipeline. The 75-item test set was scored in **score mode** against those 8 existing results; items 9–75 are marked `"status": "missing"` in the baseline and will be populated when the full live run is executed in M05.

---

## 2. Quantitative Performance Analysis

### Metrics

Four sub-metrics combine into a composite score (0–100):

| Metric | Description | Weight (single-carrier) | Weight (cross-carrier) |
|--------|-------------|------------------------|------------------------|
| **Keyword Coverage** | Fraction of `expected_keywords` found in answer | 30% | 25% |
| **Source Adequacy** | Whether `num_sources ≥ expected_min_sources` | 25% | 20% |
| **Answer Completeness** | Heuristic: length + numeric citations + failure-mode penalty | 45% | 30% |
| **Cross-Carrier Coverage** | Fraction of AIG/Travelers/Chubb mentioned (cross-carrier queries only) | — | 25% |

Cross-carrier queries are weighted differently because mentioning all three carriers is a core requirement for those items. Failure-mode penalties reduce completeness score: `retrieval_gap` → 0.20, `single_carrier_only` → 0.50, `context_truncation` → 0.60.

### Baseline Results (8 queries run)

| ID | Query (abbreviated) | Category | Score | Failure Mode |
|----|---------------------|----------|-------|--------------|
| 1 | AIG reserve adequacy | reserve_adequacy | **64.0** | retrieval_gap |
| 2 | Compare loss development (all) | cross_carrier | **76.0** | retrieval_gap |
| 3 | External factors impacting reserves | external_factors | **48.9** | retrieval_gap |
| 4 | Commercial auto reserves (Travelers) | line_of_business | **100.0** | none |
| 5 | Social inflation (all carriers) | trend_analysis | **76.0** | retrieval_gap |
| 6 | Chubb reserving approach | reserve_methodology | **82.0** | context_truncation |
| 7 | Main risk factors affecting reserves | risk_factors | **67.7** | retrieval_gap |
| 8 | Catastrophe loss reserves | catastrophe | **71.0** | retrieval_gap |

**Summary statistics (8 evaluated items):**

| Statistic | Value |
|-----------|-------|
| Mean composite score | **73.2 / 100** |
| Median composite score | **75.5 / 100** |
| Min score | 48.9 (Q3 – external factors) |
| Max score | 100.0 (Q4 – commercial auto) |
| Mean keyword coverage | 0.72 |
| Mean source adequacy | 0.85 |
| Mean completeness | 0.62 |
| Mean response time | 10.5 seconds |

### Score by Category (evaluated items)

| Category | Mean Score | Notes |
|----------|-----------|-------|
| line_of_business | 100.0 | Strong when query maps to a single company/line |
| reserve_methodology | 82.0 | Chubb 10-K has explicit methodology sections |
| cross_carrier_comparison | 76.0 | Partial—only one carrier retrieved in most cases |
| trend_analysis | 76.0 | Retrieval gap on social inflation terminology |
| catastrophe | 71.0 | Primarily Chubb data; Travelers cat data not retrieved |
| risk_factors | 67.7 | Broad queries return peripheral content |
| reserve_adequacy | 64.0 | AIG retrieval returned table-of-contents text instead of MD&A |
| external_factors | 48.9 | Worst category; query-document vocabulary mismatch |

### Per-Query Breakdown

**Q4 (Score: 100) — Best case.** "Show me information about commercial auto reserves" with `company=Travelers`. The query is specific, the company filter narrows the vector search, and Travelers' 10-Q Q2 2024 has a dedicated commercial auto section with exact numeric disclosures (9% reserve share, ±1.3% sensitivity). This query illustrates what the system does well: focused, single-carrier, well-indexed topic.

**Q3 (Score: 48.9) — Worst case.** "What external factors impacted insurance reserves?" returned passages about investment market impacts, FX exposure, and credit quality—all *consequences* of external factors, not the external factors themselves (litigation environment, social inflation, climate, economic conditions). The semantic embeddings for "external factors impacted reserves" are more similar to financial risk passages than to MD&A commentary about macro drivers.

---

## 3. Error Analysis & Failure Identification

### Failure Mode Taxonomy

**6 of 8 evaluated queries (75%) produced a `retrieval_gap` failure.** This is defined as: the answer explicitly states it cannot address the question because the retrieved passages do not contain the relevant information—even though the information exists in the corpus.

#### Failure Mode 1: Retrieval Gap (6/8 queries)

**Definition:** Retrieved chunks are topically adjacent but not semantically precise. The LLM correctly identifies that the retrieved content does not answer the question, and says so.

**Examples:**
- Q1 (AIG reserve adequacy): Returned general "critical accounting estimates" language pointing to the 2023 annual report, rather than the actual MD&A discussion of reserve adequacy in the 2024 filing.
- Q5 (Social inflation): The term "social inflation" does not appear verbatim in the filings. The agent retrieved investment-related passages (interest rates, FX), which are topically near "reserves" but unrelated to social inflation as a loss cost driver.
- Q3 (External factors): Retrieved FX and investment market content—correct domain but wrong context. The model had no way to prefer "litigation environment" passages over "interest rate sensitivity" passages because both score similarly for the generic query.

**Root cause analysis:**
1. *Vocabulary mismatch:* Actuarial queries use industry jargon ("social inflation," "loss development," "IBNR") that may not appear verbatim in the SEC filing text. The embedding model (`all-MiniLM-L6-v2`) has limited actuarial domain knowledge and maps these terms to semantically broad neighborhoods.
2. *Flat retrieval:* The system retrieves top-K chunks globally across all sections without distinguishing MD&A (the most relevant section for reserve analysis) from footnotes, table of contents, or boilerplate risk disclosures.
3. *Single keyword for table retrieval:* `get_financial_tables()` always searches with `keyword='reserve'`—regardless of the actual query. A social inflation query triggers a table search for "reserve" but the most relevant content is narrative, not tabular.

#### Failure Mode 2: Context Truncation (1/8 queries)

**Definition:** The relevant passage was retrieved but the chunk was too short to contain the complete answer. The LLM's response quotes the truncated text (e.g., *"while we believe that our reserves..."*), signaling the chunk ended mid-sentence.

**Example — Q6 (Chubb reserving approach, Score: 82.0):**
The answer correctly describes Chubb's reserve establishment process and A&E methodology, but the final passage visibly cuts off: *"'while we believe that our reserves...' (passage cuts off)"*. The 200-token chunk limit bisects the critical "reserve adequacy" statement.

**Root cause:** Chunk size of 200 tokens (≈ 150 words) is too small for financial disclosure text, which often contains multi-paragraph explanations of a single concept. Important reserve adequacy statements are frequently split across chunk boundaries.

#### Failure Mode 3: Single-Carrier Retrieval for Cross-Carrier Queries (implicit, 2/8 queries)

**Definition:** For queries that ask about all carriers (company=null), the top-K vector search returns results dominated by one company. The LLM answers correctly for that company but acknowledges it cannot compare across carriers.

**Example — Q2 (Compare loss development, Score: 76.0):**
The answer provides detailed Chubb development methodology but explicitly says *"I can only provide insights on Chubb's loss development practices... passages don't contain comparable information from AIG or Travelers."* All 5 retrieved passages happened to be from Chubb because Chubb's 10-K (largest filing in the corpus at 13.8MB) dominates the vector space by chunk count.

**Root cause:** Chubb's 10-K is the longest document and generates the most narrative chunks. With flat top-K retrieval and no per-company diversity constraint, Chubb content systematically over-represents in cross-carrier queries.

### Error Category Summary

| Category | Count | Root Cause |
|----------|-------|------------|
| Retrieval gap (vocabulary mismatch) | 4 | Domain-specific terms not in embedding model's learned space |
| Retrieval gap (section-level mismatch) | 2 | Retrieves wrong document section (footnotes vs. MD&A) |
| Context truncation | 1 | 200-token chunk splits multi-paragraph disclosures |
| Single-carrier dominance | 2 | Largest filing monopolizes top-K results for cross-carrier queries |

---

## 4. Improvement Strategy Proposals

### Strategy 1: Query Expansion with Actuarial Synonym Injection

**What will be changed:**  
Add a pre-retrieval query expansion step in `src/agents/orchestrator.py`. Before calling `semantic_search()`, use a lightweight LLM prompt (or a curated synonym dictionary) to rewrite the user query into 2–3 expanded forms that include common actuarial/SEC filing vocabulary. For example:
- "social inflation" → also search "litigation trends," "jury awards," "severity trends," "loss cost inflation"
- "reserve adequacy" → also search "prior year development," "reserve review," "IBNR," "MD&A critical estimates"

Run all expanded queries in parallel, deduplicate results by chunk ID, and pass the union to the LLM.

**Why it is expected to help:**  
The primary failure mode (75% of errors) is vocabulary mismatch—the query uses actuarial terminology that does not appear verbatim in filing text, while filing text uses different phrasing for the same concepts. Query expansion bridges this gap by casting a wider semantic net without changing the retrieval model itself.

**How impact will be measured in M05:**  
Re-run the same 8 baseline queries plus a new sample of 20 queries that previously showed retrieval gaps. Compare keyword coverage scores and failure mode classification before/after expansion. Target: reduce `retrieval_gap` failures from 75% to ≤30%; keyword coverage mean from 0.72 to ≥0.85.

---

### Strategy 2: Per-Company Retrieval Balancing for Cross-Carrier Queries

**What will be changed:**  
Modify `src/agents/tools.py` `semantic_search()` to detect when `company=None` (cross-carrier query) and enforce a per-company retrieval quota. Instead of top-K globally, retrieve top-K/3 from each of the three companies separately, then merge and re-rank by score. This requires tagging the QDrant filter by company metadata during retrieval.

**Why it is expected to help:**  
The single-carrier dominance failure occurs because Chubb's 10-K (the largest document) produces the most chunks and therefore wins a disproportionate share of top-K slots. Enforcing per-company balance ensures AIG, Travelers, and Chubb are always represented in cross-carrier answers. The 8 cross-carrier queries in our test set (IDs 2, 3, 5, 7, 8, 15, 26, 29...) directly test this.

**How impact will be measured in M05:**  
Compute cross-carrier coverage score (fraction of 3 carriers mentioned) on the 38 cross-carrier items in the full 75-item test set. Target: increase cross-carrier coverage from current 0.45 (estimated from Q2/Q5 analysis) to ≥0.80. Also verify that single-carrier query quality does not degrade.

---

### Strategy 3: Section-Aware Chunking with MD&A Priority Tagging

**What will be changed:**  
Enhance `pipeline/section_filter.py` and `pipeline/chunk_text.py` to tag each chunk with a document section label: `MD&A`, `Risk_Factors`, `Financial_Statements`, `Notes_to_FS`, `Table_of_Contents`, `Other`. During retrieval, apply a scoring boost (e.g., +0.1 cosine similarity) to chunks tagged `MD&A` or `Notes_to_FS` for reserve-related queries. Additionally, increase chunk size from 200 to 400 tokens for `MD&A` and `Notes_to_FS` sections to reduce mid-sentence truncation.

**Why it is expected to help:**  
Two distinct failure modes are addressed:
- *Retrieval gap (section mismatch):* Q1's AIG retrieval returned table-of-contents text and boilerplate capital management language instead of the MD&A reserve discussion. Section boosting ensures the MD&A—the primary source of qualitative reserve commentary—is preferred.
- *Context truncation:* Larger chunks for narrative sections (400 tokens ≈ 300 words) will capture full reserve adequacy statements. The Chubb Q6 truncation (*"while we believe that our reserves..."*) would not occur if the chunk extended another 200 tokens.

**How impact will be measured in M05:**  
Monitor `context_truncation` failure rate (target: 0 from current 1/8). For section relevance, manually review the 10 lowest-scoring queries and verify that MD&A passages now appear in the top-3 retrieved results. Composite score target: ≥80.0 mean across the 8 baseline queries (up from 73.2).

---

## Appendix: File Inventory

```
eval/
├── eval_test_set.json          # 75-item evaluation test set
├── run_evaluation.py           # Evaluation pipeline (run + score modes)
└── eval_results_baseline.json  # Scored baseline results (8 of 75 items run)

data/
├── eval_queries.json           # Original 8 M03 queries
└── results.json                # Pre-generated M03 results (8 queries)
```

**Running the complete 75-item evaluation** (requires live system):
```bash
python eval/run_evaluation.py \
  --mode live \
  --input eval/eval_test_set.json \
  --output eval/eval_results_full.json
```

Results are saved incrementally; the pipeline prints a live report on completion.
