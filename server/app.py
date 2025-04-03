from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging

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
        "http://cxraide.onrender.com"
    ]

logger.info(f"Allowed origins: {app.config['CORS_ORIGINS']}")

# Updated CORS configuration with proper headers
CORS(app, 
     resources={
         r"/*": {
             "origins": "*",  # Allow all origins, we'll filter in after_request
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
        "cors_origins": app.config['CORS_ORIGINS']
    }), 200

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', '')
    logger.info(f"Request details - Method: {request.method}, Path: {request.path}, Origin: {origin}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Allow all origins temporarily for debugging
    if ENVIRONMENT == 'production':
        response.headers.add('Access-Control-Allow-Origin', origin or '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
    # Development environment - strict CORS
    elif origin in app.config['CORS_ORIGINS']:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
    else:
        logger.warning(f"Origin not allowed: {origin}")
        
    logger.info(f"Response headers: {dict(response.headers)}")
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

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    logger.info(f"Login attempt from IP: {request.remote_addr}")
    logger.info(f"Login request headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        logger.info(f"Login attempt for username: {data.get('username')}")
        
        user = users_collection.find_one({"username": data['username']})
        
        if user and check_password_hash(user['password'], data['password']):
            token = jwt.encode({
                'sub': str(user['_id']),
                'exp': datetime.utcnow() + JWT_EXPIRATION
            }, app.config['SECRET_KEY'])
            
            logger.info(f"Successful login for user: {data['username']}")
            return jsonify({
                'token': token,
                'user_id': str(user['_id'])
            }), 200
        
        logger.warning(f"Failed login attempt for username: {data.get('username')}")
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
            "cors_origins": app.config['CORS_ORIGINS']
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "environment": ENVIRONMENT,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 10000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)