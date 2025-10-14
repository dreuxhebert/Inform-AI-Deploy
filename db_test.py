import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the MongoDB URI from .env
uri = os.getenv("MONGODB_URI")

client = MongoClient(uri)

# Create/use database "app_dev"
db = client["inform_qa"]

# Create/use collection "items"
items = db["items"]

# Insert one test document
doc = {"name": "Test Widget", "price": 9.99, "in_stock": True}
result = items.insert_one(doc)

print("Inserted id:", result.inserted_id)

# Read it back
found = items.find_one({"_id": result.inserted_id})
print("Found:", found)

print("Databases:", client.list_database_names())
