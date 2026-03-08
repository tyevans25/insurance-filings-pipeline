"""
Clean text: remove stop words, punctuation, special characters
"""
import re
import string
from typing import List, Set
import nltk
from nltk.corpus import stopwords

# Download stopwords on first run
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class TextCleaner:
    def __init__(self, remove_stopwords: bool = True):
        self.remove_stopwords = remove_stopwords
        self.stop_words = set(stopwords.words('english')) if remove_stopwords else set()
        
        # Add insurance-specific terms to NOT remove
        self.domain_terms = {
            'loss', 'reserve', 'premium', 'claim', 'liability',
            'insurance', 'reinsurance', 'actuarial', 'underwriting'
        }
        self.stop_words -= self.domain_terms
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing stopwords, punctuation, special chars
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep periods and hyphens
        text = re.sub(r'[^\w\s\.\-]', ' ', text)
        
        # Remove numbers (optional - might want to keep for financial data)
        # text = re.sub(r'\d+', '', text)
        
        if self.remove_stopwords:
            # Tokenize and remove stopwords
            words = text.split()
            words = [w for w in words if w not in self.stop_words]
            text = ' '.join(words)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words/phrases
        """
        # Simple whitespace tokenization
        tokens = text.split()
        
        # Remove tokens that are just punctuation
        tokens = [t for t in tokens if not all(c in string.punctuation for c in t)]
        
        return tokens