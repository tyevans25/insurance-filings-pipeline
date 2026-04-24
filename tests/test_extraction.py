"""Test text extraction"""
import unittest
from pathlib import Path

class TestExtraction(unittest.TestCase):
    
    def test_extract_import(self):
        """Test extract_text module imports"""
        from pipeline.extract_text import extract_text_and_metadata
        self.assertTrue(callable(extract_text_and_metadata))

if __name__ == '__main__':
    unittest.main()
