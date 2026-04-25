'use client'

interface FormattedTextProps {
  content: string
}

export default function FormattedText({ content }: FormattedTextProps) {
  const lines = content.split('\n')
  
  const renderLine = (line: string, index: number) => {
    // Skip empty lines but add spacing
    if (line.trim() === '') {
      return <div key={index} className="h-2" />
    }
    
    // H2 headers (## Text)
    if (line.startsWith('## ')) {
      return (
        <h2 key={index} className="text-base font-bold text-blue-300 mt-6 mb-3 first:mt-0">
          {line.replace('## ', '')}
        </h2>
      )
    }
    
    // H3 headers (### Text)
    if (line.startsWith('### ')) {
      return (
        <h3 key={index} className="text-sm font-semibold text-emerald-300 mt-4 mb-2">
          {line.replace('### ', '')}
        </h3>
      )
    }
    
    // List items (starting with * or -)
    if (line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
      const text = line.trim().substring(2)
      return (
        <div key={index} className="flex gap-3 my-1.5 ml-4">
          <span className="text-blue-400 mt-1.5 flex-shrink-0">•</span>
          <span className="text-white/85 leading-relaxed">{renderInlineFormatting(text)}</span>
        </div>
      )
    }
    
    // Regular paragraphs
    return (
      <p key={index} className="text-white/85 my-3 leading-[1.7]">
        {renderInlineFormatting(line)}
      </p>
    )
  }
  
  const renderInlineFormatting = (text: string) => {
    // Split by ** for bold text and * for italic text
    // Match **bold** first, then *italic*
    const parts = text.split(/(\*\*.*?\*\*|\*.*?\*)/)
    
    return parts.map((part, i) => {
      // Bold text (**text**)
      if (part.startsWith('**') && part.endsWith('**')) {
        const boldText = part.slice(2, -2)
        return (
          <strong key={i} className="font-bold text-white bg-white/5 px-1 py-0.5 rounded">
            {boldText}
          </strong>
        )
      }
      // Italic text (*text*)
      if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
        const italicText = part.slice(1, -1)
        return (
          <em key={i} className="italic text-white/60 text-xs">
            {italicText}
          </em>
        )
      }
      return <span key={i}>{part}</span>
    })
  }
  
  return (
    <div className="text-sm">
      {lines.map((line, index) => renderLine(line, index))}
    </div>
  )
}