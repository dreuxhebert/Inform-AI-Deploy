import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Mongo URI from .env
MONGO_URI = os.getenv("MONGODB_URI")

# Initialize client
client = MongoClient(MONGO_URI)

# Use your main database
db = client["inform_qa"]


# Collections
dispatchers = db["dispatchers"]
calls = db["calls"]
evaluations = db["evaluations"]
questions = db["questionSet"]

print("Database Connection successful")