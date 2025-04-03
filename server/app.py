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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Store allowed origins in app config
app.config['CORS_ORIGINS'] = [
    "http://localhost:8080",          # Local development
    "http://localhost:5000",          # Local API
    "http://192.168.68.103:8080",    # Local IP for mobile access
    "http://192.168.68.103:5000",    # Local IP API for mobile access
    "https://cxraide.onrender.com",   # Production frontend
    "http://cxraide.onrender.com",    # HTTP version
    "https://www.cxraide.onrender.com", # www version
    "http://www.cxraide.onrender.com"  # www HTTP version
]

# Updated CORS configuration with proper headers
CORS(app, 
     resources={
         r"/*": {
             "origins": app.config['CORS_ORIGINS'],
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }
     })

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    logger.info(f"Received request from origin: {origin}")
    
    # Allow the specific origin if it matches our allowed origins
    if origin in app.config['CORS_ORIGINS']:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
    else:
        logger.warning(f"Origin not allowed: {origin}")
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
    except:
        return jsonify({"valid": False}), 401

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Test MongoDB connection
        client.server_info()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 500

if __name__ == '__main__':
    # Run the app on all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)