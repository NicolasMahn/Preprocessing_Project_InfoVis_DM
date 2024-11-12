from mongo import DB

mongo = DB("test")

# Insert a document
document = {"name": "Alice", "age": 30}
mongo.insert_one_if_not_exists(document, "name")

# Find a document
query = {"name": "Alice"}
result = mongo.find(query)
print(result)

# Update a document
mongo.update_one(query, {"age": result[0]["age"] + 1})

result = mongo.find(query)
print(result)

# Check if a document exists
exists = mongo.document_exists(query)
print("Document exists:", exists)



# Close the connection
mongo.close()
