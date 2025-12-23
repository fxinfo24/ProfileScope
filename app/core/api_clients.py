"""
ProfileScope: Social Media API Clients
Handles authentication and API calls to various social media platforms
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Generator, List
from datetime import datetime, timedelta
from requests.exceptions import RequestException
from ..utils.config import load_config

# Optional imports for social media APIs
try:
    import tweepy
except ImportError:
    tweepy = None

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.user import User
    from facebook_business.adobjects.post import Post
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    # Fallback for when facebook_business is not available
    class FacebookAdsApi:
        pass
    class User:
        pass
    class Post:
        pass
    class FacebookRequestError(Exception):
        pass

logger = logging.getLogger("ProfileScope.APIClients")


class RateLimitExceededError(Exception):
    """Exception raised when API rate limit is exceeded"""

    pass


class RateLimiter:
    """Rate limiter for API calls"""

    def __init__(self, calls: int = 100, period: int = 60):
        """
        Initialize rate limiter

        Args:
            calls: Maximum number of calls allowed in the period
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.timestamps = []

    def check(self):
        """Check if a call can be made without exceeding rate limits"""
        now = time.time()

        # Remove timestamps that are older than the period
        self.timestamps = [t for t in self.timestamps if now - t < self.period]

        # If we have reached the limit, raise an exception
        if len(self.timestamps) >= self.calls:
            wait_time = self.timestamps[0] + self.period - now
            if wait_time > 0:
                logger.info(
                    f"Rate limit reached. Would need to wait {wait_time:.2f} seconds"
                )
                raise RateLimitExceededError(
                    f"Rate limit exceeded. Try again in {wait_time:.1f} seconds."
                )

        # Add current timestamp and proceed
        self.timestamps.append(now)

    def __call__(self, func):
        """Decorator for rate limiting functions"""

        def wrapper(*args, **kwargs):
            self.check()
            return func(*args, **kwargs)

        return wrapper


class RetryHandler:
    """Handles retrying failed API calls"""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5):
        """
        Initialize retry handler

        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Multiplicative factor for backoff between retries
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def __call__(self, func):
        """Decorator for handling retries"""

        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= self.max_retries:
                try:
                    return func(*args, **kwargs)
                except (
                    RequestException,
                    FacebookRequestError,
                ) + ((tweepy.TweepyException,) if tweepy else ()) as e:
                    retries += 1
                    if retries > self.max_retries:
                        logger.error(f"Max retries ({self.max_retries}) exceeded")
                        raise

                    wait_time = self.backoff_factor * (2 ** (retries - 1))
                    logger.info(
                        f"Retry {retries}/{self.max_retries} after {wait_time:.1f}s. Error: {str(e)}"
                    )
                    time.sleep(wait_time)

        return wrapper


class TwitterClient:
    """Twitter/X API client wrapper"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Twitter API client"""
        import os
        from dotenv import load_dotenv
        
        # Check if tweepy is available
        if tweepy is None:
            logger.warning("tweepy not installed - Twitter client will not be functional")
            self._api = None
            self._client_v2 = None
            self.rate_limiter = RateLimiter(calls=300, period=900)
            self.retry_handler = RetryHandler()
            return
        
        # Load environment variables
        load_dotenv()
        
        if config is None:
            config = {}
        
        # Try environment variables first, then config file
        twitter_config = config.get("twitter", {})
        
        self.api_key = os.getenv("TWITTER_API_KEY") or twitter_config.get("api_key")
        self.api_secret = os.getenv("TWITTER_API_SECRET") or twitter_config.get("api_secret")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN") or twitter_config.get("access_token")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET") or twitter_config.get("access_token_secret")
        
        self.rate_limiter = RateLimiter(calls=300, period=900)  # Twitter API v2: 300/15min
        self.retry_handler = RetryHandler()

        if self.api_key and self.api_secret and self.access_token and self.access_token_secret:
            try:
                # Using OAuth1UserHandler for API v1.1
                auth = tweepy.OAuth1UserHandler(
                    self.api_key,
                    self.api_secret,
                    self.access_token,
                    self.access_token_secret,
                )
                self._api = tweepy.API(auth, wait_on_rate_limit=True)
                
                # Twitter API v2 Client
                self._client_v2 = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )
                
                # Test connection
                self._test_connection()
                logger.info("Twitter API client initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Twitter API client: {str(e)}")
                self._api = None
                self._client_v2 = None
        else:
            logger.warning("Twitter API credentials not found in environment or config")
            self._api = None
            self._client_v2 = None

    def _test_connection(self):
        """Test API connection"""
        try:
            if self._api:
                user = self._api.verify_credentials()
                print(f"✅ Twitter API v1.1 verified: @{user.screen_name}")
            if self._client_v2:
                me = self._client_v2.get_me()
                if me.data:
                    print(f"✅ Twitter API v2 verified: @{me.data.username}")
        except Exception as e:
            logger.warning(f"Twitter API connection test failed: {e}")

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate Twitter API configuration (deprecated - now uses environment variables)"""
        pass  # No longer needed as we use environment variables

    @RetryHandler()
    @RateLimiter(50)
    def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get Twitter user profile data using API v2"""
        if not self._client_v2:
            logger.error("Twitter API v2 client not initialized")
            return None

        try:
            self.rate_limiter.check()
            
            # Use API v2 for enhanced user data
            response = self._client_v2.get_user(
                username=username,
                user_fields=['created_at', 'description', 'entities', 'location', 'pinned_tweet_id',
                           'profile_image_url', 'protected', 'public_metrics', 'url', 'verified',
                           'verified_type', 'withheld']
            )
            
            if not response.data:
                logger.error(f"User @{username} not found")
                return None
                
            user = response.data
            metrics = user.public_metrics
            
            profile_data = {
                "id": user.id,
                "username": user.username,
                "display_name": user.name,
                "bio": user.description or "",
                "location": user.location or "",
                "followers_count": metrics['followers_count'],
                "following_count": metrics['following_count'], 
                "posts_count": metrics['tweet_count'],
                "listed_count": metrics['listed_count'],
                "verified": user.verified or False,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "profile_image_url": user.profile_image_url,
                "url": user.url,
                "protected": user.protected or False,
                "pinned_tweet_id": user.pinned_tweet_id,
                "platform": "twitter"
            }
            
            # Add verified type if available
            if hasattr(user, 'verified_type') and user.verified_type:
                profile_data["verified_type"] = user.verified_type
                
            return profile_data
            
        except RateLimitExceededError:
            logger.warning("Twitter API rate limit exceeded")
            raise
        except Exception as e:
            logger.error(f"Failed to get Twitter user profile: {str(e)}")
            return None

    @RetryHandler()
    @RateLimiter(100)
    def get_user_timeline(
        self, username: str, count: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user's tweets"""
        if not self._api:
            logger.error("Twitter API client not initialized")
            return []

        try:
            tweets = self._api.user_timeline(
                screen_name=username, count=count, tweet_mode="extended"
            )

            results = []
            for tweet in tweets:
                tweet_data = {
                    "id": tweet.id_str,
                    "text": tweet.full_text,
                    "created_at": tweet.created_at.isoformat(),
                    "retweet_count": tweet.retweet_count,
                    "favorite_count": tweet.favorite_count,
                    "hashtags": [
                        tag["text"] for tag in tweet.entities.get("hashtags", [])
                    ],
                    "mentions": [
                        mention["screen_name"]
                        for mention in tweet.entities.get("user_mentions", [])
                    ],
                }

                # Add media if available
                if "media" in tweet.entities:
                    tweet_data["media"] = [
                        media["media_url_https"] for media in tweet.entities["media"]
                    ]

                # Add URLs if available
                if "urls" in tweet.entities and tweet.entities["urls"]:
                    tweet_data["urls"] = [
                        url["expanded_url"] for url in tweet.entities["urls"]
                    ]

                results.append(tweet_data)

            return results
        except Exception as e:
            logger.error(f"Failed to get Twitter timeline: {str(e)}")
            return []

    @property
    def client(self):
        """Return the underlying API client for compatibility with tests"""
        return self._api


class FacebookClient:
    """Facebook Business API client wrapper"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Facebook API client"""
        self._validate_config(config)
        self.rate_limiter = RateLimiter(
            calls=200
        )  # 200 calls per hour is a safe default
        self.retry_handler = RetryHandler()
        self._api = None  # Private API client attribute

        try:
            FacebookAdsApi.init(
                app_id=config["app_id"],
                app_secret=config["app_secret"],
                access_token=config["access_token"],
            )
            # Store the instance directly instead of using get_default()
            self._api = FacebookAdsApi.get_default_api()
            logger.info("Facebook API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Facebook API client: {str(e)}")
            self._api = None

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate Facebook API configuration"""
        required_keys = ["app_id", "app_secret", "access_token"]
        missing_keys = [key for key in required_keys if not config.get(key)]

        if missing_keys:
            raise ValueError(
                f"Missing Facebook API credentials: {', '.join(missing_keys)}"
            )

    @RetryHandler()
    @RateLimiter(200)
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get Facebook user profile data"""
        if not self._api:
            logger.error("Facebook API client not initialized")
            return None

        try:
            user = User(user_id)
            fields = [
                "id",
                "name",
                "about",
                "location",
                "link",
                "picture",
                "created_time",
            ]
            profile = user.api_get(fields=fields)

            return {
                "id": profile.get("id"),
                "name": profile.get("name"),
                "bio": profile.get("about"),
                "location": (
                    profile.get("location", {}).get("name")
                    if profile.get("location")
                    else None
                ),
                "profile_url": profile.get("link"),
                "created_at": profile.get("created_time"),
                "profile_image_url": (
                    profile.get("picture", {}).get("data", {}).get("url")
                    if profile.get("picture")
                    else None
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get Facebook user profile: {str(e)}")
            return None

    @RetryHandler()
    @RateLimiter(200)
    def get_user_posts(
        self, user_id: str, limit: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """Get user's Facebook posts with pagination"""
        if not self._api:
            logger.error("Facebook API client not initialized")
            yield from []
            return

        try:
            user = User(user_id)
            fields = [
                "id",
                "message",
                "created_time",
                "type",
                "permalink_url",
                "shares",
                "reactions.summary(true)",
            ]

            posts = user.get_posts(fields=fields, limit=min(100, limit))
            count = 0

            while posts and count < limit:
                for post in posts:
                    if count >= limit:
                        break

                    # Handle both Post objects and raw post data
                    if isinstance(post, dict):
                        post_data = post
                    else:
                        try:
                            post_data = post.api_get()
                        except:
                            # If api_get() fails or doesn't exist, try to extract data directly
                            if hasattr(post, "export_all_data"):
                                post_data = post.export_all_data()
                            elif hasattr(post, "__dict__"):
                                post_data = post.__dict__
                            else:
                                # Last resort, treat post as the data itself
                                post_data = post

                    yield self._format_post(post_data)
                    count += 1

                # Get next page if available
                if (
                    count < limit
                    and hasattr(posts, "has_next_page")
                    and posts.has_next_page()
                ):
                    posts = posts.get_next_page()
                else:
                    break

        except Exception as e:
            logger.error(f"Failed to get Facebook posts: {str(e)}")

    def _format_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Format a Facebook post object"""
        return {
            "id": post.get("id"),
            "text": post.get("message"),
            "created_at": post.get("created_time"),
            "type": post.get("type"),
            "url": post.get("permalink_url"),
            "shares": (
                post.get("shares", {}).get("count", 0) if post.get("shares") else 0
            ),
            "reactions": (
                post.get("reactions", {}).get("summary", {}).get("total_count", 0)
                if post.get("reactions")
                else 0
            ),
        }

    @property
    def client(self):
        """Return the underlying API client for compatibility with tests"""
        return self._api
