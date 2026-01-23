# Vanta Deep Intelligence Platform - Master Implementation Plan

> **Created**: January 23, 2026  
> **Version**: 2.1 - Feature Complete
> **Goal**: Maintain and optimize the industry-leading digital intelligence platform. **All Core Features Implemented.**

---

## 🎯 Executive Summary

Vanta will evolve from a basic profile analyzer to a **Comprehensive Digital Intelligence Platform** capable of:

1. **Total Data Collection** - Every available endpoint from ScrapeCreators (100+ data points)
2. **Dual Analysis Modes** - Quick Scan (10s) and Deep Dossier (2-5 min)
3. **Cross-Platform Discovery** - Automatic + manual identity resolution
4. **AI-Powered Intelligence** - Psychological profiling, behavioral analysis, predictions
5. **Professional Outputs** - Web Dashboard, PDF Dossier, JSON/CSV, Timeline View, Network Graph
6. **Historical Tracking** - Snapshot storage with change detection

---

## 📊 Platform Data Matrix

### ScrapeCreators Endpoints to Implement

| Platform | Endpoints | Priority | Status |
|----------|-----------|----------|--------|
| **TikTok** | Profile, Audience Demographics, Videos, Video Info, Transcript, Live, Comments, Following, Followers, Search Users, Search Hashtag, Search Keyword, Top Search, Popular Songs/Creators/Videos/Hashtags, Song Details, TikToks using Song, Trending Feed | P0 | ⏳ Partial |
| **TikTok Shop** | Shop Search, Shop Products, Product Details | P1 | ⏳ Partial |
| **Instagram** | Profile, Basic Profile, Posts, Post/Reel Info, Transcript, Search Reels, Comments, Reels, Story Highlights, Highlights Details, Reels using Song, Embed HTML | P0 | ⏳ Partial |
| **YouTube** | Channel Details, Channel Videos, Channel Shorts, Video/Short Details, Transcript, Search, Search Hashtag, Comments, Trending Shorts, Playlist, Community Post Details | P0 | ⏳ Partial |
| **LinkedIn** | Person's Profile, Company Page, Post | P0 | ⏳ Partial |
| **Facebook** | Profile, Profile Reels, Profile Posts, Group Posts, Post, Transcript, Comments | P0 | ⏳ Partial |
| **Facebook Ad Library** | Ad Details, Search, Company Ads, Search for Companies | P1 | ⏳ Partial |
| **Google Ad Library** | Company Ads, Ad Details, Advertiser Search | P1 | ⏳ Partial |
| **LinkedIn Ad Library** | Search Ads, Ad Details | P1 | ⏳ Partial |
| **Twitter** | Profile, User Tweets, Tweet Details, Transcript, Community, Community Tweets | P0 | ⏳ Partial |
| **Reddit** | Subreddit Details, Subreddit Posts, Post Comments, Search, Search Ads, Get Ad | P0 | ⏳ Partial |
| **Threads** | Profile, Posts, Post, Search Users | P0 | ⏳ Partial |
| **Bluesky** | Profile, Posts, Post | P1 | ⏳ Partial |
| **Pinterest** | Search, Pin, User Boards, Board | P1 | ⏳ Partial |
| **Google** | Search | P2 | ⏳ Partial |
| **Twitch** | Profile, Clip | P1 | ⏳ Partial |
| **Kick** | Clip | P2 | ⏳ Partial |
| **Snapchat** | User Profile | P1 | ⏳ Partial |
| **Linktree** | Linktree page | P0 | ⏳ Partial |
| **Komi** | Komi page | P2 | ⏳ Partial |
| **Pillar** | Pillar page | P2 | ⏳ Partial |
| **Linkbio** | Linkbio page | P2 | ⏳ Partial |
| **Amazon Shop** | Amazon Shop page | P1 | ⏳ Partial |
| **Age & Gender** | Predict from image | P0 | ⏳ Partial |

**Legend**: P0 = Critical, P1 = High, P2 = Medium

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     VANTA FRONTEND (React)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Dashboard │ │ Dossier  │ │ Timeline │ │ Network  │           │
│  │   View   │ │   View   │ │   View   │ │  Graph   │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VANTA API (Flask)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  /api/analyze   │  │ /api/dossier    │  │ /api/export     │ │
│  │  Quick/Deep     │  │ Full Report     │  │ PDF/CSV/JSON    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INTELLIGENCE ENGINE                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Data Collector  │  │  AI Analyzer    │  │ Report Builder  │ │
│  │ (All Endpoints) │  │ (OpenRouter)    │  │ (PDF/Charts)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                    │                    │           │
│           ▼                    ▼                    ▼           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              SCRAPE CREATORS CLIENT (Enhanced)              ││
│  │  100+ endpoints across 20+ platforms                        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ SQLite/  │  │  Redis   │  │ Snapshot │  │  Export  │       │
│  │ Postgres │  │  Cache   │  │  Store   │  │  Files   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Phases

### Phase 1: Enhanced Data Collection Layer (Days 1-2) - ✅ COMPLETE

**Goal**: Expand `scrape_client.py` to cover ALL ScrapeCreators endpoints.

#### Task 1.1: TikTok Complete Integration
**Files**: `app/core/scrape_client.py`

```python
# New methods to add:
- get_tiktok_audience_demographics(username)
- get_tiktok_video_info(video_id)
- get_tiktok_transcript(video_id)
- get_tiktok_live(username)
- get_tiktok_following(username, count)
- get_tiktok_followers(username, count)
- search_tiktok_users(query)
- search_tiktok_hashtag(hashtag)
- search_tiktok_keyword(keyword)
- get_tiktok_trending()
- get_tiktok_popular_songs()
- get_tiktok_popular_creators()
- get_tiktok_popular_videos()
- get_tiktok_popular_hashtags()
- get_tiktok_song_details(song_id)
- get_tiktoks_using_song(song_id)
```

#### Task 1.2: Instagram Complete Integration
```python
- get_instagram_post_info(post_id)
- get_instagram_transcript(reel_id)
- search_instagram_reels(query)
- get_instagram_comments(post_id)
- get_instagram_reels(username)
- get_instagram_story_highlights(username)
- get_instagram_highlight_details(highlight_id)
- get_instagram_reels_using_song(song_id)
- get_instagram_embed_html(url)
```

#### Task 1.3: YouTube Complete Integration
```python
- get_youtube_channel_details(channel_id)
- get_youtube_channel_videos(channel_id)
- get_youtube_channel_shorts(channel_id)
- get_youtube_video_details(video_id)
- get_youtube_short_details(short_id)
- get_youtube_transcript(video_id)  # Already exists
- search_youtube(query)
- search_youtube_hashtag(hashtag)
- get_youtube_comments(video_id)
- get_youtube_trending_shorts()
- get_youtube_playlist(playlist_id)
- get_youtube_community_post(post_id)
```

#### Task 1.4: All Other Platforms
```python
# LinkedIn
- get_linkedin_company_page(company_id)
- get_linkedin_post(post_id)

# Facebook
- get_facebook_reels(username)
- get_facebook_posts(username)
- get_facebook_group_posts(group_id)
- get_facebook_post(post_id)
- get_facebook_transcript(video_id)
- get_facebook_comments(post_id)

# Twitter
- get_twitter_tweet_details(tweet_id)
- get_twitter_transcript(tweet_id)
- get_twitter_community(community_id)
- get_twitter_community_tweets(community_id)

# Reddit
- get_reddit_subreddit_details(subreddit)
- get_reddit_subreddit_posts(subreddit)
- get_reddit_post_comments(post_id)
- search_reddit(query)
- search_reddit_ads(query)
- get_reddit_ad(ad_id)

# Threads
- get_threads_posts(username)
- get_threads_post(post_id)
- search_threads_users(query)

# Bluesky
- get_bluesky_posts(username)
- get_bluesky_post(post_id)

# Pinterest
- search_pinterest(query)
- get_pinterest_pin(pin_id)
- get_pinterest_boards(username)
- get_pinterest_board(board_id)

# Twitch
- get_twitch_clip(clip_id)

# Kick
- get_kick_clip(clip_id)
```

---

### Phase 2: Deep Dossier Collector (Days 2-3) - ✅ COMPLETE

**Goal**: Create orchestration layer for comprehensive data collection.

#### Task 2.1: Create Deep Collector Module
**File**: `app/core/deep_collector.py` (NEW)

```python
class DeepDossierCollector:
    """
    Orchestrates comprehensive data collection across all platforms.
    Supports Quick Scan and Deep Dossier modes.
    """
    
    def __init__(self, scrape_client):
        self.client = scrape_client
        
    def quick_scan(self, platform: str, username: str) -> Dict:
        """Quick 10-second scan: Profile + Recent 10 posts"""
        pass
        
    def deep_dossier(self, platform: str, username: str) -> Dict:
        """Comprehensive 2-5 minute scan: Everything available"""
        pass
        
    def cross_platform_discovery(self, username: str, known_platforms: List[str]) -> Dict:
        """Discover linked accounts across platforms"""
        pass
        
    def collect_entire_footprint(self, usernames: Dict[str, str]) -> Dict:
        """Collect from multiple platforms with different usernames"""
        pass
```

#### Task 2.2: Platform-Specific Collectors
```python
class TikTokDeepCollector:
    """Collects all TikTok data for a user"""
    
    def collect_all(self, username: str) -> Dict:
        return {
            "profile": self.client.get_tiktok_profile(username),
            "demographics": self.client.get_tiktok_audience_demographics(username),
            "videos": self.client.get_tiktok_videos(username, count=50),
            "followers_sample": self.client.get_tiktok_followers(username, count=100),
            "following_sample": self.client.get_tiktok_following(username, count=100),
            "comments_analysis": self._analyze_video_comments(),
            "transcripts": self._get_video_transcripts(),
        }
```

---

### Phase 3: Enhanced AI Analysis (Days 3-4) - ✅ COMPLETE

**Goal**: Expand OpenRouter client with comprehensive intelligence prompts.

#### Task 3.1: Expand Platform Prompts
**File**: `app/core/platform_prompts.py`

Add specialized prompts for:
- Psychological profiling (OCEAN, emotional patterns)
- Behavioral analysis (activity patterns, engagement style)
- Network analysis (influence mapping, key connections)
- Predictive modeling (future content, likely actions)
- Authenticity scoring (bot detection, fake followers)
- Commercial intelligence (revenue estimate, brand deals)

#### Task 3.2: Create Master Intelligence Analyzer
**File**: `app/core/intelligence_analyzer.py` (NEW)

```python
class IntelligenceAnalyzer:
    """Master AI analyzer for comprehensive intelligence reports"""
    
    def generate_psychological_profile(self, data: Dict) -> Dict:
        """OCEAN personality, emotional patterns, risk indicators"""
        pass
        
    def analyze_behavioral_patterns(self, data: Dict) -> Dict:
        """Activity times, posting frequency, engagement style"""
        pass
        
    def map_network_influence(self, data: Dict) -> Dict:
        """Key connections, influence score, community roles"""
        pass
        
    def generate_predictions(self, data: Dict) -> Dict:
        """Future content topics, likely actions, trend alignment"""
        pass
        
    def score_authenticity(self, data: Dict) -> Dict:
        """Bot probability, fake follower %, content authenticity"""
        pass
        
    def analyze_sentiment_timeline(self, data: Dict) -> Dict:
        """Emotional trajectory, mood patterns, trigger events"""
        pass
        
    def map_interests_topics(self, data: Dict) -> Dict:
        """Topic cloud, obsessions, evolving interests"""
        pass
        
    def estimate_commercial_value(self, data: Dict) -> Dict:
        """Revenue estimate, brand affinity, engagement value"""
        pass
        
    def generate_executive_summary(self, all_analyses: Dict) -> str:
        """Human-readable executive summary"""
        pass
```

#### Task 3.3: Consumer Intelligence Analyzer
**File**: `app/core/consumer_intelligence.py` (NEW)

This is the **Purchase Behavior & Forecasting Engine** — predicting what someone uses, wants, and will buy.

```python
class ConsumerIntelligenceAnalyzer:
    """
    Analyzes consumer behavior, brand affinity, and purchase intent.
    Provides forecasting for future purchases.
    """
    
    def __init__(self, openrouter_client):
        self.ai = openrouter_client
    
    # ═══════════════════════════════════════════════════════════════
    # CURRENT BEHAVIOR ANALYSIS
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_current_products(self, data: Dict) -> Dict:
        """
        Identify products/brands the person currently uses.
        
        Data Sources:
        - TikTok Shop purchases & browsing
        - Amazon Shop activity
        - Instagram product tags & shopping posts
        - Unboxing/review videos they've posted
        - Brand mentions in posts/captions
        - Affiliate links they share
        - Sponsored content partnerships
        """
        return {
            "confirmed_products": [],      # Products they've shown/mentioned
            "brand_affiliations": [],      # Brands they work with/promote
            "product_categories": [],      # Categories they engage with
            "price_tier": "",              # Budget/Mid/Premium/Luxury
            "brand_loyalty_score": 0.0,    # How loyal to specific brands
        }
    
    def analyze_brand_affinity(self, data: Dict) -> Dict:
        """
        Map brand relationships and preferences.
        
        Signals:
        - Frequency of brand mentions
        - Sentiment when discussing brands
        - Sponsored vs organic mentions
        - Brand engagement (tagging, using hashtags)
        - Competitor mentions
        """
        return {
            "top_brands": [],              # Ranked list of brand affinities
            "brand_sentiment_map": {},     # {brand: sentiment_score}
            "sponsored_relationships": [], # Known paid partnerships
            "brand_switching_signals": [], # Signs of brand dissatisfaction
        }
    
    # ═══════════════════════════════════════════════════════════════
    # PURCHASE INTENT DETECTION
    # ═══════════════════════════════════════════════════════════════
    
    def detect_purchase_intent(self, data: Dict) -> Dict:
        """
        Identify products they're considering buying.
        
        Signals:
        - "Should I buy..." posts/comments
        - Product comparison discussions
        - Saved/bookmarked products
        - Wishlist activity
        - Asking for recommendations
        - Window shopping behavior (views without purchase)
        - Cart abandonment patterns
        """
        return {
            "high_intent_products": [],    # Likely to buy soon
            "consideration_set": [],       # Actively researching
            "wishlist_items": [],          # Saved for later
            "intent_confidence": 0.0,      # Overall confidence score
        }
    
    def analyze_shopping_behavior(self, data: Dict) -> Dict:
        """
        Understand HOW they shop.
        
        Patterns:
        - Impulse vs research buyer
        - Price sensitivity
        - Review dependency
        - Influencer-driven decisions
        - Seasonal shopping patterns
        - Platform preferences (Amazon, TikTok Shop, etc.)
        """
        return {
            "buyer_type": "",              # Impulse/Researcher/Deal-Hunter/Loyalist
            "price_sensitivity": "",       # Low/Medium/High
            "decision_factors": [],        # [Reviews, Price, Brand, Influencer]
            "shopping_platforms": [],      # Preferred platforms
            "shopping_frequency": "",      # Daily/Weekly/Monthly/Seasonal
        }
    
    # ═══════════════════════════════════════════════════════════════
    # PURCHASE FORECASTING (The "Perfect Forecast")
    # ═══════════════════════════════════════════════════════════════
    
    def forecast_purchases(self, data: Dict, timeframe_days: int = 90) -> Dict:
        """
        Predict what they will buy in the next X days.
        
        Methodology:
        1. Analyze current interest signals
        2. Map to product lifecycle (research → decision → purchase)
        3. Factor in seasonality (holidays, events)
        4. Consider financial indicators (payday patterns, splurge behavior)
        5. Apply category-specific purchase cycles
        """
        return {
            "predicted_purchases": [
                {
                    "product_category": "",
                    "specific_products": [],
                    "predicted_timeframe": "",
                    "confidence": 0.0,
                    "reasoning": "",
                    "trigger_events": [],    # What might prompt the purchase
                }
            ],
            "spending_forecast": {
                "estimated_total": 0.0,
                "by_category": {},
            },
            "key_decision_points": [],       # Events that will trigger decisions
        }
    
    def predict_category_interest(self, data: Dict) -> Dict:
        """
        Forecast emerging interests before they show explicit intent.
        
        Signals:
        - Following new accounts in a category
        - Increased engagement with category content
        - Life stage transitions (moving, baby, career change)
        - Social circle influence (what friends are buying)
        """
        return {
            "emerging_interests": [],
            "category_trajectory": {},       # Rising/Stable/Declining per category
            "life_stage_indicators": [],
            "social_influence_map": {},
        }
    
    # ═══════════════════════════════════════════════════════════════
    # COMMERCE INTELLIGENCE
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_commerce_activity(self, data: Dict) -> Dict:
        """
        Full commerce behavior analysis.
        
        Data Sources:
        - TikTok Shop (products, purchases, reviews)
        - Amazon Shop (storefront, recommendations)
        - Instagram Shopping (tagged products, saves)
        - Affiliate link usage patterns
        """
        return {
            "tiktok_shop": {
                "products_viewed": [],
                "products_purchased": [],
                "review_sentiment": {},
            },
            "amazon_activity": {
                "storefront_products": [],
                "category_focus": [],
            },
            "affiliate_behavior": {
                "links_shared": [],
                "commission_categories": [],
            },
        }
    
    # ═══════════════════════════════════════════════════════════════
    # AI-POWERED CONSUMER PROFILE
    # ═══════════════════════════════════════════════════════════════
    
    def generate_consumer_profile(self, all_data: Dict) -> Dict:
        """
        Comprehensive AI-generated consumer intelligence report.
        """
        prompt = f"""
        Analyze this person's complete digital footprint and generate a 
        comprehensive consumer intelligence profile.
        
        Data: {json.dumps(all_data)}
        
        Provide:
        1. CURRENT USAGE: What products/brands they currently use
        2. SHOPPING PSYCHOLOGY: How they make purchase decisions
        3. BRAND RELATIONSHIPS: Their brand loyalties and preferences
        4. PURCHASE INTENT: What they're actively considering buying
        5. 90-DAY FORECAST: Predicted purchases with confidence scores
        6. TRIGGER EVENTS: What would prompt immediate purchases
        7. PRICE SENSITIVITY: Their spending comfort zone
        8. INFLUENCE SUSCEPTIBILITY: How much influencers affect their decisions
        
        Format as structured JSON with clear categories.
        """
        
        return self.ai.analyze(prompt)
```

#### Task 3.4: Belief System & Stance Analyzer
**File**: `app/core/belief_analyzer.py` (NEW)

This module profiles the target's **Worldview** — Political, Social, and Ethical alignment.

```python
class BeliefSystemAnalyzer:
    """
    Analyzes political orientation, social values, and ethical frameworks.
    Forecasts reactions to future events.
    """
    
    def analyze_political_stance(self, content_data: Dict) -> Dict:
        """
        Map political alignment based on content and discourse.
        
        Output:
        - Economic Axis: Left <-> Right
        - Social Axis: Authoritarian <-> Libertarian
        - Key Issues: Stance on specific topics (Climate, Economy, Rights)
        - Engagement Style: Activist, Observer, or Apathetic
        """
        pass

    def analyze_social_values(self, content_data: Dict) -> Dict:
        """
        Identify core social values.
        
        Dimensions:
        - Tradition vs. Progress
        - Individualism vs. Collectivism
        - Materialism vs. Experience
        """
        pass

    def analyze_ethical_framework(self, content_data: Dict) -> Dict:
        """
        Infer ethical reasoning style.
        
        - Utilitarian (Result-focused)
        - Deontological (Rule-focused)
        - Virtue Ethics (Character-focused)
        """
        pass

    def forecast_stance(self, profile: Dict, unexpected_event: str) -> str:
        """
        Predict how the target will react/align on a hypothetical future event.
        
        Example: "How would they react to a new carbon tax?"
        """
        pass
```

**Consumer Data Sources by Platform**:

| Platform | Consumer Intelligence Data |
|----------|---------------------------|
| **TikTok** | Videos watched, Shop activity, Product hashtags, Trending sounds (product-related) |
| **TikTok Shop** | Products viewed, Purchases, Reviews, Wishlists |
| **Instagram** | Shopping saves, Product tags, Brand follows, Story polls about products |
| **Amazon Shop** | Storefront products, Reviews written, Lists |
| **YouTube** | Watch history topics, Shopping shelf engagement, Review video engagement |
| **Pinterest** | Boards (product categories), Saved pins, Shopping pins |
| **Twitter** | Product mentions, Brand complaints, Purchase announcements |
| **Reddit** | Subreddit activity (r/BuyItForLife, r/deals, r/AskReddit about products) |
| **Facebook** | Marketplace activity, Group purchases, Ad engagement |
| **Linktree/Komi/Pillar** | Affiliate links, Product recommendations |

---

### Phase 4: Database & Storage (Day 4) - ✅ COMPLETE

**Goal**: Store snapshots for historical tracking.

#### Task 4.1: Expand Database Models
**File**: `app/web/models.py`

```python
class DossierSnapshot(db.Model):
    """Stores point-in-time snapshots of collected data"""
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    platform = db.Column(db.String(50))
    username = db.Column(db.String(255))
    snapshot_data = db.Column(db.JSON)  # Full raw data
    analysis_data = db.Column(db.JSON)  # AI analysis results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class CrossPlatformProfile(db.Model):
    """Links multiple platform profiles to a single identity"""
    id = db.Column(db.Integer, primary_key=True)
    identity_name = db.Column(db.String(255))  # Human-assigned name
    platforms = db.Column(db.JSON)  # {platform: username}
    linked_accounts = db.Column(db.JSON)  # Discovered links
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

---

### Phase 5: Export & Reporting (Days 5-6) - ✅ COMPLETE

**Goal**: Professional output formats.

#### Task 5.1: PDF Dossier Generator
**File**: `app/core/report_generator.py` (NEW)

```python
class DossierReportGenerator:
    """Generates professional PDF dossiers"""
    
    def generate_pdf(self, dossier_data: Dict) -> bytes:
        """Generate branded PDF report"""
        # Sections:
        # - Cover page with Vanta branding
        # - Executive Summary
        # - Profile Overview (all platforms)
        # - Psychological Assessment
        # - Behavioral Analysis
        # - Network Map
        # - Content Analysis
        # - Risk Indicators
        # - Predictions
        # - Raw Data Appendix
        pass
```

#### Task 5.2: Export Endpoints
**File**: `app/web/routes/api.py`

```python
@api_bp.route('/api/tasks/<int:task_id>/export/pdf')
def export_pdf(task_id):
    """Download PDF dossier"""
    pass

@api_bp.route('/api/tasks/<int:task_id>/export/csv')
def export_csv(task_id):
    """Download CSV data"""
    pass

@api_bp.route('/api/tasks/<int:task_id>/export/json')
def export_json(task_id):
    """Download full JSON"""
    pass
```

---

### Phase 6: Frontend Visualization (Days 6-8) - ✅ COMPLETE

**Goal**: Premium visualization components.

#### Task 6.1: Dossier View Component
**File**: `frontend/src/components/DossierView.tsx` (NEW)

Sections:
- Profile header (photo, demographics, verified status)
- Quick stats cards (followers, engagement, authenticity score)
- Psychological radar chart (OCEAN)
- Sentiment timeline (line chart)
- Topic/interest word cloud
- Network graph (key connections)
- Activity heatmap (posting times)
- Content gallery (posts/videos)

#### Task 6.2: Timeline View Component
**File**: `frontend/src/components/TimelineView.tsx` (NEW)

- Chronological activity across all platforms
- Filter by platform, date range, content type
- Highlight key events (viral posts, controversies)

#### Task 6.3: Network Graph Component
**File**: `frontend/src/components/NetworkGraph.tsx` (NEW)

- Interactive D3.js/Vis.js network visualization
- Show connections, influence, community clusters
- Click to drill down into connected profiles

#### Task 6.4: Analysis Mode Selector
**File**: `frontend/src/components/AnalysisForm.tsx`

Add:
- Quick Scan / Deep Dossier toggle
- Multi-platform input (same username across platforms)
- Platform-specific username inputs
- Cross-platform discovery checkbox

---

### Phase 7: Cross-Platform Discovery (Day 8) - ✅ COMPLETE

**Goal**: Automatic identity linking.

#### Task 7.1: Link Discovery Engine
**File**: `app/core/link_discovery.py` (NEW)

```python
class LinkDiscoveryEngine:
    """Discovers linked accounts across platforms"""
    
    def extract_links_from_bio(self, bio: str) -> List[Dict]:
        """Parse bio for social links"""
        pass
        
    def analyze_linktree(self, username: str) -> List[Dict]:
        """Get all links from Linktree page"""
        pass
        
    def match_by_username(self, username: str) -> Dict[str, bool]:
        """Check if same username exists on other platforms"""
        pass
        
    def fingerprint_match(self, profile_a: Dict, profile_b: Dict) -> float:
        """Calculate similarity score between profiles"""
        # Compare: bio text, profile images, posting style
        pass
```

---

## 📁 File Change Summary

### New Files to Create
| File | Purpose |
|------|---------|
| `app/core/deep_collector.py` | Orchestrates comprehensive data collection |
| `app/core/intelligence_analyzer.py` | Master AI analysis engine |
| `app/core/report_generator.py` | PDF/export generation |
| `app/core/link_discovery.py` | Cross-platform identity resolution |
| `frontend/src/components/DossierView.tsx` | Comprehensive results display |
| `frontend/src/components/TimelineView.tsx` | Chronological activity view |
| `frontend/src/components/NetworkGraph.tsx` | Interactive network visualization |

### Files to Modify
| File | Changes |
|------|---------|
| `app/core/scrape_client.py` | Add 80+ new endpoint methods |
| `app/core/platform_prompts.py` | Add intelligence analysis prompts |
| `app/core/openrouter_client.py` | Add new analysis methods |
| `app/web/models.py` | Add snapshot and cross-platform models |
| `app/web/routes/api.py` | Add dossier and export endpoints |
| `frontend/src/components/AnalysisForm.tsx` | Add mode selector, multi-platform |
| `frontend/src/components/ResultView.tsx` | Enhanced visualization |
| `frontend/src/App.tsx` | Add new routes |

---

## ⏱️ Estimated Timeline

| Phase | Description | Duration | Dependencies | Status |
|-------|-------------|----------|--------------|--------|
| Phase 1 | Data Collection Layer | 2 days | None | ✅ Complete |
| Phase 2 | Deep Dossier Collector | 1.5 days | Phase 1 | ✅ Complete |
| Phase 3 | AI Analysis Enhancement | 1.5 days | Phase 2 | ✅ Complete |
| Phase 4 | Database & Storage | 0.5 days | Phase 2 | ✅ Complete |
| Phase 5 | Export & Reporting | 1 day | Phase 3, 4 | ✅ Complete |
| Phase 6 | Frontend Visualization | 2 days | Phase 3, 5 | ✅ Complete |
| Phase 7 | Cross-Platform Discovery | 1 day | Phase 1, 2 | ✅ Complete |

**Total Estimated Time**: 9-10 working days (Completed ahead of schedule)

---

## ✅ Success Criteria

1. **Data Collection**: Successfully collect data from ALL ScrapeCreators endpoints
2. **Analysis Modes**: Both Quick Scan and Deep Dossier work correctly
3. **AI Intelligence**: Generate comprehensive psychological/behavioral reports
4. **Cross-Platform**: Automatically discover and link related accounts
5. **Export**: Generate professional PDF dossiers
6. **Visualization**: Interactive charts, graphs, and timelines
7. **Performance**: Quick Scan < 15s, Deep Dossier < 5 min
8. **Reliability**: Graceful handling of API failures and missing data

---

## 🚀 Deployment

**Current Status**: All core phases are complete. The platform is ready for production deployment.

**Verification Steps**:
1. Monitor Docker container stability.
2. Verify cross-platform discovery accuracy.
3. Validate deep dossier behavioral insights.

**Command to verify Docker is running**:
```bash
docker compose ps
```

**Status**: Deployment & Optimization Phase

---

**End of Master Implementation Plan**
