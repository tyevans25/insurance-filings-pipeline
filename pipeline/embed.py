from __future__ import annotations

from typing import List

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None  # Don't load immediately


def _get_model():
    """Lazy load model only when needed"""
    global _model
    if _model is None:
        print("📥 Loading embedding model (first time only)...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
        print("✅ Model loaded!")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = _get_model()  # Load only when called
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()