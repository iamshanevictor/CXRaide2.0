from pymongo import MongoClient
import pprint
from bson import ObjectId

def format_document(doc):
    """Format document for better readability"""
    formatted = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            formatted[key] = str(value)
        elif key == 'password':
            formatted[key] = '***HASHED***'
        else:
            formatted[key] = value
    return formatted

# Connect to local MongoDB
print("\n=== MongoDB Database Inspector ===")
try:
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
    # Test connection
    client.server_info()
    print("✓ Successfully connected to MongoDB")
except Exception as e:
    print(f"✗ Failed to connect to MongoDB: {str(e)}")
    exit(1)

db = client["cxraide"]

# Get database stats
print("\n=== Database Information ===")
print(f"Database name: cxraide")
collections = db.list_collection_names()
print(f"Number of collections: {len(collections)}")

# Print all collections
print("\n=== Collections ===")
for collection in collections:
    count = db[collection].count_documents({})
    print(f"• {collection} ({count} documents)")

# Print contents of each collection
print("\n=== Collection Contents ===")
for collection_name in collections:
    collection = db[collection_name]
    print(f"\n▶ {collection_name} collection:")
    documents = list(collection.find())
    if not documents:
        print("  (empty collection)")
    else:
        for doc in documents:
            formatted_doc = format_document(doc)
            pprint.pprint(formatted_doc, indent=2)

print("\n=== End of Database Inspection ===\n") 