"""
Main pipeline orchestrator
"""
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Fix Python path
sys.path.insert(0, '/app/src')

from storage.postgres_client import PostgresClient
from storage.qdrant_client import QdrantClient
from ingestion.file_scanner import FileScanner
from ingestion.metadata_parser import MetadataParser
from extraction.text_extractor import TextExtractor
from extraction.table_extractor import TableExtractor
from extraction.section_detector import SectionDetector
from extraction.chunker import TextChunker
from processing.text_cleaner import TextCleaner
from processing.embedder import TextEmbedder
from processing.financial_parser import FinancialParser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InsuranceFilingsPipeline:
    def __init__(self, input_dir: str):
        self.input_dir = input_dir
        
        # Initialize components
        logger.info("Initializing pipeline components...")
        self.file_scanner = FileScanner(input_dir)
        self.metadata_parser = MetadataParser()
        self.text_extractor = TextExtractor()
        self.table_extractor = TableExtractor()
        self.section_detector = SectionDetector()
        self.chunker = TextChunker(chunk_size=1000, overlap=200)
        self.text_cleaner = TextCleaner(remove_stopwords=True)
        self.embedder = TextEmbedder(model_name='all-MiniLM-L6-v2')
        self.financial_parser = FinancialParser()
        
        # Initialize storage
        self.postgres = PostgresClient()
        self.qdrant = QdrantClient()
        
        logger.info("Pipeline initialized successfully")
    
    def process_filing(self, file_info: dict) -> dict:
        """
        Process a single filing through the complete pipeline
        
        Returns:
            Dict with processing statistics
        """
        file_path = file_info['path']
        company = file_info['company']
        
        logger.info(f"Processing: {file_path}")
        
        stats = {
            'file_path': file_path,
            'company': company,
            'success': False,
            'chunks_created': 0,
            'tables_extracted': 0,
            'embeddings_generated': 0
        }
        
        try:
            # Step 1: Extract metadata
            logger.info("Extracting metadata...")
            metadata = self.metadata_parser.extract_metadata(file_path, company)
            
            # Step 2: Insert filing record
            filing_id = self.postgres.insert_filing(metadata)
            logger.info(f"Created filing record: {filing_id}")
            
            # Step 3: Extract text
            logger.info("Extracting text...")
            pages = self.text_extractor.extract_text(file_path)
            
            # Step 4: Detect sections
            logger.info("Detecting sections...")
            sections = self.section_detector.detect_sections(pages)
            
            # Step 5: Extract tables
            logger.info("Extracting tables...")
            tables = self.table_extractor.extract_tables(file_path)
            stats['tables_extracted'] = len(tables)
            
            # Parse financial tables
            for table in tables:
                if table['table_type'] == 'balance_sheet':
                    metrics = self.financial_parser.parse_balance_sheet(table['data'])
                    table['extracted_metrics'] = metrics
                
                self.postgres.insert_financial_table(filing_id, table)
            
            # Step 6: Chunk text from each section
            logger.info("Chunking text...")
            all_chunks = []
            
            for section_name, section_data in sections.items():
                chunk_metadata = {
                    'filing_id': filing_id,
                    'company': company,
                    'filing_date': metadata.get('filing_date'),
                    'section_type': section_name,
                    'page_num': section_data['start_page'],
                    'file_path': file_path
                }
                
                chunks = self.chunker.chunk_text(
                    section_data['text'],
                    chunk_metadata
                )
                all_chunks.extend(chunks)
            
            stats['chunks_created'] = len(all_chunks)
            
            # Step 7: Clean and embed chunks
            logger.info(f"Processing {len(all_chunks)} chunks...")
            
            for chunk in all_chunks:
                # Clean text
                chunk['cleaned_text'] = self.text_cleaner.clean_text(chunk['text'])
            
            # Generate embeddings in batch
            logger.info("Generating embeddings...")
            texts_to_embed = [chunk['cleaned_text'] for chunk in all_chunks]
            embeddings = self.embedder.embed_texts(texts_to_embed)
            
            for chunk, embedding in zip(all_chunks, embeddings):
                chunk['embedding'] = embedding.tolist()
            
            stats['embeddings_generated'] = len(embeddings)
            
            # Step 8: Store chunks and embeddings
            logger.info("Storing chunks in PostgreSQL...")
            self.postgres.insert_chunks(all_chunks)
            
            logger.info("Storing embeddings in QDrant...")
            self.qdrant.insert_embeddings(all_chunks)
            
            stats['success'] = True
            logger.info(f"Successfully processed {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)
            stats['error'] = str(e)
        
        return stats
    
    def run(self):
        """
        Run the complete pipeline on all files
        """
        logger.info("Starting insurance filings pipeline...")
        
        # Scan for files
        logger.info(f"Scanning input directory: {self.input_dir}")
        files = self.file_scanner.scan_files()
        logger.info(f"Found {len(files)} PDF files")
        
        if not files:
            logger.warning("No files found to process")
            return
        
        # Process each file
        results = []
        for file_info in files:
            stats = self.process_filing(file_info)
            results.append(stats)
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        total_chunks = sum(r['chunks_created'] for r in results)
        total_tables = sum(r['tables_extracted'] for r in results)
        
        logger.info("=" * 80)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total files processed: {len(results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {len(results) - successful}")
        logger.info(f"Total chunks created: {total_chunks}")
        logger.info(f"Total tables extracted: {total_tables}")
        logger.info("=" * 80)
        
        # Close connections
        self.postgres.close()

def main():
    """Main entry point"""
    input_dir = os.getenv('INPUT_DIR', '/data/raw')
    
    pipeline = InsuranceFilingsPipeline(input_dir)
    pipeline.run()

if __name__ == '__main__':
    main()