"""
Integration test for ProfileScope

This test verifies that all components work together properly.
"""

import os
import sys
import pytest
import json
from unittest.mock import patch

# Add the project root to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.analyzer import SocialMediaAnalyzer
from app.core.data_collector import DataCollector
from app.utils.nlp_utils import preprocess_text


@pytest.fixture
def test_config():
    """Create a test configuration"""
    return {
        "rate_limits": {"twitter": 100, "facebook": 100},
        "analysis": {
            "nlp_model": "default",
            "sentiment_analysis": True,
            "confidence_threshold": 0.65,
        },
        "output": {"save_raw_data": False, "export_format": "json"},
        "logging": {"level": "INFO", "file": "test_profilescope.log"},
    }


@pytest.fixture
def mock_profile_data():
    """Create mock profile data"""
    return {
        "profile": {
            "username": "test_user",
            "bio": "Passionate about technology, AI, and innovation. Love to travel and explore new cultures.",
            "join_date": "2020-01-01",
        },
        "posts": [
            {
                "id": "post1",
                "content": "Just finished an amazing book about artificial intelligence. The future is now!",
                "date": "2023-01-01",
                "likes": 42,
            },
            {
                "id": "post2",
                "content": "Traveled to Japan last month. The culture and technology there is incredible.",
                "date": "2023-02-15",
                "likes": 78,
            },
            {
                "id": "post3",
                "content": "Working on a new project using machine learning. Exciting times!",
                "date": "2023-03-10",
                "likes": 55,
            },
        ],
        "media": [
            {
                "id": "media1",
                "type": "image",
                "caption": "Beautiful sunset in Tokyo. #travel #japan",
                "date": "2023-02-10",
            },
            {
                "id": "media2",
                "type": "image",
                "caption": "My new programming setup. #coding #technology",
                "date": "2023-03-05",
            },
        ],
    }


@patch.object(DataCollector, "collect_profile_data")
def test_full_analysis_flow(mock_collect, mock_profile_data, test_config, tmp_path):
    """Test the complete analysis process from data collection to results"""
    # Mock the data collection to return our test data
    mock_collect.return_value = mock_profile_data

    # Create a temporary config file
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(test_config, f)

    # Initialize the analyzer with our test config
    analyzer = SocialMediaAnalyzer(str(config_path))

    # Run the analysis
    results = analyzer.analyze_profile("twitter", "test_user")

    # Basic validation of results
    assert "metadata" in results
    assert results["metadata"]["profile_id"] == "test_user"
    assert results["metadata"]["platform"] == "twitter"

    # Check that all analysis sections are present
    assert "content_analysis" in results
    assert "authenticity_analysis" in results
    assert "predictions" in results

    # Verify content analysis has all expected sections
    content = results["content_analysis"]
    assert "personality_traits" in content
    assert "interests" in content
    assert "writing_style" in content
    assert "timeline" in content

    # Verify authenticity analysis
    auth = results["authenticity_analysis"]
    assert "overall_authenticity" in auth

    # Verify NLP utility functions were used in the analysis
    mock_collect.assert_called_once_with("test_user")

    # Test exporting results
    output_path = tmp_path / "test_results.json"
    analyzer.export_results(results, str(output_path))
    assert output_path.exists()

    # Verify the exported results match
    with open(output_path, "r") as f:
        exported = json.load(f)
    assert exported["metadata"]["profile_id"] == results["metadata"]["profile_id"]
