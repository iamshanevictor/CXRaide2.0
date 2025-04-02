# Create init_db.py in server directory
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

# Create sample user
db.users.insert_one({
    "username": "admin",
    "password": generate_password_hash("password")
})