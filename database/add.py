import pandas as pd
from pymongo import MongoClient

# Function to connect to the local MongoDB
def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017/")  # Local MongoDB connection string
    db = client['minorProject']  # Replace with your database name
    return db['movies']  # Replace with your collection name

# Function to upload a DataFrame to MongoDB
def upload_dataframe_to_mongo(df, collection):
    # Iterate through each row in the DataFrame
    for _, row in df.iterrows():
        # Convert the row to a dictionary
        document = row.to_dict()
        # Insert the document into the collection
        collection.insert_one(document)
        print(f"Inserted: {document['tconst']}")

# Example usage
if __name__ == "__main__":
   
    df = pd.read_csv("C:/Users/abhi9/Desktop/mini/final_data_with_poster.csv");
    
    # Connect to MongoDB
    movies_collection = connect_to_mongodb()
    
    # Upload the DataFrame to MongoDB
    upload_dataframe_to_mongo(df, movies_collection)
    
    print("All documents uploaded!")
