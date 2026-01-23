#!/usr/bin/env python3
"""
Test runner script for Vanta
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

    # Resolve cleanup script path from repository root.
    #
    # Root cause: this script lives in `bin/`, but the cleanup script lives in
    # `<repo>/scripts/cleanup.sh` (not `<repo>/bin/scripts/cleanup.sh`).
    repo_root = Path(__file__).resolve().parent.parent
    candidate_paths = [
        repo_root / "scripts" / "cleanup.sh",  # expected location
        Path(__file__).resolve().parent / "scripts" / "cleanup.sh",  # legacy fallback
    ]

    from typing import Optional

    script_path: Optional[str] = None
    for candidate in candidate_paths:
        if candidate.exists():
            script_path = str(candidate)
            break

    if not script_path:
        print("Warning: Cleanup script not found. Tried:")
        for candidate in candidate_paths:
            print(f"  - {candidate}")
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
    """Set up the test environment.

    This script is intentionally conservative:
    - It may install `pytest` if missing (so the runner can function).
    - It does NOT auto-install the full application dependencies, because that
      can be slow/unexpected. Instead, we fail fast with actionable guidance.
    """
    print("\n=== Setting up Test Environment ===\n")

    # Create test directories if they don't exist
    os.makedirs("test_results", exist_ok=True)

    # Install test dependencies if needed
    try:
        import pytest  # noqa: F401
    except ImportError:
        print("Installing pytest...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])

    return True


def _in_virtualenv() -> bool:
    # Works for venv and virtualenv
    return getattr(sys, "base_prefix", sys.prefix) != sys.prefix


def _preflight_check_runtime_deps() -> bool:
    """Fail fast if common runtime deps required by the test suite are missing."""
    missing = []
    required_modules = [
        "requests",  # used by tweepy and API clients
        "jinja2",  # Flask templates/tests
        "flask",
        "flask_sqlalchemy",
        "flask_migrate",
        "tweepy",
    ]

    for mod in required_modules:
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)

    if not missing:
        return True

    print("\n=== Missing Dependencies Detected ===\n")
    print("The full test suite requires additional dependencies that are not available in this Python environment.")
    print(f"Missing import(s): {', '.join(missing)}")
    print("")

    if not _in_virtualenv():
        print("You do not appear to be running inside the project's virtualenv.")
        print("Recommended setup:")
        print("  python -m venv venv")
        print("  source venv/bin/activate")

    print("Install project dependencies:")
    print("  pip install -r requirements.txt")
    print("")
    print("If you only want to verify the test runner itself, use:")
    print("  python3 bin/run_tests.py --simple")

    return False


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

    # Prevent globally-installed pytest plugins from interfering with this run.
    # This is important in environments where pytest plugins (e.g. pytest-html)
    # are installed system-wide but their dependencies are not available.
    env_vars = os.environ.copy()
    env_vars.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

    result = subprocess.run(cmd, env=env_vars)

    # Clean up the temporary test file
    try:
        os.remove(test_file)
    except:
        pass

    return result.returncode == 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test runner for Vanta")
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
    # Use parse_known_args so users can pass through arbitrary pytest flags
    # (e.g. -q, -k, -m) without this wrapper rejecting them.
    args, unknown_args = parser.parse_known_args()
    if unknown_args:
        args.pytest_args.extend(unknown_args)

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

    # Preflight: avoid failing deep in pytest collection due to missing deps
    if not _preflight_check_runtime_deps():
        return 1

    # Build command for running tests
    cmd = [sys.executable, "-m", "pytest", "-v", "--no-header", "--tb=native"]

    # Create environment variables dictionary
    env_vars = os.environ.copy()
    env_vars["PROFILESCOPE_CLEANUP_RUN"] = "1"  # Prevents duplicate cleanup
    # Prevent globally-installed pytest plugins from interfering with this run.
    # (Makes test runs more deterministic across dev machines/CI images.)
    env_vars.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

    # Add HTML reporting only if explicitly requested
    if args.html_report:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = f"test_results/pytest_report_{timestamp}.html"
        # Explicitly enable pytest-html when plugin autoload is disabled.
        # (This keeps non-HTML runs deterministic and avoids global plugin conflicts.)
        try:
            import pytest_html  # noqa: F401

            cmd.extend(["-p", "pytest_html", "--html", html_report, "--self-contained-html"])
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
