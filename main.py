import os
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

# --- MongoDB Connection ---
MONGO_URI = os.getenv("MONGO_URI")  # env se le raha hai
client = MongoClient(MONGO_URI)
db = client["car_database"]
cars_collection = db["cars"]

app = FastAPI()

# --- Pydantic Model ---
class Car(BaseModel):
    model: str
    year: int
    color: str
    price: float

# --- Helpers for Mongo ObjectId ---
def car_serializer(car) -> dict:
    return {
        "id": str(car["_id"]),
        "model": car["model"],
        "year": car["year"],
        "color": car["color"],
        "price": car["price"]
    }

# --- Routes ---
@app.get("/")
def hello():
    return {"message": "Hello In The Car World"}

@app.post("/cars")
def add_car(car: Car):
    car_dict = car.dict()
    result = cars_collection.insert_one(car_dict)
    return {"message": f"{car.model} added successfully", "id": str(result.inserted_id)}

@app.get("/cars")
def get_cars():
    cars = cars_collection.find()
    return [car_serializer(car) for car in cars]

@app.put("/cars/{car_id}")
def update_car(car_id: str, updated_car: Car):
    result = cars_collection.update_one(
        {"_id": ObjectId(car_id)},
        {"$set": updated_car.dict()}
    )
    if result.modified_count:
        return {"message": "Car updated successfully"}
    return {"message": "Car not found"}

@app.delete("/cars/{car_id}")
def delete_car(car_id: str):
    result = cars_collection.delete_one({"_id": ObjectId(car_id)})
    if result.deleted_count:
        return {"message": "Car deleted successfully"}
    return {"message": "Car not found"}
