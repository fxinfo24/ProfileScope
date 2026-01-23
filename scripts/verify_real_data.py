from app.core.analyzer import SocialMediaAnalyzer
import logging
import json

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def test_real_data():
    print("--- Testing Real Data Capability ---")
    analyzer = SocialMediaAnalyzer()
    
    # Use a known, valid Twitter/X profile
    platform = "twitter"
    profile_id = "elonmusk"  # A profile that definitely exists
    
    print(f"Attempting analysis for @{profile_id} on {platform}...")
    try:
        results = analyzer.analyze_profile(platform, profile_id)
        
        # Check if we got real or mock data
        is_mock = results.get("metadata", {}).get("is_mock_data", False)
        is_real = results.get("metadata", {}).get("is_real_data", False)
        
        if is_real:
            print("✅ SUCCESS: Got REAL data from API!")
        elif is_mock:
            print("⚠️ FALLBACK: Used mock data (check API key or rate limits)")
            if "api_errors" in results.get("metadata", {}):
                print(f"   Reason: {results['metadata']['api_errors']}")
        else:
            print("✅ SUCCESS: Analysis completed (data source unclear)")
        
        print(f"\nPlatform: {results['metadata'].get('platform')}")
        print(f"Profile ID: {results['metadata'].get('profile_id')}")
        print(f"Collection Date: {results['metadata'].get('collection_date')}")
        
    except Exception as e:
        print(f"❌ FAILURE: {e}")

if __name__ == "__main__":
    test_real_data()
