import os
from pymongo import MongoClient
from datetime import datetime
import config

def get_db_connection():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/reddit_sentiment")
    client = MongoClient(mongo_uri)
    # Extract database name from URI or use default
    db_name = mongo_uri.split("/")[-1].split("?")[0] or "reddit_sentiment"
    return client[db_name]

def get_next_id(db, collection_name):
    """
    Implements auto-incrementing ID pattern for MongoDB.
    """
    counter = db.counters.find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]

def save_sentiment_results(data, time_range):
    db = get_db_connection()
    collection = db.sentiment_results
    
    # Delete existing results for the time_range
    collection.delete_many({"time_range": time_range})
    
    documents = []
    for item in data:
        # Get next auto-incrementing ID
        doc_id = get_next_id(db, "sentiment_results")
        
        documents.append({
            "id": doc_id,
            "time_range": time_range,
            "sentiment": item["sentiment"],
            "asset": item["asset"],
            "reasoning": item.get("reasoning", ""),
            "created_at": datetime.utcnow()
        })
    
    if documents:
        collection.insert_many(documents)
    
    # Connection is closed automatically when the client object is garbage collected, 
    # but for MongoClient it's usually fine to keep it or let it be handled.
    # db.client.close()

