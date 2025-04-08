"""
Quick test script for ProfileScope

This script runs a simple test analysis to verify that the system is working properly.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the path so we can import the app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.analyzer import SocialMediaAnalyzer


def run_test_analysis():
    """Run a test analysis on a sample profile"""
    print("Starting ProfileScope test analysis...")

    # Initialize the analyzer
    analyzer = SocialMediaAnalyzer()

    # Test profile - using Twitter as it's more likely to have public data
    platform = "twitter"
    profile_id = "elonmusk"  # A public profile that's unlikely to disappear

    print(f"Analyzing {platform} profile: {profile_id}")

    try:
        # Run the analysis
        results = analyzer.analyze_profile(platform, profile_id)

        # Save the results to a file in the test_results directory
        os.makedirs("test_results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"test_results/test_{platform}_{profile_id}_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Test completed successfully! Results saved to: {output_file}")
        print("\nSummary of results:")

        # Print some key results
        if "content_analysis" in results:
            content = results["content_analysis"]
            if "personality_traits" in content:
                print("\nPersonality Traits:")
                for trait, value in content["personality_traits"].items():
                    print(f"  - {trait}: {value:.2f}")

            if "writing_style" in content:
                print("\nWriting Style:")
                style = content["writing_style"]
                for key in [
                    "complexity",
                    "formality",
                    "emotional_tone",
                    "vocabulary_diversity",
                ]:
                    if key in style:
                        print(f"  - {key}: {style[key]:.2f}")

        if (
            "authenticity_analysis" in results
            and "overall_authenticity" in results["authenticity_analysis"]
        ):
            auth = results["authenticity_analysis"]["overall_authenticity"]
            print(f"\nAuthenticity Score: {auth.get('score', 0):.2f}")

        return True
    except Exception as e:
        print(f"Error during test analysis: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_test_analysis()
    sys.exit(0 if success else 1)
