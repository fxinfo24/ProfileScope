# Vanta (formerly ProfileScope) - Session Handover Document

> **Last Updated**: January 23, 2026 (Local Time)
> **Purpose**: Complete context for resuming work in a new session (Standardizing on **Vanta**)

---

## 📋 Project Summary

**Vanta** is an industry-leading social intelligence platform that provides **Deep Hybrid AI Analysis** across **21+ platforms**. It uses a "Deep Mind" intelligence engine that prioritizes **OpenRouter (Grok 4.1 Fast / GPT-4)** for psychological and semantic analysis, seamlessly falling back to local heuristics if AI services are unavailable. Vanta is built for scholars, researchers, and intelligence professionals.

### Tech Stack (Upgraded)
| Layer | Technology | Status |
|-------|------------|--------|
| **Frontend** | React 18 + TypeScript + Vite | ✅ Containerized (Docker) |
| **Backend** | Python 3.13 + Flask + Celery | ✅ Containerized (Docker) |
| **Intelligence** | Hybrid Engine (OpenRouter + Heuristic) | ✅ Best-in-Class Implementation |
| **Data** | Universal ScrapeCreators (20+ Platforms) | ✅ Configured for all platforms |
| **Infra** | Docker Compose (Full Stack) | ✅ **READY FOR DEPLOYMENT** |

---

## 🎨 Current State

### Universal Connectivity - ✅ SOLVED
The entire stack is now containerized and orchestrated via Docker Compose. No more manual terminal juggling.
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Task Monitor**: http://localhost:5555 (Flower)

### Platform Capabilities
| Category | Supported Platforms |
| :--- | :--- |
| **Social** | Twitter/X, Facebook, Instagram, Reddit, Snapchat, Pinterest |
| **Video** | TikTok, YouTube, Twitch, Kick |
| **Professional** | LinkedIn, GitHub, Threads, BlueSky |
| **Commerce** | **TikTok Shop, Amazon Shop**, Google, Linktree |
| **Intelligence** | Bot Detection, Deepfake Analysis, Commerce Conversion Metrics |

---

## 📂 Project Structure (Docker Optimized)

```
ProfileScope/
├── app/
│   ├── core/           # Hybrid Intelligence Engine
│   │   ├── analyzer.py         # Universal Orchestrator (AI -> Heuristic)
│   │   ├── openrouter_client.py # AI Client (Grok 4.1 Fast / GPT-4)
│   │   ├── scrape_client.py    # Universal Data Adapter (20+ Platforms)
│   │   └── ...
│   ├── web/            # Flask API
│   └── ...
├── frontend/           # React + TypeScript
│   ├── Dockerfile      # Frontend container config
│   └── ...
├── docker-compose.yml  # Full stack orchestration (API, Worker, Frontend, Redis)
├── Dockerfile          # Backend/Worker container config
├── requirements-full.txt # Python 3.13 dependencies
└── ...
```

---

## 🔧 Immediate Next Steps

### Priority 1: Run with Docker (Recommended)
This is the single source of truth for running the application.

```bash
# 1. Start the entire platform
docker compose up -d --build

# 2. Monitor logs (optional)
docker compose logs -f
```

### Priority 2: Verify Intelligence
Once running:
1. Go to http://localhost:5173
2. Enter a username (e.g., `elonmusk` for Twitter or a product handle for Amazon)
3. The system will auto-select the **Hybrid Engine**:
   - Tries OpenRouter AI first.
   - Falls back to internal Heuristics if offline.

---

## 🎯 Completed Work This Session

| Task | Status |
|------|--------|
| **Vanta Rebrand** | ✅ Fully implemented (Logo, Favicon, UI, Naming) |
| **Deep Mind Intelligence** | ✅ Added TikTok, YouTube, Instagram (Deep Posts) |
| **Hybrid Intelligence Engine** | ✅ AI-First logic with Heuristic Fallback |
| **Universal Platform Support** | ✅ Added Amazon, TikTok Shop, Google, Kick, (21+ Total) |
| **Docker Orchestration** | ✅ Full Stack Healthy |
| **Premium UI** | ✅ Added **Network Graph** & Deep Dossier Visualization |
| **Main Bug Fixes** | ✅ Resolved "Stuck in Processing" and "Blank Results" |

---

## 🎨 Rebrand Proposal: "Vanta"

*   **Name**: **Vanta** (derived from Vantablack - absorbing all light/data; seeing into the unknown).
*   **Concept**: Sleek, dark-mode first, "Black Box" intelligence revealed.
*   **Logo**: Abstract vortex/eye (generated in artifacts).

---

## 🔑 API Keys Location

All API keys are in `.env` file. The Docker containers automatically load these.
- `OPENROUTER_API_KEY`: Required for "Smart" analysis.
- `SCRAPECREATORS_API_KEY`: Required for "Real" data (system mocks if missing).

---

## 📞 Session Resume Prompt (Vanta Standard)

Copy this to start a new session to ensure NO confusion:

```
I'm resuming work on Vanta (Best-in-Class Social Intelligence). 
Please read HANDOVER.md and AGENTS.md immediately.

Current status:
- Infrastructure: Docker Compose (All services healthy)
- Core: "Deep Mind" profiling (Transcripts/Comments) integrated with OpenRouter Grok 4.1.
- Fixes: Data schema mismatch resolved; results now populate the Dashboard correctly.
- Tech: Python 3.13, Flask, React TypeScript, Redis/Celery.

Primary Goal: Continue enhancing Vanta's intelligence/UI.
```

---

**End of Handover Document**
