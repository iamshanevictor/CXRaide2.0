FROM python:3.9-slim AS base

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development
ENV FLASK_ENV=development
ENV SECRET_KEY=ecd500797722db1d8de3f1330c6890105c13aa4bbe4d1cce
ENV WORKER_TIMEOUT=600
ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=2
# Avoid pip network stalls on large wheels (e.g., torch)
ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_RETRIES=5
# This flag should be set to false in Docker since we'll include the model files
ENV USE_MOCK_MODELS=false
# For Render.com deployment only, leave false for local Docker
ENV RENDER=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsm6 \
    libxext6 \
    libxrender-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY requirements.local.txt .

# Install Python dependencies INCLUDING PyTorch (unlike Render)
RUN pip install --no-cache-dir --default-timeout=300 --retries=5 -r requirements.local.txt

# Development stage - expects volumes to be mounted
FROM base AS development
# Only copy essential files for startup
COPY *.py ./
COPY gunicorn.conf.py ./
COPY models ./models
# Start Flask in development mode, with auto-reload
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]

# Production stage - copies all files and downloads models
FROM base AS production
# Copy the application code
COPY . .
COPY models ./models

# Verify model files exist to avoid silent fallbacks
RUN test -f models/IT2_model_epoch_300.pth && test -f models/IT3_model_epoch_260.pth

# Expose the port the app runs on
EXPOSE 5000

# Use gunicorn for production with increased timeout
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"] 