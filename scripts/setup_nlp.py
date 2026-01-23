#!/usr/bin/env python3
"""
Setup script for NLP dependencies
Installs required packages and downloads language models
"""

import sys
import os
import subprocess
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("setup_nlp")


def check_python_version():
    """Check if Python version is compatible"""
    current_version = sys.version_info
    logger.info(
        f"Detected Python {current_version.major}.{current_version.minor}.{current_version.micro}"
    )

    if current_version.major < 3 or (
        current_version.major == 3 and current_version.minor < 8
    ):
        logger.warning("Python 3.8 or higher is recommended for Vanta")
        return False

    if current_version.major == 3 and current_version.minor >= 12:
        logger.info("Using Python 3.12+, will ensure compatible package versions")

    return True


def setup_nltk():
    """Download and set up NLTK resources"""
    logger.info("Setting up NLTK resources")
    try:
        import nltk

        # Resources to download
        resources = [
            "punkt",
            "stopwords",
            "vader_lexicon",
            "wordnet",
        ]

        for resource in resources:
            try:
                nltk.data.find(f"tokenizers/{resource}")
                logger.info(f"NLTK resource '{resource}' is already installed")
            except LookupError:
                logger.info(f"Downloading NLTK resource '{resource}'")
                nltk.download(resource)

        logger.info("NLTK setup complete")
        return True
    except Exception as e:
        logger.error(f"Error setting up NLTK: {e}")
        return False


def setup_spacy():
    """Download and set up SpaCy models"""
    logger.info("Setting up SpaCy models")
    try:
        # Check if model is already installed
        try:
            import spacy

            spacy.load("en_core_web_sm")
            logger.info("SpaCy model 'en_core_web_sm' is already installed")
        except OSError:
            logger.info("Installing SpaCy model 'en_core_web_sm'")
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
            )

        logger.info("SpaCy setup complete")
        return True
    except Exception as e:
        logger.error(f"Error setting up SpaCy: {e}")
        return False


def install_dependencies():
    """Install required dependencies"""
    logger.info("Installing required dependencies")

    packages = [
        "numpy>=1.26.0",
        "nltk>=3.8.1",
        "spacy>=3.7.2",
        "scikit-learn>=1.3.0",
        "textstat>=0.7.3",
    ]

    try:
        # Install packages
        for package in packages:
            logger.info(f"Installing {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        logger.info("Dependencies installed successfully")
        return True
    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Setup NLP dependencies for Vanta"
    )
    parser.add_argument(
        "--skip-deps", action="store_true", help="Skip installing dependencies"
    )
    parser.add_argument("--skip-nltk", action="store_true", help="Skip NLTK setup")
    parser.add_argument("--skip-spacy", action="store_true", help="Skip SpaCy setup")
    args = parser.parse_args()

    logger.info("Starting NLP dependencies setup")

    # Check Python version
    check_python_version()

    # Install dependencies if not skipped
    if not args.skip_deps:
        if not install_dependencies():
            logger.warning("Dependency installation had issues, continuing anyway...")

    # Set up NLTK if not skipped
    if not args.skip_nltk:
        if not setup_nltk():
            logger.warning("NLTK setup had issues, continuing anyway...")

    # Set up SpaCy if not skipped
    if not args.skip_spacy:
        if not setup_spacy():
            logger.warning("SpaCy setup had issues, continuing anyway...")

    logger.info("NLP dependencies setup complete")
    logger.info("\nTo run the setup manually:")
    logger.info("1. pip install numpy nltk spacy scikit-learn textstat")
    logger.info("2. python -m nltk.downloader punkt stopwords vader_lexicon wordnet")
    logger.info("3. python -m spacy download en_core_web_sm")


if __name__ == "__main__":
    main()
