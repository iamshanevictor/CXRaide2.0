FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV MONGO_URI=mongodb+srv://cxraide-admin:OhbYaa4VRXmEolR9@cxraide.av2tc7q.mongodb.net/?retryWrites=true&w=majority&appName=CXRaide
ENV DB_NAME=cxraide
ENV SECRET_KEY=ecd500797722db1d8de3f1330c6890105c13aa4bbe4d1cce
ENV WORKER_TIMEOUT=600
ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=2

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Try loading the model from different sources:
# 1. First try downloading using our script
RUN python download_model.py || echo "Download script failed, checking other methods..."

# 2. Check if model exists in build context, if not try downloading directly with wget
RUN if [ ! -f IT2_model_epoch_300.pth ]; then \
    echo "Model file not found in build context, attempting direct download..." && \
    wget -O IT2_model_epoch_300.pth https://storage.googleapis.com/example-medical-models/IT2_model_epoch_300.pth || \
    echo "Direct download failed"; \
    fi

# 3. If model still doesn't exist, fail the build
RUN if [ ! -f IT2_model_epoch_300.pth ]; then \
    echo "ERROR: Failed to obtain model file through all methods. Build will fail."; \
    ls -la .; \
    exit 1; \
    fi

# Verify model file exists and log its size
RUN ls -la IT2_model_epoch_300.pth && \
    echo "Model file successfully included in build at $(pwd)/IT2_model_epoch_300.pth" && \
    stat --format="%s bytes" IT2_model_epoch_300.pth

# Expose the port the app runs on
EXPOSE 5000

# Use python to run the app directly for development or troubleshooting
# CMD ["python", "app.py"]

# Use gunicorn for production with increased timeout
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"] 