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

load_dotenv()

# Detect environment and set model strategy
def setup_environment():
    """Choose real local models when present, otherwise fall back to mock models."""
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    it2_path = os.path.join(model_dir, 'IT2_model_epoch_300.pth')
    it3_path = os.path.join(model_dir, 'IT3_model_epoch_260.pth')

    # Check if explicit environment variable is set
    use_mock_models = os.environ.get('USE_MOCK_MODELS', '').lower()

    if use_mock_models in ['true', 'false']:
        os.environ['USE_MOCK_MODELS'] = use_mock_models
        logger.info(f"Using environment setting for mock models: {use_mock_models}")
        return

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
    # Direct import works when running from the server directory.
    from model_service import model_bp, get_model
    logger.info("Successfully imported model_service directly")
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
ALLOW_DEV_LOGIN = os.getenv('ALLOW_DEV_LOGIN', 'true').lower() == 'true'

app.config['CORS_ORIGINS'] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

frontend_url = os.getenv('FRONTEND_URL', '').strip()
if frontend_url:
    app.config['CORS_ORIGINS'].append(frontend_url)

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

logger.info("Using local JWT auth. TODO: Database-backed users will be redesigned later.")

# JWT Configuration
app.config['SECRET_KEY'] = SECRET_KEY
JWT_EXPIRATION = timedelta(hours=1)

def _verify_token(token_value):
    """Verify a local development JWT."""
    if not token_value:
        raise ValueError("Token missing")

    # Strip Bearer prefix
    if token_value.startswith('Bearer '):
        token_value = token_value[7:]

    decoded = jwt.decode(token_value, app.config["SECRET_KEY"], algorithms=["HS256"])
    logger.info(f"Local token decoded for user: {decoded.get('username', 'unknown')}")
    return decoded


# Local JWT token decorator
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
        "cors_origins": app.config['CORS_ORIGINS'],
        "auth": "local-jwt"
    }), 200

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json() or {}

        username = data.get('username') or 'guest'

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
            "message": "Local login is disabled. Set ALLOW_DEV_LOGIN=true for development."
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
        "auth_mode": "local-dev",
        "cors_origins": app.config['CORS_ORIGINS']
    }), 200

@app.route('/admin/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    # Handle OPTIONS request
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    logger.info("Password reset requested but not supported without external identity provider")
    return jsonify({
        "message": "Password resets are not available in local placeholder auth mode.",
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
    
    # Mirror allowed local/Vercel frontend origins for simple local development.
    if 'Access-Control-Allow-Origin' not in response.headers:
        allowed_origins = app.config.get('CORS_ORIGINS', [])
        response.headers.add('Access-Control-Allow-Origin', origin if origin in allowed_origins else allowed_origins[0])
    
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
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
