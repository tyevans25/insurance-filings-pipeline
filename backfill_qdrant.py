"""
Backfill QDrant with embeddings from PostgreSQL chunks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from storage.postgres_client import PostgresClient
from storage.qdrant_client import QdrantClient
from processing.embedder import TextEmbedder

print("🔄 Backfilling QDrant from PostgreSQL...")

postgres = PostgresClient()
qdrant = QdrantClient()
embedder = TextEmbedder()

# Get all chunks from PostgreSQL
with postgres.conn.cursor() as cur:
    cur.execute("""
        SELECT c.chunk_id, c.text, c.filing_id, c.section_type, 
               f.company, f.filing_date
        FROM text_chunks c
        JOIN filings f ON c.filing_id = f.filing_id
    """)
    columns = [desc[0] for desc in cur.description]
    chunks = [dict(zip(columns, row)) for row in cur.fetchall()]

print(f"📊 Found {len(chunks)} chunks in PostgreSQL")

# Generate embeddings
print("🧠 Generating embeddings...")
texts = [c['text'] for c in chunks]
embeddings = embedder.embed_texts(texts)

print(f"✅ Generated {len(embeddings)} embeddings")

# Add embeddings to chunks
for chunk, embedding in zip(chunks, embeddings):
    chunk['embedding'] = embedding.tolist()

# Insert into QDrant
print("💾 Inserting into QDrant...")
qdrant.insert_embeddings(chunks)

print("✅ Done! QDrant backfilled.")
