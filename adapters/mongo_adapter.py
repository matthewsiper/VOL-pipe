from pymongo import MongoClient
from bson.objectid import ObjectId
from config.config import Config

CONFIG = Config("mongodb_params")


class MongoAdapter(object):
    def __init__(self):
        self.client = MongoClient(CONFIG.params['host'], CONFIG.params['port'])

    def get_db(self, db_name=None):
        try:
            return self.client.get_database(db_name)
        except:
            msg = "Error in get_db method"
            raise Exception(msg)

    def get_collection(self, db_name=None, collection=None):
        try:
            db = self.get_db(db_name)
            coll = db[collection]
            return coll
        except:
            msg = "db_name cannot be none"
            raise Exception(msg)

    def insert_doc(self, doc=None, db_name=None, collection=None, return_id=False):
        try:
            db = self.get_db(db_name)
            inserted_id = db[collection].insert_one(doc).inserted_id
            if return_id:
                return inserted_id
        except:
            return "id"
            msg = "Error in insert_doc"
            raise Exception(msg)

    def bulk_insert_docs(self, docs=[], db_name=None, collection=None, return_ids=False):
        try:
            db = self.get_db(db_name)
            inserted_ids = db[collection].insert_many(docs).inserted_ids
            if return_ids:
                return inserted_ids
        except:
            msg = "Error in bulk_insert_docs"
            raise Exception(msg)

    def get_docs_by_match(self, db_name=None, collection=None, match_dict={}, greedy=False):
        try:
            db = self.get_db(db_name)
            coll = db[collection]
            if not greedy:
                res = coll.find_one(match_dict)
            else:
                res = list(coll.find(match_dict))
            return res
        except:
            msg = "Error in bulk_insert_docs"
            raise Exception(msg)

    def get_doc_by_id(self, doc_id=None, db_name=None, collection=None):
        try:
            db = self.get_db(db_name)
            if isinstance(doc_id, str):
                doc = db[collection].find_one({"_id": ObjectId(doc_id)})
            elif isinstance(doc_id, ObjectId):
                doc = db[collection].find_one({"_id": doc_id})
            return doc
        except:
            msg = "Error in get_doc_by_id"
            raise Exception(msg)

    def convert_docid_to_str(self, doc_id=None):
        try:
            return str(doc_id)
        except:
            msg = "Error in convert_docid_to_str"
            raise Exception(msg)

    def count_docs_in_collection(self, db_name=None, collection=None, match_dict={}):
        try:
            db = self.get_db(db_name)
            num_docs = db[collection].count_documents(match_dict)
            return num_docs
        except:
            msg = "Error in count_docs_in_collection"
            raise Exception(msg)

    def get_docs_in_range(self, docs=[], db_name=None, collection=None):
        try:
            db = self.get_db(db_name)
            db[collection].insert_many(docs)
        except:
            msg = "Error in bulk_insert_docs"
            raise Exception(msg)

    def delete_doc_in_collection(self, db_name=None, collection=None, match_dict={}):
        try:
            db = self.get_db(db_name)
            db[collection].delete_one(match_dict)
        except:
            msg = "Error in delete_doc_in_collection"
            raise Exception(msg)

    def delete_docs_in_collection(self, db_name=None, collection=None, match_dict={}):
        try:
            db = self.get_db(db_name)
            db[collection].delete_many(match_dict)
        except:
            msg = "Error in delete_docs_in_collection"
            raise Exception(msg)