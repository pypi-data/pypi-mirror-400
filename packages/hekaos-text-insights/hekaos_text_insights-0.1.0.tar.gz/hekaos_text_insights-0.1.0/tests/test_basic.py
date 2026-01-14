"""Basic functionality tests."""

from hekaos_text_insights import analyze_text


def test_basic_analysis():
    """Test basic text analysis."""
    text = """
    I am a Python developer with 5 years of experience in backend development.
    I have built RESTful APIs using Django and Flask. Led a team of 3 engineers.
    """
    
    result = analyze_text(text)
    
    assert "keywords" in result
    assert "insights" in result
    assert "readability_score" in result
    assert isinstance(result["keywords"], list)
    assert isinstance(result["insights"], list)
    assert isinstance(result["readability_score"], int)
    assert "python" in result["keywords"]


def test_empty_text():
    """Test handling of empty text."""
    result = analyze_text("")
    
    assert result["keywords"] == []
    assert result["insights"] == []
    assert result["readability_score"] == 0


def test_invalid_input():
    """Test type checking."""
    try:
        analyze_text(123)
        assert False, "Should raise TypeError"
    except TypeError:
        pass


if __name__ == "__main__":
    test_basic_analysis()
    test_empty_text()
    test_invalid_input()
    print("All tests passed!")