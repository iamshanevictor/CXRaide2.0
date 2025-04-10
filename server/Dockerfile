FROM python:3.9-slim AS base

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development
ENV MONGO_URI=mongodb+srv://cxraide-admin:OhbYaa4VRXmEolR9@cxraide.av2tc7q.mongodb.net/?retryWrites=true&w=majority&appName=CXRaide
ENV DB_NAME=cxraide
ENV SECRET_KEY=ecd500797722db1d8de3f1330c6890105c13aa4bbe4d1cce
ENV WORKER_TIMEOUT=600
ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=2
# This flag should be set to false in Docker since we'll include the model files
ENV USE_MOCK_MODELS=false
# For Render.com deployment only, leave false for local Docker
ENV RENDER=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY requirements.local.txt .

# Install Python dependencies INCLUDING PyTorch (unlike Render)
RUN pip install --no-cache-dir -r requirements.local.txt

# Development stage - expects volumes to be mounted
FROM base AS development
# Only copy essential files for startup
COPY *.py ./
COPY gunicorn.conf.py ./
# Start Flask in development mode, with auto-reload
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]

# Production stage - copies all files and downloads models
FROM base AS production
# Copy the application code
COPY . .

# -------------------------------------------
# MODEL DOWNLOAD SECTION
# -------------------------------------------
# Always attempt to download models for Docker environment
RUN echo "Attempting to download models using download_models.py..." && \
    python download_models.py || echo "Combined download script failed, trying alternatives..."

# If download failed, try direct download for IT2 model
RUN if [ ! -f IT2_model_epoch_300.pth ]; then \
    echo "Download script failed for IT2 model, trying backup method..." && \
    python download_from_drive.py || echo "Simplified download failed too"; \
    fi

# Try direct download for IT3 model
RUN if [ ! -f IT3_model_epoch_260.pth ]; then \
    echo "Download script failed for IT3 model, trying direct download..." && \
    (curl -L "https://drive.google.com/uc?export=download&id=1rd0j7hmw19H02z4vDfWw3Il-s4Xx-zTz" -o IT3_model_epoch_260.pth || \
     wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1rd0j7hmw19H02z4vDfWw3Il-s4Xx-zTz" -O IT3_model_epoch_260.pth); \
    fi

# Fall back to direct curl/wget for IT2 if needed
RUN if [ ! -f IT2_model_epoch_300.pth ]; then \
    echo "All IT2 model download methods failed, trying curl/wget..." && \
    (curl -L "https://drive.google.com/uc?export=download&id=1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr" -o IT2_model_epoch_300.pth || \
     wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr" -O IT2_model_epoch_300.pth); \
    fi

# Verify model files exist and log their sizes
RUN if [ -f IT2_model_epoch_300.pth ]; then \
    echo "IT2 model file successfully included in build" && \
    stat --format="%s bytes" IT2_model_epoch_300.pth; \
    else \
    echo "WARNING: Failed to obtain IT2 model file. Using mock model instead."; \
    ENV USE_MOCK_MODELS=true; \
    fi

RUN if [ -f IT3_model_epoch_260.pth ]; then \
    echo "IT3 model file successfully included in build" && \
    stat --format="%s bytes" IT3_model_epoch_260.pth; \
    else \
    echo "WARNING: Failed to obtain IT3 model file. Using mock model instead."; \
    ENV USE_MOCK_MODELS=true; \
    fi

# Expose the port the app runs on
EXPOSE 5000

# Use gunicorn for production with increased timeout
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"] 