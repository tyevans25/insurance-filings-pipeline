"""
Batch query interface for automated evaluation
"""
import sys
from pathlib import Path

# Add paths for both local and Docker environments
sys.path.insert(0, '/app/src')  # Docker path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Local path
sys.path.insert(0, str(Path(__file__).parent.parent))  # Local src path

from agents.orchestrator import ReservingAgent
import json
import argparse
from datetime import datetime
import time

def run_batch_queries(input_file: str, output_file: str):
    """
    Run batch queries from JSON file
    
    Args:
        input_file: Path to queries JSON
        output_file: Path to save results JSON
    """
    # Load queries
    print(f"📂 Loading queries from {input_file}...")
    with open(input_file, 'r') as f:
        queries = json.load(f)
    
    print(f"✅ Loaded {len(queries)} queries")
    
    # Initialize agent
    print("🤖 Initializing agent...")
    agent = ReservingAgent()
    print("✅ Agent ready")
    
    # Run each query
    results = []
    for i, query_item in enumerate(queries, 1):
        query = query_item.get('query', '')
        company = query_item.get('company', None)
        
        print(f"\n{'='*80}")
        print(f"Query {i}/{len(queries)}: {query[:60]}...")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            result = agent.answer_query(query, company=company)
            processing_time = time.time() - start_time
            
            results.append({
                'id': query_item.get('id', i),
                'query': query,
                'company_filter': company,
                'answer': result['answer'],
                'num_sources': result['num_sources'],
                'timestamp': datetime.now().isoformat(),
                'processing_time_seconds': round(processing_time, 2),
                'status': 'success'
            })
            
            print(f"✅ Completed in {processing_time:.2f}s")
            print(f"   Sources used: {result['num_sources']}")
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ Error: {e}")
            
            results.append({
                'id': query_item.get('id', i),
                'query': query,
                'company_filter': company,
                'answer': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'processing_time_seconds': round(processing_time, 2),
                'status': 'failed'
            })
    
    # Save results
    print(f"\n{'='*80}")
    print(f"💾 Saving results to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    total_time = sum(r['processing_time_seconds'] for r in results)
    avg_time = total_time / len(results) if results else 0
    
    print(f"{'='*80}")
    print(f"📊 BATCH QUERY SUMMARY")
    print(f"{'='*80}")
    print(f"Total queries: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per query: {avg_time:.2f}s")
    print(f"{'='*80}")
    print(f"✅ Results saved to {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run batch queries for evaluation')
    parser.add_argument('--input', required=True, help='Input queries JSON file')
    parser.add_argument('--output', required=True, help='Output results JSON file')
    
    args = parser.parse_args()
    run_batch_queries(args.input, args.output)