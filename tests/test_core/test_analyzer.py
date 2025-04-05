"""
Tests for the ProfileScope core analyzer
"""

import json
import pytest
from pathlib import Path
from app.core.analyzer import SocialMediaAnalyzer


@pytest.fixture
def test_config():
    return {
        "rate_limits": {"twitter": 50, "facebook": 50},
        "analysis": {
            "nlp_model": "test_model",
            "sentiment_analysis": True,
            "confidence_threshold": 0.5,
        },
        "output": {"save_raw_data": True, "export_format": "json"},
        "logging": {"level": "DEBUG", "file": "test_profilescope.log"},
    }


@pytest.fixture
def analyzer(tmp_path, test_config):
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(test_config, f)
    return SocialMediaAnalyzer(str(config_file))


def test_analyzer_initialization(analyzer):
    """Test analyzer initialization with config"""
    assert analyzer.collectors["twitter"] is not None
    assert analyzer.collectors["facebook"] is not None
    assert analyzer.content_analyzer is not None
    assert analyzer.authenticity_analyzer is not None
    assert analyzer.prediction_engine is not None


def test_analyze_profile(analyzer):
    """Test complete profile analysis"""
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
