"""
Detect and extract specific sections from filings
"""
import re
from typing import Dict, List, Optional

class SectionDetector:
    def __init__(self):
        # SEC filings have standardized section headers
        self.section_patterns = {
            'md_and_a': r"ITEM\s+2\.\s+MANAGEMENT'S\s+DISCUSSION\s+AND\s+ANALYSIS",
            'risk_factors': r"ITEM\s+1A\.\s+RISK\s+FACTORS",
            'financial_statements': r"ITEM\s+1\.\s+FINANCIAL\s+STATEMENTS",
            'reserves': r"(?i)(loss\s+reserves?|reserve\s+adequacy|unpaid\s+losses)",
            'schedule_p': r"(?i)schedule\s+p"
        }
        
        self.section_end_patterns = {
            'md_and_a': r"ITEM\s+3\.\s+QUANTITATIVE\s+AND\s+QUALITATIVE",
            'risk_factors': r"ITEM\s+[0-9]B?\.",
            'financial_statements': r"ITEM\s+2\."
        }
    
    def detect_sections(self, pages: List[Dict]) -> Dict[str, Dict]:
        """
        Detect sections across all pages
        
        Args:
            pages: List of page dicts from TextExtractor
        
        Returns:
            Dict mapping section names to {start_page, end_page, text}
        """
        # Combine all text with page markers
        full_text = ""
        page_positions = []
        
        for page in pages:
            start_pos = len(full_text)
            full_text += page['text'] + "\n"
            end_pos = len(full_text)
            page_positions.append({
                'page_num': page['page_num'],
                'start': start_pos,
                'end': end_pos
            })
        
        sections = {}
        
        # Find each section
        for section_name, start_pattern in self.section_patterns.items():
            start_match = re.search(start_pattern, full_text, re.IGNORECASE)
            
            if start_match:
                start_pos = start_match.start()
                
                # Find end of section
                end_pos = len(full_text)
                if section_name in self.section_end_patterns:
                    end_match = re.search(
                        self.section_end_patterns[section_name],
                        full_text[start_pos:],
                        re.IGNORECASE
                    )
                    if end_match:
                        end_pos = start_pos + end_match.start()
                
                # Find which pages this section spans
                start_page = self._find_page_for_position(start_pos, page_positions)
                end_page = self._find_page_for_position(end_pos, page_positions)
                
                sections[section_name] = {
                    'start_page': start_page,
                    'end_page': end_page,
                    'text': full_text[start_pos:end_pos],
                    'char_count': end_pos - start_pos
                }
        
        return sections
    
    def _find_page_for_position(self, position: int, page_positions: List[Dict]) -> int:
        """Find which page a text position belongs to"""
        for page_info in page_positions:
            if page_info['start'] <= position < page_info['end']:
                return page_info['page_num']
        return page_positions[-1]['page_num']