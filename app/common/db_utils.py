"""Module commons.db_utils"""

import os
import traceback

from bson.objectid import ObjectId
from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo import errors as mongo_errors


# from .aggregation_pipelines import job_collection_views, candidate_collection_views

load_dotenv()

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")

# DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_REPLICASET_STR")
# DB_NAME = os.getenv("DB_NAME")


class VritiDBClient:
    """
    DatabaseClient class facilitates the client level operations
    """

    client = None

    def __init__(self, *args, **kwargs):
        """
        initializing the Database Client.
        """
        # print("initializing the Database Client")
        if self.client is None:
            self.client = MongoClient(DB_CONNECTION_STRING)
        # print(f"DB-Client -> {self.client}")

    def get_client(self):
        """
        getting the client ready for some operations
        """
        # global client
        return self.client


class DatabaseConnection:
    """
    Database class facilitates the db level operations
    """

    database = None
    collection = None
    db_view = None

    seq_collection = None

    def __init__(self, *args, **kwargs):
        """
        initializing the Database Connection.
        """
        # print("initializing the Database Connection.")
        if self.database is None:
            client = VritiDBClient().get_client()
            self.database = client[DB_NAME]
        if not self.seq_collection:
            self.seq_collection = self.database["seq_collection"]

        # print(f"database -> f{self.database}")
        # print(f"database connection test -> f{self.test_connection()}")

    def list_collection(self):
        """
        Checking if the collection exists or not
        """
        try:
            # print("check Connection.")
            # print(f"collection_list-> {self.database.list_collection_names()}")
            return self.database.list_collection_names()
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

    def test_connection(self):
        """
        Checking if the collection exists or not
        """
        try:
            # print("check Connection.")
            # print(f"collection_list-> {self.list_collection()}")
            return self.list_collection() and True or False
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

    def check_collection(self, collection):
        """
        Checking if the collection exists or not
        """
        try:
            # print("check Connection.")
            # print(f"collection_list-> {self.list_collection()}")
            return collection in self.list_collection()
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

    def create_collection(self, collection, check_seq=False, seq_name=""):
        """
        Creating the collection
        """
        try:
            # print(f"Create collection-> {collection}")
            # new_collection = self.database[collection]
            new_collection = self.database.create_collection(collection)
            # print(f"new_collection-> {new_collection}")
            # print(f"new_collection exists-> {self.check_collection(collection)}")

            if check_seq:
                self.check_seq_collection(collection, seq_name=seq_name)
            return new_collection
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

    def check_seq_collection(self, collection, seq_name=""):
        """
        Checking and allocating the collection Object Sequence on the go :)
        """
        try:
            seq_exists = self.seq_collection.find_one({"name": collection})
            if not seq_exists:
                result = self.seq_collection.insert_one(
                    {"name": collection, "seq": 500}
                )
                return result or False
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

    def get_collection(self, entity, create=False, has_seq=False, seq_name=""):
        """
        Checking and allocating the collection Object on the go :)
        """
        try:
            collection = entity.collection_name
            collection_exists = self.check_collection(collection)
            print(f"collection exists->  {collection_exists}")
            if collection_exists in [None, False]:
                print("inside")
                if create:
                    self.create_collection(collection, check_seq=has_seq)
                    # collection_exists = True
                    collection_exists = self.check_collection(collection)

            print(f"collection exists-> checking again {collection_exists}")
            print(f"checking again=> self.database->  {self.database}")
            if collection_exists not in [None, False]:
                print("not none")
                self.collection = DatabaseCollection(
                    self,
                    self.database,
                    collection,
                    pk=entity.pk,
                    create=create,
                    has_seq=has_seq,
                    seq_name=seq_name,
                )
            else:
                self.collection = None
                raise mongo_errors.CollectionInvalid(f"'{collection}' not found!")

            return self.collection

        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
        return None

def get_updated_default_mapping(default_mapping, data):
    """
    get the default mapping updated as per the mapping
    """
    if default_mapping:
        for k, v in default_mapping.items():
            if v in data:
                data[k] = data[v]
    return data


class DatabaseCollection:
    """
    Collection class facilitates the collection level operations
    """

    database = None
    collection = None
    pk = None

    has_seq = False
    seq_name = ""

    def __init__(self, db_connection, database, collection, *args, **kwargs):
        """
        Initializing the Collection Object
        """
        if database is not None:
            self.collection = database[collection]
            self.database = database
            self.db_connection = db_connection
            if "has_seq" in kwargs:
                self.has_seq = kwargs["has_seq"]
            if "seq_name" in kwargs:
                self.seq_name = kwargs["seq_name"]
            if "pk" in kwargs:
                self.pk = kwargs["pk"]
        else:
            raise mongo_errors.ConnectionFailure("Database connection not found!")

    def get_one_record(self, **kwargs):
        """
        Used to fetch the query based data
        """
        try:
            data = []
            sort = []
            where = {}
            projection = {}

            # created view for jobs
            # self.create_views()
            # print("inside get records")
            if "order" in kwargs and kwargs.get("order", {}):
                sort = [(k, v) for k, v in kwargs.get("order").items()]

            if "where" in kwargs and kwargs.get("where", {}):
                where = kwargs["where"]

            if "projection" in kwargs and kwargs.get("projection", {}):
                projection = kwargs["projection"]

            # Don't provide the _id in the response by default
            if "_id" not in projection:
                projection.update({"_id": False})

            # Provide the _id in the response if requested
            if "return_with_objectid" in kwargs and kwargs["return_with_objectid"]:
                projection.update({"_id": True})
            # print("collection", self.collection)
            data = self.collection.find_one(where, sort=sort, projection=projection)
            # print("data",data)
            # breakpoint()
            return data
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
            return excep

    def get_records(self, **kwargs):
        """
        Used to fetch the query based data
        """
        try:
            data = []
            query = {}
            projection = {}
            # created view for jobs
            # self.create_views()
            # print("collection", self.collection)
            if "where" in kwargs:
                query = kwargs["where"]

            if "projection" in kwargs and kwargs.get("projection", {}):
                projection = kwargs["projection"]

            # Don't provide the _id in the response by default
            if "_id" not in projection:
                projection.update({"_id": False})

            # Provide the _id in the response if requested
            if "return_with_objectid" in kwargs and kwargs["return_with_objectid"]:
                projection.update({"_id": True})

            if "limit" in kwargs and "skip" in kwargs:
                data = (
                    self.collection.find(query, projection=projection)
                    .limit(kwargs["limit"])
                    .skip(kwargs["skip"])
                )
            elif "limit" in kwargs:
                data = self.collection.find(query, projection=projection).limit(
                    kwargs["limit"]
                )
            elif "skip" in kwargs:
                data = self.collection.find(query, projection=projection).skip(
                    kwargs["skip"]
                )
            else:
                data = self.collection.find(query, projection=projection)

            if data:
                if "order" in kwargs and kwargs.get("order", {}):
                    data.sort([(k, v) for k, v in kwargs.get("order").items()])
            return data
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
            raise excep

    def update_data(
        self, where, data, upsert=True, return_with_objectid=False, **kwargs
    ):
        """
        Creating or Updating the requested data
        """
        try:
            projection = {}
            if "projection" in kwargs:
                # TODO: handle and convert projection to dict
                projection = kwargs["projection"]
                # Don't provide the _id in the response  by default
                if "_id" not in kwargs and not return_with_objectid:
                    projection.update({"_id": False})

            if upsert:
                if self.pk:
                    has_seq, next_sequence = self.get_next_sequence(
                        self.collection.name
                    )

                    if (
                        has_seq
                        and next_sequence > 0
                        and (
                            self.pk not in data
                            or data[self.pk] not in ["", None, False]
                        )
                    ):
                        data[self.pk] = next_sequence

                if "_id" not in data:
                    data["_id"] = str(ObjectId())

            result = self.collection.find_one_and_update(
                where,
                data,
                upsert=upsert,
                projection=projection,
                # return_document=ReturnDocument.AFTER
            )
            return result or False
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
            raise excep

    def delete_data(self, where):
        """
        Creating or Updating the requested data
        """
        try:
            result = self.collection.delete_one(where)
            return result or False
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
            raise excep

    def delete_many_data(self, where):
        """
        Creating or Updating the requested data
        """
        try:
            result = self.collection.delete_many(where)
            return result or False
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
            raise excep

    def create_data(self, data, default_mapping=None):
        """
        Creating the document
        """
        try:
            if self.pk:
                has_seq, next_sequence = self.get_next_sequence(self.collection.name)

                if (
                    has_seq
                    and next_sequence > 0
                    and (self.pk not in data or data[self.pk] not in ["", None, False])
                ):
                    data[self.pk] = next_sequence

            if "_id" not in data:
                data["_id"] = str(ObjectId())

            if not default_mapping:
                default_mapping = {}
            data = get_updated_default_mapping(default_mapping, data)

            # print(f"db_utils->DatabaseCollection->create_data-> data => {data}")

            result = self.collection.insert_one(data)

            return str(result.inserted_id) or ""
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
            raise excep

    def get_next_sequence(self, collection_name):
        """
        Auto generate the next sequence
        """
        try:
            seq = 0
            has_seq = False

            if self.has_seq:
                self.db_connection.check_seq_collection(
                    collection_name, seq_name=self.seq_name
                )
                has_seq = self.has_seq
            has_seq = self.has_seq

            query = {"name": collection_name}
            current_seq = self.db_connection.seq_collection.find_one(query)

            if current_seq:
                seq = 1 + current_seq["seq"]

                self.db_connection.seq_collection.find_one_and_update(
                    query, {"$set": {"seq": seq}}, upsert=True
                )

            return self.has_seq, seq
        except Exception as excep:
            print(f"excep-> {excep}")
            traceback.print_exc()
            raise excep

    def get_updated_default_mapping(self, default_mapping, data):
        """
        get the default mapping updated as per the mapping
        """
        if default_mapping:
            for k, v in default_mapping.items():
                if v in data:
                    data[k] = data[v]
        return data

    def perform_aggregation(self, pipeline):
        result = self.collection.aggregate(pipeline)
        formatted_result = []
        for data in result:
            formatted_result.append(data)
        return formatted_result


    # def create_jobs_views(self, view_data):
    #     """
    #     Creating Views
    #     """
    #     try:
    #         self.database.create_collection(
    #             view_data[0], viewOn=view_data[1], pipeline=view_data[2]
    #         )
    #         return True
    #     except Exception as excep:
    #         traceback.print_exc()

    # def create_views(self):
    #     """
    #     Creating job and candidate collection View for search
    #     """
    #     try:
    #         for job_view in job_collection_views:
    #             if job_view[0] not in self.database.list_collection_names():
    #                 self.create_jobs_views(job_view)

    #         for candidate_view in candidate_collection_views:
    #             if candidate_view[0] not in self.database.list_collection_names():
    #                 self.create_jobs_views(candidate_view)
    #         return True
    #     except Exception as excep:
    #         traceback.print_exc()
    #         return False

    # def drop_views(self, view_name):
    #     """
    #     Delete job and candidate collection Views
    #     """
    #     try:
    #         view_collection = [
    #             collection[0]
    #             for collection in candidate_collection_views + job_collection_views
    #         ]
    #         if view_name in view_collection:
    #             self.database.drop_collection(view_name)

    #         return True
    #     except Exception as excep:
    #         traceback.print_exc()
    #         return False


db = DatabaseConnection()
