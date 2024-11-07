from pymongo import MongoClient, collection
from urllib.parse import quote_plus

import secrets  # Assuming your credentials are stored in a secrets module


class MongoDB:
    def __init__(self):
        # Initialize MongoDB client and database connection
        username = quote_plus(secrets.mongodb_username)
        password = quote_plus(secrets.mongodb_password)
        client = MongoClient(f"mongodb://{username}:{password}@{secrets.aws_dns}:{secrets.mongodb_port}")
        self.db = client[secrets.mongodb_name]

    def get_db(self):
        # Return the database object
        return self.db

    def create_collection(self, collection_name: str) -> collection.Collection:
        # Create and return a collection
        return self.db[collection_name]

    def get_collections(self) -> list:
        # List all collection names in the database
        return self.db.list_collection_names()

    def insert_many(self, collection_name: str, documents: list) -> list:
        # Insert multiple documents into a collection
        collection = self.db[collection_name]
        result = collection.insert_many(documents)
        return result.inserted_ids

    def insert_one(self, collection_name: str, document: dict) -> str:
        # Insert a single document into a collection
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return result.inserted_id

    def insert_one_if_not_exists(self, collection_name: str, document: dict, unique_field: str) -> str:
        collection = self.create_collection(collection_name)

        # Define the query to check if a document with the unique field already exists
        query = {unique_field: document[unique_field]}

        # Use upsert=True to insert the document if it doesn't exist
        result = collection.update_one(query, {"$setOnInsert": document}, upsert=True)

        if result.upserted_id is not None:
            return f"Document inserted with ID: {result.upserted_id}"
        else:
            return "Document already exists and was not inserted."

    def find(self, collection_name: str, query: dict) -> list:
        # Find documents matching a query in a collection
        collection = self.db[collection_name]
        return list(collection.find(query))

    def find_all(self, collection_name: str) -> list:
        # Find all documents in a collection
        collection = self.db[collection_name]
        return list(collection.find())

    def update_one(self, collection_name: str, query: dict, update: dict) -> dict:
        # Update a single document that matches a query
        collection = self.db[collection_name]
        result = collection.update_one(query, {'$set': update})
        return result.raw_result

    def update_many(self, collection_name: str, query: dict, update: dict) -> dict:
        # Update multiple documents that match a query
        collection = self.db[collection_name]
        result = collection.update_many(query, {'$set': update})
        return result.raw_result

    def delete_one(self, collection_name: str, query: dict) -> dict:
        # Delete a single document that matches a query
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        return result.raw_result

    def delete_many(self, collection_name: str, query: dict) -> dict:
        # Delete multiple documents that match a query
        collection = self.db[collection_name]
        result = collection.delete_many(query)
        return result.raw_result

    def document_exists(self, collection_name: str, query: dict) -> bool:
        # Check if a document exists in a collection
        collection = self.db[collection_name]
        return collection.find_one(query) is not None

    def close(self):
        # Close the client connection
        self.db.client.close()
