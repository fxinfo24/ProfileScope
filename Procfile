web: gunicorn -b 0.0.0.0:$PORT app.web.app:create_app()
worker: celery -A app.core.tasks worker --loglevel=info --queues=analysis
