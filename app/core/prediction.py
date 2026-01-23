"""
ProfileScope: Prediction Engine
Generates predictions about user traits and behaviors
"""

from typing import Dict, Any, List
import logging


class PredictionEngine:
    """Generates predictions about social media users"""

    def __init__(self, confidence_threshold: float = 0.65):
        """
        Initialize the prediction engine

        Args:
            confidence_threshold: Minimum confidence level for predictions
        """
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger("ProfileScope.PredictionEngine")

    def generate_predictions(
        self, profile_data: Dict[str, Any], content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate predictions based on profile data and content analysis

        Args:
            profile_data: Dictionary containing profile data
            content_analysis: Results from content analysis

        Returns:
            Dictionary with predictions and confidence scores
        """
        self.logger.info("Generating predictions based on profile analysis")

        # Check if we're using mock data
        is_mock = profile_data.get("metadata", {}).get("is_mock_data", False)

        if is_mock:
            # For mock data, generate comprehensive mock predictions
            return self._generate_mock_predictions(profile_data, content_analysis)

        # Initialize predictions
        predictions = {
            "personality_traits": self._predict_personality_traits(content_analysis),
            "interests": self._predict_interests(profile_data, content_analysis),
            "behavior_patterns": self._predict_behavior_patterns(content_analysis),
            "demographic": self._predict_demographics(profile_data, content_analysis),
        }

        # Filter predictions by confidence threshold
        filtered_predictions = self._filter_low_confidence_predictions(predictions)

        return {
            "predictions": filtered_predictions,
            "disclaimer": "These predictions are generated using AI analysis of public profile data "
            "and should be considered approximations rather than definitive conclusions.",
        }

    def _generate_mock_predictions(
        self, profile_data: Dict[str, Any], content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive mock predictions for demonstration purposes

        Args:
            profile_data: Dictionary containing profile data
            content_analysis: Results from content analysis

        Returns:
            Complete mock predictions data structure
        """
        import random

        # Use username as seed for deterministic results
        username = profile_data.get("profile", {}).get("username", "default")
        seed_value = sum(ord(c) for c in str(username))
        random.seed(seed_value)

        # Standard disclaimer
        disclaimer = "These predictions are generated using AI analysis of public profile data and should be considered approximations rather than definitive conclusions. For demonstration purposes only."

        # Future interests predictions
        future_interests = [
            {
                "interest": "Sustainable technology",
                "confidence": round(random.uniform(0.7, 0.95), 2),
                "reasoning": "Based on engagement with environmental content and tech discussions",
            },
            {
                "interest": "Remote work tools",
                "confidence": round(random.uniform(0.65, 0.85), 2),
                "reasoning": "Increasing mentions of productivity and digital collaboration",
            },
        ]

        # Add 1-2 more random interests
        potential_extra_interests = [
            {
                "interest": "Artificial intelligence",
                "confidence": round(random.uniform(0.6, 0.85), 2),
                "reasoning": "Recent engagement with AI-related topics",
            },
            {
                "interest": "Mindfulness & wellness",
                "confidence": round(random.uniform(0.6, 0.8), 2),
                "reasoning": "Growing interest in health-related content",
            },
            {
                "interest": "Digital privacy",
                "confidence": round(random.uniform(0.65, 0.9), 2),
                "reasoning": "Increased awareness of privacy topics in recent posts",
            },
            {
                "interest": "Data visualization",
                "confidence": round(random.uniform(0.7, 0.85), 2),
                "reasoning": "Content suggests growing interest in data presentation",
            },
        ]

        # Add 1-2 random additional interests
        future_interests.extend(
            random.sample(potential_extra_interests, random.randint(1, 2))
        )

        # Behavioral predictions
        potential_behaviors = [
            {
                "behavior": "Likely to engage with educational content",
                "confidence": round(random.uniform(0.7, 0.9), 2),
                "reasoning": "Consistent pattern of interacting with learning materials",
            },
            {
                "behavior": "Tends to be an early adopter of new technologies",
                "confidence": round(random.uniform(0.65, 0.85), 2),
                "reasoning": "History of discussing new products soon after release",
            },
            {
                "behavior": "Shares content primarily during weekday evenings",
                "confidence": round(random.uniform(0.75, 0.95), 2),
                "reasoning": "Strong temporal pattern in posting behavior",
            },
        ]

        # Demographic predictions (with appropriate caution since these are sensitive)
        demographic_predictions = {
            "age_range": {
                "prediction": "25-34",
                "confidence": round(random.uniform(0.6, 0.75), 2),
            },
            "education_level": {
                "prediction": "Bachelor's degree or higher",
                "confidence": round(random.uniform(0.55, 0.7), 2),
            },
            "occupation_category": {
                "prediction": "Technology/Digital sector",
                "confidence": round(random.uniform(0.6, 0.8), 2),
            },
        }

        # Affinities (brands, media, etc.)
        affinity_predictions = [
            {
                "category": "Technology brands",
                "affinities": ["Apple", "Google", "Microsoft"],
                "confidence": round(random.uniform(0.7, 0.9), 2),
            },
            {
                "category": "Media consumption",
                "affinities": [
                    "Technology news",
                    "Business podcasts",
                    "Documentary streaming",
                ],
                "confidence": round(random.uniform(0.65, 0.85), 2),
            },
            {
                "category": "Online platforms",
                "affinities": ["Twitter/X", "LinkedIn", "Medium"],
                "confidence": round(random.uniform(0.7, 0.95), 2),
            },
        ]

        # Assemble complete predictions
        return {
            "disclaimer": disclaimer,
            "future_interests": future_interests,
            "potential_behaviors": potential_behaviors,
            "demographic_predictions": demographic_predictions,
            "affinity_predictions": affinity_predictions,
        }

    def _predict_personality_traits(
        self, content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict personality traits based on content analysis

        Returns:
            Dictionary with trait predictions and confidence scores
        """
        traits = {}

        # Use existing personality traits if available
        if "personality_traits" in content_analysis:
            base_traits = content_analysis["personality_traits"]

            # Map traits to descriptive labels with confidence
            if "extraversion" in base_traits:
                extraversion = base_traits["extraversion"]
                if extraversion > 0.7:
                    traits["extraversion"] = {
                        "label": "extraverted",
                        "description": "Likely enjoys social interaction and being around others",
                        "confidence": min(1.0, extraversion + 0.1),
                    }
                elif extraversion < 0.3:
                    traits["extraversion"] = {
                        "label": "introverted",
                        "description": "Likely prefers solitude or small group interactions",
                        "confidence": min(1.0, 1.0 - extraversion + 0.1),
                    }

            if "openness" in base_traits:
                openness = base_traits["openness"]
                if openness > 0.7:
                    traits["openness"] = {
                        "label": "open to new experiences",
                        "description": "Shows curiosity and appreciation for variety and novel experiences",
                        "confidence": min(1.0, openness + 0.1),
                    }
                elif openness < 0.3:
                    traits["openness"] = {
                        "label": "conventional",
                        "description": "Tends to prefer familiar routines and traditional values",
                        "confidence": min(1.0, 1.0 - openness + 0.1),
                    }

            if "conscientiousness" in base_traits:
                conscientiousness = base_traits["conscientiousness"]
                if conscientiousness > 0.7:
                    traits["conscientiousness"] = {
                        "label": "highly conscientious",
                        "description": "Likely organized, responsible, and goal-oriented",
                        "confidence": min(1.0, conscientiousness + 0.1),
                    }
                elif conscientiousness < 0.3:
                    traits["conscientiousness"] = {
                        "label": "spontaneous",
                        "description": "May prefer flexibility over rigid planning and structure",
                        "confidence": min(1.0, 1.0 - conscientiousness + 0.1),
                    }

        # Additional traits based on writing style
        if "writing_style" in content_analysis:
            style = content_analysis["writing_style"]

            # Formality as a trait
            if "formality_score" in style:
                formality = style["formality_score"]
                if formality > 0.7:
                    traits["communication_style"] = {
                        "label": "formal communicator",
                        "description": "Tends to use precise, structured language in communication",
                        "confidence": min(1.0, formality + 0.1),
                    }
                elif formality < 0.3:
                    traits["communication_style"] = {
                        "label": "casual communicator",
                        "description": "Tends to use relaxed, informal language in communication",
                        "confidence": min(1.0, 1.0 - formality + 0.1),
                    }

        return traits

    def _predict_interests(
        self, profile_data: Dict[str, Any], content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict user interests based on content

        Returns:
            Dictionary with interest predictions and confidence scores
        """
        interests = {}

        # Use topic distribution if available
        if "content_topics" in content_analysis:
            topics = content_analysis["content_topics"]
            topic_dist = topics.get("topic_distribution", {})

            # Convert topics to interests with confidence scores
            for topic, count in topic_dist.items():
                # Normalize count to confidence (assuming max count around 10)
                confidence = min(0.95, count / 10)

                if confidence >= self.confidence_threshold:
                    interests[topic] = {
                        "label": topic,
                        "description": f"Shows interest in {topic}-related content",
                        "confidence": round(confidence, 2),
                    }

        # Look at hashtags for additional interest signals
        if "content_topics" in content_analysis:
            hashtags = content_analysis["content_topics"].get("top_hashtags", [])

            for hashtag, count in hashtags:
                # Skip hashtags that are just single letters or numbers
                if len(hashtag) <= 2:
                    continue

                # Convert hashtag to interest
                tag = hashtag.replace("#", "").lower()

                # Skip if already covered in topics
                if tag in interests or any(tag in t for t in interests.keys()):
                    continue

                # Normalize count to confidence
                confidence = min(0.9, 0.6 + (count / 20))

                if confidence >= self.confidence_threshold:
                    interests[tag] = {
                        "label": tag,
                        "description": f"Frequently uses {hashtag}",
                        "confidence": round(confidence, 2),
                    }

        return interests

    def _predict_behavior_patterns(
        self, content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict user behavior patterns

        Returns:
            Dictionary with behavior predictions and confidence scores
        """
        behaviors = {}

        # Use posting patterns if available
        if "posting_patterns" in content_analysis:
            patterns = content_analysis["posting_patterns"]

            # Activity time predictions
            if "activity_hours" in patterns:
                activity = patterns["activity_hours"]
                time_periods = activity.get("time_periods", {})

                # Find the dominant time period
                dominant_period = max(
                    time_periods.items(),
                    key=lambda x: (
                        x[1].get("percentage", 0) if isinstance(x[1], dict) else 0
                    ),
                )[0]

                # Calculate confidence based on percentage
                dominant_percentage = time_periods.get(dominant_period, {}).get(
                    "percentage", 0
                )
                confidence = min(0.95, dominant_percentage / 100)

                if confidence >= self.confidence_threshold:
                    behaviors["active_time"] = {
                        "label": f"{dominant_period} person",
                        "description": f"Most active during {dominant_period} hours",
                        "confidence": round(confidence, 2),
                    }

            # Posting frequency predictions
            if "frequency" in patterns:
                frequency = patterns["frequency"]
                daily_avg = frequency.get("daily_average", 0)

                if daily_avg > 5:
                    behaviors["posting_frequency"] = {
                        "label": "frequent poster",
                        "description": "Posts multiple times daily on average",
                        "confidence": min(0.95, 0.7 + (daily_avg / 20)),
                    }
                elif daily_avg < 0.3:  # Less than twice a week
                    behaviors["posting_frequency"] = {
                        "label": "occasional poster",
                        "description": "Posts infrequently, typically less than weekly",
                        "confidence": min(0.95, 0.7 + ((1 - daily_avg) / 2)),
                    }

        # Use sentiment analysis for emotional pattern predictions
        if "sentiment" in content_analysis:
            sentiment = content_analysis["sentiment"]
            overall = sentiment.get("overall_sentiment", {})

            label = overall.get("label", "")
            score = abs(
                overall.get("score", 0)
            )  # Use absolute value of sentiment score

            if label and score > 0.3:
                if label == "positive":
                    behaviors["emotional_expression"] = {
                        "label": "positive expresser",
                        "description": "Tends to express positive emotions in posts",
                        "confidence": min(0.95, 0.6 + score),
                    }
                elif label == "negative":
                    behaviors["emotional_expression"] = {
                        "label": "critical expresser",
                        "description": "Tends to express critical or negative views in posts",
                        "confidence": min(0.95, 0.6 + score),
                    }

        return behaviors

    def _predict_demographics(
        self, profile_data: Dict[str, Any], content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict demographic information
        This should be handled with extreme care and appropriate disclaimers

        Returns:
            Dictionary with demographic predictions and confidence scores
        """
        # Note: demographic predictions should be minimal and handled carefully
        demographics = {}

        # Predict occupation category based on topics and language
        if "content_topics" in content_analysis:
            topics = content_analysis["content_topics"]
            top_topics = topics.get("top_topics", [])

            # Simple occupation category inference from topics
            tech_topics = [
                "technology",
                "programming",
                "coding",
                "software",
                "development",
            ]
            creative_topics = ["design", "art", "music", "writing", "creative"]
            business_topics = ["business", "marketing", "finance", "entrepreneur"]

            # Check if any group of topics is strongly represented
            for topic_name, count in top_topics:
                confidence = 0.0
                occupation = ""

                if topic_name in tech_topics:
                    occupation = "tech professional"
                    confidence = min(0.75, 0.6 + (count / 10))
                elif topic_name in creative_topics:
                    occupation = "creative professional"
                    confidence = min(0.75, 0.6 + (count / 10))
                elif topic_name in business_topics:
                    occupation = "business professional"
                    confidence = min(0.75, 0.6 + (count / 10))

                if occupation and confidence >= self.confidence_threshold:
                    demographics["occupation_category"] = {
                        "label": occupation,
                        "description": f"Content suggests possible background in {occupation} field",
                        "confidence": round(confidence, 2),
                    }
                    break

        return demographics

    def _filter_low_confidence_predictions(
        self, predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter out predictions below the confidence threshold

        Args:
            predictions: Dictionary of predictions

        Returns:
            Filtered predictions
        """
        filtered = {}

        for category, category_predictions in predictions.items():
            filtered_category = {}

            for trait, prediction in category_predictions.items():
                confidence = prediction.get("confidence", 0)

                if confidence >= self.confidence_threshold:
                    filtered_category[trait] = prediction

            if filtered_category:
                filtered[category] = filtered_category

        return filtered
