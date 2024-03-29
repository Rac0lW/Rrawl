import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from monkey.config.config import Config
from monkey.utils.tools import singleton


@singleton
class MotorBase:
    """
    About motor's doc: https://github.com/mongodb/motor
    """

    _db = {}
    _collection = {}
    MONGODB = Config.MONGODB

    def __init__(self, loop=None):
        self.motor_uri = ""
        self.loop = loop or asyncio.get_event_loop()

    def client(self, db):
        # motor
        self.motor_uri = "mongodb://{account}{host}:{port}/{database}".format(
            account="{username}:{password}@".format(
                username=self.MONGODB["MONGO_USERNAME"],
                password=self.MONGODB["MONGO_PASSWORD"],
            )
            if self.MONGODB["MONGO_USERNAME"]
            else "",
            host=self.MONGODB["MONGO_HOST"]
            if self.MONGODB["MONGO_HOST"]
            else "localhost",
            port=self.MONGODB["MONGO_PORT"] if self.MONGODB["MONGO_PORT"] else 27017,
            database=db,
        )
        return AsyncIOMotorClient(self.motor_uri, io_loop=self.loop)

    def get_db(self, db=MONGODB["DATABASE"]):
        """
        Get a db instance
        :param db: database name
        :return: the motor db instance
        """
        if db not in self._db:
            self._db[db] = self.client(db)[db]

        return self._db[db]

    def get_collection(self, db_name, collection):
        """
        Get a collection instance
        :param db_name: database name
        :param collection: collection name
        :return: the motor collection instance
        """
        collection_key = db_name + collection
        if collection_key not in self._collection:
            self._collection[collection_key] = self.get_db(db_name)[collection]

        return self._collection[collection_key]