#!/usr/bin/env python3
"""
Celery Configuration for ProfileScope
Real-time task processing setup
"""

import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Celery instance
app = Celery('profilescope')

# Configure Celery
app.conf.update(
    # Broker settings
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result settings
    result_expires=3600,  # 1 hour
    
    # Task time limits
    task_soft_time_limit=1800,  # 30 minutes
    task_time_limit=2400,      # 40 minutes
    
    # Task routing
    task_routes={
        'app.core.tasks.analyze_profile_task': {'queue': 'analysis'},
        'app.core.tasks.process_image_task': {'queue': 'vision'},
        'app.core.tasks.generate_report_task': {'queue': 'reports'},
        'app.core.tasks.collect_profile_data': {'queue': 'data'},
    },
    
    # Worker settings
    worker_max_tasks_per_child=50,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Auto-discover tasks
app.autodiscover_tasks(['app.core'])

if __name__ == '__main__':
    app.start()