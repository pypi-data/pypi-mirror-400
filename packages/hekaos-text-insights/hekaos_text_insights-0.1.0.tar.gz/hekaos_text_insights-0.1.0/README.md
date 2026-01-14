# hekaos-text-insights

Lightweight, zero-dependency Python package for extracting keywords, insights, and readability metrics from text.

## Installation

```bash
pip install hekaos-text-insights
```

## Quick Start

```python
from hekaos_text_insights import analyze_text

text = """
I am a Python developer with 5 years of experience in backend development.
I have built RESTful APIs using Django and Flask. I led a team of 3 engineers
to deliver a microservices architecture that improved system performance by 40%.
"""

result = analyze_text(text)
print(result)
```

**Output:**
```json
{
  "keywords": ["python", "backend", "experience", "apis", "django", "flask", "led", "team", "engineers"],
  "insights": [
    "Mentions technical skills",
    "Shows leadership experience",
    "Highlights achievements"
  ],
  "readability_score": 45
}
```

## Features

- **Keywords Extraction**: Identifies top terms using frequency analysis
- **Insights Generation**: Detects patterns related to skills, achievements, leadership, etc.
- **Readability Score**: Calculates Flesch Reading Ease (0-100 scale)

## API Reference

### `analyze_text(text: str) -> dict`

Analyzes input text and returns structured data.

**Parameters:**
- `text` (str): Raw text to analyze

**Returns:**
- `dict` with keys:
  - `keywords` (list): Top keywords
  - `insights` (list): Auto-generated insights
  - `readability_score` (int): Flesch Reading Ease score

**Raises:**
- `TypeError`: If input is not a string

## Readability Score Guide

- **90-100**: Very easy to read
- **60-70**: Standard/conversational
- **30-50**: Difficult
- **0-30**: Very difficult

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT License - see LICENSE file for details.

## Contributing

Issues and pull requests welcome at [GitHub](https://github.com/hekaos/hekaos-text-insights).