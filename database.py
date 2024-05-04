from pymongo import MongoClient, UpdateOne
from config import settings
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from typing import List
import json

client = MongoClient(settings.database_url)
db = client[settings.database_name]

######### MODELS #########

class User(BaseModel):
    email: str
    password: str

class ImageMetadata(BaseModel):
    upload_timestamp: datetime
    processing_time: float  # Processing time in seconds
    file_size: int          # File size in bytes
    file_type: str          # File type, e.g., 'jpg', 'png'
    user_id: str            # User ID as a string

class PlantUsage(BaseModel):
    disease: str
    use: str

class PlantData(BaseModel):
    id: int
    name: str
    img: str
    bname: str 
    splace: List[str]
    benefit: List[str]
    usage: List[PlantUsage]

######### METHODS #########

def get_user_collection():
    return db["users"]

def store_log_in_db(message, timestamp, file_name, function_name, user_id):
    collection = db["error_logs"]
    log_entry = {
        "message": message,
        "timestamp": timestamp,
        "file_name": file_name,
        "function_name": function_name,
        "user_id": user_id
    }
    collection.insert_one(log_entry)

def store_image_metadata(upload_timestamp, processing_time, file_size, file_type, user_id):
    
    collection = db["image_metadata"]
    image_metadata = {
        "upload_timestamp": upload_timestamp,
        "processing_time": processing_time,
        "file_size": file_size,
        "file_type": file_type,
        "user_id": user_id
    }

    result = collection.insert_one(image_metadata)
    return str(result.inserted_id)

def update_processing_time(image_id, processing_time):
   
    collection = db["image_metadata"]
    try:
        processing_microseconds = processing_time.microseconds
        # ObjectId conversion is necessary if the ID is passed as a string
        collection.update_one(
            {"_id": ObjectId(image_id)},
            {"$set": {"processing_time": processing_microseconds}}
        )
        
    except Exception as e:
        print(f"An error occurred: {e}")


def store_plant_data():
    filename = 'herbs_data.json'
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        if not isinstance(data, list):
            data = [data]

        operations = []
        for item in data:
            plant_data = PlantData(**item)
            plant_data_dict = plant_data.dict(by_alias=True)
            # Prepare a bulk upsert operation
            operations.append(UpdateOne(
                {'id': plant_data_dict['id']},  # Filter by unique 'id'
                {'$set': plant_data_dict},      # Set new data or update existing
                upsert=True                     # Insert if doesn't exist
            ))

        if operations:
            result = db.herbs.bulk_write(operations)
            print (f"Batch update completed. Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_count}")
    except FileNotFoundError:
        print(f"The file {filename} does not exist.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {filename}.")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_herb(id):
    herb =  db["herbs"].find_one({"id": id})
    herb['_id'] = str(herb['_id'])
    return herb
