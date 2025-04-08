#!/usr/bin/env python3
"""
Test runner script for ProfileScope
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_quick_test():
    """Run the quick verification test"""
    print("\n=== Running Quick Test ===\n")
    result = subprocess.run([sys.executable, "test_analyzer.py"])
    return result.returncode == 0


def run_pytest(path=None, verbose=False):
    """Run pytest tests"""
    print(f"\n=== Running Pytest Tests{f' in {path}' if path else ''} ===\n")

    cmd = [sys.executable, "-m", "pytest"]
    if verbose:
        cmd.append("-v")

    if path:
        cmd.append(path)

    result = subprocess.run(cmd)
    return result.returncode == 0


def setup_test_environment():
    """Set up the test environment"""
    print("\n=== Setting up Test Environment ===\n")

    # Create test directories if they don't exist
    os.makedirs("test_results", exist_ok=True)

    # Make sure pytest is installed
    try:
        import pytest
    except ImportError:
        print("Installing pytest...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])

    # Install test dependencies
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest-mock", "pytest-cov"]
    )

    return True


def main():
    parser = argparse.ArgumentParser(description="Test runner for ProfileScope")
    parser.add_argument(
        "--quick", action="store_true", help="Run only the quick verification test"
    )
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--web", action="store_true", help="Run only web interface tests"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Run tests in verbose mode"
    )

    args = parser.parse_args()

    # Set up the test environment
    if not setup_test_environment():
        print("Failed to set up test environment")
        return 1

    success = True

    # If no specific test is requested, run all tests
    run_all = not (args.quick or args.unit or args.integration or args.web)

    # Run quick verification test
    if args.quick or run_all:
        if not run_quick_test():
            success = False
            if not run_all:
                return 1

    # Run unit tests
    if args.unit or run_all:
        if not run_pytest("tests/test_core", args.verbose):
            success = False
            if not run_all:
                return 1

    # Run integration tests
    if args.integration or run_all:
        if not run_pytest("tests/test_integration.py", args.verbose):
            success = False
            if not run_all:
                return 1

    # Run web interface tests
    if args.web or run_all:
        if not run_pytest("tests/test_web", args.verbose):
            success = False
            if not run_all:
                return 1

    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
