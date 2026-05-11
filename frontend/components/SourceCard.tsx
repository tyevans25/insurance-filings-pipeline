'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import type { Source } from '@/app/api/orchestrator'

interface SourceCardProps {
  source: Source
  index: number
}

export default function SourceCard({ source, index }: SourceCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay: index * 0.05 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="relative bg-gradient-to-r from-white/[0.02] to-black/[0.05] border-l-2 border-blue-500 rounded-lg p-4 hover:from-white/[0.04] hover:to-black/[0.08] transition-all cursor-pointer"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="text-sm text-white/85 font-medium">
          {source.type === 'narrative' ? 'Document' : 'Table'} {index}: {source.company}
        </div>
        {source.relevance_score && (
          <div className="px-2 py-0.5 bg-emerald-500/[0.12] border border-emerald-500/25 rounded text-[10px] font-medium text-emerald-400">
            {source.relevance_score.toFixed(3)}
          </div>
        )}
      </div>

      <div className="text-xs text-white/40 mb-3">
        {source.filing_type} • {source.filing_date} • Page {source.page_num}
        {source.section_type && ` • ${source.section_type}`}
        {source.table_type && ` • ${source.table_type}`}
      </div>

      {source.excerpt && (
        <div className="bg-black/30 border-l border-white/[0.08] pl-3 py-2 text-xs text-white/60 leading-relaxed">
          {source.excerpt.length > 150 ? `${source.excerpt.substring(0, 150)}...` : source.excerpt}
        </div>
      )}

      {/* Hover Preview Tooltip */}
      {isHovered && source.excerpt && source.excerpt.length > 150 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute z-10 left-0 right-0 top-full mt-2 bg-[#1a2332] border border-white/10 rounded-lg p-4 shadow-2xl"
        >
          <div className="text-xs text-white/70 leading-relaxed max-h-48 overflow-y-auto">
            {source.excerpt}
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}