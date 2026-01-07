import os
from pymongo import MongoClient

def get_db():
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["bionexo"]
    return db