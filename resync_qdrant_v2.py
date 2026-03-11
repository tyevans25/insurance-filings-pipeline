import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.postgres_client import PostgresClient
from src.storage.qdrant_client import QdrantClient
from pipeline.embed import embed_texts
from qdrant_client.models import PointStruct

print("🔄 Re-syncing QDrant from PostgreSQL (v2)...")

postgres = PostgresClient()
qdrant = QdrantClient()

# Delete and recreate collection
print("🗑️  Deleting old collection...")
try:
    qdrant.client.delete_collection("insurance_filings")
except:
    pass

print("✅ Creating fresh collection...")
qdrant._create_collection()

# Get all chunks
print("📊 Fetching chunks from PostgreSQL...")
with postgres.conn.cursor() as cur:
    cur.execute("""
        SELECT 
            c.chunk_id, 
            c.filing_id, 
            c.text, 
            c.chunk_index,
            c.metadata,
            f.company, 
            f.filing_date, 
            f.filing_type
        FROM text_chunks c
        JOIN filings f ON c.filing_id = f.filing_id
        ORDER BY c.filing_id, c.chunk_index
    """)
    
    columns = [desc[0] for desc in cur.description]
    chunks = [dict(zip(columns, row)) for row in cur.fetchall()]

print(f"✅ Found {len(chunks)} chunks")

# Process in batches
batch_size = 50  # Smaller batches
total_inserted = 0

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    
    print(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
    
    # Generate embeddings
    texts = [c['text'] for c in batch]
    try:
        vectors = embed_texts(texts)
    except Exception as e:
        print(f"❌ Failed to generate embeddings: {e}")
        continue
    
    # Prepare points for QDrant
    points = []
    for chunk, vector in zip(batch, vectors):
        # Use sequential IDs
        point_id = total_inserted
        
        payload = {
            'chunk_id': chunk['chunk_id'],
            'filing_id': chunk['filing_id'],
            'text': chunk['text'],
            'company': chunk['company'],
            'filing_date': str(chunk['filing_date']) if chunk['filing_date'] else None,
            'section_type': 'document',
            'chunk_index': chunk['chunk_index'],
            'token_count': chunk['metadata'].get('token_count', 0) if chunk['metadata'] else 0,
            'filename': chunk['metadata'].get('filename', '') if chunk['metadata'] else '',
            'filing_type': chunk['filing_type']
        }
        
        points.append(PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        ))
        total_inserted += 1
    
    # Insert batch
    try:
        qdrant.client.upsert(
            collection_name="insurance_filings",
            points=points
        )
        print(f"✅ Inserted batch {batch_num} ({len(points)} points)")
    except Exception as e:
        print(f"❌ Failed to insert batch: {e}")
        continue

print(f"\n{'='*80}")
print(f"✅ RESYNC COMPLETE!")
print(f"{'='*80}")
print(f"Total chunks processed: {len(chunks)}")
print(f"Total points inserted: {total_inserted}")

# Verify
result = qdrant.client.count("insurance_filings")
print(f"🔍 QDrant now has {result.count} points")
print(f"{'='*80}")
