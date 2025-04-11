#!/usr/bin/env python3
"""
Test runner script for ProfileScope
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import datetime


def run_cleanup_script():
    """Run the cleanup script before tests"""
    print("\n=== Running Cleanup Script ===\n")

    # Path to the cleanup script
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "cleanup.sh")

    if not os.path.exists(script_path):
        print(f"Warning: Cleanup script not found at: {script_path}")
        return False

    try:
        print(f"Executing: {script_path}")
        result = subprocess.run(["bash", script_path], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Cleanup completed successfully")
            # Mark cleanup as run to avoid duplicate execution
            os.environ["PROFILESCOPE_CLEANUP_RUN"] = "1"
            return True
        else:
            print(f"❌ Cleanup failed with exit code {result.returncode}")
            print("Error output:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run cleanup script: {e}")
        return False


def setup_test_environment():
    """Set up the test environment"""
    print("\n=== Setting up Test Environment ===\n")

    # Create test directories if they don't exist
    os.makedirs("test_results", exist_ok=True)

    # Install test dependencies if needed
    try:
        import pytest
    except ImportError:
        print("Installing pytest...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])

    # We won't require pytest-html by default to avoid the errors
    return True


def run_simple_tests():
    """Run a very simple test to verify basic pytest functionality"""
    print("\n=== Running Simple Test ===\n")

    # Create a temporary simple test file
    test_file = "test_simple.py"
    with open(test_file, "w") as f:
        f.write(
            """
import pytest

def test_simple():
    \"\"\"A simple test that must pass\"\"\"
    assert 1 == 1
"""
        )

    # Run the test with minimal options to avoid plugin conflicts
    cmd = [sys.executable, "-m", "pytest", "-v", test_file]

    result = subprocess.run(cmd)

    # Clean up the temporary test file
    try:
        os.remove(test_file)
    except:
        pass

    return result.returncode == 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test runner for ProfileScope")
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Run only simple test to verify functionality",
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML report (requires pytest-html package)",
    )
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Skip running the cleanup script before tests",
    )
    parser.add_argument(
        "--junitxml",
        help="Generate JUnit XML report at the specified path",
    )
    parser.add_argument("pytest_args", nargs="*", help="Additional pytest arguments")
    args = parser.parse_args()

    # Run cleanup script before tests unless skipped
    if not args.skip_cleanup and os.environ.get("PROFILESCOPE_CLEANUP_RUN") != "1":
        run_cleanup_script()
    else:
        if args.skip_cleanup:
            print("\n=== Skipping cleanup (--skip-cleanup) ===\n")
        elif os.environ.get("PROFILESCOPE_CLEANUP_RUN") == "1":
            print("\n=== Cleanup already run in this session ===\n")

    # Set up test environment
    if not setup_test_environment():
        print("Failed to set up test environment")
        return 1

    # Run simple verification test
    if args.simple:
        if run_simple_tests():
            print("\n✅ Simple test passed!")
            return 0
        else:
            print("\n❌ Simple test failed.")
            return 1

    # Build command for running tests
    cmd = [sys.executable, "-m", "pytest", "-v", "--no-header", "--tb=native"]

    # Create environment variables dictionary
    env_vars = os.environ.copy()
    env_vars["PROFILESCOPE_CLEANUP_RUN"] = "1"  # Prevents duplicate cleanup

    # Add HTML reporting only if explicitly requested
    if args.html_report:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = f"test_results/pytest_report_{timestamp}.html"
        try:
            import pytest_html

            cmd.extend(["--html", html_report, "--self-contained-html"])
            print(f"HTML report will be saved to: {html_report}")
        except ImportError:
            print("Warning: pytest-html not installed. HTML report won't be generated.")
            print("Install with: pip install pytest-html")

    # Add JUnit XML report if specified
    if args.junitxml:
        cmd.extend(["--junitxml", args.junitxml])

    # Add any additional pytest arguments
    if args.pytest_args:
        cmd.extend(args.pytest_args)

    print(f"\n=== Running Tests ===")

    result = subprocess.run(cmd, env=env_vars)

    if result.returncode == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
