import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from bionexo.domain.entity.user import User
from bionexo.infrastructure.utils.functions import hash_password

def get_db():
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["bionexo"]
    return db

def db_user_exists(db, email: str, password: str) -> bool:
    users_collection = db["users"]
    user = users_collection.find_one({"email": email, "password": hash_password(password)})
    return user is not None

def save_user(db, user_data: User):
    users_collection = db["users"]
    try:
        users_collection.insert_one(user_data.model_dump())
        return True
    except DuplicateKeyError:
        return None

def get_intakes_from_db(db, user_id: str):
    intakes_collection = db["intakes"]
    intakes = list(intakes_collection.find({"id": user_id}))
    return intakes