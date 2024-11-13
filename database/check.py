import base64
from pymongo import MongoClient
from PIL import Image
from io import BytesIO

# Function to connect to MongoDB Atlas
def connect_to_mongodb():
    # Replace with your MongoDB Atlas connection string
    client = MongoClient("mongodb://localhost:27017/")
    db = client['minorProject']  # Replace with your database name
    return db['movies']  # Replace with your collection name

# Function to retrieve and decode the Base64 image
def retrieve_image(movie_id, movies_collection):
    # Find the movie document by its ID
    movie = movies_collection.find_one({'tconst': movie_id})
    
    if movie and 'poster_image_base64' in movie and movie['poster_image_base64']:
        # Decode the Base64 image string
        image_data = base64.b64decode(movie['poster_image_base64'])
        # Open the image using PIL for testing/display
        image = Image.open(BytesIO(image_data))
        image.show()  # This will display the image
        print(f"Retrieved and displayed image for movie ID: {movie_id}")
    else:
        print(f"No image found for movie ID: {movie_id}")

if __name__ == "__main__":
    # Connect to MongoDB
    movies_collection = connect_to_mongodb()
    
    # Test by retrieving an image for a specific movie ID
    movie_id = 'tt1582519'  # Replace with an actual movie ID from your database
    retrieve_image(movie_id, movies_collection)
