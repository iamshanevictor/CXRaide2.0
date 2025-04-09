# Render.com Deployment Instructions for CXRaide Backend

This guide provides instructions for deploying the CXRaide backend on Render.com with proper configuration to handle the large PyTorch model file.

## Prerequisites

- A Render.com account
- Access to the CXRaide repository
- Google Drive link to the model file (already configured)

## Model File Considerations

The CXRaide backend uses a large PyTorch model file (`IT2_model_epoch_300.pth`, ~136MB). This file is downloaded during the build process from Google Drive with the ID `1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr`.

### Important Notes About Google Drive Model Download

1. **File Access**: Ensure the Google Drive file is accessible with the shared link:

   - The file should be publicly accessible (or at least have "Anyone with the link can view" permissions)
   - If the file access permissions change, the build will fail

2. **Download Methods**: We've implemented several fallback methods to handle Google Drive's limitations:

   - Primary method: `download_model.py` script with Google Drive API handling
   - Backup method: `download_from_drive.py` with simpler approach
   - Last resort: Direct wget/curl commands in the Dockerfile

3. **Large File Limitations**: Google Drive imposes restrictions on large file downloads:
   - For files > 100MB, Google Drive might prompt a virus scan warning
   - Our scripts handle this with cookie handling for confirmation tokens
   - In some cases, very large files might require manual download and inclusion in the repo

## Deployment Steps

### 1. Verify Google Drive File Access

Before deploying, verify that the model file is accessible:

```bash
# Test locally first
cd server
python download_from_drive.py
```

If successful, you'll see the model downloaded to your local machine.

### 2. Configure Render Web Service

1. Navigate to your Render.com dashboard
2. Click "New" > "Web Service"
3. Connect your repository
4. Configure the service with these settings:

   - **Name**: cxraide-backend
   - **Environment**: Python
   - **Region**: Choose the region closest to your users
   - **Branch**: main (or whichever branch you're deploying from)
   - **Build Command**: `pip install -r requirements.txt && cd server && python download_model.py`
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
MODEL_GOOGLE_DRIVE_ID=1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr
```

### 4. Set Resource Allocation

Increase the resources allocated to the service:

- **Memory**: 4GB minimum
- **CPU**: 1 CPU minimum

### 5. Deploy

Click "Create Web Service" and wait for the deployment to complete.

### 6. Monitor Build Logs

Watch the build logs carefully to ensure the model downloads successfully. If the download fails, you might need to:

1. Check Google Drive file permissions
2. Try an alternative hosting method
3. Contact Render support if timeouts occur during the build

## Troubleshooting

### Google Drive Download Issues

If the model fails to download during build:

1. **Check Google Drive Permissions**:

   - Ensure the file has "Anyone with the link can view" permissions
   - Try accessing the file directly from an incognito browser window

2. **Alternative Hosting**:

   - Consider uploading the model to AWS S3, Google Cloud Storage, or another provider
   - Update the `download_model.py` script with the new URL

3. **Manual Upload**:
   - As a last resort, you can manually upload the model when creating a new deployment
   - Use Render's disk mounting options to persist the file

### Memory and Resource Issues

If the server crashes after deployment:

1. **Check Memory Usage**:

   - Visit `/loading-status` to see current memory usage
   - Increase memory allocation if needed

2. **Reduce Worker Count**:
   - Keep worker count at 1 for large models
   - Use threads instead of multiple workers

## Testing the Deployment

After deploying, test the following endpoints:

1. `GET /health` - Should return a 200 response with "healthy" status
2. `GET /loading-status` - Should show details about the server and model status, including whether the model file was found
3. `GET /model-status` - Should show the model loading status

Only attempt to use the `/predict` endpoint after confirming the model is loaded.
