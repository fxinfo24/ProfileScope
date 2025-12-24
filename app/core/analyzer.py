"""
ProfileScope: Core Analyzer Module
Main orchestrator for social media profile analysis
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from .data_collector import DataCollector
from .content_analyzer import ContentAnalyzer
from .authenticity import ProfileAuthenticityAnalyzer
from .prediction import PredictionEngine
from ..utils.logger import setup_logger


class SocialMediaAnalyzer:
    """Main application for social media profile analysis"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the analyzer with optional configuration
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = setup_logger("ProfileScope.Analyzer", self.config["logging"])

        # Initialize components
        self.collectors = {
            "twitter": DataCollector("twitter", self.config["rate_limits"]["twitter"]),
            "facebook": DataCollector(
                "facebook", self.config["rate_limits"]["facebook"]
            ),
        }

        self.content_analyzer = ContentAnalyzer(
            nlp_model=self.config["analysis"]["nlp_model"],
            sentiment_analyzer=self.config["analysis"]["sentiment_analysis"],
        )

        self.authenticity_analyzer = ProfileAuthenticityAnalyzer()

        threshold = self.config["analysis"]["confidence_threshold"]
        self.prediction_engine = PredictionEngine(confidence_threshold=threshold)

    def analyze_profile(self, platform: str, profile_id: str) -> Dict[str, Any]:
        """
        Perform complete analysis of a social media profile
        Args:
            platform: Social platform name (e.g., 'twitter', 'facebook')
            profile_id: Username or ID of the profile
        Returns:
            Complete analysis results
        """
        self.logger.info(f"Starting analysis of {profile_id} on {platform}")

        try:
            # Step 1: Collect profile data
            if platform.lower() not in self.collectors:
                raise ValueError(f"Unsupported platform: {platform}")

            collector = self.collectors[platform.lower()]
            profile_data = collector.collect_profile_data(profile_id)

            # Step 2: Analyze content
            content_analysis = self.content_analyzer.analyze_profile(profile_data)

            # Step 3: Analyze authenticity
            authenticity_analysis = self.authenticity_analyzer.analyze_authenticity(
                profile_data, content_analysis
            )

            # Step 4: Generate predictions
            predictions = self.prediction_engine.generate_predictions(
                profile_data, content_analysis
            )

            # Compile complete results
            results = {
                "metadata": {
                    "profile_id": profile_id,
                    "platform": platform,
                    "analysis_date": datetime.now().isoformat(),
                    "analyzer_version": "1.0.0",
                },
                "content_analysis": content_analysis,
                "authenticity_analysis": authenticity_analysis,
                "predictions": predictions,
            }

            # Save raw data if configured
            if self.config["output"]["save_raw_data"]:
                results["raw_data"] = profile_data

            self.logger.info(f"Analysis completed for {profile_id}")
            return results
        except Exception as e:
            self.logger.error(
                f"Error analyzing profile {profile_id} on {platform}: {str(e)}",
                exc_info=True,
            )
            raise

    def export_results(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Export analysis results to file
        Args:
            results: Analysis results to export
            output_path: Path to save results
        """
        format_type = self.config["output"]["export_format"].lower()
        self.logger.info(f"Exporting results to {output_path} in {format_type} format")

        if format_type == "json":
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

        self.logger.info(f"Results exported to {output_path}")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "rate_limits": {"twitter": 100, "facebook": 100},
            "analysis": {
                "nlp_model": "default",
                "sentiment_analysis": True,
                "confidence_threshold": 0.65,
            },
            "output": {"save_raw_data": True, "export_format": "json"},
            "logging": {"level": "INFO", "file": "logs/profilescope.log"},
        }

        if not config_path:
            return default_config

        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            # Merge with defaults for any missing values
            merged_config = default_config.copy()
            for section, values in config.items():
                if section in merged_config:
                    if isinstance(merged_config[section], dict):
                        merged_config[section].update(values)
                    else:
                        merged_config[section] = values
                else:
                    merged_config[section] = values

            return merged_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
