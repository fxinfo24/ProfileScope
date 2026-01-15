# ProfileScope - Session Handover Document

> **Last Updated**: January 15, 2026  
> **Purpose**: Complete context for resuming work in a new session

---

## 📋 Project Summary

**ProfileScope** is an AI-powered social media intelligence platform that analyzes profiles across 10+ platforms (Twitter, Instagram, LinkedIn, TikTok, etc.) using machine learning, NLP, and computer vision.

### Tech Stack
| Layer | Technology | Status |
|-------|------------|--------|
| **Frontend** | React 18 + TypeScript + Vite + Tailwind | ✅ Deployed on Vercel |
| **Backend** | Flask + SQLAlchemy + Celery | ⚠️ Needs hosting (Railway trial ended) |
| **AI** | OpenRouter (Grok 4.1 Fast, GPT-4, Gemini) | ✅ Configured |
| **Data Collection** | ScrapeCreators API | ✅ Configured |
| **Database** | SQLite (dev) / PostgreSQL (prod) | ✅ Ready |

---

## 🎨 Current State

### Frontend (Vercel) - ✅ WORKING
- **URL**: https://profile-scope.vercel.app/
- **Status**: Deployed with Premium Glassmorphism UI
- **Features**:
  - Dark mode enforced
  - Glass-panel aesthetic with neon accents
  - SPA routing configured (`vercel.json`)
  - All components styled (Dashboard, TasksList, AnalysisForm, TaskView, ResultView)

### Backend - ⚠️ NEEDS HOSTING
- **Previous Host**: Railway (trial ended)
- **Issue**: CORS errors when frontend calls API (no backend running)
- **Required Environment Variables**:
  ```bash
  # Core
  SECRET_KEY=your-secure-random-key
  DATABASE_URI=postgresql://... (or sqlite:///data/profilescope.db for dev)
  
  # CORS - Must include your frontend URL
  CORS_ORIGINS=https://profile-scope.vercel.app
  
  # AI (OpenRouter with Grok 4.1 Fast)
  OPENROUTER_API_KEY=sk-or-v1-...
  
  # Data Collection
  SCRAPECREATORS_API_KEY=your-scrapecreators-key
  
  # Optional
  REDIS_URL=redis://localhost:6379/0  # For Celery background tasks
  FORCE_CELERY=false  # Use threading by default
  ```

---

## 📂 Project Structure

```
ProfileScope/
├── app/
│   ├── core/           # Analysis engine
│   │   ├── analyzer.py         # Main orchestrator
│   │   ├── openrouter_client.py # AI integration (Grok 4.1 Fast)
│   │   ├── scrape_client.py    # ScrapeCreators API
│   │   ├── content_analyzer.py # NLP analysis
│   │   ├── authenticity.py     # Fake account detection
│   │   └── prediction.py       # Growth forecasting
│   ├── web/            # Flask API
│   │   ├── app.py              # App factory
│   │   ├── models.py           # SQLAlchemy models
│   │   └── routes/api.py       # REST endpoints
│   ├── desktop/        # PyQt5 desktop app
│   └── enterprise/     # Team/white-label features
├── frontend/           # React + TypeScript
│   ├── src/
│   │   ├── components/         # UI components (Glassmorphism styled)
│   │   ├── services/api.ts     # API client
│   │   └── index.css           # Global glass styles
│   ├── tailwind.config.js      # Dark theme config
│   └── vercel.json             # SPA routing
├── directives/         # SOPs (consolidated from docs/)
│   ├── api.md
│   ├── setup_guide.md
│   ├── development.md
│   └── desktop_mobile.md
├── mobile/             # React Native + Expo
├── AGENTS.md           # Core operating principles
└── README.md           # Project overview
```

---

## 🔧 Immediate Next Steps

### Priority 1: Deploy Backend
Choose ONE of these hosting options:

#### Option A: Render.com (Recommended - Free Tier)
1. Go to https://render.com
2. Connect GitHub repo `fxinfo24/ProfileScope`
3. Create "Web Service" with:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -b 0.0.0.0:$PORT app.web.app:create_app()`
4. Add environment variables (see above)
5. Update Vercel with `VITE_API_BASE_URL=https://your-app.onrender.com/api`

#### Option B: Fly.io (Free Tier)
1. Install `flyctl`: `brew install flyctl`
2. Run `fly launch` in project root
3. Set secrets: `fly secrets set OPENROUTER_API_KEY=...`
4. Deploy: `fly deploy`

#### Option C: Local Development
```bash
# Terminal 1: Backend
source venv/bin/activate
python3 bin/run.py --web

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Priority 2: Verify Full Flow
After backend is deployed:
1. Open https://profile-scope.vercel.app/
2. Click "New Analysis"
3. Enter a Twitter username (e.g., "elonmusk")
4. Verify task creates and processes successfully

---

## 🎯 Completed Work This Session

| Task | Status |
|------|--------|
| Premium Glassmorphism UI overhaul | ✅ |
| Fixed SPA routing (vercel.json) | ✅ |
| Fixed CSS theme conflicts | ✅ |
| Replaced Claude with Grok 4.1 Fast | ✅ |
| Consolidated docs/ → directives/ | ✅ |
| Removed 11 legacy/redundant docs | ✅ |
| Updated README.md references | ✅ |
| Updated AGENTS.md references | ✅ |
| All changes pushed to GitHub | ✅ |

---

## 🐛 Known Issues

1. **Backend Hosting**: Railway trial ended - need alternative hosting
2. **CORS Errors**: Frontend can't reach backend (because no backend is running)
3. **Mock Data**: When `SCRAPECREATORS_API_KEY` is not set, returns mock profile data

---

## 🔑 API Keys Location

All API keys are in `.env` file (local only, not committed):
```
/Volumes/ByteSmith/BuildLab/Python Projects/Profile_Scope_AI/ProfileScope/.env
```

**Keys configured**:
- ✅ OPENROUTER_API_KEY (for Grok 4.1 Fast AI)
- ✅ SCRAPECREATORS_API_KEY (for social media data)
- ✅ TWITTER_API_KEY (legacy, optional)

---

## 📚 Key Files to Review

| File | Purpose |
|------|---------|
| `AGENTS.md` | Core operating principles, 3-layer architecture |
| `README.md` | Full project documentation |
| `app/core/openrouter_client.py` | AI integration (Grok models) |
| `app/web/routes/api.py` | All REST API endpoints |
| `frontend/src/services/api.ts` | Frontend API client |
| `frontend/src/components/*.tsx` | UI components |

---

## 🚀 Quick Start Commands

```bash
# Navigate to project
cd /Volumes/ByteSmith/BuildLab/Python\ Projects/Profile_Scope_AI/ProfileScope

# Activate virtual environment
source venv/bin/activate

# Run backend locally
python3 bin/run.py --web

# Run frontend locally
cd frontend && npm run dev

# Run tests
python3 bin/run_tests.py --simple

# Build frontend for production
cd frontend && npm run build
```

---

## 📞 Session Resume Prompt

Copy this to start a new session:

```
I'm resuming work on ProfileScope. Please read HANDOVER.md for context.

Current status:
- Frontend: Deployed on Vercel (https://profile-scope.vercel.app/)
- Backend: Needs hosting (Railway trial ended)
- UI: Premium Glassmorphism completed
- AI: Using Grok 4.1 Fast via OpenRouter

My goal: [describe what you want to do]
```

---

**End of Handover Document**
