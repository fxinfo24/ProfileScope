#!/usr/bin/env python3
"""
Setup script for ProfileScope environment
Installs required packages and sets up dependencies
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_environment():
    """Set up the development environment"""
    print("Setting up ProfileScope development environment...")

    # Install setuptools first (needed for package builds)
    print("Installing setuptools...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "setuptools", "--upgrade"]
    )

    # Install latest numpy (compatible with Python 3.12)
    print("Installing numpy...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "numpy>=1.26.0", "--upgrade"]
    )

    # Install testing dependencies
    print("Installing testing dependencies...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pytest", "pytest-mock", "pytest-cov"]
    )

    # Run NLP setup script
    print("\nSetting up NLP dependencies...")
    nlp_setup_path = Path(__file__).parent / "scripts" / "setup_nlp.py"
    if nlp_setup_path.exists():
        subprocess.check_call([sys.executable, str(nlp_setup_path)])
    else:
        print(f"Warning: NLP setup script not found at {nlp_setup_path}")
        print("Installing NLP dependencies directly...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "nltk", "spacy", "scikit-learn"]
        )

        # Download NLTK resources
        print("Downloading NLTK resources...")
        subprocess.check_call(
            [
                sys.executable,
                "-c",
                "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')",
            ]
        )

        # Download spaCy model
        print("Downloading spaCy model...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
            )
        except:
            print(
                "Warning: Could not download spaCy model. You may need to install it manually."
            )

    print("\nSetup complete! You can now run the tests with: pytest")


def main():
    parser = argparse.ArgumentParser(description="Set up ProfileScope environment")
    args = parser.parse_args()

    setup_environment()


if __name__ == "__main__":
    main()
