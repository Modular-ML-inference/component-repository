from pymongo import MongoClient

from application.config import DB_PORT


client = MongoClient('repository_db', DB_PORT)
