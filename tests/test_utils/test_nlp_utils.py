"""
Tests for NLP utility functions
"""

import pytest

# Try importing the nlp_utils functions, but handle import errors gracefully
try:
    from app.utils.nlp_utils import (
        preprocess_text,
        extract_keywords,
        analyze_sentiment,
        analyze_writing_style,
    )

    IMPORTS_SUCCESSFUL = True
except (ImportError, ValueError, Exception) as e:
    IMPORTS_SUCCESSFUL = False
    print(f"WARNING: Could not import NLP functions: {e}")


# Skip all tests if imports failed
pytestmark = pytest.mark.skipif(
    not IMPORTS_SUCCESSFUL, reason="NLP dependencies not properly installed"
)


def test_preprocess_text():
    """Test text preprocessing function"""
    # Skip if imports failed
    if not IMPORTS_SUCCESSFUL:
        pytest.skip("NLP dependencies not properly installed")

    # Test removing URLs
    text_with_url = "Check out this link: https://example.com and read more"
    preprocessed = preprocess_text(text_with_url)
    assert "https://example.com" not in preprocessed

    # Test lowercasing
    text_with_case = "This Has Mixed CASE text"
    preprocessed = preprocess_text(text_with_case)
    assert preprocessed == preprocessed.lower()

    # Test removing punctuation
    text_with_punct = "Hello, world! How are you? This is a test."
    preprocessed = preprocess_text(text_with_punct)
    for punct in ",.!?":
        assert punct not in preprocessed


def test_extract_keywords():
    """Test keyword extraction function"""
    # Skip if imports failed
    if not IMPORTS_SUCCESSFUL:
        pytest.skip("NLP dependencies not properly installed")

    text = "Artificial intelligence and machine learning are transforming the technology industry."
    keywords = extract_keywords(text, top_n=3)

    # Test the return type and length
    assert isinstance(keywords, list)
    assert len(keywords) <= 3

    # Test that keywords are relevant
    relevant_words = ["artificial", "intelligence", "machine", "learning", "technology"]
    for keyword in keywords:
        assert any(word in keyword[0].lower() for word in relevant_words)


def test_analyze_sentiment():
    """Test sentiment analysis function"""
    # Skip if imports failed
    if not IMPORTS_SUCCESSFUL:
        pytest.skip("NLP dependencies not properly installed")

    # Test positive text
    positive_text = "I love this product! It's amazing and works perfectly."
    positive_sentiment = analyze_sentiment(positive_text)

    # Check if sentiment analysis returns expected structure
    assert "pos" in positive_sentiment
    assert "neg" in positive_sentiment
    assert "neu" in positive_sentiment
    assert "compound" in positive_sentiment

    # Verify positive text has higher positive score than negative
    assert positive_sentiment["pos"] > positive_sentiment["neg"]

    # Test negative text
    negative_text = "This is terrible. I hate it and it doesn't work at all."
    negative_sentiment = analyze_sentiment(negative_text)
    assert negative_sentiment["neg"] > negative_sentiment["pos"]

    # Test neutral text
    neutral_text = "This is a product. It exists. I purchased it yesterday."
    neutral_sentiment = analyze_sentiment(neutral_text)
    assert neutral_sentiment["neu"] > 0.5


def test_analyze_writing_style():
    """Test writing style analysis"""
    # Skip if imports failed
    if not IMPORTS_SUCCESSFUL:
        pytest.skip("NLP dependencies not properly installed")

    # Test simple text
    simple_text = "This is a simple test. It has short words. It is easy to read."
    simple_style = analyze_writing_style(simple_text)

    # Test complex text
    complex_text = (
        "The interpretability of recurrent neural networks remains problematic, "
        "particularly when utilizing non-interpretable activation functions in conjunction "
        "with high-dimensional embeddings that exacerbate the inherent opacity of the model's "
        "computational mechanisms."
    )
    complex_style = analyze_writing_style(complex_text)

    # Check if style analysis returns expected fields
    expected_fields = [
        "complexity",
        "formality",
        "emotional_tone",
        "vocabulary_diversity",
    ]
    for field in expected_fields:
        assert field in simple_style
        assert field in complex_style

    # Complex text should have higher complexity and formality scores
    assert complex_style["complexity"] > simple_style["complexity"]
    assert complex_style["vocabulary_diversity"] > simple_style["vocabulary_diversity"]

    # Test with empty text
    empty_style = analyze_writing_style("")
    assert empty_style["complexity"] == 0.0
