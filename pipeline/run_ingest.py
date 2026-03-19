print("=" * 80)
print("SCRIPT STARTING - BEFORE ANY IMPORTS")
print("=" * 80)

import hashlib
print("✓ hashlib")
import json
print("✓ json")
import sys
print("✓ sys")
from pathlib import Path
print("✓ Path")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
print("✓ Added src to path")

print("\nImporting pipeline modules...")
from pipeline.ingest import ingest
print("✓ ingest")
from pipeline.extract_text import extract_text_and_metadata
print("✓ extract_text")
from pipeline.chunk_text import clean_and_tokenize, chunk_tokens
print("✓ chunk_text")
from pipeline.embed import embed_texts
print("✓ embed")
from pipeline.section_filter import filter_chunks_for_narrative
print("✓ section_filter")
from pipeline.table_extractor import extract_tables_from_pdf
print("✓ table_extractor")

print("\nImporting database clients...")
from src.storage.postgres_client import PostgresClient
print("✓ PostgresClient")
from src.storage.qdrant_client import QdrantClient
print("✓ QdrantClient")

print("\n" + "=" * 80)
print("ALL IMPORTS COMPLETE - STARTING MAIN()")
print("=" * 80 + "\n")

COLLECTION_NAME = "insurance_filings"


def stable_chunk_id(doc_id: str, chunk_index: int) -> str:
    """Generate unique chunk ID"""
    return hashlib.md5(f"{doc_id}_{chunk_index}".encode()).hexdigest()[:16]


def extract_company_from_filename(filepath: str) -> str:
    """Extract company name from filename"""
    filename = Path(filepath).name.lower()
    
    company_map = {
        'aig': 'AIG',
        'travelers': 'Travelers',
        'trv': 'Travelers',
        'chubb': 'Chubb',
        'cb': 'Chubb',
        'progressive': 'Progressive',
        'pgr': 'Progressive',
        'allstate': 'Allstate',
        'all': 'Allstate',
        'geico': 'Geico',
        'state farm': 'State Farm',
        'liberty mutual': 'Liberty Mutual',
    }
    
    for key, company in company_map.items():
        if key in filename:
            return company
    
    parts = filename.replace('.pdf', '').replace('.txt', '').split('_')
    if parts:
        return parts[0].capitalize()
    
    return 'Unknown'


def extract_filing_info(filename: str) -> dict:
    """Extract filing type and fiscal period from filename"""
    filename_lower = filename.lower()
    
    if '10-k' in filename_lower or '10k' in filename_lower:
        filing_type = '10-K'
        fiscal_period = 'FY'
    elif '10-q' in filename_lower or '10q' in filename_lower:
        filing_type = '10-Q'
        if 'q1' in filename_lower:
            fiscal_period = 'Q1'
        elif 'q2' in filename_lower:
            fiscal_period = 'Q2'
        elif 'q3' in filename_lower:
            fiscal_period = 'Q3'
        elif 'q4' in filename_lower:
            fiscal_period = 'Q4'
        else:
            fiscal_period = 'Q3'
    else:
        filing_type = 'Unknown'
        fiscal_period = 'Unknown'
    
    return {
        'filing_type': filing_type,
        'fiscal_period': fiscal_period
    }


def main():
    input_dir = Path("/data/input")
    output_dir = Path("/data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📂 Scanning directory: {input_dir}")
    jobs = ingest(input_dir)
    print(f"\n✅ Ingestion complete: {len(jobs)} files found\n")

    if not jobs:
        print("⚠️  No files found! Check that PDFs/TXT files are in /data/input/")
        return

    print("🔌 Connecting to databases...")
    postgres = PostgresClient()
    qdrant = QdrantClient()
    print("✅ Database connections established\n")
    
    collection_ready = False
    total_chunks = 0
    total_narrative_chunks = 0
    total_embeddings = 0
    total_tables = 0

    for idx, job in enumerate(jobs, 1):
        path = Path(job.filepath)
        print(f"\n{'='*80}")
        print(f"📄 File {idx}/{len(jobs)}: {job.filename}")
        print(f"{'='*80}")

        # 1) Extract text + metadata
        try:
            raw_text, meta = extract_text_and_metadata(path)
            print(f"✅ Extracted {len(raw_text):,} characters")
            print(f"📋 Metadata: title={meta.get('title')}, author={meta.get('author')}, pages={meta.get('page_count')}")
        except Exception as e:
            print(f"❌ Failed to extract text: {e}")
            continue

        # 2) Extract company and filing info
        company = extract_company_from_filename(job.filepath)
        filing_info = extract_filing_info(job.filename)
        print(f"🏢 Company: {company}")
        print(f"📊 Filing: {filing_info['filing_type']} ({filing_info['fiscal_period']})")

        # 3) Insert filing into PostgreSQL
        filing_data = {
            'company': company,
            'filing_date': meta.get('created_date'),
            'filing_type': filing_info['filing_type'],
            'fiscal_period': filing_info['fiscal_period'],
            'file_path': job.filepath,
            'page_count': meta.get('page_count', 0),
            'metadata': {
                'title': meta.get('title'),
                'author': meta.get('author'),
                'doc_id': job.doc_id,
                'sha256': job.sha256,
                'file_size_bytes': job.file_size_bytes,
                'mime_type': job.mime_type
            }
        }
        
        try:
            filing_id = postgres.insert_filing(filing_data)
            print(f"💾 PostgreSQL: Inserted filing (id={filing_id})")
        except Exception as e:
            print(f"❌ Failed to insert filing: {e}")
            continue

        # 4) Extract financial tables (only for PDFs)
        if path.suffix.lower() == '.pdf':
            try:
                tables = extract_tables_from_pdf(str(path))
                print(f"📊 Extracted {len(tables)} financial tables")
                
                for table in tables:
                    table_data = {
                        'filing_id': filing_id,
                        'table_type': 'loss_reserves',
                        'page_num': table.get('page_num', 0),
                        'table_data': table,
                        'metadata': {
                            'title': table.get('title', ''),
                            'years': table.get('years', []),
                            'company': company,
                            'filing_type': filing_info['filing_type']
                        }
                    }
                    try:
                        postgres.insert_table(table_data)
                        total_tables += 1
                    except Exception as e:
                        print(f"⚠️  Failed to insert table: {e}")
                
                if tables:
                    print(f"💾 PostgreSQL: Inserted {len(tables)} tables")
            except Exception as e:
                print(f"⚠️  Table extraction skipped: {e}")

        # 5) Clean + tokenize
        tokens = clean_and_tokenize(raw_text)
        print(f"🔤 Tokens after cleaning: {len(tokens):,}")

        if len(tokens) < 10:
            print("⚠️  Too few tokens, skipping file")
            continue

        # 6) Chunk
        chunks = chunk_tokens(tokens, chunk_size=200, overlap=50)
        print(f"📦 Created {len(chunks)} total chunks")

        if not chunks:
            print("⚠️  No chunks created, skipping")
            continue

        # 7) Filter for narrative content only
        narrative_indices = filter_chunks_for_narrative(chunks)
        filtered_chunks = [chunks[i] for i in narrative_indices]
        print(f"📝 Kept {len(filtered_chunks)} narrative chunks (filtered out {len(chunks) - len(filtered_chunks)} table/numeric chunks)")

        if not filtered_chunks:
            print("⚠️  No narrative chunks after filtering, skipping")
            continue

        chunks = filtered_chunks

        # 8) Prepare chunks for PostgreSQL
        pg_chunks = []
        for chunk in chunks:
            chunk_id = stable_chunk_id(job.doc_id, chunk.chunk_index)
            pg_chunks.append({
                'chunk_id': chunk_id,
                'filing_id': filing_id,
                'chunk_index': chunk.chunk_index,
                'section_type': 'narrative',
                'page_num': 1,
                'text': chunk.chunk_text,
                'cleaned_text': chunk.chunk_text,
                'char_count': len(chunk.chunk_text),
                'metadata': {
                    'token_count': chunk.token_count,
                    'company': company,
                    'filing_date': meta.get('created_date'),
                    'filing_type': filing_info['filing_type'],
                    'is_narrative': True
                }
            })

        try:
            postgres.insert_chunks(pg_chunks)
            print(f"💾 PostgreSQL: Inserted {len(pg_chunks)} chunks")
            total_chunks += len(pg_chunks)
            total_narrative_chunks += len(pg_chunks)
        except Exception as e:
            print(f"❌ Failed to insert chunks: {e}")
            continue

        # 9) Generate embeddings
        print(f"🧠 Generating embeddings...")
        try:
            chunk_texts = [c.chunk_text for c in chunks]
            vectors = embed_texts(chunk_texts)
            print(f"✅ Generated {len(vectors)} embeddings")
        except Exception as e:
            print(f"❌ Failed to generate embeddings: {e}")
            continue

        # 10) Ensure QDrant collection exists
        if not collection_ready:
            try:
                qdrant._create_collection()
                collection_ready = True
                print(f"✅ QDrant: Collection ready ({COLLECTION_NAME})")
            except Exception as e:
                print(f"❌ Failed to create QDrant collection: {e}")
                continue

        # 11) Prepare chunks for QDrant
        qdrant_chunks = []
        for chunk, vector in zip(chunks, vectors):
            chunk_id = stable_chunk_id(job.doc_id, chunk.chunk_index)
            qdrant_chunks.append({
                'chunk_id': chunk_id,
                'filing_id': filing_id,
                'text': chunk.chunk_text,
                'embedding': vector,
                'metadata': {
                    'company': company,
                    'filing_date': meta.get('created_date'),
                    'section_type': 'narrative',
                    'chunk_index': chunk.chunk_index,
                    'token_count': chunk.token_count,
                    'filename': job.filename,
                    'filing_type': filing_info['filing_type'],
                    'is_narrative': True
                }
            })

        try:
            qdrant.insert_embeddings(qdrant_chunks)
            print(f"💾 QDrant: Inserted {len(qdrant_chunks)} embeddings")
            total_embeddings += len(qdrant_chunks)
        except Exception as e:
            print(f"❌ Failed to insert into QDrant: {e}")
            continue

    # Final summary
    print(f"\n{'='*80}")
    print("🎉 PIPELINE COMPLETE!")
    print(f"{'='*80}")
    print(f"📊 Summary:")
    print(f"   • Files processed: {len(jobs)}")
    print(f"   • Total narrative chunks: {total_narrative_chunks:,}")
    print(f"   • Total tables extracted: {total_tables:,}")
    print(f"   • Total embeddings: {total_embeddings:,}")
    print(f"   • PostgreSQL: ✅ {total_chunks:,} chunks, {total_tables:,} tables")
    print(f"   • QDrant: ✅ {total_embeddings:,} vectors")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()