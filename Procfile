# Railway Procfile - Deploy web and worker as SEPARATE services
# 
# Service 1 (Web): Use "web" command below
# Service 2 (Worker): Use "worker" command below
# Both services should point to the same GitHub repo
#
# To deploy worker:
# 1. Create new service in Railway from same repo
# 2. Set start command to: celery -A app.core.tasks worker --pool=solo --loglevel=info --queues=analysis
# 3. Ensure REDIS_URL environment variable is available
#
# Note: Using --pool=solo to avoid mmap dependency issues in containerized environments

web: gunicorn -b 0.0.0.0:$PORT app.web.app:create_app()
worker: celery -A app.core.tasks worker --pool=solo --loglevel=info --queues=analysis
