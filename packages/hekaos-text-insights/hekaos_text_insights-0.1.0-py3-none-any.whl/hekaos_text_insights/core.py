"""Core analysis function."""

from .keywords import extract_keywords
from .insights import generate_insights
from .readability import calculate_readability


def analyze_text(text):
    """
    Analyze text and return keywords, insights, and readability score.
    
    Args:
        text (str): Raw text to analyze
        
    Returns:
        dict: {
            "keywords": list of str,
            "insights": list of str,
            "readability_score": int
        }
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    if not text.strip():
        return {
            "keywords": [],
            "insights": [],
            "readability_score": 0
        }
    
    return {
        "keywords": extract_keywords(text),
        "insights": generate_insights(text),
        "readability_score": calculate_readability(text)
    }