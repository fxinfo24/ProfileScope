#!/usr/bin/env python3
"""
ProfileScope CLI
Command line interface for ProfileScope social media analysis
"""

import argparse
import sys
from pathlib import Path
from app.core.analyzer import SocialMediaAnalyzer


def main():
    """Command line entry point"""
    parser = argparse.ArgumentParser(
        description="ProfileScope: Social Media Profile Analysis Tool"
    )

    parser.add_argument(
        "--platform",
        required=True,
        choices=["twitter", "facebook"],
        help="Social media platform to analyze",
    )

    parser.add_argument(
        "--profile", required=True, help="Profile ID or username to analyze"
    )

    parser.add_argument("--config", type=Path, help="Path to configuration file (JSON)")

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/results/analysis.json"),
        help="Output file path for analysis results",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging output"
    )

    args = parser.parse_args()

    try:
        # Create output directory if it doesn't exist
        args.output.parent.mkdir(parents=True, exist_ok=True)

        # Create analyzer instance
        analyzer = SocialMediaAnalyzer(
            config_path=str(args.config) if args.config else None
        )

        # Run analysis
        print(f"Analyzing {args.profile} on {args.platform}...")
        results = analyzer.analyze_profile(args.platform, args.profile)

        # Export results
        analyzer.export_results(results, str(args.output))
        print(f"Analysis complete! Results saved to {args.output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
