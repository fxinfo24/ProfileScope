"""
ScrapeCreators API Client for Social Media Data Collection
Universal social media scraping using ScrapeCreators API
"""

import os
import requests
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ScrapeCreatorsError(Exception):
    """ScrapeCreators API related errors"""
    pass

class RateLimitError(Exception):
    """Rate limit exceeded error"""
    pass

class ScrapeCreatorsClient:
    """Enhanced client for ScrapeCreators API"""
    
    def __init__(self):
        self.api_key = os.getenv("SCRAPECREATORS_API_KEY")
        self.base_url = os.getenv("SCRAPECREATORS_BASE_URL", "https://api.scrapecreators.com")
        
        if not self.api_key or self.api_key == "your_scrapecreators_api_key_here":
            logger.warning("ScrapeCreators API key not configured")
            self.api_key = None
            
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ProfileScope/1.0"
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling"""
        if not self.api_key:
            raise ScrapeCreatorsError("API key not configured")
        
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 401:
                raise ScrapeCreatorsError("Invalid API key")
            elif response.status_code == 404:
                raise ScrapeCreatorsError("Profile not found")
            elif response.status_code != 200:
                raise ScrapeCreatorsError(f"API error: {response.status_code} - {response.text}")
                
            return response.json()
            
        except requests.RequestException as e:
            raise ScrapeCreatorsError(f"Request failed: {str(e)}")
    
    def get_twitter_profile(self, username: str) -> Dict[str, Any]:
        """Get Twitter profile data"""
        endpoint = f"twitter/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_twitter_data(response)
        except Exception as e:
            logger.error(f"Failed to get Twitter profile {username}: {e}")
            raise
    
    def get_instagram_profile(self, username: str) -> Dict[str, Any]:
        """Get Instagram profile data"""
        endpoint = f"instagram/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_instagram_data(response)
        except Exception as e:
            logger.error(f"Failed to get Instagram profile {username}: {e}")
            raise
    
    def get_linkedin_profile(self, username: str) -> Dict[str, Any]:
        """Get LinkedIn profile data"""
        endpoint = f"linkedin/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_linkedin_data(response)
        except Exception as e:
            logger.error(f"Failed to get LinkedIn profile {username}: {e}")
            raise
    
    def get_tiktok_profile(self, username: str) -> Dict[str, Any]:
        """Get TikTok profile data"""
        endpoint = f"tiktok/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_tiktok_data(response)
        except Exception as e:
            logger.error(f"Failed to get TikTok profile {username}: {e}")
            raise
    
    def get_youtube_profile(self, username: str) -> Dict[str, Any]:
        """Get YouTube profile data"""
        endpoint = f"youtube/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_youtube_data(response)
        except Exception as e:
            logger.error(f"Failed to get YouTube profile {username}: {e}")
            raise
    
    def get_snapchat_profile(self, username: str) -> Dict[str, Any]:
        """Get Snapchat profile data"""
        endpoint = f"snapchat/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_snapchat_data(response)
        except Exception as e:
            logger.error(f"Failed to get Snapchat profile {username}: {e}")
            raise
    
    def get_pinterest_profile(self, username: str) -> Dict[str, Any]:
        """Get Pinterest profile data"""
        endpoint = f"pinterest/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_pinterest_data(response)
        except Exception as e:
            logger.error(f"Failed to get Pinterest profile {username}: {e}")
            raise
    
    def get_reddit_profile(self, username: str) -> Dict[str, Any]:
        """Get Reddit profile data"""
        endpoint = f"reddit/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_reddit_data(response)
        except Exception as e:
            logger.error(f"Failed to get Reddit profile {username}: {e}")
            raise
    
    def get_github_profile(self, username: str) -> Dict[str, Any]:
        """Get GitHub profile data"""
        endpoint = f"github/profile/{username}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._normalize_github_data(response)
        except Exception as e:
            logger.error(f"Failed to get GitHub profile {username}: {e}")
            raise
    
    def get_twitter_posts(self, username: str, count: int = 20) -> List[Dict[str, Any]]:
        """Get Twitter posts"""
        endpoint = f"twitter/posts/{username}"
        params = {"count": count}
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            return [self._normalize_twitter_post(post) for post in response.get("posts", [])]
        except Exception as e:
            logger.error(f"Failed to get Twitter posts for {username}: {e}")
            raise
    
    def _normalize_twitter_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Twitter profile data to standard format"""
        return {
            "platform": "twitter",
            "id": data.get("id"),
            "username": data.get("username"),
            "display_name": data.get("name", data.get("display_name")),
            "bio": data.get("description", data.get("bio", "")),
            "location": data.get("location", ""),
            "followers_count": data.get("followers_count", 0),
            "following_count": data.get("following_count", 0),
            "posts_count": data.get("tweet_count", data.get("posts_count", 0)),
            "verified": data.get("verified", False),
            "created_at": data.get("created_at"),
            "profile_image_url": data.get("profile_image_url"),
            "banner_url": data.get("banner_url"),
            "website_url": data.get("url"),
            "raw_data": data  # Keep original data for reference
        }
    
    def _normalize_instagram_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Instagram profile data to standard format"""
        return {
            "platform": "instagram",
            "id": data.get("id"),
            "username": data.get("username"),
            "display_name": data.get("full_name", data.get("name")),
            "bio": data.get("biography", ""),
            "location": "",  # Instagram doesn't provide location in profile
            "followers_count": data.get("followers_count", 0),
            "following_count": data.get("following_count", 0),
            "posts_count": data.get("media_count", 0),
            "verified": data.get("is_verified", False),
            "created_at": None,  # Instagram doesn't provide creation date
            "profile_image_url": data.get("profile_pic_url"),
            "website_url": data.get("external_url"),
            "is_private": data.get("is_private", False),
            "is_business": data.get("is_business_account", False),
            "raw_data": data
        }
    
    def _normalize_linkedin_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize LinkedIn profile data to standard format"""
        return {
            "platform": "linkedin",
            "id": data.get("id"),
            "username": data.get("username", data.get("public_identifier")),
            "display_name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            "bio": data.get("summary", data.get("headline", "")),
            "location": data.get("location", ""),
            "followers_count": data.get("followers_count", 0),
            "connections_count": data.get("connections_count", 0),
            "posts_count": 0,  # LinkedIn doesn't provide post count in profile
            "verified": False,  # LinkedIn doesn't have verification badges
            "profile_image_url": data.get("profile_image_url"),
            "industry": data.get("industry"),
            "current_position": data.get("current_position"),
            "company": data.get("company"),
            "raw_data": data
        }
    
    def _normalize_tiktok_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize TikTok profile data to standard format"""
        return {
            "platform": "tiktok",
            "id": data.get("id"),
            "username": data.get("unique_id", data.get("username")),
            "display_name": data.get("nickname", data.get("display_name")),
            "bio": data.get("signature", ""),
            "followers_count": data.get("follower_count", 0),
            "following_count": data.get("following_count", 0),
            "posts_count": data.get("video_count", 0),
            "likes_count": data.get("heart_count", 0),
            "verified": data.get("verified", False),
            "profile_image_url": data.get("avatar_larger"),
            "is_private": data.get("secret", False),
            "raw_data": data
        }
    
    def _normalize_youtube_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize YouTube profile data to standard format"""
        return {
            "platform": "youtube",
            "id": data.get("id"),
            "username": data.get("custom_url", data.get("username")),
            "display_name": data.get("title", data.get("name")),
            "bio": data.get("description", ""),
            "subscribers_count": data.get("subscriber_count", 0),
            "video_count": data.get("video_count", 0),
            "view_count": data.get("view_count", 0),
            "verified": data.get("verified", False),
            "profile_image_url": data.get("thumbnail_url"),
            "banner_url": data.get("banner_url"),
            "country": data.get("country"),
            "created_at": data.get("published_at"),
            "raw_data": data
        }
    
    def _normalize_snapchat_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Snapchat profile data to standard format"""
        return {
            "platform": "snapchat",
            "id": data.get("id"),
            "username": data.get("username"),
            "display_name": data.get("display_name"),
            "bio": data.get("bio", ""),
            "snapcode_url": data.get("snapcode_url"),
            "profile_image_url": data.get("profile_image_url"),
            "verified": data.get("verified", False),
            "raw_data": data
        }
    
    def _normalize_pinterest_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Pinterest profile data to standard format"""
        return {
            "platform": "pinterest",
            "id": data.get("id"),
            "username": data.get("username"),
            "display_name": data.get("full_name", data.get("name")),
            "bio": data.get("about", ""),
            "followers_count": data.get("follower_count", 0),
            "following_count": data.get("following_count", 0),
            "board_count": data.get("board_count", 0),
            "pin_count": data.get("pin_count", 0),
            "verified": data.get("verified", False),
            "profile_image_url": data.get("image_medium_url"),
            "website_url": data.get("website_url"),
            "location": data.get("location"),
            "raw_data": data
        }
    
    def _normalize_reddit_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Reddit profile data to standard format"""
        return {
            "platform": "reddit",
            "id": data.get("id"),
            "username": data.get("name"),
            "display_name": data.get("subreddit", {}).get("display_name"),
            "bio": data.get("subreddit", {}).get("public_description", ""),
            "comment_karma": data.get("comment_karma", 0),
            "link_karma": data.get("link_karma", 0),
            "total_karma": data.get("total_karma", 0),
            "created_at": data.get("created_utc"),
            "verified": data.get("verified", False),
            "profile_image_url": data.get("icon_img"),
            "is_gold": data.get("is_gold", False),
            "is_mod": data.get("is_mod", False),
            "raw_data": data
        }
    
    def _normalize_github_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize GitHub profile data to standard format"""
        return {
            "platform": "github",
            "id": data.get("id"),
            "username": data.get("login"),
            "display_name": data.get("name"),
            "bio": data.get("bio", ""),
            "location": data.get("location"),
            "followers_count": data.get("followers", 0),
            "following_count": data.get("following", 0),
            "public_repos": data.get("public_repos", 0),
            "public_gists": data.get("public_gists", 0),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "profile_image_url": data.get("avatar_url"),
            "website_url": data.get("blog"),
            "company": data.get("company"),
            "hireable": data.get("hireable", False),
            "raw_data": data
        }
    
    def _normalize_twitter_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Twitter post data"""
        return {
            "id": post.get("id"),
            "text": post.get("text", post.get("full_text", "")),
            "created_at": post.get("created_at"),
            "likes_count": post.get("favorite_count", post.get("likes", 0)),
            "retweets_count": post.get("retweet_count", post.get("retweets", 0)),
            "replies_count": post.get("reply_count", post.get("replies", 0)),
            "is_retweet": post.get("is_retweet", False),
            "media": post.get("media", []),
            "hashtags": post.get("hashtags", []),
            "mentions": post.get("mentions", []),
            "raw_data": post
        }

# Fallback mock client for testing when API key is not available
class MockScrapeCreatorsClient:
    """Mock client for testing without API key"""
    
    def get_twitter_profile(self, username: str) -> Dict[str, Any]:
        return {
            "platform": "twitter",
            "username": username,
            "display_name": f"Mock {username.title()}",
            "bio": f"This is a mock profile for {username}",
            "followers_count": 10000,
            "following_count": 500,
            "posts_count": 1000,
            "verified": False,
            "created_at": "2020-01-01T00:00:00Z"
        }
    
    def get_twitter_posts(self, username: str, count: int = 20) -> List[Dict[str, Any]]:
        return [
            {
                "id": f"mock_{i}",
                "text": f"Mock tweet {i} from {username}",
                "likes_count": 10 * i,
                "retweets_count": 5 * i,
                "replies_count": 2 * i
            }
            for i in range(1, count + 1)
        ]

def get_scrape_client() -> ScrapeCreatorsClient:
    """Get ScrapeCreators client instance"""
    client = ScrapeCreatorsClient()
    
    # Return mock client if API key not configured
    if not client.api_key:
        logger.warning("Using mock ScrapeCreators client - add real API key for production")
        return MockScrapeCreatorsClient()
    
    return client