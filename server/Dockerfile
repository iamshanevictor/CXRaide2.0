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

# Log the mode we're running in
RUN echo "Using lightweight model implementation - no model download required"

# Expose the port the app runs on
EXPOSE 5000

# Use gunicorn for production with increased timeout
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"] 