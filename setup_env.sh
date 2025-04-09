#!/bin/bash
# Setup script for ProfileScope environment

echo "Setting up ProfileScope environment..."

# Activate virtual environment if not already activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Please activate your virtual environment first."
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Clean existing packages that might cause conflicts
echo "Removing conflicting packages..."
pip uninstall -y numpy spacy

# Install core dependencies first
echo "Installing core dependencies..."
pip install wheel
pip install numpy==1.26.2

# Install remaining dependencies
echo "Installing remaining dependencies..."
pip install -r requirements.txt

# Download required NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon'); nltk.download('wordnet'); nltk.download('punkt_tab')"

# Verify installation
echo "Verifying installation..."
python -c "import numpy; print('NumPy version:', numpy.__version__)"
python -c "import spacy; print('spaCy version:', spacy.__version__)"
python -c "import nltk; print('NLTK data path:', nltk.data.path)"

echo "Setup complete. You can now run ProfileScope."
