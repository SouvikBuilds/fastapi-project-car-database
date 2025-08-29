import os
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

# --- FastAPI app ---
app = FastAPI()

# --- CORS setup ---
origins = [
    "http://localhost:5173",  # React dev server
    "https://fastapi-project-car-database.onrender.com",  # future frontend
    "https://car-crud-git-main-souvik-chatterjees-projects-308ce5f4.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MongoDB Connection ---
MONGO_URI = os.getenv("MONGO_URI")  # env se le raha hai
client = MongoClient(MONGO_URI)
db = client["car_database"]
cars_collection = db["cars"]

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

# Create / Add Car
@app.post("/cars")
def add_car(car: Car):
    car_dict = car.dict()
    result = cars_collection.insert_one(car_dict)
    new_car = cars_collection.find_one({"_id": result.inserted_id})
    return car_serializer(new_car)  # frontend gets full object

# Read / Get all Cars
@app.get("/cars")
def get_cars():
    cars = cars_collection.find()
    return [car_serializer(car) for car in cars]

# Update Car by ID
@app.put("/cars/{car_id}")
def update_car(car_id: str, updated_car: Car):
    result = cars_collection.update_one(
        {"_id": ObjectId(car_id)},
        {"$set": updated_car.dict()}
    )
    if result.modified_count:
        updated = cars_collection.find_one({"_id": ObjectId(car_id)})
        return car_serializer(updated)  # return updated object
    return {"message": "Car not found"}

# Delete Car by ID
@app.delete("/cars/{car_id}")
def delete_car(car_id: str):
    result = cars_collection.delete_one({"_id": ObjectId(car_id)})
    if result.deleted_count:
        return {"message": "Car deleted successfully"}
    return {"message": "Car not found"}
