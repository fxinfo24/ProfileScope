"""
Real-Time Processing Tasks for ProfileScope
Celery-based background task processing with Redis
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from celery import Celery, Task
from celery.exceptions import Retry
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from ..web.database import engine, get_database_session
from ..web.models.analysis import Analysis, AnalysisStatus
from ..web.models.user import User
from .scrape_client import get_scrape_client
from .openrouter_client import openrouter_client
from .vision_analyzer import vision_analyzer
from ..utils.logger import get_logger

# Load environment variables
load_dotenv()

# Configure Celery
celery_app = Celery(
    'profilescope',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['app.core.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
    task_soft_time_limit=1800,  # 30 minutes
    task_time_limit=2400,  # 40 minutes
    task_routes={
        'app.core.tasks.analyze_profile_task': {'queue': 'analysis'},
        'app.core.tasks.process_image_task': {'queue': 'vision'},
        'app.core.tasks.generate_report_task': {'queue': 'reports'},
    }
)

logger = get_logger(__name__)

class ProfileAnalysisTask(Task):
    """Custom task class for profile analysis with progress tracking"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        analysis_id = args[0] if args else kwargs.get('analysis_id')
        if analysis_id:
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            try:
                analysis = session.query(Analysis).filter_by(id=analysis_id).first()
                if analysis:
                    analysis.fail_analysis(f"Task failed: {str(exc)}")
                    session.commit()
                    logger.error(f"Analysis {analysis_id} failed: {exc}")
            except Exception as e:
                logger.error(f"Failed to update analysis status: {e}")
            finally:
                session.close()

@celery_app.task(bind=True, base=ProfileAnalysisTask, max_retries=3, default_retry_delay=60)
def analyze_profile_task(self, analysis_id: int) -> Dict[str, Any]:
    """
    Main profile analysis task - coordinates all analysis steps
    """
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Get analysis record
        analysis = session.query(Analysis).filter_by(id=analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        # Start processing
        analysis.start_processing()
        session.commit()
        
        logger.info(f"Starting analysis {analysis_id} for {analysis.platform}/@{analysis.profile_id}")
        
        # Step 1: Collect profile data (20% progress)
        self.update_state(state='PROGRESS', meta={'progress': 20, 'message': 'Collecting profile data...'})
        analysis.update_progress(20, 'Collecting profile data...')
        session.commit()
        
        profile_data = collect_profile_data.delay(analysis.platform.value, analysis.profile_id).get()
        if not profile_data.get('success'):
            raise Exception(profile_data.get('error', 'Failed to collect profile data'))
        
        # Step 2: Analyze content with AI (40% progress)
        self.update_state(state='PROGRESS', meta={'progress': 40, 'message': 'Analyzing content with AI...'})
        analysis.update_progress(40, 'Analyzing content with AI...')
        session.commit()
        
        content_analysis = analyze_content_with_ai.delay(
            profile_data['profile'], 
            profile_data.get('posts', [])
        ).get()
        
        # Step 3: Analyze authenticity (60% progress)
        self.update_state(state='PROGRESS', meta={'progress': 60, 'message': 'Analyzing authenticity...'})
        analysis.update_progress(60, 'Analyzing authenticity...')
        session.commit()
        
        authenticity_analysis = analyze_authenticity.delay(
            profile_data['profile'], 
            content_analysis
        ).get()
        
        # Step 4: Generate predictions (80% progress)
        self.update_state(state='PROGRESS', meta={'progress': 80, 'message': 'Generating predictions...'})
        analysis.update_progress(80, 'Generating predictions...')
        session.commit()
        
        predictions = generate_predictions.delay(
            profile_data['profile'], 
            content_analysis
        ).get()
        
        # Step 5: Analyze profile image if available (90% progress)
        visual_analysis = None
        if profile_data['profile'].get('profile_image_url'):
            self.update_state(state='PROGRESS', meta={'progress': 90, 'message': 'Analyzing profile image...'})
            analysis.update_progress(90, 'Analyzing profile image...')
            session.commit()
            
            visual_analysis = analyze_profile_image.delay(
                profile_data['profile']['profile_image_url']
            ).get()
        
        # Step 6: Compile final results (100% progress)
        self.update_state(state='PROGRESS', meta={'progress': 95, 'message': 'Compiling results...'})
        analysis.update_progress(95, 'Compiling results...')
        session.commit()
        
        # Generate summary
        summary = generate_summary.delay(
            profile_data['profile'],
            content_analysis,
            authenticity_analysis,
            predictions
        ).get()
        
        # Compile final results
        final_results = {
            'profile_data': profile_data['profile'],
            'content_analysis': content_analysis,
            'authenticity_analysis': authenticity_analysis,
            'predictions': predictions,
            'visual_analysis': visual_analysis,
            'summary': summary,
            'metadata': {
                'analysis_version': '2.0',
                'timestamp': datetime.utcnow().isoformat(),
                'processing_details': {
                    'platforms_analyzed': [analysis.platform.value],
                    'posts_analyzed': len(profile_data.get('posts', [])),
                    'image_analyzed': bool(visual_analysis),
                    'ai_models_used': ['OpenRouter Universal']
                }
            }
        }
        
        # Calculate confidence scores
        confidence_score = calculate_confidence_score(content_analysis, authenticity_analysis)
        authenticity_score = authenticity_analysis.get('overall_authenticity', {}).get('score', 0.5)
        influence_score = calculate_influence_score(profile_data['profile'], content_analysis)
        
        # Complete analysis
        analysis.complete_analysis(
            results=final_results,
            confidence=confidence_score,
            authenticity=authenticity_score,
            influence=influence_score
        )
        session.commit()
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
        return {
            'success': True,
            'analysis_id': analysis_id,
            'results': final_results
        }
        
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {e}")
        analysis.fail_analysis(str(e))
        session.commit()
        raise
    
    finally:
        session.close()

@celery_app.task(bind=True, max_retries=3)
def collect_profile_data(self, platform: str, profile_id: str) -> Dict[str, Any]:
    """Collect profile and posts data from social media platform"""
    try:
        scrape_client = get_scrape_client()
        
        # Get profile data based on platform
        if platform == 'twitter':
            profile = scrape_client.get_twitter_profile(profile_id)
            posts = scrape_client.get_twitter_posts(profile_id, count=50)
        elif platform == 'instagram':
            profile = scrape_client.get_instagram_profile(profile_id)
            posts = []  # Instagram posts would require additional API calls
        elif platform == 'linkedin':
            profile = scrape_client.get_linkedin_profile(profile_id)
            posts = []
        elif platform == 'tiktok':
            profile = scrape_client.get_tiktok_profile(profile_id)
            posts = []
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return {
            'success': True,
            'profile': profile,
            'posts': posts
        }
        
    except Exception as e:
        logger.error(f"Failed to collect data for {platform}/@{profile_id}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@celery_app.task
def analyze_content_with_ai(profile_data: Dict[str, Any], posts: list) -> Dict[str, Any]:
    """Analyze profile content using OpenRouter AI models"""
    try:
        return openrouter_client.analyze_profile_content(profile_data, posts)
    except Exception as e:
        logger.error(f"Content analysis failed: {e}")
        return {'error': str(e)}

@celery_app.task
def analyze_authenticity(profile_data: Dict[str, Any], content_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze profile authenticity"""
    try:
        return openrouter_client.analyze_authenticity(profile_data, content_analysis)
    except Exception as e:
        logger.error(f"Authenticity analysis failed: {e}")
        return {'error': str(e)}

@celery_app.task
def generate_predictions(profile_data: Dict[str, Any], content_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate future predictions"""
    try:
        return openrouter_client.generate_predictions(profile_data, content_analysis)
    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        return {'error': str(e)}

@celery_app.task
def analyze_profile_image(image_url: str) -> Dict[str, Any]:
    """Analyze profile image using computer vision"""
    try:
        return vision_analyzer.analyze_profile_image(image_url)
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return {'error': str(e)}

@celery_app.task
def generate_summary(profile_data: Dict[str, Any], content_analysis: Dict[str, Any], 
                    authenticity_analysis: Dict[str, Any], predictions: Dict[str, Any]) -> str:
    """Generate human-readable summary"""
    try:
        return openrouter_client.get_quick_summary(profile_data)
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return f"Analysis completed for @{profile_data.get('username', 'unknown')}"

def calculate_confidence_score(content_analysis: Dict[str, Any], authenticity_analysis: Dict[str, Any]) -> float:
    """Calculate overall confidence score"""
    # Base confidence from authenticity analysis
    auth_confidence = authenticity_analysis.get('overall_authenticity', {}).get('confidence', 0.5)
    
    # Boost confidence if we have good content analysis
    content_boost = 0.1 if content_analysis.get('key_insights') else 0
    
    return min(auth_confidence + content_boost, 1.0)

def calculate_influence_score(profile_data: Dict[str, Any], content_analysis: Dict[str, Any]) -> float:
    """Calculate influence score based on metrics"""
    followers = profile_data.get('followers_count', 0)
    following = profile_data.get('following_count', 1)
    verified = profile_data.get('verified', False)
    
    # Follower ratio component (0-0.4)
    ratio_score = min(followers / max(following, 1) / 10000, 0.4)
    
    # Verification boost (0-0.3)
    verification_score = 0.3 if verified else 0
    
    # Content quality boost (0-0.3)
    content_score = 0.3 if content_analysis.get('key_insights') else 0.1
    
    return min(ratio_score + verification_score + content_score, 1.0)

# Task monitoring and management
@celery_app.task
def cleanup_old_results():
    """Clean up old analysis results"""
    # This would implement cleanup logic
    pass

@celery_app.task
def health_check():
    """Health check for the task queue"""
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}