"""
Scan input directory for PDF files and validate them
"""
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from io import BytesIO
import pdfplumber

class FileScanner:
    def __init__(self, input_directory: str):
        self.input_directory = Path(input_directory)
    
    def scan_files(self) -> List[Dict]:
        """
        Scan input directory for PDFs and extract basic metadata
        
        Returns:
            List of dicts with file info: path, company, year, size
        """
        files = []
        
        # Expected structure: /data/raw/{company}/{year}/{filename}.pdf
        for company_dir in self.input_directory.iterdir():
            if not company_dir.is_dir():
                continue
            
            company_name = company_dir.name
            
            for year_dir in company_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                
                year = year_dir.name
                
                for file_path in year_dir.glob("*.pdf"):
                    if self._validate_pdf(file_path):
                        files.append({
                            'path': str(file_path),
                            'company': company_name,
                            'year': year,
                            'filename': file_path.name,
                            'size_mb': file_path.stat().st_size / (1024 * 1024),
                            'discovered_at': datetime.now().isoformat()
                        })
        
        return files
    
    def _validate_pdf(self, file_path: Path) -> bool:
        """
        Validate that file is a readable PDF
        Load into memory first to avoid Docker/Mac file locking issues
        """
        try:
            # Read entire file into memory first
            with open(file_path, 'rb') as f:
                pdf_bytes = BytesIO(f.read())
            
            # Open from memory instead of file
            with pdfplumber.open(pdf_bytes) as pdf:
                if len(pdf.pages) > 0:
                    # Try to extract text from first page
                    _ = pdf.pages[0].extract_text()
                    return True
        except Exception as e:
            print(f"Invalid PDF {file_path}: {e}")
            return False
        
        return False