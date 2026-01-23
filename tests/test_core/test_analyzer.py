"""
Tests for the ProfileScope core analyzer
"""

import json
import pytest
from unittest.mock import patch, Mock, MagicMock

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

    return SocialMediaAnalyzer(str(config_file))


def test_analyzer_initialization(analyzer):
    """Test analyzer initialization with config"""
    # Analyzer initializes components lazily or in __init__
    assert analyzer.content_analyzer is not None
    assert analyzer.authenticity_analyzer is not None
    assert analyzer.prediction_engine is not None
    assert hasattr(analyzer, "_get_collector")


@patch("app.core.analyzer.DataCollector")
def test_analyze_profile(mock_collector_class, analyzer):
    """Test complete profile analysis"""
    # Configure mock collector
    mock_collector = Mock()
    mock_collector.collect_profile_data.return_value = {
        "user_id": "test_user",
        "username": "test_user",
        "display_name": "Test User", 
        "bio": "Test bio",
        "posts": [{"id": "1", "content": "Test post content"}],
        "metadata": {"platform": "twitter", "is_real_data": True}
    }
    mock_collector_class.return_value = mock_collector

    # Inject the mock collector into the cache to avoid instantiation logic if needed
    # But since _get_collector instantiates DataCollector, our patch on the class should work.
    
    # Run analysis
    results = analyzer.analyze_profile("twitter", "test_user")

    # Verify DataCollector was initialized and called
    mock_collector_class.assert_called_with("twitter", 50) # 50 from test_config
    mock_collector.collect_profile_data.assert_called_with("test_user")

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
