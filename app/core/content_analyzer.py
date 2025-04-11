# ProfileScope: Social Media Profile Analyzer
# A comprehensive framework for analyzing public social media profiles

import os
import json
import datetime
import argparse
import logging
from typing import Dict, List, Any, Optional, Tuple


# Core analysis modules
class DataCollector:
    """Module for collecting data from social media profiles"""

    def __init__(self, platform: str, rate_limit: int = 100):
        """
        Initialize data collector for specific platform

        Args:
            platform: Social media platform (e.g., 'twitter', 'facebook')
            rate_limit: Maximum requests per minute to avoid API throttling
        """
        self.platform = platform
        self.rate_limit = rate_limit
        self.logger = logging.getLogger(f"DataCollector.{platform}")

    def collect_profile_data(self, profile_id: str) -> Dict[str, Any]:
        """
        Collect all available public data from a profile

        Args:
            profile_id: Username or profile identifier

        Returns:
            Dictionary containing profile data
        """
        if self.platform == "twitter":
            return self._collect_twitter_data(profile_id)
        elif self.platform == "facebook":
            return self._collect_facebook_data(profile_id)
        else:
            self.logger.error(f"Unsupported platform: {self.platform}")
            raise ValueError(f"Unsupported platform: {self.platform}")

    def _collect_twitter_data(self, username: str) -> Dict[str, Any]:
        """Implementation for Twitter/X data collection"""
        # This would use Twitter API or web scraping techniques
        # For demo purposes, returning mock structure
        self.logger.info(f"Collecting Twitter data for {username}")

        return {
            "profile": {
                "username": username,
                "bio": "Mock bio for demonstration",
                "join_date": "2020-01-01",
                "location": "Example City",
                "mock_data": True,
            },
            "posts": self._generate_mock_posts(50),
            "media": self._generate_mock_media(20),
            "links": self._generate_mock_links(15),
        }

    def _collect_facebook_data(self, profile_id: str) -> Dict[str, Any]:
        """Implementation for Facebook data collection"""
        # Similar implementation for Facebook
        self.logger.info(f"Collecting Facebook data for {profile_id}")

        return {
            "profile": {
                "id": profile_id,
                "name": "Example User",
                "bio": "Mock Facebook bio",
                "join_date": "2015-03-15",
                "mock_data": True,
            },
            "posts": self._generate_mock_posts(30),
            "media": self._generate_mock_media(40),
            "links": self._generate_mock_links(25),
        }

    def _generate_mock_posts(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock posts for demonstration"""
        posts = []
        for i in range(count):
            date = datetime.datetime.now() - datetime.timedelta(days=i * 3)
            posts.append(
                {
                    "id": f"post{i}",
                    "content": f"This is mock post content #{i}",
                    "date": date.strftime("%Y-%m-%d"),
                    "likes": i * 5,
                    "shares": i * 2,
                }
            )
        return posts

    def _generate_mock_media(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock media items for demonstration"""
        media = []
        for i in range(count):
            date = datetime.datetime.now() - datetime.timedelta(days=i * 7)
            media.append(
                {
                    "id": f"media{i}",
                    "type": "image" if i % 3 != 0 else "video",
                    "url": f"https://example.com/media/{i}.jpg",
                    "date": date.strftime("%Y-%m-%d"),
                    "caption": f"Media caption #{i}" if i % 2 == 0 else None,
                }
            )
        return media

    def _generate_mock_links(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock shared links for demonstration"""
        links = []
        domains = ["news.example.com", "blog.example.com", "example.org", "example.edu"]
        for i in range(count):
            date = datetime.datetime.now() - datetime.timedelta(days=i * 5)
            domain = domains[i % len(domains)]
            links.append(
                {
                    "id": f"link{i}",
                    "url": f"https://{domain}/article{i}",
                    "title": f"Shared link #{i}",
                    "date": date.strftime("%Y-%m-%d"),
                    "domain": domain,
                }
            )
        return links


"""
ProfileScope: Content Analysis Module
Performs natural language processing and content analysis on social media posts
"""

from typing import Dict, Any, List, Optional
import re
from collections import Counter
import datetime
import logging


class ContentAnalyzer:
    """Analyzes social media content using NLP and other techniques"""

    def __init__(self, nlp_model: str = "default", sentiment_analyzer: bool = True):
        """
        Initialize content analyzer with specified models

        Args:
            nlp_model: Name of NLP model to use
            sentiment_analyzer: Whether to include sentiment analysis
        """
        self.nlp_model = nlp_model
        self.use_sentiment = sentiment_analyzer
        self.logger = logging.getLogger("ProfileScope.ContentAnalyzer")
        # TODO: Load actual NLP models based on configuration

    def analyze_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete content analysis on a social media profile

        Args:
            profile_data: Dictionary containing profile data

        Returns:
            Dictionary with analysis results
        """
        self.logger.info("Starting profile content analysis")
        posts = profile_data.get("posts", [])

        # Extract all text content for analysis
        text_content = self._extract_text_content(profile_data)

        # Calculate various metrics
        posting_frequency = self._calculate_posting_frequency(posts)
        topics = self._identify_topics(posts)
        sentiment = self._analyze_sentiment(posts) if self.use_sentiment else None
        writing_style = self._analyze_writing_style(posts)
        personality_traits = self._infer_personality(posts, profile_data)
        interests = self._analyze_interests(text_content, profile_data)

        # Generate timeline from profile data
        timeline = self._generate_timeline(profile_data)

        # Analyze sentiment trends
        sentiment_trends = self._analyze_sentiment_trends(profile_data)

        # Generate summary of findings
        summary = self._generate_summary(
            profile_data, posting_frequency, topics, sentiment, personality_traits
        )

        # Check if this is mock data
        if "profile" in profile_data and profile_data["profile"].get(
            "mock_data", False
        ):
            mock_disclaimer = "This analysis is based on mock data generated for demonstration purposes. In a production environment, this would be replaced with actual social media data analysis."
        else:
            mock_disclaimer = None

        # Compile results
        analysis_results = {
            "summary": summary,
            "posting_patterns": {
                "frequency": posting_frequency,
                "activity_hours": self._identify_activity_hours(posts),
            },
            "content_topics": topics,
            "writing_style": writing_style,
            "personality_traits": personality_traits,
            "interests": interests,
            "timeline": timeline,
            "sentiment_trends": sentiment_trends,
        }

        if sentiment:
            analysis_results["sentiment"] = sentiment

        if mock_disclaimer:
            analysis_results["mock_data_disclaimer"] = mock_disclaimer

        return analysis_results

    def _generate_summary(
        self,
        profile_data: Dict[str, Any],
        posting_frequency: Dict[str, Any],
        topics: Dict[str, Any],
        sentiment: Optional[Dict[str, Any]],
        personality_traits: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a summary of the profile analysis

        Args:
            profile_data: Complete profile data
            posting_frequency: Posting frequency analysis
            topics: Content topics analysis
            sentiment: Sentiment analysis results
            personality_traits: Personality traits analysis

        Returns:
            Dictionary with summary information
        """
        # Get profile basics
        platform = profile_data.get("metadata", {}).get("platform", "social media")
        profile_name = profile_data.get("profile", {}).get("username", "this profile")

        # Activity level
        posts_count = len(profile_data.get("posts", []))
        daily_avg = posting_frequency.get("daily_average", 0)

        if daily_avg > 3:
            activity_level = "very active"
        elif daily_avg > 1:
            activity_level = "active"
        elif daily_avg > 0.3:  # About 2-3 times per week
            activity_level = "moderately active"
        else:
            activity_level = "occasionally active"

        # Top topics/interests
        top_topics = [topic for topic, _ in topics.get("top_topics", [])][:2]
        top_topics_text = " and ".join(top_topics) if top_topics else "various topics"

        # Sentiment summary
        sentiment_text = "neutral tone"
        if sentiment:
            sentiment_label = sentiment.get("overall_sentiment", {}).get("label")
            if sentiment_label == "positive":
                sentiment_text = "generally positive tone"
            elif sentiment_label == "negative":
                sentiment_text = "generally critical tone"

        # Create summary text components
        profile_summary = f"Based on the analysis of {posts_count} posts, {profile_name} appears to be {activity_level} on {platform}."
        content_summary = (
            f"Content primarily focuses on {top_topics_text} with a {sentiment_text}."
        )

        # Extract top personality traits
        top_traits = []
        for trait, value in personality_traits.items():
            if value > 0.7:
                top_traits.append(trait.replace("_", " "))

        personality_summary = ""
        if top_traits:
            traits_text = ", ".join(top_traits)
            personality_summary = f"Analysis suggests tendencies toward {traits_text}."

        return {
            "profile_overview": profile_summary,
            "content_overview": content_summary,
            "personality_overview": personality_summary,
            "post_count": posts_count,
            "activity_level": activity_level,
            "main_topics": top_topics,
            "general_sentiment": sentiment_text,
        }

    def _extract_text_content(self, profile_data: Dict[str, Any]) -> str:
        """
        Extract all text content from profile data

        Args:
            profile_data: Dictionary containing profile data

        Returns:
            Concatenated text content from profile
        """
        all_text = []

        # Extract profile bio/description
        if "profile" in profile_data:
            if "bio" in profile_data["profile"]:
                all_text.append(profile_data["profile"]["bio"])
            elif "description" in profile_data["profile"]:
                all_text.append(profile_data["profile"]["description"])

        # Extract post content
        for post in profile_data.get("posts", []):
            if "content" in post:
                all_text.append(post["content"])

        # Extract media captions
        for media in profile_data.get("media", []):
            if "caption" in media:
                all_text.append(media["caption"])

        return " ".join(all_text)

    def _calculate_posting_frequency(
        self, posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate posting frequency metrics"""
        if not posts:
            return {"daily_average": 0, "weekly_average": 0, "monthly_average": 0}

        # Extract dates and count posts per day
        dates = []
        for post in posts:
            try:
                date_str = post.get("created_at", "") or post.get("date", "")
                # Parse ISO format date
                date = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                dates.append(date)
            except (ValueError, TypeError):
                # Skip posts with invalid dates
                continue

        if not dates:
            return {"daily_average": 0, "weekly_average": 0, "monthly_average": 0}

        # Count posts per day
        date_counts = Counter(dates)

        # Calculate date range
        min_date = min(dates)
        max_date = max(dates)
        date_range = (max_date - min_date).days + 1  # Add 1 to include the last day

        if date_range <= 0:
            date_range = 1  # Avoid division by zero

        # Calculate averages
        daily_avg = len(posts) / date_range
        weekly_avg = daily_avg * 7
        monthly_avg = daily_avg * 30

        # Find most active days
        active_days = date_counts.most_common(3)
        active_days = [(day.strftime("%Y-%m-%d"), count) for day, count in active_days]

        return {
            "daily_average": round(daily_avg, 2),
            "weekly_average": round(weekly_avg, 2),
            "monthly_average": round(monthly_avg, 2),
            "most_active_days": active_days,
        }

    def _identify_activity_hours(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify hours of day with most activity"""
        hours = []

        for post in posts:
            try:
                time_str = post.get("created_at", "") or post.get("date", "")
                # Extract hour from ISO format timestamp
                hour = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ").hour
                hours.append(hour)
            except (ValueError, TypeError):
                # Skip posts with invalid timestamps
                continue

        # Count posts per hour
        hour_counts = Counter(hours)

        # Find peak hours (top 3)
        peak_hours = hour_counts.most_common(3)

        # Group into time periods
        morning = sum(hour_counts.get(h, 0) for h in range(5, 12))  # 5am-11am
        afternoon = sum(hour_counts.get(h, 0) for h in range(12, 17))  # 12pm-4pm
        evening = sum(hour_counts.get(h, 0) for h in range(17, 22))  # 5pm-9pm
        night = sum(hour_counts.get(h, 0) for h in range(22, 24)) + sum(
            hour_counts.get(h, 0) for h in range(0, 5)
        )  # 10pm-4am

        total = morning + afternoon + evening + night
        if total == 0:
            total = 1  # Avoid division by zero

        return {
            "peak_hours": peak_hours,
            "time_periods": {
                "morning": {
                    "count": morning,
                    "percentage": round(morning * 100 / total, 1),
                },
                "afternoon": {
                    "count": afternoon,
                    "percentage": round(afternoon * 100 / total, 1),
                },
                "evening": {
                    "count": evening,
                    "percentage": round(evening * 100 / total, 1),
                },
                "night": {"count": night, "percentage": round(night * 100 / total, 1)},
            },
        }

    def _identify_topics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify main topics from posts"""
        # Extract all text content
        all_text = " ".join([post.get("content", "") for post in posts])
        all_text = all_text.lower()

        # Extract hashtags
        hashtags = []
        for post in posts:
            post_hashtags = post.get("hashtags", [])
            if post_hashtags:
                hashtags.extend(post_hashtags)
            else:
                # Try to extract hashtags from content if not provided
                content = post.get("content", "")
                if content:
                    found_tags = re.findall(r"#(\w+)", content)
                    hashtags.extend(["#" + tag for tag in found_tags])

        # Count hashtag frequency
        hashtag_counts = Counter(hashtags).most_common(10)

        # Basic topic detection based on keywords
        # In a real system, this would use topic modeling or NLP classification
        topics = {
            "politics": self._count_keyword_matches(
                all_text, ["politics", "election", "vote", "government", "president"]
            ),
            "technology": self._count_keyword_matches(
                all_text,
                ["tech", "technology", "computer", "software", "app", "digital"],
            ),
            "entertainment": self._count_keyword_matches(
                all_text, ["movie", "music", "concert", "TV", "show", "celebrity"]
            ),
            "sports": self._count_keyword_matches(
                all_text, ["sports", "game", "team", "win", "player", "score"]
            ),
            "lifestyle": self._count_keyword_matches(
                all_text, ["food", "travel", "fashion", "home", "fitness"]
            ),
            "business": self._count_keyword_matches(
                all_text, ["business", "company", "market", "startup", "entrepreneur"]
            ),
        }

        # Find top topics
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "top_hashtags": hashtag_counts,
            "topic_distribution": topics,
            "top_topics": top_topics,
        }

    def _count_keyword_matches(self, text: str, keywords: List[str]) -> int:
        """Count occurrences of keywords in text"""
        return sum(text.count(keyword.lower()) for keyword in keywords)

    def _analyze_sentiment(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment in posts"""
        # In a real system, this would use a proper sentiment analysis model
        # Here, we use a simple approach based on keyword matching

        positive_words = [
            "happy",
            "great",
            "excellent",
            "good",
            "love",
            "amazing",
            "best",
            "awesome",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "worst",
            "sad",
            "angry",
            "disappointed",
        ]

        post_sentiments = []

        for post in posts:
            content = post.get("content", "").lower()
            pos_count = sum(content.count(word) for word in positive_words)
            neg_count = sum(content.count(word) for word in negative_words)

            # Calculate simple sentiment score
            if pos_count > neg_count:
                sentiment = "positive"
                score = min(1.0, 0.5 + (pos_count - neg_count) * 0.1)
            elif neg_count > pos_count:
                sentiment = "negative"
                score = max(-1.0, -0.5 - (neg_count - pos_count) * 0.1)
            else:
                sentiment = "neutral"
                score = 0.0

            post_sentiments.append(
                {
                    "post_id": post.get("id", ""),
                    "sentiment": sentiment,
                    "score": score,
                }
            )

        # Calculate overall sentiment
        if not post_sentiments:
            avg_score = 0.0
        else:
            avg_score = sum(s["score"] for s in post_sentiments) / len(post_sentiments)

        if avg_score > 0.2:
            overall = "positive"
        elif avg_score < -0.2:
            overall = "negative"
        else:
            overall = "neutral"

        # Count sentiment distribution
        sentiment_counts = Counter(s["sentiment"] for s in post_sentiments)

        return {
            "overall_sentiment": {"label": overall, "score": round(avg_score, 2)},
            "distribution": {
                "positive": sentiment_counts.get("positive", 0),
                "neutral": sentiment_counts.get("neutral", 0),
                "negative": sentiment_counts.get("negative", 0),
            },
            "post_sentiments": post_sentiments[:5],  # Return only first 5 for brevity
        }

    def _analyze_writing_style(
        self, posts: List[Dict[str, Any]] or str
    ) -> Dict[str, Any]:
        """Analyze writing style patterns"""
        if not posts:
            return {}

        # Extract all text content
        if isinstance(posts, str):
            # If input is already a string, use it directly
            all_text = posts
        else:
            # If input is a list of posts, extract the content
            all_text = " ".join([post.get("content", "") for post in posts])

        # Basic metrics
        word_count = len(re.findall(r"\b\w+\b", all_text))
        sentences = re.split(r"[.!?]+", all_text)
        sentence_count = len([s for s in sentences if s.strip()])

        # Avoid division by zero
        if sentence_count == 0:
            sentence_count = 1

        avg_sentence_length = word_count / sentence_count

        # Simple vocabulary diversity
        words = re.findall(r"\b\w+\b", all_text.lower())
        unique_words = len(set(words))
        vocabulary_diversity = unique_words / max(1, word_count)

        # Simple formality and complexity metrics
        long_words = sum(1 for word in words if len(word) > 6)
        complex_word_ratio = long_words / max(1, word_count)
        formal_words = self._count_keyword_matches(
            all_text.lower(),
            ["therefore", "however", "consequently", "furthermore", "nevertheless"],
        )
        formal_ratio = formal_words / max(1, word_count) * 10  # Scale up for visibility

        # Emotional content
        emotional_words = self._count_keyword_matches(
            all_text.lower(),
            ["love", "hate", "happy", "sad", "angry", "excited", "afraid", "proud"],
        )
        emotional_ratio = (
            emotional_words / max(1, word_count) * 5
        )  # Scale up for visibility

        # Results with normalized average_sentence_length
        return {
            "average_sentence_length": round(avg_sentence_length, 1),
            "vocabulary_diversity": round(vocabulary_diversity, 2),
            "complexity": round(
                min((complex_word_ratio * 2) + (avg_sentence_length / 25), 1.0), 2
            ),
            "formality": round(min(formal_ratio + 0.3, 1.0), 2),
            "emotional_tone": round(min(emotional_ratio, 1.0), 2),
            "word_count": word_count,
            "normalized_sentence_length": round(min(avg_sentence_length / 15, 1.0), 2),
        }

    def _infer_personality(
        self, posts: List[Dict[str, Any]], profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Infer personality traits based on content
        This is a simplified placeholder - real implementation would use psycholinguistic models
        """
        # Extract all text content
        all_text = " ".join([post.get("content", "") for post in posts])
        all_text = all_text.lower()

        # For the sake of simplicity in tests, return default values
        # In a real system, this would use NLP and linguistic analysis
        return {
            "extraversion": 0.5,
            "openness": 0.5,
            "conscientiousness": 0.5,
        }

    def _analyze_interests(
        self, text_content: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze user interests from content

        Args:
            text_content: Extracted text content
            profile_data: Complete profile data

        Returns:
            Dictionary of identified interests
        """
        # Simple placeholder implementation for tests
        # In a real system, this would use topic modeling and interest extraction
        interests = {}

        # Extract hashtags as potential interests
        hashtags = []
        for post in profile_data.get("posts", []):
            content = post.get("content", "")
            if content:
                found_tags = re.findall(r"#(\w+)", content)
                hashtags.extend(found_tags)

        # Count hashtag frequency
        tag_counts = Counter(hashtags)

        # Convert top hashtags to interests
        for tag, count in tag_counts.most_common(5):
            interests[tag] = {
                "confidence": min(0.95, 0.5 + count / 10),
                "mentions": count,
                "source": "hashtags",
            }

        return interests

    def _generate_timeline(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate chronological timeline of user activity

        Args:
            profile_data: Profile data dictionary

        Returns:
            List of timeline events
        """
        timeline = []

        # Add profile creation if available
        if "profile" in profile_data:
            profile = profile_data["profile"]
            join_date = profile.get("created_at") or profile.get("join_date")
            if join_date:
                timeline.append(
                    {
                        "date": join_date,
                        "type": "account_creation",
                        "description": "Account created",
                    }
                )

        # Add posts to timeline
        for post in profile_data.get("posts", []):
            date = post.get("created_at") or post.get("date")
            if date:
                timeline.append(
                    {
                        "date": date,
                        "type": "post",
                        "description": post.get("content", "")[:50]
                        + ("..." if len(post.get("content", "")) > 50 else ""),
                    }
                )

        # Add media to timeline
        for media in profile_data.get("media", []):
            date = media.get("created_at") or media.get("date")
            if date:
                media_type = media.get("type", "media")
                timeline.append(
                    {
                        "date": date,
                        "type": media_type,
                        "description": media.get("caption", f"Shared {media_type}"),
                    }
                )

        # Sort timeline by date
        timeline.sort(key=lambda x: x["date"])

        return timeline

    def _analyze_sentiment_trends(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment trends over time

        Args:
            profile_data: Complete profile data

        Returns:
            Dictionary of sentiment analysis results
        """
        posts = profile_data.get("posts", [])
        if not posts:
            return {
                "overall_sentiment": {"label": "neutral", "score": 0.0},
                "distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "post_sentiments": [],
            }

        # Sort posts by date
        try:
            sorted_posts = sorted(
                posts,
                key=lambda p: p.get("created_at", "") or p.get("date", ""),
                reverse=False,
            )
        except:
            sorted_posts = posts  # If sorting fails, use original order

        # Generate time-based sentiment analysis
        post_sentiments = []
        sentiments_by_month = {}
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for post in sorted_posts:
            content = post.get("content", "").lower()
            date_str = post.get("created_at", "") or post.get("date", "")

            # Simple sentiment scoring system
            pos_words = [
                "happy",
                "great",
                "excellent",
                "good",
                "love",
                "amazing",
                "best",
            ]
            neg_words = ["bad", "terrible", "awful", "hate", "worst", "sad", "angry"]

            pos_count = sum(content.count(word) for word in pos_words)
            neg_count = sum(content.count(word) for word in neg_words)

            # Calculate sentiment and score
            if pos_count > neg_count:
                sentiment = "positive"
                score = min(1.0, 0.5 + (pos_count - neg_count) * 0.1)
                positive_count += 1
            elif neg_count > pos_count:
                sentiment = "negative"
                score = max(-1.0, -0.5 - (neg_count - pos_count) * 0.1)
                negative_count += 1
            else:
                sentiment = "neutral"
                score = 0.0
                neutral_count += 1

            # Add to post sentiments
            post_sentiments.append(
                {
                    "post_id": post.get("id", ""),
                    "date": date_str,
                    "sentiment": sentiment,
                    "score": score,
                }
            )

            # Group by month
            try:
                month = date_str[:7]  # YYYY-MM
                if month not in sentiments_by_month:
                    sentiments_by_month[month] = {
                        "scores": [],
                        "positive": 0,
                        "negative": 0,
                        "neutral": 0,
                    }

                sentiments_by_month[month]["scores"].append(score)
                sentiments_by_month[month][sentiment] += 1
            except:
                pass  # Skip if date parsing fails

        # Calculate monthly averages
        monthly_trend = []
        for month, data in sorted(sentiments_by_month.items()):
            if data["scores"]:
                avg_score = sum(data["scores"]) / len(data["scores"])
                monthly_trend.append(
                    {
                        "month": month,
                        "average_score": round(avg_score, 2),
                        "positive": data["positive"],
                        "neutral": data["neutral"],
                        "negative": data["negative"],
                    }
                )

        # Calculate overall sentiment
        total = len(post_sentiments)
        if total == 0:
            avg_score = 0.0
            overall = "neutral"
        else:
            avg_score = sum(ps["score"] for ps in post_sentiments) / total
            if avg_score > 0.2:
                overall = "positive"
            elif avg_score < -0.2:
                overall = "negative"
            else:
                overall = "neutral"

        return {
            "overall_sentiment": {"label": overall, "score": round(avg_score, 2)},
            "distribution": {
                "positive": positive_count,
                "neutral": neutral_count,
                "negative": negative_count,
            },
            "post_sentiments": post_sentiments[:5],  # Return only first 5 for brevity
            "monthly_trend": monthly_trend,
        }
