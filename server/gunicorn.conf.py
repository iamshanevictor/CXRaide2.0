import os

# Increase worker timeout to handle long-running ML predictions
timeout = int(os.getenv('WORKER_TIMEOUT', 300))  # 5 minutes default

# Gunicorn worker configuration
workers = int(os.getenv('GUNICORN_WORKERS', 2))
threads = int(os.getenv('GUNICORN_THREADS', 4))

# Avoid worker timeout issues with ML models
worker_class = 'gthread'

# Log level
loglevel = os.getenv('LOG_LEVEL', 'info')

# Whether to reload on code changes (development only)
reload = os.getenv('FLASK_ENV', 'production') == 'development'

# Bind to this socket
bind = f"0.0.0.0:{int(os.getenv('PORT', 5000))}"

# Limit worker restart on memory leaks
max_requests = 1000
max_requests_jitter = 50

# Set keep-alive for persistent connections
keepalive = 65 