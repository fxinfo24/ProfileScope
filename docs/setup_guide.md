# ProfileScope Setup Guide

## Quick Start

### 1. Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (already done if following from README)
pip install -r requirements-full.txt  # For local development
# OR: pip install -r requirements.txt  # For Railway (minimal)
```

### 2. Universal API Configuration

#### ScrapeCreators Setup (Primary - 10+ Platforms)
ProfileScope uses ScrapeCreators for universal access to 10+ social media platforms:

1. **Configuration Required**: Add your ScrapeCreators API key to .env file
2. **Supported Platforms**: Twitter/X, Instagram, LinkedIn, TikTok, Facebook, YouTube, Snapchat, Pinterest, Reddit, GitHub
3. **Setup Instructions**: 
   ```
   # Copy .env.example to .env and add your API key
   SCRAPECREATORS_API_KEY=your_scrapecreators_api_key_here
   SCRAPECREATORS_BASE_URL=https://api.scrapecreators.com
   ```

#### OpenRouter AI Setup (Universal AI Access)
ProfileScope uses OpenRouter for access to multiple AI models:

1. **Configuration Required**: Add your OpenRouter API key to .env file
2. **Available Models**: GPT-4, Claude-3, Gemini, Llama-2, Mixtral
3. **Setup Instructions**:
   ```
   # Add your OpenRouter API key to .env file
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

#### Legacy Individual APIs (Optional)
For direct API access (not recommended - use ScrapeCreators instead):
- Twitter Developer Portal: https://developer.twitter.com/
- Facebook for Developers: https://developers.facebook.com/

### 3. Verify Installation
```bash
# Test core functionality with universal APIs
python -c "from app.core.scrape_client import get_scrape_client; from app.core.openrouter_client import openrouter_client; print('✅ Universal APIs ready')"

# Start web interface (Flask)
python3 bin/run.py --web

# Start desktop interface
python3 bin/run.py --desktop

# Start real-time processing
scripts/start_celery.sh

# Start mobile development
cd mobile && npx expo start

# Build frontend
cd frontend && npm run build
```

## Architecture Overview

### Fixed Issues
The following critical issues have been resolved:

1. **Circular Import Dependencies**: Removed Flask initialization from core package
2. **Database Integration**: Fixed SQLAlchemy model imports
3. **Missing Dependencies**: Installed all required packages with fallbacks
4. **API Client Issues**: Added graceful handling for optional packages

### Current Status
- ✅ **Web Interface**: React + TypeScript at http://127.0.0.1:5000
- ✅ **Mobile Applications**: React Native + Expo (iOS/Android)
- ✅ **Desktop Application**: PyQt5 GUI with advanced visualizations
- ✅ **10+ Platform Support**: Universal data collection via ScrapeCreators
- ✅ **Universal AI**: GPT-4, Claude-3, Gemini, Llama-2 via OpenRouter
- ✅ **Real-time Processing**: Celery + Redis with Flower monitoring
- ✅ **Enterprise Features**: Team management and white-label ready
- ✅ **Database**: PostgreSQL (production), SQLite (development)
- ✅ **Computer Vision**: OpenCV-based image analysis

### Component Architecture
```
ProfileScope/
├── app/
│   ├── core/           # Universal API integration & analysis engine
│   ├── web/            # Flask API + database models
│   ├── desktop/        # PyQt5 GUI application
│   ├── enterprise/     # Team management & white-label features
│   └── utils/          # Shared utilities and helpers
├── frontend/           # React + TypeScript web interface
├── mobile/             # React Native + Expo mobile apps
├── data/               # Data storage and results
├── tests/              # Comprehensive test suites
├── docs/               # Complete documentation
└── scripts/            # Deployment and management scripts
```

## Testing

### Automated Tests
```bash
# Run all tests
python3 bin/run_tests.py

# Run specific test categories
pytest tests/test_core/
pytest tests/test_web/
pytest tests/test_utils/
```

### Manual Testing
```bash
# Test web API (tasks)
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"platform":"twitter","profile_id":"elonmusk"}'

# List tasks
curl http://127.0.0.1:5000/api/tasks
```

## Production Deployment

### Security / environment configuration (production)
1. Set `SECRET_KEY` as an environment variable (do not hardcode)
2. Set `FLASK_DEBUG=false`
3. Configure `DATABASE_URI` to point to Postgres
4. Configure `REDIS_URL` for Celery workers

### Web Server Setup (Railway)
```bash
# Web service (Railway provides $PORT)
gunicorn -b 0.0.0.0:$PORT app.web.app:create_app()

# Worker service
celery -A app.core.tasks worker --loglevel=info --queues=analysis
```

### Frontend Setup (Vercel)
Set `VITE_API_BASE_URL` to your Railway backend URL + `/api`, e.g.
`https://<your-service>.up.railway.app/api`

### Database Setup
```bash
# Run migrations (recommended for production)
export FLASK_APP=app.web.app
flask db upgrade
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Missing NLTK Data**: Run the NLTK download commands in the setup
3. **API Errors**: Check your API credentials in the .env file
4. **Database Issues**:
   - SQLite (dev): delete `data/profilescope.db` and restart
   - Postgres (prod): run `flask db upgrade` and verify `DATABASE_URI`

### Debug Mode
```bash
# Run with debug logging
python3 bin/run.py --web --debug

# Check logs
tail -f data/logs/profilescope.log
```