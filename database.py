import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "").strip()

if not MONGO_URI:
    print("CRITICAL ERROR: MONGO_URI environment variable is not set!")
    raise ValueError("MONGO_URI environment variable is not set. Please check your Railway Variables.")

print(f"Connecting to MongoDB with URI starting with: {MONGO_URI[:20]}...")

client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

# Debug: Verify we are using the async client
print(f"Database client type: {type(client)}")

db = client.get_database("todo")

users_collection = db.get_collection("users")
tasks_collection = db.get_collection("tasks")
