"""Data validation utilities"""

def validate_chunk(chunk: dict) -> bool:
    """Validate chunk has required fields"""
    required = ['chunk_id', 'filing_id', 'text']
    return all(k in chunk for k in required)

def validate_filing(filing: dict) -> bool:
    """Validate filing has required fields"""
    required = ['company', 'filing_type']
    return all(k in filing for k in required)
