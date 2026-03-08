"""
Chunk text for embedding
"""
from typing import List, Dict
import re
import hashlib

class TextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict
    ) -> List[Dict]:
        """
        Chunk text into overlapping segments
        
        Args:
            text: Full text to chunk
            metadata: Metadata to attach to each chunk
        
        Returns:
            List of chunk dicts with text and metadata
        """
        # Clean text
        text = self._clean_text(text)
        
        if not text or len(text) < 50:
            print(f"⚠️  Skipping empty or very short text")
            return []
        
        print(f"📊 Chunking {len(text):,} characters (target: {self.chunk_size} chars/chunk)...")
        
        # Create unique prefix from file path
        file_path = metadata.get('file_path', 'unknown')
        path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        
        chunks = []
        start = 0
        chunk_idx = 0
        max_chunks = 2000  # Safety limit to prevent infinite loops
        
        while start < len(text) and chunk_idx < max_chunks:
            # Find end of chunk (try to break at sentence boundary)
            end = min(start + self.chunk_size, len(text))
            
            if end < len(text):
                # Look for sentence boundary
                boundary = self._find_sentence_boundary(text, start, end)
                if boundary > start:
                    end = boundary
            
            chunk_text = text[start:end].strip()
            
            # Only keep substantial chunks
            if len(chunk_text) > 50:
                # Use file hash + index for truly unique IDs
                chunk_id = f"{path_hash}_{chunk_idx}"
                
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'start_char': start,
                    'end_char': end,
                    'chunk_index': chunk_idx,
                    **metadata
                })
                chunk_idx += 1
                
                # Progress logging every 100 chunks
                if chunk_idx % 100 == 0:
                    print(f"  ✅ Created {chunk_idx} chunks so far...")
            
            # Move to next chunk with overlap
            next_start = end - self.overlap
            
            # Prevent infinite loop - ensure we're making progress
            if next_start <= start:
                next_start = end
            
            start = next_start
            
            # Safety check
            if start >= len(text):
                break
        
        if chunk_idx >= max_chunks:
            print(f"⚠️  WARNING: Hit max chunk limit ({max_chunks})")
        
        print(f"✅ Created {len(chunks)} chunks total")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace and special characters"""
        if not text:
            return ""
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers and headers/footers
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text)
        return text.strip()
    
    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """
        Find nearest sentence boundary after end position
        
        Args:
            text: Full text
            start: Start position of current chunk
            end: Target end position
        
        Returns:
            Adjusted end position at sentence boundary
        """
        # Look for period, question mark, or exclamation followed by space
        # Search in a 200-char window around the target end
        search_start = max(start, end - 100)
        search_end = min(len(text), end + 100)
        search_text = text[search_start:search_end]
        
        boundary_pattern = r'[.!?]\s+'
        matches = list(re.finditer(boundary_pattern, search_text))
        
        if matches:
            # Find closest match to our target position
            target_offset = end - search_start
            closest = min(
                matches,
                key=lambda m: abs(m.end() - target_offset)
            )
            return search_start + closest.end()
        
        # No sentence boundary found, just use the target position
        return end