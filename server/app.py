import os
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from jose import jwt
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Detect environment and set model strategy
def setup_environment():
    """Configure environment variables based on deployment context"""
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    it2_path = os.path.join(model_dir, 'IT2_model_epoch_300.pth')
    it3_path = os.path.join(model_dir, 'IT3_model_epoch_260.pth')

    # Check if explicit environment variable is set
    use_mock_models = os.environ.get('USE_MOCK_MODELS', '').lower()

    if use_mock_models in ['true', 'false']:
        os.environ['USE_MOCK_MODELS'] = use_mock_models
        logger.info(f"Using environment setting for mock models: {use_mock_models}")
        return

    is_render = os.environ.get('RENDER', 'False').lower() == 'true'

    try:
        import torch
        pytorch_available = True
        logger.info("PyTorch is available - can use real models if present")
    except ImportError:
        pytorch_available = False
        logger.warning("PyTorch import failed - will use mock models")
        os.environ['USE_MOCK_MODELS'] = 'True'
        return

    if pytorch_available:
        if is_render:
            os.environ['USE_MOCK_MODELS'] = 'True'
            logger.info("Running on Render.com - using mock models by default")
        else:
            if os.path.exists(it2_path) and os.path.exists(it3_path):
                os.environ['USE_MOCK_MODELS'] = 'False'
                logger.info("Real model files found - using real models")
                logger.info(f"IT2 model: {it2_path} ({os.path.getsize(it2_path) / (1024*1024):.1f} MB)")
                logger.info(f"IT3 model: {it3_path} ({os.path.getsize(it3_path) / (1024*1024):.1f} MB)")
            else:
                os.environ['USE_MOCK_MODELS'] = 'True'
                logger.warning("Model files not found - using mock models")
                if not os.path.exists(it2_path):
                    logger.warning(f"Missing IT2 model file: {it2_path}")
                if not os.path.exists(it3_path):
                    logger.warning(f"Missing IT3 model file: {it3_path}")

# Set up environment before other operations
setup_environment()

# Import the model blueprint - properly handle different import paths
model_bp = None
get_model = None

try:
    # Try direct import first (Docker container)
    from model_service import model_bp, get_model
    logger.info("Successfully imported model_service directly (Docker mode)")
except ImportError:
    try:
        # Then try with server prefix (local development)
        from server.model_service import model_bp, get_model
        logger.info("Successfully imported model_service with server prefix (local mode)")
    except ImportError:
        logger.error("Could not import model_service. Check file paths and dependencies.")
        # Create dummy blueprint to avoid errors
        from flask import Blueprint
        model_bp = Blueprint('model', __name__)
        def get_model():
            logger.error("Model loading function not available")
            return None, None

load_dotenv()

app = Flask(__name__)

# Register the model blueprint
if model_bp:
    app.register_blueprint(model_bp, url_prefix='/api')
    logger.info("Registered model_bp blueprint with prefix /api")
else:
    logger.error("model_bp is not available, cannot register blueprint")

# Get environment
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
logger.info(f"Running in {ENVIRONMENT} environment")

# JWT Configuration - Direct configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'ecd500797722db1d8de3f1330c6890105c13aa4bbe4d1cce')
USE_FIREBASE_AUTH = os.getenv('USE_FIREBASE_AUTH', 'false').lower() == 'true'
ALLOW_DEV_LOGIN = os.getenv('ALLOW_DEV_LOGIN', 'true').lower() == 'true'

firebase_admin = None
fb_auth = None
firebase_ready = False

if USE_FIREBASE_AUTH:
    try:
        import firebase_admin
        from firebase_admin import credentials, auth as fb_auth

        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '').strip()
        if cred_path:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Initialized Firebase with service account credential")
        else:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
            logger.info("Initialized Firebase with application default credential")
        firebase_ready = True
    except Exception as e:
        firebase_ready = False
        logger.error(f"Failed to initialize Firebase Admin: {e}")
        USE_FIREBASE_AUTH = False

# Store allowed origins in app config based on environment
if ENVIRONMENT == 'production':
    app.config['CORS_ORIGINS'] = [
        "https://cxraide.onrender.com",     # Production frontend
        "http://cxraide.onrender.com",      # HTTP version
        "https://www.cxraide.onrender.com",  # www version
        "http://www.cxraide.onrender.com",   # www HTTP version
        "https://cxraide-backend.onrender.com",  # Backend URL
        "http://cxraide-backend.onrender.com",   # Backend HTTP URL
        "*"  # Allow all origins temporarily for debugging
    ]
else:
    # Development environment - include local addresses
    app.config['CORS_ORIGINS'] = [
        "http://localhost:8080",           # Local development
        "http://localhost:3000",           # New frontend port
        "http://localhost:5000",           # Local API
        "http://127.0.0.1:8080",          # Alternative local
        "http://127.0.0.1:3000",          # New frontend port alternative
        "http://127.0.0.1:5000",          # Alternative local API
        "http://192.168.68.103:8080",     # Local network
        "http://192.168.68.103:3000",     # New frontend port local network
        "http://192.168.68.103:5000",     # Local network API
        "https://cxraide.onrender.com",    # Also allow production URLs in development
        "http://cxraide.onrender.com",
        "https://cxraide-backend.onrender.com",
        "http://cxraide-backend.onrender.com"
    ]

logger.info(f"Allowed origins: {app.config['CORS_ORIGINS']}")

# Updated CORS configuration with proper headers
CORS(
    app, 
    resources={
        r"/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    }
)

# Authentication configuration
if USE_FIREBASE_AUTH:
    logger.info("Firebase authentication mode enabled - backend login endpoints are stubbed")
else:
    logger.info("Firebase authentication disabled - using local JWT auth (no database)")

# JWT Configuration
app.config['SECRET_KEY'] = SECRET_KEY
JWT_EXPIRATION = timedelta(hours=1)

def _verify_token(token_value):
    """Verify token using Firebase if enabled, otherwise local JWT."""
    if not token_value:
        raise ValueError("Token missing")

    # Strip Bearer prefix
    if token_value.startswith('Bearer '):
        token_value = token_value[7:]

    if USE_FIREBASE_AUTH and firebase_ready and fb_auth:
        decoded = fb_auth.verify_id_token(token_value)
        logger.info(f"Firebase token verified for user: {decoded.get('user_id')}")
        return {
            "username": decoded.get("email") or decoded.get("user_id"),
            "sub": decoded.get("uid") or decoded.get("user_id"),
            "is_admin": False,
        }

    decoded = jwt.decode(token_value, app.config["SECRET_KEY"], algorithms=["HS256"])
    logger.info(f"Local token decoded for user: {decoded.get('username', 'unknown')}")
    return decoded


# JWT/Firebase token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            logger.warning("Token missing in request")
            return jsonify({"message": "Token is missing!", "valid": False}), 401

        try:
            data = _verify_token(token)
            g.user = data
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({"message": "Token is invalid!", "valid": False}), 401
        return f(*args, **kwargs)

    return decorated

# Helper function for CORS preflight responses
def _build_cors_preflight_response():
    response = jsonify({"message": "CORS preflight handled"})
    origin = request.headers.get('Origin', '')
    response.headers.add('Access-Control-Allow-Origin', origin or '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response, 200

# Token creation helper
def create_token(user_id, username=None, is_admin=False):
    payload = {
        'sub': user_id,
        'exp': datetime.utcnow() + JWT_EXPIRATION,
        'iat': datetime.utcnow()
    }
    
    if username:
        payload['username'] = username
    
    if is_admin:
        payload['is_admin'] = True
        
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
    logger.info(f"Created token for user ID: {user_id}")
    return token

# Define routes
@app.route('/')
def home():
    return jsonify({
        "message": "CXRaide API is running",
        "environment": ENVIRONMENT,
        "cors_origins": "All origins allowed (*)",
        "auth": "firebase" if USE_FIREBASE_AUTH else "local-jwt"
    }), 200

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    # In Firebase mode the client authenticates directly with Firebase and sends tokens to us.
    if USE_FIREBASE_AUTH:
        return jsonify({
            "success": True,
            "message": "Firebase handles login on the client. Use the ID token in Authorization header.",
        }), 200

    try:
        data = request.get_json() or {}

        username = data.get('username') or 'guest'
        password = data.get('password') or 'guest'

        logger.info(f"Login attempt for user: {username}")

        # Development-only fallback login (no persistence)
        if ALLOW_DEV_LOGIN:
            logger.warning("Developer login used (no persistence, no database)")
            return jsonify({
                "success": True,
                "token": create_token(username or 'user', username=username or 'user', is_admin=username == 'admin'),
                "user_id": username or 'user',
                "username": username or 'user',
                "message": "Developer login successful (in-memory only)"
            }), 200

        logger.warning("Local login attempted but dev login is disabled")
        return jsonify({
            "success": False,
            "message": "Local login is disabled. Enable Firebase authentication or set ALLOW_DEV_LOGIN=true."
        }), 403

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred during login"
        }), 500

@app.route('/check-session', methods=['GET', 'OPTIONS'])
def check_session():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("Token missing in request")
        return jsonify({"message": "Token is missing!", "valid": False}), 401

    try:
        data = _verify_token(token)
        return jsonify({
            "valid": True,
            "user": {
                "username": data.get("username"),
                "user_id": data.get("sub"),
                "is_admin": data.get("is_admin", False)
            }
        })
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({"message": "Token is invalid!", "valid": False}), 401

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    return jsonify({
        "status": "healthy",
        "environment": ENVIRONMENT,
        "auth_mode": "firebase" if USE_FIREBASE_AUTH else "local-dev",
        "cors_origins": "All origins allowed (*)"
    }), 200

@app.route('/admin/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    # Handle OPTIONS request
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    logger.info("Password reset requested but not supported without external identity provider")
    return jsonify({
        "message": "Password resets are not available in local auth mode. Use external identity provider for this flow.",
        "handled_by": "local-dev"
    }), 501

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Endpoint to get predictions from the model and return annotated images"""
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
        
    try:
        # Check if the model blueprint is loaded
        if not model_bp:
            logger.error("Model service is not available")
            return jsonify({"error": "Model service is not available"}), 500
            
        # Redirect to the model blueprint's predict endpoint
        # The real implementation is in model_service.py
        return model_bp.url_map.dispatch_rule('/predict', request)
    except Exception as e:
        logger.error(f"Error redirecting to prediction endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add route to access model-status directly from the root as a convenience
@app.route('/model-status', methods=['GET', 'OPTIONS'])
def model_status_redirect():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    try:
        # Redirect to the model blueprint's model-status endpoint
        # The real implementation is in model_service.py
        return model_bp.url_map.dispatch_rule('/model-status', request)
    except Exception as e:
        logger.error(f"Error redirecting to model-status endpoint: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', '')
    logger.info(f"Request details - Method: {request.method}, Path: {request.path}, Origin: {origin}")
    
    # Allow all origins for all environments - but don't add header if it already exists
    if 'Access-Control-Allow-Origin' not in response.headers:
        response.headers.add('Access-Control-Allow-Origin', origin or '*')
    
    # Handle OPTIONS requests explicitly for CORS preflight
    if request.method == 'OPTIONS':
        response.status_code = 200
    
    # Only add headers if they don't exist yet
    if 'Access-Control-Allow-Headers' not in response.headers:
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
    if 'Access-Control-Allow-Methods' not in response.headers:
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    if 'Access-Control-Allow-Credentials' not in response.headers:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    if 'Access-Control-Max-Age' not in response.headers:
        response.headers.add('Access-Control-Max-Age', '3600')
    if 'Access-Control-Expose-Headers' not in response.headers:
        response.headers.add('Access-Control-Expose-Headers', 'Content-Type, Authorization')
    
    return response

# Add this at the end of the file to support development mode with hot-reloading
if __name__ == "__main__":
    # Enable hot-reloading in development
    app.run(host="0.0.0.0", port=8080, debug=True)