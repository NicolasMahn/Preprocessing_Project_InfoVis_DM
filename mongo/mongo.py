from pymongo import MongoClient, collection
from urllib.parse import quote_plus

import scrt  # Assuming your credentials are stored in a secrets module


class DB:
    def __init__(self, collection_name: str):
        # Initialize MongoDB client and database connection
        username = quote_plus(secrets.mongodb_username)
        password = quote_plus(secrets.mongodb_password)
        client = MongoClient(f"mongodb://{username}:{password}@{secrets.aws_dns}:{secrets.mongodb_port}")

        self.db = client[secrets.mongodb_name]
        self.collection = self.db[collection_name]

    def get_db(self):
        # Return the database object
        return self.db

    def get_collection(self):
        # Return the collection object
        return self.collection

    def change_collection(self, collection_name: str):
        # Change the collection object
        self.collection = self.db[collection_name]

    def get_collections(self) -> list:
        # List all collection names in the database
        return self.db.list_collection_names()

    def insert_many(self, documents: list) -> list:
        # Insert multiple documents into a collection
        result = self.collection.insert_many(documents)
        return result.inserted_ids

    def insert_one(self, document: dict) -> str:
        # Insert a single document into a collection
        result = self.collection.insert_one(document)
        return result.inserted_id

    def insert_one_if_not_exists(self, document: dict, unique_field: str) -> str:

        # Define the query to check if a document with the unique field already exists
        query = {unique_field: str(document[unique_field])}

        # Use upsert=True to insert the document if it doesn't exist
        result = self.collection.update_one(query, {"$setOnInsert": document}, upsert=True)

        if result.upserted_id is not None:
            return result.upserted_id
        else:
            return f"Document with {unique_field}={document[unique_field]} already exists and was not inserted."

    def insert_many_if_not_exists(self, documents: list, unique_field: str) -> list:
        inserted_ids = []
        for document in documents:
            inserted_ids.append(self.insert_one_if_not_exists(document, unique_field))
        return inserted_ids

    def insert_one_replace_if_exists(self, document: dict, unique_field: str) -> str:
        # Define the query to check if a document with the unique field already exists
        query = {unique_field: str(document[unique_field])}

        # Use upsert=True to replace the document if it exists
        result = self.collection.replace_one(query, document, upsert=True)

        if result.upserted_id is not None:
            return result.upserted_id
        else:
            return f"Document with {unique_field}={document[unique_field]} replaced."

    def insert_many_replace_if_exists(self, documents: list, unique_field: str) -> list:
        inserted_ids = []
        for document in documents:
            inserted_ids.append(self.insert_one_replace_if_exists(document, unique_field))
        return inserted_ids

    def find(self, query: dict) -> list:
        # Find documents matching a query in a collection
        return list(self.collection.find(query))

    def find_all(self) -> list:
        # Find all documents in a collection
        return list(self.collection.find())

    def update_one(self, query: dict, update: dict) -> dict:
        # Update a single document that matches a query
        result = self.collection.update_one(query, {'$set': update})
        return result.raw_result

    def update_many(self, query: dict, update: dict) -> dict:
        # Update multiple documents that match a query
        result = self.collection.update_many(query, {'$set': update})
        return result.raw_result

    def delete_one(self, query: dict) -> dict:
        # Delete a single document that matches a query
        result = self.collection.delete_one(query)
        return result.raw_result

    def delete_many(self, query: dict) -> dict:
        # Delete multiple documents that match a query
        result = self.collection.delete_many(query)
        return result.raw_result

    def document_exists(self, query: dict) -> bool:
        # Check if a document exists in a collection
        return self.collection.find_one(query) is not None

    def close(self):
        # Close the client connection
        self.db.client.close()
