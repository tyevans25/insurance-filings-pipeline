"""
Extract and parse financial tables from insurance filings
"""
import re
from typing import List, Dict
import fitz  # PyMuPDF


def detect_table_pages(doc: fitz.Document) -> List[int]:
    """Identify pages likely to contain tables"""
    table_pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # More lenient table detection
        has_dollar_amounts = len(re.findall(r'\$\s*[\d,]+', text)) > 5
        has_percentages = len(re.findall(r'\d+\.?\d*\s*%', text)) > 3
        has_years = len(re.findall(r'\b20\d{2}\b', text)) > 2
        has_numbers = len(re.findall(r'\b\d{1,3}(,\d{3})+\b', text)) > 5  # Formatted numbers
        
        # Table structure indicators
        has_alignment = len(re.findall(r'\s{10,}', text)) > 5  # Multiple spacing
        has_lines = '___' in text or '---' in text  # Separator lines
        
        is_table_page = (has_dollar_amounts or has_percentages) and (has_years or has_numbers)
        
        if is_table_page:
            table_pages.append(page_num)
    
    return table_pages


def extract_reserve_tables(text: str, page_num: int) -> List[Dict]:
    """Extract loss reserve tables from text"""
    tables = []
    
    # Broader keyword matching
    reserve_keywords = [
        'reserve',
        'unpaid',
        'liability',
        'loss',
        'ibnr',
        'claim',
        'incurred',
        'reported'
    ]
    
    lines = text.split('\n')
    
    # Look for lines with both keywords and dollar amounts
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Check if line has reserve keywords AND dollar amounts
        has_keyword = any(keyword in line_lower for keyword in reserve_keywords)
        has_amounts = len(re.findall(r'\$\s*[\d,]+', line)) >= 2
        
        if has_keyword and has_amounts:
            # Extract the table section (next 10 lines)
            table_section = '\n'.join(lines[i:min(i+10, len(lines))])
            
            # Extract years
            years = re.findall(r'\b(20\d{2})\b', table_section)
            
            # Extract all dollar amounts
            amounts = re.findall(r'\$\s*([\d,]+)', table_section)
            
            if len(amounts) >= 2:
                tables.append({
                    'title': line.strip(),
                    'page_num': page_num,
                    'years': list(set(years)),  # Unique years
                    'values': amounts,
                    'raw_text': table_section[:500]  # Store sample
                })
    
    return tables


def extract_tables_from_pdf(pdf_path: str) -> List[Dict]:
    """Extract all financial tables from a PDF"""
    doc = fitz.open(pdf_path)
    all_tables = []
    
    # Detect potential table pages
    table_pages = detect_table_pages(doc)
    
    print(f"  🔍 Detected {len(table_pages)} potential table pages")
    
    for page_num in table_pages:
        page = doc[page_num]
        text = page.get_text()
        
        # Extract tables from this page
        tables = extract_reserve_tables(text, page_num + 1)
        
        for table in tables:
            table['source'] = 'pdf_extraction'
            all_tables.append(table)
    
    doc.close()
    
    # Deduplicate similar tables
    unique_tables = []
    seen_titles = set()
    
    for table in all_tables:
        title_key = table['title'][:50].lower()  # First 50 chars
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_tables.append(table)
    
    return unique_tables