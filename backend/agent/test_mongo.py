import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

# Fix encoding for Windows terminals
sys.stdout.reconfigure(encoding='utf-8')

# Load .env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

def test_connection():
    mongo_uri = os.getenv("MONGO_URI")
    print(f"Testing connection to cloud MongoDB...")
    
    try:
        # We use a 10s timeout to be sure
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        
        # Check connectivity
        info = client.admin.command('ismaster')
        print("Success: Connected to cluster!")
        
        db = client.get_database("reddit_sentiment")
        print(f"Connected to database: {db.name}")
        
        collection = db.test_connection
        
        # Insert a dummy document
        result = collection.insert_one({"test": "connection", "status": "active"})
        print(f"Success: Document inserted with ID: {result.inserted_id}")
        
        # Clean up
        collection.delete_one({"_id": result.inserted_id})
        print("Success: Cleanup (deletion) completed.")
        print("\n--- CONCLUSION: MongoDB Connection is WORKING PERFECTLY ---")
        
    except Exception as e:
        print(f"FAILURE: Could not connect to MongoDB.")
        print(f"Error details: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_connection()
