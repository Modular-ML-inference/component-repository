from pymongo import MongoClient

from application.config import DB_PORT, DB_ADDRESS


client = MongoClient(DB_ADDRESS, DB_PORT)
