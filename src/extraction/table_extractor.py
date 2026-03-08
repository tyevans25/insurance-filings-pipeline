"""
Extract tables from PDFs
"""
import pdfplumber
import pandas as pd
from typing import List, Dict, Optional
import re

class TableExtractor:
    def __init__(self):
        self.financial_table_keywords = [
            'balance sheet', 'assets', 'liabilities',
            'income statement', 'revenue', 'expenses',
            'schedule p', 'loss development', 'reserves'
        ]
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """
        Extract all tables from PDF
        
        Returns:
            List of dicts with table data and metadata
        """
        all_tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text().lower()
                
                # Extract tables from this page
                tables = page.extract_tables(table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                })
                
                if not tables:
                    continue
                
                for table_idx, table in enumerate(tables):
                    # Identify table type based on surrounding text
                    table_type = self._identify_table_type(page_text)
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0] if table[0] else None)
                    
                    all_tables.append({
                        'page_num': page_num,
                        'table_idx': table_idx,
                        'table_type': table_type,
                        'data': df.to_dict('records'),
                        'row_count': len(df),
                        'col_count': len(df.columns) if df.columns is not None else 0
                    })
        
        return all_tables
    
    def _identify_table_type(self, page_text: str) -> str:
        """
        Identify type of financial table based on keywords
        """
        if 'balance sheet' in page_text:
            return 'balance_sheet'
        elif 'income statement' in page_text or 'statement of income' in page_text:
            return 'income_statement'
        elif 'schedule p' in page_text or 'loss development' in page_text:
            return 'schedule_p'
        elif 'reserve' in page_text:
            return 'reserves'
        else:
            return 'unknown'