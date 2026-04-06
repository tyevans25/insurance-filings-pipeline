"""
M04 Evaluation Pipeline
=======================
Runs the evaluation test set against the batch interface and scores results.

Usage:
    # Run evaluation against live system (requires API key + running databases)
    python eval/run_evaluation.py --mode live --input eval/eval_test_set.json --output eval/eval_results.json

    # Score pre-existing results (offline mode)
    python eval/run_evaluation.py --mode score --input eval/eval_test_set.json --results data/results.json --output eval/eval_results.json

    # Quick test with subset
    python eval/run_evaluation.py --mode live --input eval/eval_test_set.json --output eval/eval_results.json --limit 10
"""

import json
import argparse
import sys
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


# ─────────────────────────────────────────────
# Scoring Functions
# ─────────────────────────────────────────────

def score_keyword_coverage(answer: str, expected_keywords: List[str]) -> float:
    """
    Fraction of expected keywords found in the answer (case-insensitive).
    Returns 0.0 – 1.0
    """
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return round(found / len(expected_keywords), 3)


def score_source_adequacy(num_sources: int, expected_min: int) -> float:
    """
    Whether the answer drew on enough sources.
    Returns 1.0 if met, partial credit if close, 0.0 if far below.
    """
    if num_sources >= expected_min:
        return 1.0
    elif num_sources == 0:
        return 0.0
    else:
        return round(num_sources / expected_min, 3)


def detect_failure_mode(answer: str) -> str:
    """
    Classify the type of failure based on answer content.
    Returns a short failure category string.
    """
    if not answer:
        return "null_answer"

    a = answer.lower()

    retrieval_failure_phrases = [
        "cannot provide", "no relevant information", "passages don't contain",
        "passages provided", "limited information", "not available in",
        "i cannot adequately", "unable to find", "not found in",
        "would need to search", "no information", "passages focus",
        "the passages you've shared"
    ]
    for phrase in retrieval_failure_phrases:
        if phrase in a:
            return "retrieval_gap"

    single_carrier_phrases = [
        "only provide insights on",
        "only chubb", "only aig", "only travelers",
        "limiting my ability to make cross-carrier",
        "don't include comparative data"
    ]
    for phrase in single_carrier_phrases:
        if phrase in a:
            return "single_carrier_only"

    truncation_phrases = [
        "passage cuts off", "while we believe that our reserves...",
        "(passage cuts off)", "text is cut off"
    ]
    for phrase in truncation_phrases:
        if phrase in a:
            return "context_truncation"

    if len(answer) < 200:
        return "answer_too_short"

    return "none"


def score_answer_completeness(answer: str) -> float:
    """
    Heuristic completeness score based on answer length and structure.
    Returns 0.0 – 1.0
    """
    if not answer:
        return 0.0

    failure = detect_failure_mode(answer)
    if failure == "retrieval_gap":
        return 0.2
    if failure == "single_carrier_only":
        return 0.5
    if failure == "context_truncation":
        return 0.6
    if failure == "answer_too_short":
        return 0.3

    # Length-based scoring (diminishing returns after 500 chars)
    length_score = min(len(answer) / 1500, 1.0)

    # Bonus for citing specific numbers / entities
    has_numbers = bool(re.search(r'\$[\d,]+|\d+%|\d+\.\d+', answer))
    has_citations = bool(re.search(r'\b(10-K|10-Q|filing|AIG|Travelers|Chubb)\b', answer, re.I))

    score = length_score * 0.6
    if has_numbers:
        score += 0.2
    if has_citations:
        score += 0.2

    return round(min(score, 1.0), 3)


def score_cross_carrier_coverage(answer: str, query_company: Optional[str]) -> float:
    """
    For cross-carrier queries (company=null), check that multiple carriers are referenced.
    Returns 1.0 if all 3 carriers mentioned, 0.67 for 2, 0.33 for 1, 0.0 for none.
    """
    if query_company is not None:
        return 1.0  # Single-carrier query, not applicable

    carriers = ["AIG", "Travelers", "Chubb"]
    mentioned = sum(1 for c in carriers if c.lower() in answer.lower())
    return round(mentioned / 3, 3)


def compute_composite_score(
    keyword_score: float,
    source_score: float,
    completeness_score: float,
    cross_carrier_score: float,
    query_company: Optional[str]
) -> float:
    """
    Weighted composite score (0–100).
    """
    if query_company is None:
        # Cross-carrier query: carrier coverage matters more
        score = (
            keyword_score * 25 +
            source_score * 20 +
            completeness_score * 30 +
            cross_carrier_score * 25
        )
    else:
        # Single-carrier query
        score = (
            keyword_score * 30 +
            source_score * 25 +
            completeness_score * 45
        )
    return round(score, 1)


# ─────────────────────────────────────────────
# Result Scorer
# ─────────────────────────────────────────────

def score_result(test_item: Dict, result: Dict) -> Dict:
    """Score a single result against its test item specification."""

    answer = result.get("answer") or ""
    num_sources = result.get("num_sources", 0)
    status = result.get("status", "unknown")
    processing_time = result.get("processing_time_seconds", 0)

    keyword_score = score_keyword_coverage(answer, test_item.get("expected_keywords", []))
    source_score = score_source_adequacy(num_sources, test_item.get("expected_min_sources", 1))
    completeness_score = score_answer_completeness(answer)
    cross_carrier_score = score_cross_carrier_coverage(answer, test_item.get("company"))
    failure_mode = detect_failure_mode(answer)

    composite = compute_composite_score(
        keyword_score, source_score, completeness_score, cross_carrier_score,
        test_item.get("company")
    )

    return {
        "id": test_item["id"],
        "category": test_item["category"],
        "difficulty": test_item["difficulty"],
        "company": test_item.get("company"),
        "query": test_item["query"],
        "status": status,
        "processing_time_seconds": processing_time,
        "num_sources": num_sources,
        "failure_mode": failure_mode,
        "scores": {
            "keyword_coverage": keyword_score,
            "source_adequacy": source_score,
            "answer_completeness": completeness_score,
            "cross_carrier_coverage": cross_carrier_score,
            "composite_score": composite
        },
        "answer_length": len(answer),
        "answer_snippet": answer[:200] if answer else ""
    }


# ─────────────────────────────────────────────
# Batch Runner
# ─────────────────────────────────────────────

def run_live_batch(test_items: List[Dict], limit: Optional[int] = None) -> List[Dict]:
    """
    Run test items through the live batch_query interface.
    Requires ANTHROPIC_API_KEY and running databases.
    """
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))

    try:
        from src.agents.orchestrator import ReservingAgent
    except ImportError:
        try:
            from agents.orchestrator import ReservingAgent
        except ImportError:
            print("❌ Could not import ReservingAgent. Ensure you are running from the project root.")
            print("   Try: python eval/run_evaluation.py --mode score ...")
            sys.exit(1)

    agent = ReservingAgent()
    items_to_run = test_items[:limit] if limit else test_items
    results = []

    print(f"\n🚀 Running {len(items_to_run)} queries through live agent...\n")

    for i, item in enumerate(items_to_run, 1):
        print(f"[{i}/{len(items_to_run)}] ID={item['id']} | {item['query'][:60]}...")
        start = time.time()

        try:
            result = agent.answer_query(item["query"], company=item.get("company"))
            elapsed = time.time() - start

            results.append({
                "id": item["id"],
                "query": item["query"],
                "company_filter": item.get("company"),
                "answer": result.get("answer", ""),
                "num_sources": result.get("num_sources", 0),
                "processing_time_seconds": round(elapsed, 2),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            print(f"   ✅ {elapsed:.1f}s | {result.get('num_sources', 0)} sources")

        except Exception as e:
            elapsed = time.time() - start
            print(f"   ❌ Error: {e}")
            results.append({
                "id": item["id"],
                "query": item["query"],
                "company_filter": item.get("company"),
                "answer": None,
                "num_sources": 0,
                "error": str(e),
                "processing_time_seconds": round(elapsed, 2),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            })

    return results


# ─────────────────────────────────────────────
# Analysis & Reporting
# ─────────────────────────────────────────────

def analyze_scored_results(scored: List[Dict]) -> Dict:
    """Compute aggregate statistics over all scored results."""

    if not scored:
        return {}

    composites = [s["scores"]["composite_score"] for s in scored]
    keyword_scores = [s["scores"]["keyword_coverage"] for s in scored]
    source_scores = [s["scores"]["source_adequacy"] for s in scored]
    completeness_scores = [s["scores"]["answer_completeness"] for s in scored]
    times = [s["processing_time_seconds"] for s in scored if s["processing_time_seconds"]]

    # Failure mode breakdown
    failure_modes = {}
    for s in scored:
        fm = s["failure_mode"]
        failure_modes[fm] = failure_modes.get(fm, 0) + 1

    # Category breakdown
    category_scores = {}
    for s in scored:
        cat = s["category"]
        if cat not in category_scores:
            category_scores[cat] = []
        category_scores[cat].append(s["scores"]["composite_score"])

    category_avg = {
        cat: round(sum(scores) / len(scores), 1)
        for cat, scores in category_scores.items()
    }

    # Difficulty breakdown
    difficulty_scores = {}
    for s in scored:
        diff = s["difficulty"]
        if diff not in difficulty_scores:
            difficulty_scores[diff] = []
        difficulty_scores[diff].append(s["scores"]["composite_score"])

    difficulty_avg = {
        d: round(sum(scores) / len(scores), 1)
        for d, scores in difficulty_scores.items()
    }

    def avg(lst):
        return round(sum(lst) / len(lst), 3) if lst else 0

    return {
        "total_items": len(scored),
        "successful": sum(1 for s in scored if s["status"] == "success"),
        "failed": sum(1 for s in scored if s["status"] != "success"),
        "composite_score": {
            "mean": avg(composites),
            "min": min(composites),
            "max": max(composites),
            "p25": sorted(composites)[len(composites) // 4],
            "p75": sorted(composites)[3 * len(composites) // 4],
        },
        "keyword_coverage_mean": avg(keyword_scores),
        "source_adequacy_mean": avg(source_scores),
        "completeness_mean": avg(completeness_scores),
        "avg_processing_time_seconds": avg(times),
        "failure_modes": failure_modes,
        "by_category": category_avg,
        "by_difficulty": difficulty_avg,
        "low_performers": [
            {"id": s["id"], "query": s["query"][:60], "score": s["scores"]["composite_score"],
             "failure_mode": s["failure_mode"]}
            for s in sorted(scored, key=lambda x: x["scores"]["composite_score"])[:10]
        ],
        "top_performers": [
            {"id": s["id"], "query": s["query"][:60], "score": s["scores"]["composite_score"]}
            for s in sorted(scored, key=lambda x: x["scores"]["composite_score"], reverse=True)[:5]
        ]
    }


def print_report(analysis: Dict):
    """Print a human-readable evaluation report."""
    print("\n" + "=" * 70)
    print("M04 EVALUATION REPORT")
    print("=" * 70)
    print(f"Total items:   {analysis['total_items']}")
    print(f"Successful:    {analysis['successful']}")
    print(f"Failed:        {analysis['failed']}")
    print()

    cs = analysis["composite_score"]
    print(f"Composite Score (0–100):")
    print(f"  Mean:  {cs['mean']}")
    print(f"  Min:   {cs['min']}")
    print(f"  Max:   {cs['max']}")
    print(f"  P25:   {cs['p25']}  |  P75: {cs['p75']}")
    print()

    print(f"Sub-metrics (0–1):")
    print(f"  Keyword coverage:   {analysis['keyword_coverage_mean']}")
    print(f"  Source adequacy:    {analysis['source_adequacy_mean']}")
    print(f"  Completeness:       {analysis['completeness_mean']}")
    print(f"  Avg response time:  {analysis['avg_processing_time_seconds']}s")
    print()

    print("Failure Modes:")
    for mode, count in analysis["failure_modes"].items():
        print(f"  {mode:30s} {count}")
    print()

    print("Score by Category:")
    for cat, score in sorted(analysis["by_category"].items(), key=lambda x: x[1]):
        bar = "█" * int(score / 5)
        print(f"  {cat:35s} {score:5.1f}  {bar}")
    print()

    print("Score by Difficulty:")
    for diff, score in analysis["by_difficulty"].items():
        print(f"  {diff:10s} {score}")
    print()

    print("Top 5 Performers:")
    for item in analysis["top_performers"]:
        print(f"  [{item['id']:3d}] {item['query']:55s} {item['score']}")
    print()

    print("Bottom 10 Low Performers:")
    for item in analysis["low_performers"]:
        print(f"  [{item['id']:3d}] {item['query']:50s} {item['score']:5.1f}  [{item['failure_mode']}]")
    print("=" * 70)


# ─────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="M04 Evaluation Pipeline")
    parser.add_argument("--mode", choices=["live", "score"], required=True,
                        help="'live' runs queries against agent; 'score' scores pre-existing results")
    parser.add_argument("--input", required=True, help="Path to eval_test_set.json")
    parser.add_argument("--output", required=True, help="Path to write scored results JSON")
    parser.add_argument("--results", help="[score mode] Path to existing results JSON")
    parser.add_argument("--limit", type=int, default=None,
                        help="[live mode] Only run first N items")
    args = parser.parse_args()

    # Load test set
    print(f"📂 Loading test set from {args.input} ...")
    with open(args.input) as f:
        test_items = json.load(f)
    print(f"   {len(test_items)} items loaded")

    # Get raw results
    if args.mode == "live":
        raw_results = run_live_batch(test_items, limit=args.limit)
    else:
        if not args.results:
            print("❌ --results is required in score mode")
            sys.exit(1)
        print(f"📂 Loading existing results from {args.results} ...")
        with open(args.results) as f:
            raw_results = json.load(f)
        # Handle both list and dict-wrapped formats
        if isinstance(raw_results, dict):
            raw_results = raw_results.get("results", raw_results)
        print(f"   {len(raw_results)} results loaded")

    # Build a lookup: result_id -> result
    results_by_id = {r.get("id"): r for r in raw_results}

    # Score each test item against its result (if available)
    scored = []
    for item in test_items:
        result = results_by_id.get(item["id"])
        if result is None:
            # No result for this item — mark as missing
            result = {"id": item["id"], "answer": None, "num_sources": 0,
                      "status": "missing", "processing_time_seconds": 0}
        scored.append(score_result(item, result))

    # Analyze
    analysis = analyze_scored_results(scored)
    print_report(analysis)

    # Save output
    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "mode": args.mode,
            "total_test_items": len(test_items),
            "results_evaluated": len([s for s in scored if s["status"] != "missing"])
        },
        "summary": analysis,
        "scored_results": scored
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n💾 Scored results saved to {args.output}")


if __name__ == "__main__":
    main()
