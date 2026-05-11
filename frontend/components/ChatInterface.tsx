'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, AlertCircle, ChevronDown } from 'lucide-react'
import { queryOrchestrator, type QueryResponse } from '@/app/api/orchestrator'
import { motion, AnimatePresence } from 'framer-motion'
import FormattedText from './FormattedText'
import SourceCard from './SourceCard'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: QueryResponse['sources']
  stats?: QueryResponse['pipeline_stats']
}

interface RecentQuery {
  query: string
  timestamp: string
}

const EXAMPLE_QUERIES = [
  {
    category: 'Reserve adequacy',
    questions: [
      'Reserve adequacy by carrier',
      'Environmental exposures',
    ],
  },
  {
    category: 'Catastrophe impact',
    questions: [
      'Hurricane Helene impact on reserves',
      'CAT loss development trends',
    ],
  },
]

const SEARCH_SUGGESTIONS = [
  'reserve adequacy trends',
  'catastrophe losses 2024',
  'IBNR methodology comparison',
  'loss development by line of business',
  'prior year development',
  'asbestos and environmental exposures',
  'combined ratio analysis',
  'reserve strengthening events',
]

const LOADING_STEPS = [
  { text: 'Searching documents', duration: 1000 },
  { text: 'Analyzing sources', duration: 1500 },
  { text: 'Generating response', duration: 2000 },
]

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "👋 Welcome! I'm your P&C Reserving Intelligence assistant. I can help you analyze insurance reserves, loss development, and catastrophe events from SEC filings.\n\n**What I can do:**\n- Answer questions about reserve adequacy and prior year development\n- Compare trends across AIG, Travelers, and Chubb\n- Analyze catastrophe impacts and external risks\n- Provide insights backed by source documents\n\n**Try asking:**\n- \"What did AIG say about reserve adequacy in their latest filing?\"\n- \"Compare loss development across all carriers\"\n- \"What external risks impacted reserves this quarter?\"\n\nJust type your question below to get started!",
      sources: []
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [company, setCompany] = useState<string>('All Companies')
  const [useBalanced, setUseBalanced] = useState(true)
  const [year, setYear] = useState('All years')
  const [quarter, setQuarter] = useState('All quarters')
  const [filingType, setFilingType] = useState('All filings')
  const [llmProvider, setLlmProvider] = useState<string>('claude')
  const [availableProviders, setAvailableProviders] = useState<any[]>([])
  const [isDevMode, setIsDevMode] = useState(false)
  const [recentQueries, setRecentQueries] = useState<RecentQuery[]>([
    { query: 'AIG catastrophe events 2024', timestamp: '2 hours ago' },
    { query: 'Reserve adequacy trends', timestamp: 'Yesterday' },
    { query: 'IBNR methodology comparison', timestamp: '3 days ago' },
  ])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)

  // Check if in dev mode and fetch available providers
  useEffect(() => {
    const checkDevMode = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/providers`)
        const data = await response.json()
        
        if (data.available) {
          setIsDevMode(true)
          setAvailableProviders(data.providers || [])
          setLlmProvider(data.current_provider || 'claude')
        }
      } catch (error) {
        console.log('Dev mode not available')
      }
    }
    
    checkDevMode()
  }, [])

  // Handle search suggestions
  useEffect(() => {
    if (input.trim().length > 2) {
      const filtered = SEARCH_SUGGESTIONS.filter(suggestion =>
        suggestion.toLowerCase().includes(input.toLowerCase())
      )
      setFilteredSuggestions(filtered)
      setShowSuggestions(filtered.length > 0)
    } else {
      setShowSuggestions(false)
    }
  }, [input])

  // Loading step animation
  useEffect(() => {
    if (loading && loadingStep < LOADING_STEPS.length - 1) {
      const timer = setTimeout(() => {
        setLoadingStep(prev => prev + 1)
      }, LOADING_STEPS[loadingStep].duration)
      return () => clearTimeout(timer)
    }
  }, [loading, loadingStep])

  const handleSubmit = async (queryText?: string) => {
    const query = queryText || input
    if (!query.trim() || loading) return

    setError(null)
    setInput('')
    setShowSuggestions(false)
    setLoadingStep(0)
    
    // Add to recent queries
    const newRecent: RecentQuery = {
      query: query,
      timestamp: 'Just now'
    }
    setRecentQueries(prev => [newRecent, ...prev.slice(0, 4)])
    
    // Add user message
    const userMessage: Message = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      const response = await queryOrchestrator({
        query,
        company: company === 'All Companies' ? null : company,
        use_balanced_search: useBalanced,
        llm_provider: isDevMode ? llmProvider : undefined,
      })

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        stats: response.pipeline_stats,
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process query')
      // Remove user message on error
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
      setLoadingStep(0)
    }
  }

  const selectSuggestion = (suggestion: string) => {
    setInput(suggestion)
    setShowSuggestions(false)
    inputRef.current?.focus()
  }

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <motion.aside 
        initial={{ x: -300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-80 bg-black/15 border-r border-white/[0.06] flex flex-col overflow-y-auto"
      >
        <div className="p-6 border-b border-white/[0.06]">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span className="text-xs text-white/60 font-medium">Active</span>
          </div>
        </div>

        <div className="flex-1 p-6 space-y-8">
          {/* Query Config */}
          <div>
            <h3 className="text-[11px] text-white/40 font-medium uppercase tracking-wider mb-4">
              Query settings
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs text-white/50 mb-2 font-medium">
                  Company
                </label>
                <select
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full bg-white/[0.04] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white/90 focus:outline-none focus:border-blue-500/50"
                >
                  <option>All Companies</option>
                  <option>AIG</option>
                  <option>Travelers</option>
                  <option>Chubb</option>
                </select>
              </div>

              {/* LLM Provider Selector - Dev Mode Only */}
              {isDevMode && availableProviders.length > 0 && (
                <div className="pt-4 border-t border-white/[0.06]">
                  <label className="block text-xs text-white/50 mb-2 font-medium">
                    LLM Provider
                    <span className="ml-2 text-[10px] text-amber-400/70">(Dev Mode)</span>
                  </label>
                  <select
                    value={llmProvider}
                    onChange={(e) => setLlmProvider(e.target.value)}
                    className="w-full bg-amber-500/[0.08] border border-amber-500/20 rounded-lg px-3 py-2.5 text-sm text-white/90 focus:outline-none focus:border-amber-500/50"
                  >
                    {availableProviders.map((provider) => (
                      <option key={provider.id} value={provider.id}>
                        {provider.name} {provider.recommended ? '(Recommended)' : ''}
                      </option>
                    ))}
                  </select>
                  <p className="mt-2 text-[10px] text-white/30 leading-relaxed">
                    Current model: {availableProviders.find(p => p.id === llmProvider)?.model}
                  </p>
                </div>
              )}

              <label className="flex items-center gap-3 cursor-pointer py-2">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={useBalanced}
                    onChange={(e) => setUseBalanced(e.target.checked)}
                    className="sr-only"
                  />
                  <div className={`w-10 h-[22px] rounded-full border transition-colors ${
                    useBalanced 
                      ? 'bg-blue-500/20 border-blue-500/30' 
                      : 'bg-white/[0.04] border-white/10'
                  }`}>
                    <div className={`w-4 h-4 bg-blue-500 rounded-full transition-transform ${
                      useBalanced ? 'translate-x-5' : 'translate-x-0.5'
                    } mt-0.5`} />
                  </div>
                </div>
                <span className="text-sm text-white/70">Balanced search</span>
              </label>
            </div>
          </div>

          {/* Filters */}
          <div>
            <h3 className="text-[11px] text-white/40 font-medium uppercase tracking-wider mb-4">
              Filters
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs text-white/50 mb-2 font-medium">
                  Year
                </label>
                <select
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  className="w-full bg-white/[0.04] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white/90 focus:outline-none focus:border-blue-500/50"
                >
                  <option>All years</option>
                  <option>2024</option>
                  <option>2023</option>
                  <option>2022</option>
                  <option>2021</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-white/50 mb-2 font-medium">
                  Quarter
                </label>
                <select
                  value={quarter}
                  onChange={(e) => setQuarter(e.target.value)}
                  className="w-full bg-white/[0.04] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white/90 focus:outline-none focus:border-blue-500/50"
                >
                  <option>All quarters</option>
                  <option>Q1</option>
                  <option>Q2</option>
                  <option>Q3</option>
                  <option>Q4</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-white/50 mb-2 font-medium">
                  Filing type
                </label>
                <select
                  value={filingType}
                  onChange={(e) => setFilingType(e.target.value)}
                  className="w-full bg-white/[0.04] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white/90 focus:outline-none focus:border-blue-500/50"
                >
                  <option>All filings</option>
                  <option>10-K (Annual)</option>
                  <option>10-Q (Quarterly)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Recent Queries */}
          <div>
            <h3 className="text-[11px] text-white/40 font-medium uppercase tracking-wider mb-4">
              Recent
            </h3>
            <div className="space-y-2">
              {recentQueries.map((recent, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSubmit(recent.query)}
                  className="w-full text-left bg-white/[0.02] border border-white/[0.06] rounded-lg px-3 py-3 hover:bg-white/[0.04] hover:border-white/10 transition-all"
                >
                  <div className="text-sm text-white/80 mb-1 line-clamp-1">{recent.query}</div>
                  <div className="text-[11px] text-white/30">{recent.timestamp}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-white/[0.06] text-center">
          <div className="text-[10px] text-white/30">v2.0</div>
        </div>
      </motion.aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <motion.header 
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-gradient-to-r from-blue-500/[0.06] via-purple-500/[0.04] to-blue-500/[0.06] border-b border-white/[0.06]"
        >
          <div className="px-12 py-12">
            <h1 className="text-4xl font-medium text-white tracking-tight">
              P&C Reserving Intelligence
            </h1>
          </div>
        </motion.header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-12 py-8 bg-black/[0.08]">
          {messages.length === 0 && !loading && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="max-w-4xl mx-auto space-y-8"
            >
              {/* Welcome Message */}
              <div className="text-center mb-12">
                <h2 className="text-3xl font-medium text-white mb-4">
                  Welcome to P&C Reserving Intelligence
                </h2>
                <p className="text-base text-white/70 max-w-2xl mx-auto leading-relaxed">
                  Your AI-powered assistant for analyzing insurance reserves, loss development, and catastrophe events from SEC filings. Ask questions in natural language and get instant insights backed by source documents.
                </p>
              </div>

              {/* Tips */}
              <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-6 mb-8">
                <h3 className="text-sm font-medium text-white/80 mb-4">Quick tips</h3>
                <ul className="space-y-3 text-sm text-white/70">
                  <li className="flex items-start gap-3">
                    <span className="text-blue-400 mt-0.5">•</span>
                    <span>Ask about reserve adequacy, prior year development, or catastrophe impacts</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-blue-400 mt-0.5">•</span>
                    <span>Filter by specific companies or compare across carriers</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-blue-400 mt-0.5">•</span>
                    <span>Enable balanced search for comprehensive multi-company analysis</span>
                  </li>
                </ul>
              </div>

              {/* Example queries */}
              {EXAMPLE_QUERIES.map((category, idx) => (
                <motion.div
                  key={category.category}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.4 + idx * 0.1 }}
                >
                  <h3 className="text-xs text-white/60 mb-3 font-medium">
                    {category.category}
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    {category.questions.map((question, qIdx) => (
                      <button
                        key={qIdx}
                        onClick={() => handleSubmit(question)}
                        className="text-left p-4 bg-white/[0.03] border border-white/[0.08] rounded-lg hover:bg-white/[0.05] hover:border-white/[0.12] transition-all text-sm text-white/85 leading-relaxed"
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}

          <AnimatePresence>
            {messages.map((message, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className={`mb-6 ${message.role === 'user' ? 'flex justify-end' : ''}`}
              >
                <div className={`max-w-4xl ${message.role === 'user' ? 'ml-auto' : ''}`}>
                  <div className={`mb-3 text-[11px] font-medium uppercase tracking-wider ${
                    message.role === 'user' ? 'text-right text-white/35' : 'text-white/35'
                  }`}>
                    {message.role === 'user' ? 'You' : 'Assistant'}
                  </div>
                  
                  <div className={`rounded-xl border ${
                    message.role === 'user'
                      ? 'bg-blue-500/[0.08] border-blue-500/[0.15] p-5 max-w-[80%] ml-auto'
                      : 'bg-white/[0.02] border-white/[0.06] p-6 max-w-[95%]'
                  }`}>
                    <FormattedText content={message.content} />

                    {/* Stats */}
                    {message.stats && (
                      <div className="mt-4 pt-4 border-t border-white/[0.04] flex items-center gap-8 text-xs text-white/40 font-medium">
                        <div>{message.stats.documents_retrieved} documents</div>
                        <div>{message.stats.tables_retrieved} tables</div>
                        <div>{message.stats.companies_mentioned?.length || 0} companies</div>
                      </div>
                    )}

                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <details className="mt-5">
                        <summary className="cursor-pointer text-xs text-blue-400/80 hover:text-blue-400 transition-colors font-medium list-none flex items-center gap-2">
                          <span>View sources ({message.sources.length})</span>
                          <ChevronDown className="w-3 h-3" />
                        </summary>
                        <div className="mt-4 space-y-3">
                          {message.sources.slice(0, 5).map((source, sourceIdx) => (
                            <SourceCard key={sourceIdx} source={source} index={sourceIdx + 1} />
                          ))}
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading State */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-4xl mb-6"
            >
              <div className="mb-3 text-[11px] font-medium uppercase tracking-wider text-white/35">
                Assistant
              </div>
              <div className="rounded-xl border bg-white/[0.02] border-white/[0.06] p-6">
                <div className="space-y-4">
                  {LOADING_STEPS.map((step, idx) => (
                    <div 
                      key={idx}
                      className={`flex items-center gap-3 transition-opacity ${
                        idx <= loadingStep ? 'opacity-100' : 'opacity-30'
                      }`}
                    >
                      {idx < loadingStep ? (
                        <div className="w-4 h-4 rounded-full bg-blue-500/30 border border-blue-500/50 flex items-center justify-center">
                          <div className="w-2 h-2 rounded-full bg-blue-500" />
                        </div>
                      ) : idx === loadingStep ? (
                        <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-white/10" />
                      )}
                      <span className="text-sm text-white/70">{step.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-4xl mb-6"
            >
              <div className="p-4 rounded-xl border bg-red-500/[0.05] border-red-500/20 flex items-center gap-3 text-red-400">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            </motion.div>
          )}
        </div>

        {/* Input */}
        <motion.div 
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="border-t border-white/[0.06] bg-black/[0.15] backdrop-blur-sm p-6"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSubmit()
            }}
            className="max-w-4xl mx-auto relative"
          >
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about reserves, development, catastrophe events..."
                  disabled={loading}
                  className="w-full bg-white/[0.04] border border-white/10 rounded-lg px-4 py-3.5 text-sm text-white/90 placeholder-white/40 focus:outline-none focus:border-blue-500/50 disabled:opacity-50"
                />
                
                {/* Search Suggestions */}
                {showSuggestions && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute bottom-full left-0 right-0 mb-2 bg-[#1a2332] border border-white/10 rounded-lg overflow-hidden shadow-xl"
                  >
                    {filteredSuggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => selectSuggestion(suggestion)}
                        className="w-full text-left px-4 py-3 text-sm text-white/80 hover:bg-white/[0.05] transition-colors border-b border-white/[0.05] last:border-b-0"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </motion.div>
                )}
              </div>
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-8 py-3.5 bg-blue-500/[0.12] border border-blue-500/25 rounded-lg text-blue-400/95 text-sm font-medium hover:bg-blue-500/[0.18] hover:border-blue-500/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                Send
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}