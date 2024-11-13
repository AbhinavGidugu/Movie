from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['minorProject']
movies_collection = db['movies']

result = movies_collection.update_one(
    {"originalTitle": "RRR (Rise Roar Revolt)"},  
    {"$set": {"description": "A fearless warrior on a perilous mission comes face to face with a steely cop serving British forces in this epic saga set in pre-independent India."}}  
)

if result.modified_count > 0:
    print("Plot updated successfully!")
else:
    print("No document was updated.")