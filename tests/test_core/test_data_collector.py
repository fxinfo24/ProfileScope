"""Tests for the data collector module"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import tweepy
import requests
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

MOCK_TWITTER_CONFIG = {
    "api_key": "test_key",
    "api_secret": "test_secret",
    "access_token": "test_token",
    "access_token_secret": "test_token_secret",
}

MOCK_FACEBOOK_CONFIG = {
    "app_id": "test_app_id",
    "app_secret": "test_app_secret",
    "access_token": "test_access_token",
}


# Helper function to create mock responses for tweepy exceptions
def create_mock_tweepy_response(status_code=429, reason="Rate limit exceeded"):
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = status_code
    mock_response.reason = reason
    mock_response.text = f"Error: {reason}"

    def mock_json():
        return {"errors": [{"message": reason, "code": status_code}]}

    mock_response.json = mock_json
    return mock_response


@pytest.fixture
def mock_twitter_client():
    """Mock Twitter API client"""
    with patch("app.core.data_collector.TwitterClient") as MockClient:
        mock_client = Mock()
        # Set up the mock profile data
        mock_client.get_user_profile.return_value = MOCK_TWITTER_PROFILE
        mock_client.get_user_timeline.return_value = [MOCK_TWITTER_POST] * 5
        MockClient.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_facebook_api():
    """Mock Facebook API client"""
    with patch("app.core.data_collector.FacebookClient") as MockClient:
        mock_client = Mock()
        mock_client.get_user_profile.return_value = MOCK_FACEBOOK_PROFILE
        mock_client.get_user_posts.return_value = [MOCK_FACEBOOK_POST] * 3
        MockClient.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_config():
    """Mock configuration"""
    with patch("app.core.data_collector.load_config") as mock_load_config:
        mock_load_config.return_value = {
            "api": {"twitter": MOCK_TWITTER_CONFIG, "facebook": MOCK_FACEBOOK_CONFIG}
        }
        yield mock_load_config.return_value


def test_data_collector_initialization(mock_config):
    """Test DataCollector initialization"""
    # Patch TwitterClient to ensure it returns a properly initialized client
    with patch("app.core.data_collector.TwitterClient") as mock_client_class:
        mock_client = Mock()
        # Return a valid client property to pass the client validation
        mock_client.client = Mock()
        mock_client_class.return_value = mock_client

        collector = DataCollector("twitter")
        assert collector.platform == "twitter"
        assert collector.use_mock is False  # Now using real API


def test_invalid_platform():
    """Test initialization with invalid platform"""
    with pytest.raises(ValueError, match="Unsupported platform: 'invalid_platform'"):
        DataCollector("invalid_platform")


def test_missing_config():
    """Test initialization with missing configuration"""
    with patch(
        "app.core.data_collector.load_config", side_effect=ConfigError("Missing config")
    ):
        # We need to patch the logger that's expected to be called
        with patch("app.core.data_collector.logger.error") as mock_logger_error:
            collector = DataCollector("twitter")
            assert collector.use_mock  # Should default to mock data
            # Check that the error was logged
            mock_logger_error.assert_called_once()


def test_collect_twitter_data(mock_twitter_client, mock_config):
    """Test collecting Twitter profile data"""
    collector = DataCollector("twitter")
    data = collector.collect_profile_data("testuser")

    assert data["profile"]["id"] == MOCK_TWITTER_PROFILE["id"]
    assert data["profile"]["username"] == MOCK_TWITTER_PROFILE["username"]
    assert "posts" in data
    assert len(data["posts"]) == 5
    assert data["posts"][0]["id"] == MOCK_TWITTER_POST["id"]


def test_collect_facebook_data(mock_facebook_api, mock_config):
    """Test collecting Facebook profile data"""
    collector = DataCollector("facebook")
    data = collector.collect_profile_data("testuser")

    assert data["profile"]["id"] == MOCK_FACEBOOK_PROFILE["id"]
    assert data["profile"]["name"] == MOCK_FACEBOOK_PROFILE["name"]
    assert "posts" in data
    assert len(data["posts"]) == 3
    assert data["posts"][0]["id"] == MOCK_FACEBOOK_POST["id"]


def test_twitter_rate_limit_error(mock_twitter_client, mock_config):
    """Test handling of Twitter rate limit errors"""
    collector = DataCollector("twitter")
    # Create a proper mock response for TooManyRequests
    mock_response = create_mock_tweepy_response(
        status_code=429, reason="Rate limit exceeded"
    )
    mock_twitter_client.get_user_profile.side_effect = tweepy.errors.TooManyRequests(
        mock_response
    )

    with pytest.raises(RateLimitError):
        collector.collect_profile_data("testuser")


def test_facebook_rate_limit_error(mock_facebook_api, mock_config):
    """Test handling of Facebook rate limit errors"""
    collector = DataCollector("facebook")
    # Create a FacebookRequestError with code attribute
    error = FacebookRequestError(
        message="Rate limit",
        request_context={"response": Mock(status_code=4)},
        http_status=4,
        http_headers={},
        body={},
    )
    # Set code attribute manually
    error.code = 4
    mock_facebook_api.get_user_profile.side_effect = error

    with pytest.raises(RateLimitError):
        collector.collect_profile_data("testuser")


def test_twitter_auth_error(mock_twitter_client, mock_config):
    """Test handling of Twitter authentication errors"""
    collector = DataCollector("twitter")
    # Create a proper mock response for Unauthorized
    mock_response = create_mock_tweepy_response(status_code=401, reason="Unauthorized")
    mock_twitter_client.get_user_profile.side_effect = tweepy.errors.Unauthorized(
        mock_response
    )

    with pytest.raises(AuthenticationError):
        collector.collect_profile_data("testuser")


def test_facebook_auth_error(mock_facebook_api, mock_config):
    """Test handling of Facebook authentication errors"""
    collector = DataCollector("facebook")
    # Create a FacebookRequestError with code attribute
    error = FacebookRequestError(
        message="Invalid OAuth access token",
        request_context={"response": Mock(status_code=190)},
        http_status=190,
        http_headers={},
        body={},
    )
    # Set code attribute manually
    error.code = 190
    mock_facebook_api.get_user_profile.side_effect = error

    with pytest.raises(AuthenticationError):
        collector.collect_profile_data("testuser")


@pytest.mark.parametrize(
    "platform,client_fixture",
    [("twitter", "mock_twitter_client"), ("facebook", "mock_facebook_api")],
)
def test_profile_not_found(platform, client_fixture, mock_config, request):
    """Test handling of non-existent profiles"""
    # Patch the client initialization to return a working mock
    with patch("app.core.data_collector.TwitterClient") as mock_twitter_class, patch(
        "app.core.data_collector.FacebookClient"
    ) as mock_facebook_class:

        # Get the fixture based on platform
        client = request.getfixturevalue(client_fixture)

        # Add critical property to allow correct client validation
        client.client = Mock()  # This ensures the client passes validation

        # Set up the correct mock based on platform
        if platform == "twitter":
            mock_twitter_class.return_value = client
            # Create a proper mock response for NotFound
            mock_response = create_mock_tweepy_response(
                status_code=404, reason="Not Found"
            )
            client.get_user_profile.side_effect = tweepy.errors.NotFound(mock_response)
        else:
            mock_facebook_class.return_value = client
            # Create a FacebookRequestError with correct http_status
            error = FacebookRequestError(
                message="Profile not found",
                request_context={"response": Mock(status_code=404)},
                http_status=404,
                http_headers={},
                body={},
            )
            # Set code attribute manually
            error.code = 404
            client.get_user_profile.side_effect = error

        collector = DataCollector(platform)

        # Make sure we're not using mock data
        collector.use_mock = False

        with pytest.raises(APIError) as exc_info:
            collector.collect_profile_data("nonexistent_user")

        # Verify error code is properly set
        assert exc_info.value.error_code == 404


def test_fallback_to_mock_data(mock_config):
    """Test fallback to mock data when API is unavailable"""
    collector = DataCollector("twitter")
    collector.client = None

    # Use the updated parameter name
    data = collector.collect_profile_data("testuser", use_mock_data=True)

    assert "profile" in data
    assert "posts" in data
    assert data["profile"]["username"] == "testuser"


def test_mock_data_with_parameter():
    """Test using mock data with parameter"""
    collector = DataCollector("twitter")

    # Force mock data even if client is available
    data = collector.collect_profile_data("testuser", use_mock_data=True)

    assert "profile" in data
    assert "posts" in data
    assert data["profile"]["username"] == "testuser"


def test_api_error_fallback(mock_twitter_client, mock_config):
    """Test fallback to mock data after API error"""
    collector = DataCollector("twitter")

    # First make it return a forbidden error
    mock_response = create_mock_tweepy_response(status_code=403, reason="Forbidden")
    mock_twitter_client.get_user_profile.side_effect = tweepy.errors.Forbidden(
        mock_response
    )

    # This should fall back to mock data
    data = collector.collect_profile_data("testuser")

    assert "profile" in data
    assert "posts" in data
    assert collector.use_mock  # Should now be set to use mock data
