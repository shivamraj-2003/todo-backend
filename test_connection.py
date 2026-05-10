import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

async def test_connection():

    uri = "mongodb+srv://sr0047172_db_user:Todo12345@cluster0.p7vaibe.mongodb.net/todo?retryWrites=true&w=majority"

    try:
        client = AsyncIOMotorClient(
            uri,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000
        )

        await client.admin.command("ping")

        print("✅ MongoDB Connected Successfully!")

        db = client["todo"]

        collections = await db.list_collection_names()

        print("Collections:", collections)

    except Exception as e:
        print("❌ Error:", e)

asyncio.run(test_connection())