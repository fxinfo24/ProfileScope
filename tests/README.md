# ProfileScope Testing Guide

## Installation

First, install the project dependencies:

```bash
# Install setuptools first (needed for package builds)
pip install setuptools

# And then
python setup_env.py

# Install requirements with compatibility
pip install -r requirements.txt

# Install testing dependencies
pip install pytest pytest-mock pytest-cov
```

## Running Tests

Run the test suite using the following command:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app

# Run specific test file
pytest tests/test_core/test_analyzer.py
```

## Troubleshooting

If you encounter installation errors with specific package versions:

1. For numpy compatibility issues with Python 3.12+:
   ```bash
   pip install numpy --upgrade
   ```

2. For other dependency errors:
   ```bash
   pip install -r requirements.txt --ignore-installed
   ```

3. If tests are failing:
   - Check that all dependencies are installed correctly
   - Verify that the test environment is set up properly
   - Look for error messages in the test output
   - For web interface issues, check the Flask logs
