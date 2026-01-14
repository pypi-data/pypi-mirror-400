"""Insight generation based on pattern matching."""

import re


PATTERNS = {
    "technical_skills": (
        r'\b(python|javascript|java|api|backend|frontend|database|sql|aws|docker|kubernetes|react|node)\b',
        "Mentions technical skills"
    ),
    "leadership": (
        r'\b(led|managed|directed|coordinated|supervised|team|leadership)\b',
        "Shows leadership experience"
    ),
    "achievements": (
        r'\b(increased|improved|reduced|achieved|delivered|launched|built|created)\b',
        "Highlights achievements"
    ),
    "education": (
        r'\b(university|college|degree|bachelor|master|phd|certification)\b',
        "Contains educational background"
    ),
    "communication": (
        r'\b(presented|communicated|collaborated|stakeholder|client|customer)\b',
        "Demonstrates communication skills"
    ),
}


def generate_insights(text, max_insights=5):
    """
    Generate insights based on pattern matching.
    
    Args:
        text (str): Input text
        max_insights (int): Maximum insights to return
        
    Returns:
        list: Insight strings
    """
    text_lower = text.lower()
    insights = []
    
    for pattern, insight in PATTERNS.values():
        if re.search(pattern, text_lower):
            insights.append(insight)
            if len(insights) >= max_insights:
                break
    
    if not insights:
        insights.append("General content analyzed")
    
    return insights