import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("CRITICAL ERROR: MONGO_URI environment variable is not set!")
    # In production, we want to know why it failed
    raise ValueError("MONGO_URI environment variable is not set. Please check your Railway Variables.")

client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)
db = client.get_database("todo")

users_collection = db.get_collection("users")
tasks_collection = db.get_collection("tasks")
