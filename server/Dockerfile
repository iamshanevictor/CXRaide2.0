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
ENV USE_LIGHTWEIGHT_MODEL=true

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
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
# Try downloading both models using the new combined script
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
    echo "WARNING: Failed to obtain IT2 model file. Some features may not work."; \
    fi

RUN if [ -f IT3_model_epoch_260.pth ]; then \
    echo "IT3 model file successfully included in build" && \
    stat --format="%s bytes" IT3_model_epoch_260.pth; \
    else \
    echo "WARNING: Failed to obtain IT3 model file. Some features may not work."; \
    fi

# Expose the port the app runs on
EXPOSE 5000

# Use gunicorn for production with increased timeout
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"] 