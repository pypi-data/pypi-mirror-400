"""Readability score calculator using Flesch Reading Ease."""

import re


def count_syllables(word):
    """
    Estimate syllable count in a word.
    
    Args:
        word (str): Word to analyze
        
    Returns:
        int: Estimated syllable count
    """
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent 'e'
    if word.endswith('e'):
        count -= 1
    
    # Ensure at least 1 syllable
    return max(1, count)


def calculate_readability(text):
    """
    Calculate Flesch Reading Ease score.
    
    Score ranges:
    90-100: Very easy
    60-70: Standard
    0-30: Very difficult
    
    Args:
        text (str): Input text
        
    Returns:
        int: Readability score (0-100)
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    words = re.findall(r'\b\w+\b', text)
    
    if not sentences or not words:
        return 0
    
    total_syllables = sum(count_syllables(word) for word in words)
    
    # Flesch Reading Ease formula
    score = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (total_syllables / len(words))
    
    # Clamp between 0 and 100
    return max(0, min(100, int(score)))