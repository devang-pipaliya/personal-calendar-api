"""
A layer between DB and API for User related Entities
"""

import datetime
import traceback

from app.common.db_utils import db


class User:
    """
    Entity for User's Profile.
    """

    collection_name = "user"

    collection = None

    pk = "id"

    def __init__(self):
        """
        Initializing the Database Connection.
        """
        self.collection = db.get_collection(self, create=True, has_seq=False)
        if not self.collection:
            raise Exception("Collection not found!")


    def get_single_record(self, where=None, projection=None, **kwargs):
        """
        Get single record based on query
        """
        try:
            if not where:
                where = {}
            if not projection:
                projection = {}
            if "_id" not in projection:
                projection.setdefault("_id", False)
            record = self.collection.get_one_record(
                where=where, projection=projection, **kwargs
            )
            return record
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

    def get_records(self, where=None, projection=None, **kwargs):
        """
        Get list of record based on query
        """
        try:
            if not where:
                where = {}
            if not projection:
                projection = {}
            if "_id" not in projection:
                projection.setdefault("_id", False)
            records = self.collection.get_records(
                where=where, projection=projection, **kwargs
            )
            return records
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

    def create_record(self, data):
        """
        Create the record
        """
        try:
            # vals = self.get_updated_dict(self.get_default_dict(), data)
            # print(f"vals-> {vals}")

            resulted_id = self.collection.create_data(data)
            print(f"resulted_id-> {resulted_id}")

            query = {
                "_id": resulted_id,
            }
            user = self.get_single_record(
                where=query, projection={"_id": True, }
            )
            print(f"user-> {user}")
            if user:
                return user["_id"]

            return resulted_id
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

    # def update_record(self, record_id, new_data, create=False):
    #     """
    #     Update the record
    #     """
    #     try:
    #         vals = self.get_updated_dict({}, new_data)
    #         self.collection.update_data(
    #             {"user_id": record_id}, {"$set": vals}, upsert=create
    #         )
    #     except Exception as excep:
    #         print(f"excep-> {excep}")
    #         traceback.print_exc()

    # def delete_record(self, record_id):
    #     """
    #     Delete the record
    #     """
    #     try:
    #         self.collection.delete_data({"user_id": record_id})
    #     except Exception as excep:
    #         print(f"excep-> {excep}")
    #         traceback.print_exc()
