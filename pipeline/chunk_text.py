from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import List

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


@dataclass
class ChunkRecord:
    chunk_index: int
    chunk_text: str
    token_count: int


_word_re = re.compile(r"[A-Za-z0-9']+")


def clean_and_tokenize(text: str) -> List[str]:
    """
    - Lowercase
    - Tokenize into words
    - Remove stopwords
    - Remove very short tokens
    """
    text = text.lower()

    tokens = _word_re.findall(text)  # pulls words/numbers, drops punctuation automatically

    cleaned = [
        t for t in tokens
        if t not in ENGLISH_STOP_WORDS and len(t) >= 2
    ]
    return cleaned


def chunk_tokens(tokens: List[str], chunk_size: int = 200, overlap: int = 50) -> List[ChunkRecord]:
    """
    Chunk by token count (good for embeddings later).
    Example default:
      - 200 tokens per chunk
      - 50 token overlap
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    chunks: List[ChunkRecord] = []

    step = chunk_size - overlap
    i = 0
    chunk_index = 0

    while i < len(tokens):
        window = tokens[i:i + chunk_size]
        if not window:
            break

        chunk_text = " ".join(window)
        chunks.append(
            ChunkRecord(
                chunk_index=chunk_index,
                chunk_text=chunk_text,
                token_count=len(window),
            )
        )

        chunk_index += 1
        i += step

    return chunks


def chunks_to_dicts(chunks: List[ChunkRecord]) -> List[dict]:
    return [asdict(c) for c in chunks]
