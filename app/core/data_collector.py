"""
ProfileScope: Data Collection Module
Handles collecting profile data from various social media platforms
"""

import os
import json
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import tweepy
try:
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    # Fallback for when facebook_business is not available
    class FacebookRequestError(Exception):
        pass
import requests
import time

from ..utils.config import load_config, ConfigError
from .api_clients import TwitterClient, FacebookClient, RateLimitExceededError

# Setup module logger
logger = logging.getLogger("ProfileScope.DataCollector")


class DataCollectionError(Exception):
    """Base exception for data collection errors"""

    pass


class APIError(DataCollectionError):
    """Exception raised when an API request fails"""

    def __init__(self, message: str, platform: str, error_code: int = None):
        self.platform = platform
        self.error_code = error_code
        super().__init__(f"{platform.capitalize()} API error: {message}")


class RateLimitError(DataCollectionError):
    """Exception raised when API rate limit is exceeded"""

    def __init__(self, platform: str, reset_time: Optional[datetime] = None):
        self.platform = platform
        self.reset_time = reset_time
        message = f"{platform.capitalize()} API rate limit exceeded"
        if reset_time:
            message += f". Try again after {reset_time}"
        super().__init__(message)


class AuthenticationError(DataCollectionError):
    """Exception raised when authentication fails"""

    def __init__(self, message: str, platform: str):
        self.platform = platform
        super().__init__(f"{platform.capitalize()} authentication error: {message}")


class DataCollector:
    """Collects data from social media platforms."""

    def __init__(self, platform: str, rate_limit: int, use_mock_data: bool = False):
        """
        Initialize data collector for a specific platform

        Args:
            platform: Social media platform name
            rate_limit: API rate limit per minute
            use_mock_data: If True, use mock data instead of API calls
        """
        self.platform = platform.lower()
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.use_mock_data = use_mock_data
        self.logger = logging.getLogger(f"ProfileScope.DataCollector.{platform}")
        self.error_messages = []  # Store error messages

        # Initialize API clients if not using mock data
        if not self.use_mock_data:
            try:
                config = load_config()
                if "api" in config:
                    if platform == "twitter" and "twitter" in config["api"]:
                        self.twitter_client = TwitterClient(config["api"]["twitter"])
                    elif platform == "facebook" and "facebook" in config["api"]:
                        self.facebook_client = FacebookClient(config["api"]["facebook"])
            except (ConfigError, ValueError) as e:
                error_msg = f"Could not initialize API clients: {str(e)}"
                self.logger.warning(error_msg)
                self.error_messages.append(error_msg)
                self.use_mock_data = True
                self.logger.info("Falling back to mock data generation")

    def collect_profile_data(self, profile_id: str) -> Dict[str, Any]:
        """
        Collect complete profile data from the platform

        Args:
            profile_id: Username or ID of the profile to analyze

        Returns:
            Dictionary containing profile data
        """
        self._respect_rate_limit()

        if self.platform == "twitter":
            return self._collect_twitter_data(profile_id)
        elif self.platform == "facebook":
            return self._collect_facebook_data(profile_id)
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")

    def collect_posts(self, profile_id: str, count: int = 100) -> List[Dict[str, Any]]:
        """
        Collect recent posts from a profile

        Args:
            profile_id: Username or ID of the profile
            count: Number of posts to collect

        Returns:
            List of post data dictionaries
        """
        self._respect_rate_limit()

        if self.platform == "twitter":
            return self._collect_twitter_posts(profile_id, count)
        elif self.platform == "facebook":
            return self._collect_facebook_posts(profile_id, count)
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")

    def _respect_rate_limit(self) -> None:
        """Ensure we don't exceed the platform's API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        # If we're making requests too quickly, pause
        if time_since_last < (60 / self.rate_limit):
            sleep_time = (60 / self.rate_limit) - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _collect_twitter_data(self, profile_id: str) -> Dict[str, Any]:
        """Collect Twitter profile data"""
        self.logger.info(f"Collecting Twitter data for {profile_id}")

        # Use mock data if specified or if real data collection fails
        try:
            if not self.use_mock_data and hasattr(self, "twitter_client"):
                # Try to get real profile data from Twitter API
                self.logger.info("Attempting to get real Twitter profile data")
                profile = self.twitter_client.get_user_profile(profile_id)

                if profile:
                    # Successfully retrieved real profile data
                    profile_data = {
                        "user_id": profile["id"],
                        "screen_name": profile["username"],
                        "follower_count": profile["followers_count"],
                        "following_count": profile["following_count"],
                        "created_at": profile["created_at"],
                        "verified": profile["verified"],
                        "description": profile["bio"],
                        "profile_image_url": profile["profile_image_url"],
                        "posts": self._collect_twitter_posts(profile_id, 100),
                        "metadata": {
                            "platform": "twitter",
                            "collection_date": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "is_real_data": True,
                        },
                    }
                    return profile_data

                # If we got here, real data retrieval failed
                error_msg = "Failed to get real Twitter data, using mock data"
                self.logger.warning(error_msg)
                self.error_messages.append(error_msg)
        except Exception as e:
            error_detail = str(e)
            # Capture specific API error codes and messages if available
            if hasattr(e, "response") and hasattr(e.response, "status_code"):
                status_code = e.response.status_code
                error_msg = f"Twitter API error {status_code}: {error_detail}"
            else:
                error_msg = f"Error retrieving real Twitter data: {error_detail}"

            self.logger.warning(error_msg)
            self.error_messages.append(error_msg)
            self.logger.info("Falling back to mock data generation")

        # Generate mock data if real data collection failed or was not requested
        profile_data = {
            "user_id": profile_id,
            "screen_name": profile_id,
            "follower_count": 1000,
            "following_count": 500,
            "created_at": "2020-01-01T00:00:00Z",
            "verified": False,
            "description": "This is a placeholder Twitter profile description",
            "profile_image_url": f"https://example.com/{profile_id}/profile.jpg",
            "posts": self._collect_twitter_posts(profile_id, 100),
            "metadata": {
                "platform": "twitter",
                "collection_date": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "is_mock_data": True,
                "api_errors": self.error_messages if self.error_messages else None,
            },
        }

        return profile_data

    def _collect_facebook_data(self, profile_id: str) -> Dict[str, Any]:
        """Collect Facebook profile data"""
        self.logger.info(f"Collecting Facebook data for {profile_id}")

        # Use mock data if specified or if real data collection fails
        try:
            if not self.use_mock_data and hasattr(self, "facebook_client"):
                # Try to get real profile data from Facebook API
                self.logger.info("Attempting to get real Facebook profile data")
                profile = self.facebook_client.get_user_profile(profile_id)

                if profile:
                    # Create posts list from generator
                    posts = []
                    for post in self.facebook_client.get_user_posts(profile_id, 100):
                        posts.append(post)
                        if len(posts) >= 100:
                            break

                    # Successfully retrieved real profile data
                    profile_data = {
                        "user_id": profile["id"],
                        "name": profile["name"],
                        "created_at": profile.get("created_at", "Unknown"),
                        "bio": profile.get("bio", ""),
                        "location": profile.get("location", ""),
                        "profile_url": profile.get("profile_url", ""),
                        "profile_image_url": profile.get("profile_image_url", ""),
                        "posts": posts,
                        "metadata": {
                            "platform": "facebook",
                            "collection_date": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "is_real_data": True,
                        },
                    }
                    return profile_data

                # If we got here, real data retrieval failed
                error_msg = "Failed to get real Facebook data, using mock data"
                self.logger.warning(error_msg)
                self.error_messages.append(error_msg)
        except Exception as e:
            error_detail = str(e)
            # Capture specific Facebook API error details if available
            if isinstance(e, FacebookRequestError):
                error_msg = (
                    f"Facebook API error {e.api_error_code()}: {e.api_error_message()}"
                )
            else:
                error_msg = f"Error retrieving real Facebook data: {error_detail}"

            self.logger.warning(error_msg)
            self.error_messages.append(error_msg)
            self.logger.info("Falling back to mock data generation")

        # Generate mock data if real data collection failed or was not requested
        profile_data = {
            "user_id": profile_id,
            "name": f"{profile_id} User",
            "friend_count": 500,
            "created_at": "2018-01-01T00:00:00Z",
            "verified": False,
            "description": "This is a placeholder Facebook profile description",
            "profile_image_url": f"https://example.com/{profile_id}/profile.jpg",
            "posts": self._collect_facebook_posts(profile_id, 100),
            "metadata": {
                "platform": "facebook",
                "collection_date": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "is_mock_data": True,
                "api_errors": self.error_messages if self.error_messages else None,
            },
        }

        return profile_data

    def _collect_twitter_posts(
        self, profile_id: str, count: int
    ) -> List[Dict[str, Any]]:
        """Collect posts from Twitter profile"""
        # Try to get real posts if we're not using mock data
        try:
            if not self.use_mock_data and hasattr(self, "twitter_client"):
                self.logger.info(
                    f"Attempting to get real Twitter posts for {profile_id}"
                )
                real_posts = self.twitter_client.get_user_timeline(profile_id, count)

                if real_posts:
                    # Convert the tweet data to our format
                    formatted_posts = []
                    for post in real_posts:
                        formatted_posts.append(
                            {
                                "post_id": post["id"],
                                "content": post["text"],
                                "created_at": post["created_at"],
                                "likes": post["favorite_count"],
                                "retweets": post["retweet_count"],
                                "hashtags": post["hashtags"],
                                "urls": post.get("urls", []),
                                "media": post.get("media", []),
                                "mentions": post.get("mentions", []),
                                "is_real_data": True,
                            }
                        )
                    return formatted_posts

                # If we got here, real posts retrieval failed
                error_msg = "Failed to get real Twitter posts, using mock data"
                self.logger.warning(error_msg)
                self.error_messages.append(error_msg)
        except Exception as e:
            error_detail = str(e)
            # Capture specific API error codes and messages if available
            if hasattr(e, "response") and hasattr(e.response, "status_code"):
                status_code = e.response.status_code
                error_msg = f"Twitter API error {status_code} when retrieving posts: {error_detail}"
            else:
                error_msg = f"Error retrieving real Twitter posts: {error_detail}"

            self.logger.warning(error_msg)
            self.error_messages.append(error_msg)

        # Generate mock data if real data collection failed or was not requested
        posts = []
        for i in range(min(count, 20)):  # Limit to 20 for sample data
            posts.append(
                {
                    "post_id": f"{profile_id}_post_{i}",
                    "content": f"This is sample tweet #{i} content for testing",
                    "created_at": f"2023-01-{i+1:02d}T12:00:00Z",
                    "likes": i * 5,
                    "retweets": i * 2,
                    "replies": i,
                    "hashtags": [
                        f"#{tag}" for tag in ["sample", "test", "placeholder"]
                    ],
                    "is_mock_data": True,
                }
            )
        return posts

    def _collect_facebook_posts(
        self, profile_id: str, count: int
    ) -> List[Dict[str, Any]]:
        """Collect posts from Facebook profile"""
        # Try to get real posts if we're not using mock data
        try:
            if not self.use_mock_data and hasattr(self, "facebook_client"):
                self.logger.info(
                    f"Attempting to get real Facebook posts for {profile_id}"
                )

                # Get posts from the generator
                real_posts = []
                for post in self.facebook_client.get_user_posts(profile_id, count):
                    real_posts.append(post)
                    if len(real_posts) >= count:
                        break

                if real_posts:
                    # Convert the post data to our format
                    formatted_posts = []
                    for post in real_posts:
                        formatted_posts.append(
                            {
                                "post_id": post["id"],
                                "content": post["text"] if "text" in post else "",
                                "created_at": post["created_at"],
                                "likes": post.get("reactions", 0),
                                "comments": 0,  # We don't have this in the API response
                                "shares": post.get("shares", 0),
                                "url": post.get("url", ""),
                                "type": post.get("type", ""),
                                "is_real_data": True,
                            }
                        )
                    return formatted_posts

                # If we got here, real posts retrieval failed
                error_msg = "Failed to get real Facebook posts, using mock data"
                self.logger.warning(error_msg)
                self.error_messages.append(error_msg)
        except Exception as e:
            error_detail = str(e)
            # Capture specific Facebook API error details if available
            if isinstance(e, FacebookRequestError):
                error_msg = f"Facebook API error {e.api_error_code()} when retrieving posts: {e.api_error_message()}"
            else:
                error_msg = f"Error retrieving real Facebook posts: {error_detail}"

            self.logger.warning(error_msg)
            self.error_messages.append(error_msg)

        # Generate mock data if real data collection failed or was not requested
        posts = []
        for i in range(min(count, 20)):  # Limit to 20 for sample data
            posts.append(
                {
                    "post_id": f"{profile_id}_post_{i}",
                    "content": f"This is sample Facebook post #{i} content for testing",
                    "created_at": f"2023-02-{i+1:02d}T14:00:00Z",
                    "likes": i * 10,
                    "comments": i * 3,
                    "shares": i,
                    "tags": [f"{tag}" for tag in ["sample", "test", "placeholder"]],
                    "is_mock_data": True,
                }
            )
        return posts
