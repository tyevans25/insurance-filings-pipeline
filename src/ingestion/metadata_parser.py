"""
Extract metadata from filing PDFs
"""
import re
from pathlib import Path
from typing import Dict, Optional
import pdfplumber

class MetadataParser:
    def __init__(self):
        self.filing_type_patterns = {
            '10-K': r'ANNUAL\s+REPORT|FORM\s+10-K',
            '10-Q': r'QUARTERLY\s+REPORT|FORM\s+10-Q'
        }
        self.date_pattern = r'(?:For\s+the\s+(?:quarter|period)\s+ended|As\s+of)\s+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})'
    
    def extract_metadata(self, file_path: str, company_name: str) -> Dict:
        """Extract metadata from PDF"""
        metadata = {
            'company': company_name,
            'filing_type': None,
            'filing_date': None,
            'fiscal_period': None,
            'page_count': 0,
            'file_path': file_path
        }
        
        try:
            # Use pdfplumber instead of PyPDF2 to avoid file locking
            with pdfplumber.open(file_path) as pdf:
                metadata['page_count'] = len(pdf.pages)
                
                # Extract text from first 3 pages
                first_pages_text = ""
                for i in range(min(3, len(pdf.pages))):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        first_pages_text += page_text
                
                # Detect filing type
                for filing_type, pattern in self.filing_type_patterns.items():
                    if re.search(pattern, first_pages_text, re.IGNORECASE):
                        metadata['filing_type'] = filing_type
                        break
                
                # Extract filing date
                date_match = re.search(self.date_pattern, first_pages_text)
                if date_match:
                    metadata['filing_date'] = date_match.group(1)
                
                # Determine fiscal period
                if metadata['filing_type'] == '10-Q':
                    q_match = re.search(r'[Qq]([1-3])', file_path)
                    if q_match:
                        metadata['fiscal_period'] = f"Q{q_match.group(1)}"
                elif metadata['filing_type'] == '10-K':
                    metadata['fiscal_period'] = 'FY'
        
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
        
        return metadata