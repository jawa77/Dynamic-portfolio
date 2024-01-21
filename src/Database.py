from pymongo import MongoClient
from src import get_config

class Database:
    @staticmethod
    def get_connection(database=None):
        client = MongoClient(get_config("mangodb_conection_string"))
        if database is None:
            return client[get_config('mongodb_database')]
        else:
            return client[database]
