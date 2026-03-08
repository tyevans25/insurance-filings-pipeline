"""
Extract text from PDFs using pdfplumber
"""
import pdfplumber
from typing import List, Dict
import re

class TextExtractor:
    def __init__(self):
        self.page_text = []
    
    def extract_text(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF page by page
        
        Returns:
            List of dicts: [{'page_num': 1, 'text': '...', 'has_tables': bool}, ...]
        """
        pages = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text
                text = page.extract_text()
                
                # Check if page has tables
                tables = page.extract_tables()
                has_tables = len(tables) > 0 if tables else False
                
                pages.append({
                    'page_num': page_num,
                    'text': text if text else "",
                    'has_tables': has_tables,
                    'char_count': len(text) if text else 0
                })
        
        return pages