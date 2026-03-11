import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.postgres_client import PostgresClient
from src.storage.qdrant_client import QdrantClient
from pipeline.embed import embed_texts

print("🔄 Re-syncing QDrant from PostgreSQL...")

postgres = PostgresClient()
qdrant = QdrantClient()

# Recreate collection
try:
    qdrant.client.delete_collection("insurance_filings")
    print("🗑️  Deleted old collection")
except:
    pass

qdrant._create_collection()
print("✅ Created fresh collection")

# Get all chunks from PostgreSQL
with postgres.conn.cursor() as cur:
    cur.execute("""
        SELECT 
            c.chunk_id, c.filing_id, c.text, c.chunk_index,
            c.metadata->>'token_count' as token_count,
            f.company, f.filing_date, f.filing_type
        FROM text_chunks c
        JOIN filings f ON c.filing_id = f.filing_id
        ORDER BY c.filing_id, c.chunk_index
    """)
    chunks = cur.fetchall()

print(f"📊 Found {len(chunks)} chunks in PostgreSQL")

# Process in batches
batch_size = 100
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    print(f"Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}...")
    
    # Generate embeddings
    texts = [c[2] for c in batch]  # c[2] is text
    vectors = embed_texts(texts)
    
    # Prepare for QDrant
    qdrant_chunks = []
    for (chunk_id, filing_id, text, chunk_index, token_count, company, filing_date, filing_type), vector in zip(batch, vectors):
        qdrant_chunks.append({
            'chunk_id': chunk_id,
            'filing_id': filing_id,
            'text': text,
            'embedding': vector,
            'metadata': {
                'company': company,
                'filing_date': str(filing_date) if filing_date else None,
                'section_type': 'document',
                'chunk_index': chunk_index,
                'token_count': int(token_count) if token_count else 0,
                'filing_type': filing_type
            }
        })
    
    # Insert
    qdrant.insert_embeddings(qdrant_chunks)

print(f"✅ Done! Inserted {len(chunks)} embeddings into QDrant")

# Verify
from qdrant_client.models import Filter
result = qdrant.client.count("insurance_filings")
print(f"🔍 QDrant now has {result.count} points")
