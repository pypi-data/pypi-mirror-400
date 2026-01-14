"""Keyword extraction logic."""

import re
from collections import Counter


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "should", "could", "may", "might", "must", "can", "this",
    "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
    "what", "which", "who", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very"
}


def extract_keywords(text, top_n=10):
    """
    Extract top keywords from text.
    
    Args:
        text (str): Input text
        top_n (int): Number of keywords to return
        
    Returns:
        list: Top keywords sorted by frequency
    """
    # Lowercase and extract words
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Filter stopwords
    filtered = [w for w in words if w not in STOPWORDS]
    
    # Count and return top N
    counter = Counter(filtered)
    return [word for word, _ in counter.most_common(top_n)]