#!/usr/bin/env python3
"""
Simple test runner for ProfileScope without HTML reports
Use this script if you're experiencing issues with pytest-html
"""

import os
import sys
import subprocess
import datetime


def main():
    """Main function"""
    # Ensure cleanup has been run
    cleanup_script = os.path.join("scripts", "cleanup.sh")
    if os.path.exists(cleanup_script):
        print("\n=== Running Cleanup Script ===\n")
        try:
            subprocess.run(["bash", cleanup_script], check=True)
            print("✅ Cleanup completed successfully")
        except subprocess.CalledProcessError:
            print("⚠️ Cleanup failed")
    else:
        print(f"⚠️ Cleanup script not found: {cleanup_script}")

    # Run pytest without HTML plugin
    cmd = [sys.executable, "-m", "pytest", "-v"] + sys.argv[1:]

    # Add JUnit XML report option (works better than HTML)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    xml_report = f"test_results/pytest_results_{timestamp}.xml"
    cmd.extend(["--junitxml", xml_report])

    print("\n=== Running Tests ===\n")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print(f"XML report saved to: {xml_report}")
        return 0
    else:
        print("\n❌ Some tests failed.")
        print(f"See XML report for details: {xml_report}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
