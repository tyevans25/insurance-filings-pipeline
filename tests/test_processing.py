"""Test text processing"""
import unittest

class TestProcessing(unittest.TestCase):
    
    def test_chunk_import(self):
        """Test chunk module imports"""
        from pipeline.chunk_text import chunk_tokens
        self.assertTrue(callable(chunk_tokens))
    
    def test_filter_import(self):
        """Test filter module imports"""
        from pipeline.section_filter import filter_chunks_for_narrative
        self.assertTrue(callable(filter_chunks_for_narrative))

if __name__ == '__main__':
    unittest.main()
