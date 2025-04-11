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
pip install pytest pytest-mock pytest-cov pytest-html
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

# Generate HTML report
pytest --html=test_results/report.html --self-contained-html
```

Alternatively, use our test runner script:

```bash
# Run all tests with HTML report
python run_tests.py

# Run only unit tests with HTML report 
python run_tests.py --unit --html=unit_tests_report.html

# Run all tests in verbose mode
python run_tests.py -v
```

### HTML Test Reports

The HTML test reports provide a detailed breakdown of test results with the following features:

- Summary of passed, failed, and skipped tests
- Environment information
- Test case details including duration
- Traceback information for failures
- Charts and statistics

Reports are generated in the `test_results` directory by default and can be viewed in any web browser.

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
   - Review the HTML test report for detailed information
