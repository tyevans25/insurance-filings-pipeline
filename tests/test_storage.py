"""Test database storage"""
import unittest

class TestStorage(unittest.TestCase):
    
    def test_postgres_import(self):
        """Test PostgreSQL client imports"""
        from src.storage.postgres_client import PostgresClient
        self.assertTrue(PostgresClient)
    
    def test_qdrant_import(self):
        """Test QDrant client imports"""
        from src.storage.qdrant_client import QdrantClient
        self.assertTrue(QdrantClient)

if __name__ == '__main__':
    unittest.main()
