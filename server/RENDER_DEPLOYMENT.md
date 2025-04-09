# Render.com Deployment Instructions for CXRaide Backend

This guide provides instructions for deploying the CXRaide backend on Render.com with a simplified approach that doesn't require the large PyTorch model file.

## Prerequisites

- A Render.com account
- Access to the CXRaide repository

## Lightweight Model Implementation

The CXRaide backend now uses a lightweight implementation that provides demo predictions without requiring the large PyTorch model file. This approach has several advantages:

1. **Easier Deployment**: No need to download and store a large model file
2. **Lower Resource Requirements**: Can run on smaller instances with less memory
3. **Faster Startup**: Application initializes quickly without loading a large model
4. **Reliable Operation**: Works even when PyTorch isn't installed

Note that predictions are demonstrations only and not based on real model inference.

## Deployment Steps

### 1. Configure Render Web Service

1. Navigate to your Render.com dashboard
2. Click "New" > "Web Service"
3. Connect your repository
4. Configure the service with these settings:

   - **Name**: cxraide-backend
   - **Environment**: Python
   - **Region**: Choose the region closest to your users
   - **Branch**: main (or whichever branch you're deploying from)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server.app:app --config server/gunicorn.conf.py`
   - **Plan**: Free (or Standard for better performance)

### 2. Add Environment Variables

Add these environment variables in the Render dashboard:

```
FLASK_ENV=production
WORKER_TIMEOUT=300
GUNICORN_WORKERS=1
GUNICORN_THREADS=2
PYTHON_VERSION=3.9.0
USE_LIGHTWEIGHT_MODEL=true
```

### 3. Set Resource Allocation

Since we're using a lightweight implementation, resource requirements are minimal:

- **Memory**: 1GB is sufficient
- **CPU**: 0.5 CPU is adequate

### 4. Deploy

Click "Create Web Service" and wait for the deployment to complete.

## Switching to Real Model (Optional)

If you want to use the real PyTorch model in the future:

1. Uncomment the PyTorch dependencies in `requirements.txt`
2. Upload the model file to a reliable location
3. Update the model loading code in `model_service.py` to load the real model
4. Set `USE_LIGHTWEIGHT_MODEL=false` in your environment variables
5. Increase the memory allocation to at least 4GB

## Testing the Deployment

After deploying, test the following endpoints:

1. `GET /health` - Should return a 200 response with "healthy" status
2. `GET /loading-status` - Should show details about the server and model status
3. `GET /model-status` - Should indicate that the lightweight model is being used

The `/predict` endpoint will work, but will return demo predictions with a message indicating they are not based on a real model.
