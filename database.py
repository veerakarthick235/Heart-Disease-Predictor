"""
database.py — MongoDB Atlas connection and collection accessors.
Uses PyMongo with connection pooling and automatic retries.
"""

import sys
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import os

load_dotenv()

_client = None
_db = None


def get_client():
    """Return (or create) the MongoClient singleton."""
    global _client
    if _client is None:
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
        _client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
    return _client


def get_db():
    """Return the database instance."""
    global _db
    if _db is None:
        client = get_client()
        dbname = os.environ.get('MONGO_DBNAME', 'heartdisease')
        _db = client[dbname]
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db):
    """Create indexes for performance and uniqueness constraints."""
    # Unique email index on users
    db.users.create_index([('email', ASCENDING)], unique=True)
    # User-based lookup on predictions
    db.predictions.create_index([('user_id', ASCENDING)])
    db.predictions.create_index([('created_at', ASCENDING)])


def test_connection():
    """Test MongoDB connection — call at startup."""
    try:
        client = get_client()
        client.admin.command('ping')
        print("[OK] MongoDB Atlas connected successfully.")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"[ERROR] MongoDB connection failed: {e}")
        print("   Check your MONGO_URI in .env file.")
        return False


# Collection helpers
def users_col():
    return get_db().users


def predictions_col():
    return get_db().predictions
