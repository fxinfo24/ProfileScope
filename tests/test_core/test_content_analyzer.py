"""
Unit tests for the ContentAnalyzer class
"""

import pytest
from unittest.mock import MagicMock, patch
from app.core.content_analyzer import ContentAnalyzer


@pytest.fixture
def mock_profile_data():
    """Create mock profile data for testing"""
    return {
        "profile": {
            "username": "test_user",
            "bio": "This is a test bio for the content analyzer unit tests. I love technology and science.",
        },
        "posts": [
            {
                "id": "post1",
                "content": "Just finished reading a great book about artificial intelligence. Highly recommended!",
                "date": "2023-01-01",
            },
            {
                "id": "post2",
                "content": "Beautiful day for hiking in the mountains. Nature is amazing!",
                "date": "2023-01-15",
            },
        ],
        "media": [
            {
                "id": "media1",
                "type": "image",
                "caption": "Evening sunset at the beach #nature #peace",
                "date": "2023-01-10",
            }
        ],
    }


@pytest.fixture
def analyzer():
    """Create a ContentAnalyzer instance for testing"""
    return ContentAnalyzer()


def test_analyze_profile_returns_required_fields(analyzer, mock_profile_data):
    """Test that analyze_profile returns all required fields"""
    result = analyzer.analyze_profile(mock_profile_data)

    # Check that the result contains all expected top-level keys
    expected_keys = [
        "personality_traits",
        "interests",
        "writing_style",
        "content_topics",
        "sentiment",
        "posting_patterns",
    ]

    for key in expected_keys:
        assert key in result, f"Missing expected key: {key}"


def test_extract_text_content(analyzer, mock_profile_data):
    """Test the _extract_text_content method"""
    text = analyzer._extract_text_content(mock_profile_data)

    # Check that the text includes content from profile bio, posts, and media captions
    assert "test bio for the content analyzer" in text
    assert "finished reading a great book" in text
    assert "Beautiful day for hiking" in text
    assert "Evening sunset at the beach" in text


@patch("app.utils.nlp_utils.analyze_sentiment")
def test_analyze_sentiment_trends(mock_analyze_sentiment, analyzer, mock_profile_data):
    """Test the _analyze_sentiment_trends method"""
    # Configure the mock to return a consistent sentiment
    mock_analyze_sentiment.return_value = {"score": 0.75, "label": "positive"}

    result = analyzer._analyze_sentiment_trends(mock_profile_data)

    # Check that the result contains the expected fields
    assert "overall_sentiment" in result
    assert "distribution" in result
    assert "trend" in result

    # Check that the mock function was called for each text content
    expected_calls = len(mock_profile_data["posts"]) + (
        len([m for m in mock_profile_data["media"] if "caption" in m])
    )
    assert mock_analyze_sentiment.call_count >= expected_calls


def test_analyze_sentiment_trends(analyzer, mock_profile_data):
    """Test the _analyze_sentiment_trends method"""
    # Skip if dependencies aren't available
    try:
        result = analyzer._analyze_sentiment_trends(mock_profile_data)
    except (ImportError, ValueError):
        pytest.skip("NLP dependencies not properly installed")

    # Verify we got the expected structure
    assert "overall_sentiment" in result
    assert "distribution" in result
    assert "post_sentiments" in result

    # Verify values are reasonable
    assert result["overall_sentiment"]["label"] in ["positive", "negative", "neutral"]
    assert -1.0 <= result["overall_sentiment"]["score"] <= 1.0
    assert all(k in result["distribution"] for k in ["positive", "neutral", "negative"])

    # If we have monthly trends, check their structure
    if "monthly_trend" in result:
        for month_data in result["monthly_trend"]:
            assert "month" in month_data
            assert "average_score" in month_data
            assert -1.0 <= month_data["average_score"] <= 1.0


def test_analyze_writing_style(analyzer):
    """Test the _analyze_writing_style method"""
    text = """This is a sample text to test the writing style analysis. 
              It has multiple sentences with different structures.
              Some are short. Others are longer and more descriptive, using various words."""

    result = analyzer._analyze_writing_style(text)

    # Check that the result contains the expected fields
    assert "complexity" in result
    assert "formality" in result
    assert "emotional_tone" in result
    assert "vocabulary_diversity" in result

    # Check that the core metrics are in the expected range (0 to 1)
    # These metrics are normalized and should be between 0 and 1
    core_metrics = ["complexity", "formality", "emotional_tone", "vocabulary_diversity"]
    for key in core_metrics:
        assert 0 <= result[key] <= 1, f"Value for {key} is out of range: {result[key]}"

    # Check that the average sentence length is reasonable
    # But DON'T enforce a 0-1 range here since it's a raw count metric
    assert "average_sentence_length" in result
    assert (
        result["average_sentence_length"] > 0
    ), "Average sentence length should be positive"

    # Check that a normalized version of sentence length is present and in correct range
    if "normalized_sentence_length" in result:
        assert 0 <= result["normalized_sentence_length"] <= 1

    # Check word count is reasonable
    assert result["word_count"] > 10


def test_generate_timeline(analyzer, mock_profile_data):
    """Test the _generate_timeline method"""
    timeline = analyzer._generate_timeline(mock_profile_data)

    # Check that the timeline contains entries for each post and media item
    expected_entries = len(mock_profile_data["posts"]) + len(mock_profile_data["media"])
    assert len(timeline) == expected_entries

    # Check that each entry has the required fields
    for entry in timeline:
        assert "date" in entry
        assert "type" in entry
        assert "description" in entry


def test_empty_profile_data_handling(analyzer):
    """Test handling of empty profile data"""
    empty_data = {"profile": {}, "posts": [], "media": []}

    result = analyzer.analyze_profile(empty_data)

    # Check that the analyzer doesn't crash and returns valid results
    assert "personality_traits" in result
    assert "interests" in result
    assert "writing_style" in result
    assert "content_topics" in result
