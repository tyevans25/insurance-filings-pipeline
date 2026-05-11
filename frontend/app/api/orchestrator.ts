/**
 * API Client for Multi-Agent Orchestrator
 * Communicates with FastAPI backend running on localhost:8000
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface QueryRequest {
  query: string
  company?: string | null
  use_balanced_search?: boolean
  llm_provider?: string
}

export interface Source {
  source_id: number
  type: 'narrative' | 'table'
  company: string
  filing_type: string
  filing_date: string
  page_num: string
  section_type?: string
  table_type?: string
  relevance_score?: number
  excerpt?: string
}

export interface QueryResponse {
  answer: string
  sources: Source[]
  num_sources: number
  companies_mentioned: string[]
  pipeline_stats: {
    documents_retrieved: number
    tables_retrieved: number
    companies_mentioned: string[]
    avg_relevance_score: number
  }
}

export async function queryOrchestrator(
  request: QueryRequest
): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }

  return response.json()
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`)
  return response.json()
}