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
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# -------------------------------------------
# MODEL DOWNLOAD SECTION
# -------------------------------------------
# Try downloading from Google Drive first
RUN echo "Attempting to download model from Google Drive..." && \
    python download_model.py || echo "Google Drive download failed, trying alternatives..."

# If download failed, try direct download from public URL
RUN if [ ! -f IT2_model_epoch_300.pth ]; then \
    echo "Google Drive download failed, trying backup method..." && \
    python download_from_drive.py || echo "Simplified download failed too"; \
    fi

# Fall back to direct curl/wget if needed
RUN if [ ! -f IT2_model_epoch_300.pth ]; then \
    echo "All Python download methods failed, trying curl/wget..." && \
    (curl -L "https://drive.google.com/uc?export=download&id=1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr" -o IT2_model_epoch_300.pth || \
     wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr" -O IT2_model_epoch_300.pth); \
    fi

# For very large files, Google Drive might require an additional confirmation token
# We can't easily handle that in a Dockerfile, so we'll need the file to be accessible
# through one of the above methods

# Verify model file exists and log its size
RUN if [ -f IT2_model_epoch_300.pth ]; then \
    echo "Model file successfully included in build at $(pwd)/IT2_model_epoch_300.pth" && \
    stat --format="%s bytes" IT2_model_epoch_300.pth; \
    else \
    echo "ERROR: Failed to obtain model file through all methods. Build will fail."; \
    exit 1; \
    fi

# Expose the port the app runs on
EXPOSE 5000

# Use python to run the app directly for development or troubleshooting
# CMD ["python", "app.py"]

# Use gunicorn for production with increased timeout
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"] 