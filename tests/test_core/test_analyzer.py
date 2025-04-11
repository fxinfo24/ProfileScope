"""
Tests for the ProfileScope core analyzer
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from app.core.analyzer import SocialMediaAnalyzer


@pytest.fixture
def test_config():
    """Create test configuration"""
    return {
        "rate_limits": {"twitter": 50, "facebook": 50},
        "analysis": {
            "nlp_model": "test_model",
            "sentiment_analysis": True,
            "confidence_threshold": 0.5,
            "use_mock_data": True,
        },
        "output": {"save_raw_data": True, "export_format": "json"},
        "logging": {"level": "DEBUG", "file": "test_analyzer.log"},
    }


@pytest.fixture
def analyzer(tmp_path, test_config):
    """Create analyzer instance with test configuration"""
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(test_config, f)

    # Mock the collectors to avoid actual API calls during tests
    with patch("app.core.analyzer.DataCollector") as mock_collector_class:
        # Configure the mock to return test data
        mock_collector = mock_collector_class.return_value
        mock_collector.collect_profile_data.return_value = {
            "profile": {"username": "test_user", "name": "Test User"},
            "posts": [{"id": "1", "content": "Test post content"}],
            "media": [{"id": "1", "type": "image", "caption": "Test image"}],
        }

        yield SocialMediaAnalyzer(str(config_file))


def test_analyzer_initialization(analyzer):
    """Test analyzer initialization with config"""
    assert analyzer.collectors["twitter"] is not None
    assert analyzer.collectors["facebook"] is not None
    assert analyzer.content_analyzer is not None
    assert analyzer.authenticity_analyzer is not None
    assert analyzer.prediction_engine is not None


def test_analyze_profile(analyzer):
    """Test complete profile analysis"""
    with patch.object(
        analyzer.collectors["twitter"], "collect_profile_data"
    ) as mock_collect:
        # Configure mock to return test data
        mock_collect.return_value = {
            "profile": {"username": "test_user", "name": "Test User"},
            "posts": [{"id": "1", "content": "Test post content"}],
            "media": [{"id": "1", "type": "image", "caption": "Test image"}],
        }

        # Run analysis
        results = analyzer.analyze_profile("twitter", "test_user")

        # Check all required components are present
        assert "metadata" in results
        assert "content_analysis" in results
        assert "authenticity_analysis" in results
        assert "predictions" in results

        # Check metadata
        assert results["metadata"]["profile_id"] == "test_user"
        assert results["metadata"]["platform"] == "twitter"
        assert "analysis_date" in results["metadata"]
        assert "analyzer_version" in results["metadata"]


def test_unsupported_platform(analyzer):
    """Test error handling for unsupported platforms"""
    with pytest.raises(ValueError) as exc_info:
        analyzer.analyze_profile("unsupported", "test_user")

    assert "Unsupported platform" in str(exc_info.value)


def test_export_results(analyzer, tmp_path):
    """Test results export functionality"""
    results = {
        "metadata": {
            "profile_id": "test_user",
            "platform": "twitter",
        },
        "test_data": "test_value",
    }

    output_file = tmp_path / "test_results.json"
    analyzer.export_results(results, str(output_file))

    # Verify file was created and contains correct data
    assert output_file.exists()
    with open(output_file) as f:
        loaded_results = json.load(f)

    assert loaded_results == results


def test_export_unsupported_format(analyzer, tmp_path):
    """Test error handling for unsupported export formats"""
    analyzer.config["output"]["export_format"] = "unsupported"

    with pytest.raises(ValueError) as exc_info:
        analyzer.export_results({}, str(tmp_path / "test.txt"))

    assert "Unsupported export format" in str(exc_info.value)
