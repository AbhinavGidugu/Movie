from pymongo import MongoClient

# Function to connect to MongoDB Atlas
def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['minorProject']  # Replace with your database name
    return db['movies']  # Replace with your collection name

# Function to count documents where poster field is not null
def count_documents_with_non_null_posters(movies_collection):
    count = movies_collection.count_documents({'poster_image_base64': {'$ne': None}})
    return count

if __name__ == "__main__":
    # Connect to MongoDB
    movies_collection = connect_to_mongodb()
    
    # Count documents with non-null posters
    count = count_documents_with_non_null_posters(movies_collection)
    
    print(f"Number of documents with non-null poster_image_base64: {count}")
