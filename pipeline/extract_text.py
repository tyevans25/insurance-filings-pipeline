from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple
from io import BytesIO
import re
from datetime import datetime

import fitz  # PyMuPDF


def parse_pdf_date(pdf_date: str) -> str:
    """
    Convert PyMuPDF date format to ISO format
    Input: "D:20260307211245+00'00'"
    Output: "2026-03-07T21:12:45+00:00"
    """
    if not pdf_date or not pdf_date.startswith('D:'):
        return None
    
    try:
        # Extract date parts: D:YYYYMMDDHHmmSS
        date_str = pdf_date[2:16]  # Get YYYYMMDDHHmmSS
        dt = datetime.strptime(date_str, '%Y%m%d%H%M%S')
        return dt.isoformat()
    except:
        return None


def extract_text_and_metadata(path: Path) -> Tuple[str, Dict]:
    """
    Extract text + PDF metadata using PyMuPDF.
    """
    ext = path.suffix.lower()

    if ext == ".txt":
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta = {
            "title": path.name,
            "author": None,
            "created_date": None,
            "page_count": None,
        }
        return text, meta

    if ext == ".pdf":
        # Read into memory
        with open(path, 'rb') as f:
            pdf_bytes = BytesIO(f.read())
        
        # Open PDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        meta_raw = doc.metadata or {}

        # Extract text
        parts = []
        for page in doc:
            parts.append(page.get_text("text"))

        text = "\n".join(parts).strip()

        # Parse creation date
        created_date = parse_pdf_date(meta_raw.get("creationDate"))

        meta = {
            "title": meta_raw.get("title") or path.name,
            "author": meta_raw.get("author"),
            "created_date": created_date,  # Now in proper format
            "page_count": doc.page_count,
        }
        doc.close()
        return text, meta

    raise ValueError(f"Unsupported file type for extraction: {ext}")