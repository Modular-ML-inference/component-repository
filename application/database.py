from pymongo import MongoClient

from application.config import DB_PORT, DB_ADDRESS
import logging

logger = logging.getLogger()
# log all messages, debug and up
logger.setLevel(logging.INFO)
logging.log(logging.INFO, f'{DB_ADDRESS}')
client = MongoClient(DB_ADDRESS, int(DB_PORT))
