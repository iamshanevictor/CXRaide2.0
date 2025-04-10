# CXRaide Local Model Server Setup Guide

This guide explains how to run the CXRaide model locally while using Render.com for your frontend and backend proxy.

## Overview

The setup consists of three components:

1. Frontend on Render.com (cxraide.onrender.com)
2. Backend on Render.com (cxraide-backend.onrender.com)
3. Local model server (running on your computer)

Your Render.com backend will forward model prediction requests to your local computer, which will process them and return the results.

## Step 1: Set Up the Local Model Server

### Create a Directory

```
mkdir cxraide-local-model
cd cxraide-local-model
```

### Copy Files

Copy these files from the repository to your local directory:

- `local_model_server.py` - The Flask server that handles model predictions
- `start_local_model_server.bat` - Windows batch script to start the server

### Download Model Files

You need both model files in the same directory:

- `IT2_model_epoch_300.pth`
- `IT3_model_epoch_260.pth`

## Step 2: Start the Local Server

Double-click the `start_local_model_server.bat` file to:

1. Create a Python virtual environment
2. Install required dependencies
3. Start the model server on port 5500

The first time you run this, it will install all necessary dependencies including PyTorch.

## Step 3: Make Your Local Server Accessible

### Option A: Use ngrok (Easiest for Testing)

1. Download and install [ngrok](https://ngrok.com/download)
2. Start ngrok with: `ngrok http 5500`
3. Copy the HTTPS URL provided by ngrok (e.g., `https://a1b2c3d4.ngrok.io`)

### Option B: Port Forwarding (More Permanent)

1. Configure your router to forward port 5500 to your computer
2. Get a dynamic DNS service like [No-IP](https://www.noip.com/)
3. Install their update client to keep your dynamic DNS record updated

## Step 4: Configure Your Render.com Backend

Add these environment variables to your Render.com backend service:

| Variable           | Value                            | Description                    |
| ------------------ | -------------------------------- | ------------------------------ |
| LOCAL_MODEL_SERVER | Your ngrok URL or dynamic DNS    | URL to your local model server |
| MODEL_API_KEY      | Same key as in your local server | For authentication             |

## Step 5: Update Your Frontend API Calls

Modify your frontend to use the proxy endpoint:

```javascript
// Change from
const response = await api.post("/predict", data);

// To
const response = await api.post("/proxy/predict", data);
```

## Security Considerations

1. **API Key**: Change the default API key in both your local server and Render.com environment variables
2. **Firewall Rules**: If using port forwarding, limit connections to only your Render.com backend IP

## Troubleshooting

### Local Server Issues

- Check if PyTorch installed correctly: Run `python -c "import torch; print(torch.__version__)"`
- Verify models are loaded: Access `http://localhost:5500/health` in your browser

### Connection Issues

- Test the proxy: `curl -X GET https://cxraide-backend.onrender.com/proxy/health`
- Check ngrok is running: The URL changes each time you restart ngrok

### Memory Issues

- The local server uses CPU-only PyTorch to reduce memory usage
- Close other memory-intensive applications when running the server

## Keeping Your Computer Always On

Since predictions require your local computer to be running:

1. **Power Settings**: Set your computer to never sleep when plugged in
2. **Auto-Start**: Configure the local server to start automatically on boot
3. **Monitoring**: Consider setting up alerts if your local server goes offline

For uninterrupted service, consider moving to a more robust cloud hosting solution that can handle the model memory requirements.

## Testing the Setup

1. Start your local model server
2. Make a test prediction through your Render.com frontend
3. Check the logs on your local server to verify it's processing the request

If everything is set up correctly, predictions should work even though the model processing happens on your local machine instead of Render.com.
