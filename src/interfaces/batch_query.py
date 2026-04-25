"""
Batch Query Interface - Updated for Multi-Agent Architecture (M06)
Processes multiple queries and saves results to JSON
"""

import json
import argparse
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import multi-agent orchestrator
from src.agents import MultiAgentOrchestrator


def run_batch_evaluation(input_file: str, output_file: str):
    """
    Run batch evaluation using multi-agent orchestrator.
    
    Args:
        input_file: Path to JSON file with queries
        output_file: Path to save results
    """
    print("🚀 Starting Multi-Agent Batch Evaluation")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    # Load queries
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    queries = data.get('queries', data)  # Handle both formats
    print(f"📋 Loaded {len(queries)} queries")
    
    # Initialize multi-agent orchestrator
    print("🏗️ Initializing Multi-Agent System...")
    orchestrator = MultiAgentOrchestrator()
    print("✅ Orchestrator ready (Retrieval → Analysis → Synthesis)")
    
    # Process queries
    results = []
    successful = 0
    failed = 0
    
    for idx, query_item in enumerate(queries):
        query_id = query_item.get('id', idx + 1)
        query_text = query_item.get('query', '')
        company = query_item.get('company')
        
        print(f"\n[{idx+1}/{len(queries)}] Processing Query {query_id}...")
        print(f"Query: {query_text[:80]}...")
        
        try:
            # Run multi-agent pipeline
            response = orchestrator.query(
                user_query=query_text,
                company=company,
                use_balanced_search=(company is None)  # Use balanced for multi-company
            )
            
            # Format result
            result = {
                'id': query_id,
                'query': query_text,
                'company': company,
                'answer': response['answer'],
                'sources': response['sources'],
                'num_sources': response['num_sources'],
                'companies_mentioned': response.get('companies_mentioned', []),
                'pipeline_stats': response.get('pipeline_stats', {}),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            results.append(result)
            successful += 1
            print(f"✅ Success - {response['num_sources']} sources")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
            result = {
                'id': query_id,
                'query': query_text,
                'company': company,
                'answer': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
            
            results.append(result)
            failed += 1
    
    # Save results
    output_data = {
        'metadata': {
            'total_queries': len(queries),
            'successful': successful,
            'failed': failed,
            'timestamp': datetime.now().isoformat(),
            'architecture': 'multi-agent',
            'agents': ['RetrievalAgent', 'AnalysisAgent', 'SynthesisAgent']
        },
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ Batch Evaluation Complete!")
    print(f"📊 Results: {successful} successful, {failed} failed")
    print(f"💾 Saved to: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch query evaluation with multi-agent system")
    parser.add_argument(
        "--input",
        type=str,
        default="eval/eval_test_set.json",
        help="Input JSON file with queries"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval/batch_results_multiagent.json",
        help="Output JSON file for results"
    )
    
    args = parser.parse_args()
    
    run_batch_evaluation(args.input, args.output)