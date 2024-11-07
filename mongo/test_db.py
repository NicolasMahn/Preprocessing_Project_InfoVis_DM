from db import MongoDB

mongo = MongoDB()
collection_name = "test"

# Insert a document
document = {"name": "Alice", "age": 30}
mongo.insert_one_if_not_exists(collection_name, document, "name")

# Find a document
query = {"name": "Alice"}
result = mongo.find(collection_name, query)
print(result)

# Update a document
mongo.update_one(collection_name, query, {"age": result[0]["age"] + 1})

result = mongo.find(collection_name, query)
print(result)

# Check if a document exists
exists = mongo.document_exists(collection_name, query)
print("Document exists:", exists)



# Close the connection
mongo.close()
