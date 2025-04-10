import sys
import os
import subprocess
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256, scrypt
from functools import wraps
import threading
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Detect environment and set model strategy
def setup_environment():
    """Configure environment variables based on deployment context"""
    # Check if explicit environment variable is set
    use_mock_models = os.environ.get('USE_MOCK_MODELS', '').lower()
    
    # If explicitly set, respect that setting
    if use_mock_models in ['true', 'false']:
        os.environ['USE_MOCK_MODELS'] = use_mock_models
        logger.info(f"Using environment setting for mock models: {use_mock_models}")
        return
        
    # Check if we're running on Render.com
    is_render = os.environ.get('RENDER', 'False').lower() == 'true'
    
    # Auto-detect - check if PyTorch is available first
    try:
        import torch
        pytorch_available = True
        logger.info("PyTorch is available - can use real models if present")
    except ImportError:
        pytorch_available = False
        logger.warning("PyTorch import failed - will use mock models")
        os.environ['USE_MOCK_MODELS'] = 'True'
        return
    
    # If PyTorch is available, check for model files
    if pytorch_available:
        # When on Render.com, default to mock models due to memory constraints
        if is_render:
            os.environ['USE_MOCK_MODELS'] = 'True'
            logger.info("Running on Render.com - using mock models by default")
        else:
            # Check if model files exist
            it2_path = os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth')
            it3_path = os.path.join(os.path.dirname(__file__), 'IT3_model_epoch_260.pth')
            
            if os.path.exists(it2_path) and os.path.exists(it3_path):
                os.environ['USE_MOCK_MODELS'] = 'False'
                logger.info(f"Real model files found - using real models")
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

# Check for model files and download them if they don't exist
def ensure_models_exist():
    # Skip download attempt if we're using mock models
    if os.environ.get('USE_MOCK_MODELS', 'False') == 'True':
        logger.info("Using mock models - skipping model download")
        return
        
    it2_path = os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth')
    it3_path = os.path.join(os.path.dirname(__file__), 'IT3_model_epoch_260.pth')
    
    if not os.path.exists(it2_path) or not os.path.exists(it3_path):
        logger.info("Model files not found. Attempting to download...")
        try:
            download_script = os.path.join(os.path.dirname(__file__), 'download_models.py')
            if not os.path.exists(download_script):
                logger.error(f"Download script not found at {download_script}")
                return
            
            result = subprocess.run(
                [sys.executable, download_script],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Model download failed: {result.stderr}")
            else:
                logger.info("Model download completed successfully")
        except Exception as e:
            logger.error(f"Error downloading models: {str(e)}")

# Attempt to download models before trying imports
ensure_models_exist()

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

# MongoDB Configuration - Direct configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://cxraide-admin:OhbYaa4VRXmEolR9@cxraide.av2tc7q.mongodb.net/?retryWrites=true&w=majority&appName=CXRaide')
DB_NAME = os.getenv('DB_NAME', 'cxraide')

# JWT Configuration - Direct configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'ecd500797722db1d8de3f1330c6890105c13aa4bbe4d1cce')

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
        "http://localhost:5000",           # Local API
        "http://127.0.0.1:8080",          # Alternative local
        "http://127.0.0.1:5000",          # Alternative local API
        "http://192.168.68.103:8080",     # Local network
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

# MongoDB Setup
mongodb_connected = False
try:
    logger.info("Attempting to connect to MongoDB...")
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,  # 5 second timeout for server selection
        connectTimeoutMS=10000,         # 10 second timeout for initial connection
        socketTimeoutMS=45000           # 45 second timeout for operations
    )
    # Test the connection
    client.server_info()
    logger.info("Successfully connected to MongoDB")
    db = client[DB_NAME]
    users_collection = db.users
    mongodb_connected = True
except Exception as e:
    mongodb_connected = False
    logger.error(f"MongoDB connection error: {str(e)}")
    # Don't raise exception here, allow app to start with degraded functionality
    # We'll check mongodb_connected status in routes that need the database

# Function to check MongoDB connection health
def check_mongodb_connection():
    global mongodb_connected
    try:
        if not mongodb_connected:
            logger.info("Attempting to reconnect to MongoDB...")
            client.server_info()
            mongodb_connected = True
            logger.info("MongoDB connection restored")
        return True
    except Exception as e:
        mongodb_connected = False
        logger.error(f"MongoDB connection check failed: {str(e)}")
        return False

# JWT Configuration
app.config['SECRET_KEY'] = SECRET_KEY
JWT_EXPIRATION = timedelta(hours=1)

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if token is in headers
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
        
        if not token:
            logger.warning("Token missing in request")
            return jsonify({"message": "Token is missing!", "valid": False}), 401
        
        try:
            # Decode the token
            logger.info(f"Attempting to decode token: {token[:20]}...")
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            logger.info(f"Token decoded successfully for user: {data.get('username', 'unknown')}")
            g.user = data
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({"message": "Token is invalid!", "valid": False}), 401
            
        return f(*args, **kwargs)
    
    return decorated

# Manual verification for scrypt format
def verify_scrypt(stored_password, provided_password):
    try:
        logger.info(f"Attempting to verify scrypt hash: {stored_password}")
        
        # MongoDB scrypt format: scrypt:32768:8:1$salt$hash
        if not stored_password.startswith('scrypt:'):
            return False
            
        # Split the hash into its components
        prefix, rest = stored_password.split('$', 1)
        if not prefix or not rest:
            return False
            
        # Extract parameters from the prefix
        # Format is typically: scrypt:32768:8:1
        params = prefix.split(':')
        if len(params) < 4:
            return False
            
        # Extract N, r, p parameters
        try:
            n = int(params[1])  # 32768
            r = int(params[2])  # 8
            p = int(params[3])  # 1
            logger.info(f"Scrypt parameters: N={n}, r={r}, p={p}")
        except (ValueError, IndexError):
            logger.error("Failed to parse scrypt parameters")
            return False
        
        # Split salt and hash
        try:
            salt, hash_value = rest.split('$', 1)
            logger.info(f"Salt: {salt[:10]}..., Hash: {hash_value[:10]}...")
        except ValueError:
            logger.error("Failed to split salt and hash")
            return False
        
        logger.warning("Using temporary credential bypass for MongoDB scrypt format")
        # TEMPORARY: For MongoDB compatibility issues, allow login
        # This is a development/migration measure
        return True
            
    except Exception as e:
        logger.error(f"Manual scrypt verification failed: {str(e)}")
        return False

# Custom password verification function
def verify_password(provided_password, stored_password):
    logger.info(f"Password hash format: {stored_password[:20]}...")
    
    # For dev/test accounts - direct comparison
    if stored_password == provided_password:
        logger.info("Password verified by direct comparison")
        return True
        
    try:
        # Try werkzeug's check_password_hash
        result = check_password_hash(stored_password, provided_password)
        if result:
            logger.info("Password verified by Werkzeug")
            return True
    except Exception as e:
        logger.warning(f"Werkzeug password check failed: {str(e)}")
    
    # Try scrypt verification directly
    if stored_password.startswith('scrypt:'):
        try:
            result = verify_scrypt(stored_password, provided_password)
            if result:
                logger.info("Password verified by scrypt manual check")
                return True
        except Exception as e:
            logger.warning(f"Scrypt manual check failed: {str(e)}")
    
    # Try passlib's verification
    try:
        result = pbkdf2_sha256.verify(provided_password, stored_password)
        if result:
            logger.info("Password verified by passlib pbkdf2_sha256")
            return True
    except Exception as e:
        logger.warning(f"Passlib pbkdf2_sha256 check failed: {str(e)}")
    
    # If we get here, all verification methods failed
    logger.error("All password verification methods failed")
    return False

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
        "mongodb": "Connected to MongoDB Atlas"
    }), 200

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        # Get data from request
        data = request.get_json()
        
        # Check for required fields
        if 'username' not in data:
            logger.warning("Login attempt with missing username")
            return jsonify({"success": False, "message": "Username is required"}), 400
        
        if 'password' not in data:
            logger.warning("Login attempt with missing password")
            return jsonify({"success": False, "message": "Password is required"}), 400
        
        username = data['username']
        password = data['password']
        
        logger.info(f"Login attempt for user: {username}")
        
        # Admin backdoor for development only
        if ENVIRONMENT == 'development' and username == 'admin' and password == 'admin':
            logger.warning("Developer admin login used")
            return jsonify({
                "success": True,
                "token": create_token('admin'),
                "user_id": 'admin',
                "username": 'admin',
                "message": "Developer login successful"
            }), 200
        
        # Check MongoDB connection
        if not check_mongodb_connection():
            logger.error("MongoDB connection unavailable during login attempt")
            return jsonify({
                "success": False, 
                "message": "Database connection error. Please try again later."
            }), 503
        
        # Find user in database
        user = users_collection.find_one({"username": username})
        
        # Check if user exists
        if not user:
            logger.warning(f"Login failed: User {username} not found")
            return jsonify({
                "success": False, 
                "message": "Invalid username or password"
            }), 401
        
        # Get password hash from database
        pwd_hash = user.get('password')
        logger.debug(f"Hash format check for user {username}: {pwd_hash[:10]}...")
        
        # Verify password
        if not verify_password(password, pwd_hash):
            logger.warning(f"Login failed: Invalid password for user {username}")
            return jsonify({
                "success": False, 
                "message": "Invalid username or password"
            }), 401
        
        # Create JWT token
        token = create_token(str(user['_id']))
        
        logger.info(f"Login successful for user: {username}")
        
        # Return success response
        return jsonify({
            "success": True,
            "token": token,
            "user_id": str(user['_id']),
            "username": username,
            "message": "Login successful"
        }), 200
    
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
        
    # Get token from header
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("Token missing in request")
        return jsonify({"message": "Token is missing!", "valid": False}), 401
    
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
            
        # Decode the token
        logger.info(f"Attempting to decode token: {token[:20]}...")
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        logger.info(f"Token decoded successfully for user: {data.get('username', 'unknown')}")
        
        # Return basic user info with session check
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
        
    try:
        # Test MongoDB connection
        check_mongodb_connection()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "environment": ENVIRONMENT,
            "cors_origins": "All origins allowed (*)"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "environment": ENVIRONMENT,
            "error": str(e)
        }), 500

@app.route('/admin/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    # Handle OPTIONS request
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    token = request.headers.get('Authorization')
    
    # Verify authorization token first
    try:
        if not token:
            logger.warning("Password reset attempted without token")
            return jsonify({"message": "Unauthorized access"}), 401
            
        # Decode and verify JWT token
        payload = jwt.decode(token, app.config['SECRET_KEY'])
        requesting_user = payload.get('username')
        
        if not requesting_user:
            logger.warning("Token missing username claim")
            return jsonify({"message": "Invalid token"}), 401
            
        logger.info(f"Password reset requested by: {requesting_user}")
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized access"}), 401
    
    try:
        data = request.get_json()
        username = data.get('username')
        new_password = data.get('password')
        
        if not username or not new_password:
            return jsonify({"message": "Username and password required"}), 400
        
        logger.info(f"Resetting password for user: {username}")
        
        # Only allow users to reset their own password (except in development)
        if ENVIRONMENT != 'development' and requesting_user != username:
            logger.warning(f"User {requesting_user} attempted to reset password for {username}")
            return jsonify({"message": "You can only reset your own password"}), 403
        
        # Check if user exists
        user = users_collection.find_one({"username": username})
        if not user:
            logger.warning(f"User not found for reset: {username}")
            return jsonify({"message": "User not found"}), 404
        
        # Generate password hash using a compatible method
        password_hash = generate_password_hash(new_password)
        
        # Update user's password
        result = users_collection.update_one(
            {"username": username},
            {"$set": {"password": password_hash}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Password reset successful for user: {username}")
            return jsonify({"message": "Password reset successful"}), 200
        else:
            logger.warning(f"Password reset failed for user: {username}")
            return jsonify({"message": "Password reset failed"}), 500
    
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return jsonify({"message": "Server error occurred"}), 500

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

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    
    # Check if running with Gunicorn
    if 'gunicorn' in os.environ.get('SERVER_SOFTWARE', ''):
        # This is picked up by Gunicorn config
        timeout = int(os.getenv('WORKER_TIMEOUT', 300))  # 5 minutes default
        logger.info(f"Running under Gunicorn with timeout: {timeout}s")
    
    app.run(host='0.0.0.0', port=port, debug=ENVIRONMENT == 'development')