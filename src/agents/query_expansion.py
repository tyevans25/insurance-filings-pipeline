"""Query expansion with actuarial synonyms"""

ACTUARIAL_SYNONYMS = {
    'reserve': ['loss reserve', 'unpaid claim', 'loss and LAE reserve', 'IBNR', 'claim reserve'],
    'catastrophe': ['cat loss', 'natural disaster', 'hurricane', 'wildfire', 'severe weather'],
    'combined ratio': ['underwriting ratio', 'loss ratio plus expense ratio'],
    'premium': ['earned premium', 'written premium', 'net premium'],
    'reinsurance': ['reinsurer', 'retrocession', 'ceded premium'],
    'adequacy': ['sufficiency', 'reserve strength'],
    'development': ['emergence', 'loss development', 'adverse development'],
}

def expand_query(query: str) -> str:
    """Expand query with actuarial synonyms"""
    q_lower = query.lower()
    additions = []
    
    for term, synonyms in ACTUARIAL_SYNONYMS.items():
        if term in q_lower:
            additions.extend(synonyms[:3])  # Top 3 synonyms
    
    if additions:
        return f"{query} {' '.join(additions)}"
    return query
