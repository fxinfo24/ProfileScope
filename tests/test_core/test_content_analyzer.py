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

    # Check that all required sections are present
    assert "personality_traits" in result
    assert "interests" in result
    assert "beliefs" in result
    assert "writing_style" in result
    assert "timeline" in result

    # Check that personality_traits contains expected traits
    traits = result["personality_traits"]
    expected_traits = [
        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism",
    ]
    for trait in expected_traits:
        assert trait in traits
        assert isinstance(traits[trait], float)
        assert 0 <= traits[trait] <= 1


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
    # Mock the sentiment analysis to return consistent values
    mock_analyze_sentiment.return_value = {
        "compound": 0.5,
        "pos": 0.6,
        "neg": 0.1,
        "neu": 0.3,
    }

    result = analyzer._analyze_sentiment_trends(mock_profile_data)

    assert "trend" in result
    assert "overall_sentiment" in result
    assert len(result["trend"]) > 0
    assert isinstance(result["overall_sentiment"], float)


def test_analyze_writing_style(analyzer):
    """Test the _analyze_writing_style method"""
    test_text = """
    This is a sample text to analyze writing style. It contains multiple sentences with different
    structures and vocabulary. The purpose is to test the writing style analysis functionality.
    Some sentences are short. Others are more complex and contain subordinate clauses. 
    This text is designed to have a moderate level of complexity and formality.
    """

    result = analyzer._analyze_writing_style(test_text)

    assert "complexity" in result
    assert "formality" in result
    assert "emotional_tone" in result
    assert "vocabulary_diversity" in result
    assert "average_sentence_length" in result
    assert "stylistic_fingerprint" in result

    assert isinstance(result["complexity"], float)
    assert 0 <= result["complexity"] <= 1
    assert isinstance(result["formality"], float)
    assert 0 <= result["formality"] <= 1


def test_generate_timeline(analyzer, mock_profile_data):
    """Test the _generate_timeline method"""
    timeline = analyzer._generate_timeline(mock_profile_data)

    assert len(timeline) == 3  # Should have 3 items (2 posts + 1 media)

    # Check that timeline items have the required fields
    for item in timeline:
        assert "date" in item
        assert "type" in item
        assert "description" in item


def test_empty_profile_data_handling(analyzer):
    """Test handling of empty profile data"""
    empty_data = {"profile": {}, "posts": [], "media": []}
    result = analyzer.analyze_profile(empty_data)

    # Should still return all sections even with empty data
    assert "personality_traits" in result
    assert "interests" in result
    assert "beliefs" in result
    assert "writing_style" in result
    assert "timeline" in result

    # Timeline should be empty
    assert len(result["timeline"]) == 0
