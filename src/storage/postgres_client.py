"""
PostgreSQL database client for storing metadata and structured data
"""
import psycopg2
from psycopg2.extras import Json, execute_values
from typing import List, Dict, Optional
import os
import json


class PostgresClient:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'insurance_filings'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres')
        )
        self.conn.autocommit = False
        self._create_tables()
    
    def _create_tables(self):
        """Create database schema"""
        schema = """
        CREATE TABLE IF NOT EXISTS filings (
            filing_id SERIAL PRIMARY KEY,
            company VARCHAR(100) NOT NULL,
            filing_date DATE,
            filing_type VARCHAR(10),
            fiscal_period VARCHAR(10),
            file_path TEXT,
            page_count INTEGER,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB
        );
        
        CREATE TABLE IF NOT EXISTS text_chunks (
            chunk_id VARCHAR(255) PRIMARY KEY,
            filing_id INTEGER REFERENCES filings(filing_id) ON DELETE CASCADE,
            chunk_index INTEGER,
            section_type VARCHAR(50),
            page_num INTEGER,
            text TEXT,
            cleaned_text TEXT,
            char_count INTEGER,
            metadata JSONB
        );
        
        CREATE TABLE IF NOT EXISTS financial_tables (
            table_id SERIAL PRIMARY KEY,
            filing_id INTEGER REFERENCES filings(filing_id) ON DELETE CASCADE,
            table_type VARCHAR(50),
            page_num INTEGER,
            table_data JSONB,
            metadata JSONB
        );
        
        CREATE TABLE IF NOT EXISTS financial_metrics (
            metric_id SERIAL PRIMARY KEY,
            filing_id INTEGER REFERENCES filings(filing_id) ON DELETE CASCADE,
            metric_name VARCHAR(100),
            metric_value NUMERIC,
            period_date DATE,
            line_of_business VARCHAR(100),
            metadata JSONB
        );
        
        CREATE INDEX IF NOT EXISTS idx_filings_company ON filings(company);
        CREATE INDEX IF NOT EXISTS idx_filings_date ON filings(filing_date);
        CREATE INDEX IF NOT EXISTS idx_chunks_filing ON text_chunks(filing_id);
        CREATE INDEX IF NOT EXISTS idx_chunks_section ON text_chunks(section_type);
        CREATE INDEX IF NOT EXISTS idx_metrics_name ON financial_metrics(metric_name);
        CREATE INDEX IF NOT EXISTS idx_metrics_filing ON financial_metrics(filing_id);
        CREATE INDEX IF NOT EXISTS idx_tables_filing ON financial_tables(filing_id);
        """
        
        with self.conn.cursor() as cur:
            cur.execute(schema)
        self.conn.commit()
    
    def insert_filing(self, metadata: Dict) -> int:
        """Insert filing metadata. Returns filing_id"""
        query = """
        INSERT INTO filings (company, filing_date, filing_type, fiscal_period, file_path, page_count, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING filing_id
        """
        
        with self.conn.cursor() as cur:
            cur.execute(query, (
                metadata.get('company'),
                metadata.get('filing_date'),
                metadata.get('filing_type'),
                metadata.get('fiscal_period'),
                metadata.get('file_path'),
                metadata.get('page_count'),
                Json(metadata)
            ))
            filing_id = cur.fetchone()[0]
        
        self.conn.commit()
        return filing_id
    
    def insert_chunks(self, chunks: List[Dict]):
        """Insert text chunks in batch, skip duplicates"""
        query = """
        INSERT INTO text_chunks (chunk_id, filing_id, chunk_index, section_type, page_num, text, cleaned_text, char_count, metadata)
        VALUES %s
        ON CONFLICT (chunk_id) DO NOTHING
        """
        
        values = [
            (
                chunk['chunk_id'],
                chunk.get('filing_id'),
                chunk.get('chunk_index'),
                chunk.get('section_type'),
                chunk.get('page_num'),
                chunk.get('text'),
                chunk.get('cleaned_text'),
                len(chunk.get('text', '')),
                Json(chunk.get('metadata', {}))
            )
            for chunk in chunks
        ]
        
        with self.conn.cursor() as cur:
            execute_values(cur, query, values)
        
        self.conn.commit()
    
    def insert_table(self, table_data: dict) -> int:
        """Insert financial table. Returns table_id"""
        query = """
        INSERT INTO financial_tables (filing_id, table_type, page_num, table_data, metadata)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING table_id
        """
        
        with self.conn.cursor() as cur:
            cur.execute(query, (
                table_data['filing_id'],
                table_data.get('table_type', 'unknown'),
                table_data.get('page_num', 0),
                Json(table_data.get('table_data', {})),
                Json(table_data.get('metadata', {}))
            ))
            table_id = cur.fetchone()[0]
        
        self.conn.commit()
        return table_id
    
    def insert_financial_table(self, filing_id: int, table: Dict):
        """Insert financial table data (legacy method)"""
        query = """
        INSERT INTO financial_tables (filing_id, table_type, page_num, table_data, metadata)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        with self.conn.cursor() as cur:
            cur.execute(query, (
                filing_id,
                table.get('table_type'),
                table.get('page_num'),
                Json(table.get('data', [])),
                Json(table.get('extracted_metrics', {}))
            ))
        
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.conn.close()