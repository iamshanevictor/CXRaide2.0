import os
import requests
import logging
from flask import Blueprint, request, jsonify

# Get logger
logger = logging.getLogger('app')

# Create blueprint
model_proxy_bp = Blueprint('model_proxy', __name__)

# Get local model server URL from environment variable or use default
LOCAL_MODEL_SERVER = os.environ.get('LOCAL_MODEL_SERVER', 'http://localhost:5500')
MODEL_API_KEY = os.environ.get('MODEL_API_KEY', 'default-secure-key-change-me')

@model_proxy_bp.route('/proxy/health', methods=['GET'])
def check_local_server():
    """Check if the local model server is available"""
    try:
        response = requests.get(
            f"{LOCAL_MODEL_SERVER}/health",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to local model server: {str(e)}")
        return jsonify({
            "error": "Local model server unavailable",
            "status": "service_unavailable",
            "detail": str(e)
        }), 503

@model_proxy_bp.route('/proxy/predict', methods=['POST', 'OPTIONS'])
def proxy_predict():
    """Proxy /predict requests to local model server"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = jsonify({"message": "CORS preflight handled"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    try:
        # Forward the request to the local model server
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': MODEL_API_KEY
        }
        
        # Send request to local model server
        response = requests.post(
            f"{LOCAL_MODEL_SERVER}/predict",
            json=request.json,
            headers=headers,
            timeout=30  # 30 second timeout for model processing
        )
        
        # Return the response from the local server
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to local model server")
        return jsonify({
            "error": "Model server unavailable. Please ensure your local server is running.",
            "status": "service_unavailable"
        }), 503
    except requests.exceptions.Timeout:
        logger.error("Request to local model server timed out")
        return jsonify({
            "error": "Model prediction timed out. The image may be too complex to process.",
            "status": "request_timeout"
        }), 504
    except Exception as e:
        logger.error(f"Error proxying request to local model server: {str(e)}")
        return jsonify({
            "error": f"Failed to process prediction: {str(e)}",
            "status": "internal_server_error"
        }), 500 