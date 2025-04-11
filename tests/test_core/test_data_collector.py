"""Tests for the data collector module"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tweepy
import json
from facebook_business.exceptions import FacebookRequestError

from app.core.data_collector import (
    DataCollector,
    APIError,
    RateLimitError,
    AuthenticationError,
    DataCollectionError,
)
from app.utils.config import ConfigError

# Mock Data
MOCK_TWITTER_PROFILE = {
    "id": "123456",
    "username": "testuser",
    "name": "Test User",
    "bio": "Test bio",
    "location": "Test City",
    "profile_url": "https://twitter.com/testuser",
    "created_at": datetime.now().isoformat(),
    "verified": True,
    "followers_count": 1000,
    "following_count": 500,
    "tweets_count": 1500,
    "profile_image_url": "https://example.com/image.jpg",
}

MOCK_TWITTER_POST = {
    "id": "tweet123",
    "text": "Test tweet",
    "created_at": datetime.now().isoformat(),
    "retweet_count": 10,
    "favorite_count": 20,
    "reply_count": 5,
    "is_retweet": False,
    "hashtags": ["test"],
    "mentions": ["mentioned_user"],
    "urls": ["https://example.com"],
    "media": ["https://example.com/media.jpg"],
}

MOCK_FACEBOOK_PROFILE = {
    "id": "123456",
    "name": "Test User",
    "bio": "Test bio",
    "location": "Test City",
    "profile_url": "https://facebook.com/testuser",
    "created_at": datetime.now().isoformat(),
    "profile_image_url": "https://example.com/image.jpg",
}

MOCK_FACEBOOK_POST = {
    "id": "post123",
    "text": "Test post",
    "created_at": datetime.now().isoformat(),
    "type": "status",
    "url": "https://facebook.com/post123",
    "shares": 10,
    "reactions": 20,
}


@pytest.fixture
def mock_twitter_client():
    """Mock Twitter API client"""
    with patch("app.core.data_collector.TwitterClient") as MockClient:
        mock_client = Mock()
        mock_client.get_user_profile.return_value = MOCK_TWITTER_PROFILE
        mock_client.get_user_timeline.return_value = [MOCK_TWITTER_POST] * 5
        MockClient.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_facebook_client():
    """Mock Facebook API client"""
    with patch("app.core.data_collector.FacebookClient") as MockClient:
        mock_client = Mock()
        mock_client.get_user_profile.return_value = MOCK_FACEBOOK_PROFILE
        mock_client.get_user_posts.return_value = [MOCK_FACEBOOK_POST] * 3
        MockClient.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_config():
    """Mock configuration loader"""
    with patch("app.core.data_collector.load_config") as mock_load_config:
        mock_load_config.return_value = {
            "api": {
                "twitter": {"api_key": "test_key", "api_secret": "test_secret"},
                "facebook": {"app_id": "test_app_id", "app_secret": "test_secret"},
            }
        }
        yield mock_load_config.return_value


def test_data_collector_initialization(mock_config):
    """Test DataCollector initialization"""
    collector = DataCollector("twitter", rate_limit=100)
    assert collector.platform == "twitter"
    assert collector.rate_limit == 100


def test_invalid_platform():
    """Test initialization with invalid platform"""
    with pytest.raises(ValueError) as exc_info:
        collector = DataCollector("invalid_platform", rate_limit=100)
        collector.collect_profile_data("test_user")

    assert "Unsupported platform" in str(exc_info.value)


@patch("app.core.data_collector.TwitterClient")
def test_collect_twitter_data(mock_twitter_client_class, mock_config):
    """Test collecting Twitter profile data"""
    # Setup the mock
    mock_twitter_client = Mock()
    mock_twitter_client.get_user_profile.return_value = MOCK_TWITTER_PROFILE
    mock_twitter_client.get_user_timeline.return_value = [MOCK_TWITTER_POST] * 5
    mock_twitter_client_class.return_value = mock_twitter_client

    # Create a collector with mocked use_mock_data = True to ensure we use mock data
    collector = DataCollector("twitter", rate_limit=100, use_mock_data=True)
    profile_data = collector.collect_profile_data("test_user")

    assert profile_data["user_id"] == "test_user"
    assert "posts" in profile_data
    assert "metadata" in profile_data
    assert profile_data["metadata"]["platform"] == "twitter"


@patch("app.core.data_collector.FacebookClient")
def test_collect_facebook_data(mock_facebook_client_class, mock_config):
    """Test collecting Facebook profile data"""
    # Setup the mock
    mock_facebook_client = Mock()
    mock_facebook_client.get_user_profile.return_value = MOCK_FACEBOOK_PROFILE
    mock_facebook_client.get_user_posts.return_value = [MOCK_FACEBOOK_POST] * 3
    mock_facebook_client_class.return_value = mock_facebook_client

    # Create a collector with mocked use_mock_data = True to ensure we use mock data
    collector = DataCollector("facebook", rate_limit=100, use_mock_data=True)
    profile_data = collector.collect_profile_data("test_user")

    assert profile_data["user_id"] == "test_user"
    assert "posts" in profile_data
    assert "metadata" in profile_data
    assert profile_data["metadata"]["platform"] == "facebook"


def test_mock_data_generation():
    """Test that mock data is generated correctly"""
    collector = DataCollector("twitter", rate_limit=100)
    posts = collector._collect_twitter_posts("test_user", 10)

    assert len(posts) == 10
    assert all(isinstance(post, dict) for post in posts)
    assert all("post_id" in post for post in posts)
    assert all("content" in post for post in posts)
