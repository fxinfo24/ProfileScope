from app.core.analyzer import SocialMediaAnalyzer
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def test_universal_capability():
    print("--- Testing Universal Platform Capability ---")
    analyzer = SocialMediaAnalyzer()
    
    # Test a newly supported platform (TikTok)
    platform = "tiktok"
    profile_id = "test_user"
    
    print(f"Attempting analysis for {profile_id} on {platform}...")
    try:
        results = analyzer.analyze_profile(platform, profile_id)
        print(f"SUCCESS: Analysis completed for {results['metadata']['platform']}")
        print(f"Logic used: {'Mock' if results['metadata'].get('is_mock_data') else 'Real'} Data")
        
        # Verify content analysis was triggered
        if "content_analysis" in results:
            print("SUCCESS: Content analysis found in results.")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_universal_capability()
