import os

# Increase worker timeout to handle long-running ML predictions
timeout = int(os.getenv('WORKER_TIMEOUT', 600))  # 10 minutes default

# Gunicorn worker configuration - keep low for memory-intensive ML models
workers = int(os.getenv('GUNICORN_WORKERS', 1))
threads = int(os.getenv('GUNICORN_THREADS', 2))

# Worker class for long-running processes like ML predictions
worker_class = 'gthread'

# Log level
loglevel = os.getenv('LOG_LEVEL', 'info')

# Whether to reload on code changes (development only)
reload = os.getenv('FLASK_ENV', 'production') == 'development'

# Bind to this socket
bind = f"0.0.0.0:{int(os.getenv('PORT', 5000))}"

# Limit worker restart on memory leaks - important for ML models
max_requests = 20  # Lower for ML models that may use a lot of memory
max_requests_jitter = 5

# Set keep-alive for persistent connections
keepalive = 65

# Configure graceful timeout
graceful_timeout = 120

# Preload application to load the ML model once
preload_app = True

# Log to stdout for container environments
accesslog = '-'
errorlog = '-' 