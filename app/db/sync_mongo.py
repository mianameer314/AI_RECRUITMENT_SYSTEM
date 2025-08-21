# app/db/sync_mongo.py
from pymongo import MongoClient
from app.core.config import settings

client_sync = MongoClient(settings.MONGO_URI)
db_sync = client_sync[settings.MONGO_DB]
