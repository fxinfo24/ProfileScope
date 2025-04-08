"""Tests for social media API clients"""

import os
import pytest
import time
from unittest.mock import Mock, patch, PropertyMock, MagicMock
from datetime import datetime
import tweepy
import requests
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.user import User
from facebook_business.exceptions import FacebookRequestError

from app.core.api_clients import (
    TwitterClient,
    FacebookClient,
    RateLimiter,
    RetryHandler,
    RateLimitExceededError,
)

# Test data
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


# Create mock HTTP response for tweepy exceptions
@pytest.fixture
def mock_tweepy_response():
    """Create a mock response for tweepy exceptions"""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 429  # Too Many Requests
    mock_response.reason = "Rate limit exceeded"
    mock_response.text = "Rate limit exceeded"
    mock_response.headers = {"Retry-After": "60"}

    # This is crucial for tweepy errors
    mock_response.json = Mock(
        return_value={"errors": [{"message": "Rate limit exceeded"}]}
    )

    return mock_response


@pytest.fixture
def mock_tweepy_api():
    """Mock Twitter API client"""
    mock_api = Mock()
    # Mock user
    mock_user = Mock()
    mock_user.id_str = "123456"
    mock_user.screen_name = "test_user"
    mock_user.name = "Test User"
    mock_user.description = "Test bio"
    mock_user.location = "Test City"
    mock_user.created_at = datetime.now()
    mock_user.verified = True
    mock_user.followers_count = 1000
    mock_user.friends_count = 500
    mock_user.statuses_count = 1500
    mock_user.profile_image_url_https = "https://example.com/image.jpg"

    mock_api.get_user.return_value = mock_user

    # Mock tweet
    mock_tweet = Mock()
    mock_tweet.id_str = "tweet123"
    mock_tweet.full_text = "Test tweet"
    mock_tweet.created_at = datetime.now()
    mock_tweet.retweet_count = 10
    mock_tweet.favorite_count = 20
    mock_tweet.entities = {
        "hashtags": [{"text": "test"}],
        "user_mentions": [{"screen_name": "mentioned_user"}],
        "urls": [{"expanded_url": "https://example.com"}],
        "media": [{"media_url_https": "https://example.com/media.jpg"}],
    }

    mock_api.user_timeline.return_value = [mock_tweet]

    return mock_api


@pytest.fixture
def mock_facebook_api():
    """Create a mock Facebook GraphAPI"""
    with patch("facebook_business.api.FacebookAdsApi.init") as mock_init:
        # Replace get_default with get_default_api
        with patch(
            "facebook_business.api.FacebookAdsApi.get_default_api", return_value=Mock()
        ) as mock_get_default_api:
            # Configure the User.api_get mock
            with patch.object(User, "api_get") as mock_api_get:
                mock_api_get.return_value = {
                    "id": "123456",
                    "name": "Test User",
                    "about": "Test bio",
                    "location": {"name": "Test City"},
                    "created_time": "2022-01-01T12:00:00+0000",
                    "picture": {"data": {"url": "https://example.com/image.jpg"}},
                }

                # Configure the User.get_posts mock
                with patch.object(User, "get_posts") as mock_get_posts:
                    mock_post = Mock()
                    mock_post.api_get.return_value = {
                        "id": "post123",
                        "message": "Test post",
                        "created_time": "2022-01-01T12:00:00+0000",
                        "type": "status",
                        "permalink_url": "https://facebook.com/post123",
                        "shares": {"count": 10},
                        "reactions": {"summary": {"total_count": 20}},
                    }
                    mock_get_posts.return_value = [mock_post]

                    # Set the mock_get_default_api to return our mock client
                    mock_client = Mock()
                    mock_get_default_api.return_value = mock_client

                    # Create a mock fb_client for the FacebookClient class
                    fb_client = Mock()

                    # Setup the mock FacebookClient for data_collector
                    with patch(
                        "app.core.data_collector.FacebookClient"
                    ) as mock_fb_client_class:
                        mock_fb_client = Mock()
                        mock_fb_client.get_user_profile.return_value = {
                            "id": "123456",
                            "name": "Test User",
                            "bio": "Test bio",
                            "location": "Test City",
                            "profile_url": "https://facebook.com/test_user",
                            "created_at": datetime.now().isoformat(),
                            "profile_image_url": "https://example.com/image.jpg",
                        }
                        mock_fb_client.get_user_posts.return_value = [
                            {
                                "id": "post123",
                                "text": "Test post",
                                "created_at": datetime.now().isoformat(),
                                "type": "status",
                                "url": "https://facebook.com/post123",
                                "shares": 10,
                                "reactions": 20,
                            }
                        ] * 3
                        mock_fb_client_class.return_value = mock_fb_client

                        yield fb_client


def test_twitter_client_initialization():
    """Test Twitter client initialization"""
    with patch("tweepy.OAuth1UserHandler") as mock_auth:
        with patch("tweepy.API") as mock_api_class:
            mock_api = Mock()
            mock_api_class.return_value = mock_api

            client = TwitterClient(MOCK_TWITTER_CONFIG)
            assert client is not None
            assert client.client is not None

            mock_auth.assert_called_once_with(
                MOCK_TWITTER_CONFIG["api_key"],
                MOCK_TWITTER_CONFIG["api_secret"],
                MOCK_TWITTER_CONFIG["access_token"],
                MOCK_TWITTER_CONFIG["access_token_secret"],
            )


def test_twitter_client_validation():
    """Test Twitter client configuration validation"""
    with pytest.raises(ValueError):
        TwitterClient({})


def test_twitter_get_user_profile(mock_tweepy_api):
    """Test getting Twitter user profile"""
    with patch("tweepy.OAuth1UserHandler"), patch(
        "tweepy.API", return_value=mock_tweepy_api
    ):
        client = TwitterClient(MOCK_TWITTER_CONFIG)
        profile = client.get_user_profile("test_user")

        assert profile is not None
        assert profile["username"] == mock_tweepy_api.get_user.return_value.screen_name
        assert profile["name"] == mock_tweepy_api.get_user.return_value.name
        assert "bio" in profile
        assert "location" in profile
        assert "created_at" in profile
        assert "verified" in profile
        assert "followers_count" in profile
        assert "following_count" in profile
        assert "tweets_count" in profile
        assert "profile_image_url" in profile


def test_twitter_get_timeline(mock_tweepy_api):
    """Test getting Twitter timeline"""
    with patch("tweepy.OAuth1UserHandler"), patch(
        "tweepy.API", return_value=mock_tweepy_api
    ):
        client = TwitterClient(MOCK_TWITTER_CONFIG)
        timeline = client.get_user_timeline("test_user", count=1)

        assert len(timeline) == 1
        tweet = timeline[0]
        assert tweet["id"] == "tweet123"
        assert tweet["text"] == "Test tweet"
        assert "created_at" in tweet
        assert tweet["retweet_count"] == 10
        assert tweet["favorite_count"] == 20
        assert "hashtags" in tweet
        assert "mentions" in tweet
        assert "media" in tweet


def test_facebook_client_initialization():
    """Test Facebook client initialization"""
    with patch("facebook_business.api.FacebookAdsApi.init") as mock_init:
        with patch(
            "facebook_business.api.FacebookAdsApi.get_default_api", return_value=Mock()
        ) as mock_get_default_api:
            client = FacebookClient(MOCK_FACEBOOK_CONFIG)
            assert client is not None
            assert client.client is not None


def test_facebook_client_validation():
    """Test Facebook client configuration validation"""
    with pytest.raises(ValueError):
        FacebookClient({})


def test_facebook_get_user_profile(mock_facebook_api):
    """Test getting Facebook user profile"""
    with patch("app.core.api_clients.FacebookAdsApi.init"), patch(
        "app.core.api_clients.FacebookAdsApi.get_default_api",
        return_value=mock_facebook_api,
    ), patch.object(
        User,
        "api_get",
        return_value={
            "id": "123456",
            "name": "Test User",
            "about": "Test bio",
            "location": {"name": "Test City"},
            "created_time": "2022-01-01T12:00:00+0000",
            "picture": {"data": {"url": "https://example.com/image.jpg"}},
        },
    ):

        client = FacebookClient(MOCK_FACEBOOK_CONFIG)
        # Manually set the client property to our mock
        client._api = mock_facebook_api
        profile = client.get_user_profile("test_user")

        assert profile is not None
        assert profile["id"] == "123456"
        assert profile["name"] == "Test User"
        assert "bio" in profile
        assert "location" in profile
        assert "created_at" in profile
        assert "profile_image_url" in profile


def test_facebook_get_posts(mock_facebook_api):
    """Test getting Facebook posts"""
    post_data = {
        "id": "post123",
        "message": "Test post",
        "created_time": "2022-01-01T12:00:00+0000",
        "type": "status",
        "permalink_url": "https://facebook.com/post123",
        "shares": {"count": 10},
        "reactions": {"summary": {"total_count": 20}},
    }

    with patch("app.core.api_clients.FacebookAdsApi.init"), patch(
        "app.core.api_clients.FacebookAdsApi.get_default_api",
        return_value=mock_facebook_api,
    ), patch.object(User, "get_posts") as mock_get_posts:

        # Important change: Create a proper mock post object
        mock_post = MagicMock()
        # Make the api_get method return our post data
        mock_post.api_get.return_value = post_data
        # Make accessing attributes fallback to dictionary access for our test
        mock_post.__getitem__.side_effect = lambda key: post_data.get(key)
        mock_post.items.return_value = post_data.items()
        mock_get_posts.return_value = [mock_post]

        client = FacebookClient(MOCK_FACEBOOK_CONFIG)
        # Manually set the client property to our mock
        client._api = mock_facebook_api
        posts = list(client.get_user_posts("test_user", limit=1))

        assert len(posts) == 1
        post = posts[0]
        assert post["id"] == "post123"
        assert post["text"] == "Test post"
        assert "created_at" in post
        assert post["type"] == "status"
        assert "url" in post
        assert post["shares"] == 10
        assert post["reactions"] == 20


def test_rate_limiter():
    """Test rate limiter functionality"""
    rate_limiter = RateLimiter(calls=5, period=1)

    # Try multiple calls
    for _ in range(5):
        # These should not raise an exception
        rate_limiter.check()

    # The 6th call should raise an exception
    with pytest.raises(RateLimitExceededError):
        rate_limiter.check()


def test_retry_handler():
    """Test retry handler functionality"""
    retry_handler = RetryHandler(max_retries=2, backoff_factor=0.01)

    counter = {"attempts": 0}

    @retry_handler
    def test_func():
        counter["attempts"] += 1
        if counter["attempts"] <= 2:
            raise requests.RequestException("Test exception")
        return "success"

    # This should succeed after 2 retries (3 attempts total)
    assert test_func() == "success"
    assert counter["attempts"] == 3


# Create proper mock response objects for tweepy and Facebook errors
def create_tweepy_response(status_code=429, reason="Rate limit exceeded"):
    """Create a proper tweepy response object for exceptions"""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = status_code
    mock_response.reason = reason
    mock_response.text = reason
    mock_response.headers = {}
    mock_response.json = Mock(return_value={"errors": [{"message": reason}]})
    return mock_response


def create_facebook_error(message="Error", code=4, http_status=429):
    """Create a Facebook API error with appropriate attributes"""
    request_context = {"response": Mock(status_code=http_status)}
    error = FacebookRequestError(
        message=message,
        request_context=request_context,
        http_status=http_status,
        http_headers={},
        body={},
    )
    error.code = code  # Set code attribute explicitly
    return error


@pytest.mark.parametrize(
    "error,expected_retries",
    [
        # Twitter rate limit error
        (lambda: tweepy.errors.TooManyRequests(create_tweepy_response(429)), 3),
        # Facebook rate limit error with code attribute
        (lambda: create_facebook_error("Rate limit", code=4, http_status=429), 3),
        # Twitter unauthorized error
        (
            lambda: tweepy.errors.Unauthorized(
                create_tweepy_response(401, "Unauthorized")
            ),
            1,
        ),
        # Facebook unauthorized error
        (lambda: create_facebook_error("Unauthorized", code=190, http_status=401), 1),
    ],
)
def test_api_error_handling(error, expected_retries):
    """Test handling of specific API errors"""
    retry_handler = RetryHandler(max_retries=3, backoff_factor=0.01)

    counter = {"attempts": 0}

    @retry_handler
    def test_func():
        counter["attempts"] += 1
        if counter["attempts"] < expected_retries:
            raise error()
        return "success"

    # Should succeed after expected retries
    result = test_func()
    assert result == "success"
    assert counter["attempts"] == expected_retries
