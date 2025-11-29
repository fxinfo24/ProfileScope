# ProfileScope Setup Guide

## Quick Start

### 1. Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (already done if following from README)
pip install -r requirements.txt
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

# Start web interface (Flask + React)
python run.py --web

# Start desktop interface
python run.py --desktop

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
python run_tests.py

# Run specific test categories
pytest tests/test_core/
pytest tests/test_web/
pytest tests/test_utils/
```

### Manual Testing
```bash
# Test web API
curl http://127.0.0.1:5000/api/status

# Test analysis with mock data
python tmp_rovodev_test_analysis.py
```

## Production Deployment

### Security Configuration
1. Change the Flask secret key in config.json
2. Set `debug: false` in web configuration
3. Use environment variables for sensitive data
4. Configure proper database for production (not SQLite)

### Web Server Setup
```bash
# Using gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app.web.app:create_app()
```

### Database Setup
```bash
# Initialize database
python -c "
from app.web.app import create_app
from app.web.models import db
app = create_app()
with app.app_context():
    db.create_all()
"
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Missing NLTK Data**: Run the NLTK download commands in the setup
3. **API Errors**: Check your API credentials in the .env file
4. **Database Issues**: Delete `data/profilescope.db` and reinitialize

### Debug Mode
```bash
# Run with debug logging
python run.py --web --debug

# Check logs
tail -f data/logs/profilescope.log
```