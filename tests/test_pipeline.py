"""Pipeline integration tests"""
import unittest
from pathlib import Path

class TestPipeline(unittest.TestCase):
    
    def test_imports(self):
        """Test all pipeline modules import"""
        from pipeline import ingest, extract_text, chunk_text, embed
        self.assertTrue(True)
    
    def test_chunk_validation(self):
        """Test chunk has required fields"""
        from src.utils.validators import validate_chunk
        chunk = {'chunk_id': '123', 'filing_id': 1, 'text': 'test'}
        self.assertTrue(validate_chunk(chunk))
    
    def test_filing_validation(self):
        """Test filing validation"""
        from src.utils.validators import validate_filing
        filing = {'company': 'AIG', 'filing_type': '10-K'}
        self.assertTrue(validate_filing(filing))

if __name__ == '__main__':
    unittest.main()
