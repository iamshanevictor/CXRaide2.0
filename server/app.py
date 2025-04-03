from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Updated CORS configuration
CORS(app, supports_credentials=True, origins=[
    "http://localhost:8080",          # Local development
    "https://cxraide.onrender.com",   # Production frontend
    "http://cxraide.onrender.com",    # HTTP version
    "https://www.cxraide.onrender.com", # www version
    "http://www.cxraide.onrender.com"  # www HTTP version
], methods=["GET", "POST", "OPTIONS"], 
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"])

# MongoDB Configuration
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
users_collection = db.users

# JWT Configuration
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
JWT_EXPIRATION = timedelta(hours=1)

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    user = users_collection.find_one({"username": data['username']})
    
    if user and check_password_hash(user['password'], data['password']):
        token = jwt.encode({
            'sub': str(user['_id']),
            'exp': datetime.utcnow() + JWT_EXPIRATION
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'user_id': str(user['_id'])
        }), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

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

if __name__ == '__main__':
    app.run(debug=True)