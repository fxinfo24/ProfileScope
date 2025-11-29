# ProfileScope API Documentation

## Overview
ProfileScope provides a comprehensive RESTful API for social media profile analysis across 10+ major platforms. The API leverages universal data collection through ScrapeCreators and advanced AI analysis via OpenRouter, enabling real-time insights from Twitter/X, Instagram, LinkedIn, TikTok, Facebook, YouTube, Snapchat, Pinterest, Reddit, and GitHub.

## Supported Platforms

- **Twitter/X**: Profile data, tweets, engagement metrics, verification status
- **Instagram**: Profile information, post data, business accounts
- **LinkedIn**: Professional profiles, company data, network analysis
- **TikTok**: Creator profiles, video metrics, follower engagement
- **Facebook**: Public profiles, page data, community insights
- **YouTube**: Channel analysis, subscriber data, video performance
- **Snapchat**: User profiles, snap metrics, audience insights
- **Pinterest**: Board analytics, pin performance, trending content
- **Reddit**: User karma, community analysis, post engagement
- **GitHub**: Developer profiles, repository data, contribution analysis

**Total Coverage**: 10+ major social media and professional platforms

## API Endpoints

### Authentication
All API requests require authentication via JWT token or API key.

```bash
Authorization: Bearer <jwt_token>
# OR
X-API-Key: <api_key>
```

### Core Analysis Endpoints

#### GET /api/status
Check the service status and platform availability.

#### POST /api/analyze
Start a new profile analysis.

**Request Body:**
```json
{
  "platform": "twitter",
  "profile_id": "elonmusk",
  "include_images": true,
  "include_posts": true,
  "post_count": 50
}
```

#### GET /api/analysis/{analysis_id}
Get the status and results of an analysis.

#### GET /api/analysis/{analysis_id}/status
Get real-time status of ongoing analysis.

#### DELETE /api/analysis/{analysis_id}
Cancel or delete an analysis.

### Team Management (Enterprise)

#### GET /api/teams
List user's teams.

#### POST /api/teams
Create a new team.

#### GET /api/teams/{team_id}/members
List team members.

#### POST /api/teams/{team_id}/invite
Invite new team member.

### Usage and Billing

#### GET /api/usage/stats
Get usage statistics and billing information.

#### GET /api/invoices
List invoices for the user.

#### POST /api/subscriptions/upgrade
Upgrade subscription plan.

## WebSocket Endpoints

### Real-time Analysis Updates
Connect to `/ws/analysis/{analysis_id}` for live progress updates.

## Rate Limits

- **Free Tier**: 1,000 requests/month
- **Basic Tier**: 10,000 requests/month  
- **Professional Tier**: 50,000 requests/month
- **Enterprise Tier**: 200,000 requests/month

## Error Codes

- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Invalid authentication
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `429`: Rate Limited - Too many requests
- `500`: Internal Server Error - Server issue

## SDKs and Libraries

### Python
```python
from profilescope import ProfileScopeAPI

client = ProfileScopeAPI(api_key="your-api-key")
analysis = client.analyze_profile("twitter", "username")
```

### JavaScript
```javascript
import { ProfileScopeClient } from 'profilescope-js';

const client = new ProfileScopeClient('your-api-key');
const analysis = await client.analyzeProfile('twitter', 'username');
```
