# Render.com Deployment Guide for CXRaide

This guide explains how to deploy the CXRaide application to Render.com and GitHub while handling large model files.

## Deployment Strategy for Large Model Files

CXRaide uses PyTorch-based deep learning models that are too large to push to GitHub and can cause issues with Render's free tier due to memory constraints. To address this, the application includes a lightweight model fallback system that allows for:

- **Local development**: Uses real models for full accuracy
- **Render.com deployment**: Uses mock models that simulate real model behavior
- **GitHub**: Repository can be pushed without large model files

## Setting Up Environment Variables

The application automatically detects its environment and selects the appropriate model approach:

- On Render.com, set the `RENDER=True` environment variable
- For local testing of the mock model behavior, set `USE_MOCK_MODELS=True`
- For normal local development with real models, no special configuration is needed

## GitHub Repository Setup

1. Ensure all model files (`.pth`) are in your `.gitignore` file:

```
# Ignore all PyTorch model files
*.pth
```

2. Push your code to GitHub without the model files:

```bash
git add .
git commit -m "Deploy with mock model fallback"
git push
```

## Render.com Deployment

### Backend Service

1. Connect your GitHub repository
2. Set up a Web Service with these settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r server/requirements.txt`
   - **Start Command**: `cd server && gunicorn app:app`
   - **Environment Variables**:
     - `RENDER=True`
     - `USE_MOCK_MODELS=True`
     - Any other environment variables for your DB, etc.

### Frontend Service

1. Connect your GitHub repository
2. Set up a Static Site or Web Service for the frontend
3. Configure to point to your backend service

## Local Development

To run locally with real models:

1. Download the model files:
   - `IT2_model_epoch_300.pth`
   - `IT3_model_epoch_260.pth`
2. Place them in the `server` directory
3. Start the server:
   ```bash
   cd server
   pip install -r requirements.txt
   python app.py
   ```

To test locally with mock models:

```bash
cd server
USE_MOCK_MODELS=True python app.py
```

## How Mock Models Work

The mock model system simulates what the real models would predict:

1. It provides realistic bounding boxes for chest X-ray findings
2. It generates predictions with varying confidence scores
3. It simulates the correct output format so the application UI works the same way

This approach allows you to:

- Deploy to resource-limited environments
- Share code on GitHub without large files
- Test the application flow even without the real models

## Model Status API

You can check which model implementation is being used via the `/api/model-status` endpoint, which returns detailed information about the loaded models.

## Troubleshooting

If you encounter issues on Render.com, check:

1. Memory usage in the Render dashboard
2. Logs for any PyTorch-related errors
3. That the `USE_MOCK_MODELS` environment variable is set to `True`

## 1. Deploy the Backend Service

1. Log in to your Render.com account and go to the Dashboard
2. Click "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:

   - **Name**: `cxraide-backend`
   - **Environment**: Docker
   - **Region**: Choose the one closest to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**: (leave blank, Docker will handle this)
   - **Start Command**: `gunicorn server.app:app --bind 0.0.0.0:$PORT --workers 2`

5. Add the following environment variables:

   ```
   DB_NAME=your_database_name
   FLASK_ENV=production
   MONGO_URI=your_mongodb_connection_string
   PORT=10000
   SECRET_KEY=your_secret_key
   ```

6. Click "Create Web Service"

## 2. Deploy the Frontend Service

1. Click "New" and select "Static Site"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `cxraide`
   - **Branch**: main (or your preferred branch)
   - **Root Directory**: (leave blank)
   - **Build Command**: `cd client && npm install && npm run build`
   - **Publish Directory**: `client/dist`
4. Add the following environment variables:

   ```
   VITE_API_URL=https://cxraide-backend.onrender.com
   ```

5. Click "Create Static Site"

## 3. Additional Setup for Cross-Network Access

To ensure your application works from any network or device:

1. **Verify backend CORS settings**:

   - Make sure your app.py has the updated CORS configuration that allows all origins
   - Check that `withCredentials: true` is used consistently in frontend API calls

2. **Configure environment variables properly**:

   - Double-check that the backend URL in frontend's `.env.production` is correct
   - Make sure to use HTTPS URLs for both frontend and backend

3. **Check DNS and firewall settings**:

   - Ensure your domain (if custom) is properly configured
   - Verify Render.com domains are accessible from your network
   - Test with mobile data vs. Wi-Fi to isolate network issues

4. **Important**: After deployment, clear browser cache on all devices before testing

## 4. First-Time Login

After deployment, you can log in using the hardcoded admin credentials:

- Username: `admin`
- Password: `admin123`

**IMPORTANT**: This is only for initial setup. After deployment, you should:

1. Create proper user accounts
2. Remove or change the hardcoded admin credentials

## 5. Production Security Considerations

For production deployment, you should:

1. Remove the hardcoded admin credentials after setting up proper accounts
2. Remove the temporary verification bypasses once all users have migrated to the new password format
3. Set strong, unique values for SECRET_KEY and other sensitive environment variables
4. Set FLASK_ENV=production to ensure stricter security checks
5. Consider enabling HTTPS-only cookies for the JWT tokens

## 6. Troubleshooting Network Errors

If you encounter "Connection Failed" or network errors from certain devices:

1. **Test backend directly**:

   - Visit `https://cxraide-backend.onrender.com/health` from the problematic device
   - If this works but the app doesn't, it's likely a CORS or frontend issue

2. **Check browser console for CORS errors**:

   - Look for messages like "Access-Control-Allow-Origin" or "No 'Access-Control-Allow-Origin' header"
   - Make sure `withCredentials` setting matches your CORS configuration

3. **Network troubleshooting**:

   - On mobile devices, try switching between Wi-Fi and cellular data
   - Use browser developer tools to verify the exact URL being requested

4. **Common fixes**:

   - Try accessing with HTTPS instead of HTTP
   - Clear browser cache and cookies
   - Try different browsers
   - Ensure Render.com hasn't experienced any outages

5. **If all else fails**:
   - Deploy a temporary debug version with:
     ```javascript
     // Add this to frontend code
     axios.interceptors.request.use((request) => {
       console.log("Starting Request", request);
       return request;
     });
     ```
   - Check Render.com logs with:
     ```
     render logs --follow
     ```

## 7. Ongoing Maintenance

1. Update the code in your GitHub repository as needed
2. Render.com will automatically deploy new changes
3. Monitor server logs for errors
4. Regularly back up your MongoDB database
