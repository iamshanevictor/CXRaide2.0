# Render.com Deployment Instructions for CXRaide Backend

This guide provides instructions for deploying the CXRaide backend on Render.com with proper configuration to handle the large PyTorch model file.

## Prerequisites

- A Render.com account
- Access to the CXRaide repository
- A location to host the PyTorch model file (Google Drive, AWS S3, etc.)

## Model File Considerations

The CXRaide backend uses a large PyTorch model file (`IT2_model_epoch_300.pth`, ~136MB). This file needs to be accessible during the build process. There are several ways to handle this:

1. **Update the download URL**: Edit `server/download_model.py` to point to the actual public URL where your model file is hosted.
2. **Host the model file**: Upload the model file to a public storage service and update the URL in `download_model.py`.
3. **Include the model file**: If you're deploying directly from your local machine, make sure the model file is included in the repository.

## Deployment Steps

### 1. Prepare the Model File

Make sure your model file is hosted somewhere public or included in your repository.

### 2. Configure Render Web Service

1. Navigate to your Render.com dashboard
2. Click "New" > "Web Service"
3. Connect your repository
4. Configure the service with these settings:

   - **Name**: cxraide-backend
   - **Environment**: Python
   - **Region**: Choose the region closest to your users
   - **Branch**: main (or whichever branch you're deploying from)
   - **Build Command**: `pip install -r requirements.txt && python server/download_model.py`
   - **Start Command**: `gunicorn server.app:app --config server/gunicorn.conf.py`
   - **Plan**: Standard (at minimum)

### 3. Add Environment Variables

Add these environment variables in the Render dashboard:

```
FLASK_ENV=production
WORKER_TIMEOUT=600
GUNICORN_WORKERS=1
GUNICORN_THREADS=2
PYTHON_VERSION=3.9.0
```

### 4. Set Resource Allocation

Increase the resources allocated to the service:

- **Memory**: 4GB minimum
- **CPU**: 1 CPU minimum

### 5. Deploy

Click "Create Web Service" and wait for the deployment to complete.

## Troubleshooting

If you encounter issues, check the following:

1. **Model Loading Failures**:

   - Visit `/loading-status` endpoint to check the model status
   - Check if the model file was successfully downloaded
   - Verify memory allocation is sufficient

2. **Memory Issues**:

   - Increase the allocated memory in Render dashboard
   - Reduce worker count to 1

3. **Timeout Issues**:

   - Increase `WORKER_TIMEOUT` environment variable
   - Consider using a larger instance type

4. **502 Errors**:
   - These usually indicate the service crashed, check logs
   - Look for memory-related errors or model loading failures

## Testing the Deployment

After deploying, test the following endpoints:

1. `GET /health` - Should return a 200 response with "healthy" status
2. `GET /loading-status` - Should show details about the server and model status
3. `GET /model-status` - Should show the model loading status

Only attempt to use the `/predict` endpoint after confirming the model is loaded.
