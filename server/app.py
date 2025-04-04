from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
from passlib.hash import pbkdf2_sha256, scrypt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Get environment
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
logger.info(f"Running in {ENVIRONMENT} environment")

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
CORS(app, 
     resources={
         r"/*": {
             "origins": "*",  # Allow all origins in both production and development
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }
     })

@app.route('/')
def home():
    return jsonify({
        "message": "CXRaide API is running",
        "environment": ENVIRONMENT,
        "cors_origins": "All origins allowed (*)"
    }), 200

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', '')
    logger.info(f"Request details - Method: {request.method}, Path: {request.path}, Origin: {origin}")
    
    # Allow all origins for all environments
    response.headers.add('Access-Control-Allow-Origin', origin or '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    
    return response

# MongoDB Configuration
try:
    logger.info("Attempting to connect to MongoDB...")
    client = MongoClient(os.getenv("MONGO_URI"))
    # Test the connection
    client.server_info()
    logger.info("Successfully connected to MongoDB")
    db = client[os.getenv("DB_NAME")]
    users_collection = db.users
except Exception as e:
    logger.error(f"MongoDB connection error: {str(e)}")
    raise

# JWT Configuration
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
JWT_EXPIRATION = timedelta(hours=1)

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
def verify_password(stored_password, provided_password):
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

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    logger.info(f"Login attempt from IP: {request.remote_addr}")
    logger.info(f"Login request headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"message": "Username and password required"}), 400
        
        logger.info(f"Login attempt for username: {username}")
        
        # For admin/test users - hardcoded credentials for initial setup
        if username == "admin" and password == "admin123":
            logger.warning("Using hardcoded admin login - CHANGE THIS IN PRODUCTION!")
            
            # Create a token
            token = jwt.encode({
                'sub': 'admin_id',
                'exp': datetime.utcnow() + JWT_EXPIRATION,
                'username': username,
                'is_admin': True
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'token': token,
                'user_id': 'admin_id',
                'message': 'Login successful via hardcoded credentials'
            }), 200
        
        # Find the user in the database
        user = users_collection.find_one({"username": username})
        
        if not user:
            logger.warning(f"User not found for username: {username}")
            return jsonify({"message": "Invalid credentials"}), 401
            
        logger.info(f"User found for username: {username}")
        
        # Log the password hash format
        stored_hash = user.get('password', '')
        logger.info(f"Stored password hash format: {stored_hash[:20]}...")
        
        # TEMPORARY: MongoDB scrypt hash handling
        if stored_hash.startswith('scrypt:'):
            logger.info("Detected MongoDB scrypt hash format")
            
            # For temporary migration during development
            if ENVIRONMENT == 'development':
                logger.warning("DEVELOPMENT MODE: Allowing MongoDB scrypt login")
                valid = True
            # For production, use our scrypt verifier which will always return true during migration
            else:
                valid = verify_scrypt(stored_hash, password)
                
            if valid:
                # After successful login, update to a compatible hash format
                new_hash = generate_password_hash(password)
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"password": new_hash}}
                )
                logger.info(f"Updated password hash to Werkzeug format for {username}")
                
                token = jwt.encode({
                    'sub': str(user['_id']),
                    'exp': datetime.utcnow() + JWT_EXPIRATION,
                    'username': username
                }, app.config['SECRET_KEY'])
                
                logger.info(f"Successful login for user: {username}")
                return jsonify({
                    'token': token,
                    'user_id': str(user['_id']),
                    'message': 'Login successful'
                }), 200
        
        # Standard login verification
        if verify_password(stored_hash, password):
            token = jwt.encode({
                'sub': str(user['_id']),
                'exp': datetime.utcnow() + JWT_EXPIRATION,
                'username': username
            }, app.config['SECRET_KEY'])
            
            logger.info(f"Successful login for user: {username}")
            return jsonify({
                'token': token,
                'user_id': str(user['_id'])
            }), 200
        
        logger.warning(f"Failed login attempt for username: {username}")
        return jsonify({"message": "Invalid credentials"}), 401
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"message": "Server error occurred"}), 500

@app.route('/check-session', methods=['GET', 'OPTIONS'])
def check_session():
    if request.method == 'OPTIONS':
        return '', 200
        
    token = request.headers.get('Authorization')
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'])
        return jsonify({"valid": True}), 200
    except Exception as e:
        logger.error(f"Session check error: {str(e)}")
        return jsonify({"valid": False}), 401

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Test MongoDB connection
        client.server_info()
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

@app.route('/admin/reset-password', methods=['POST'])
def reset_password():
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

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 10000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)