# Create init_db.py in server directory
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["cxraide"]

# Drop existing users collection if it exists
db.users.drop()

# Create admin user with specified credentials
db.users.insert_one({
    "username": "admin",
    "password": generate_password_hash("admin123")
})