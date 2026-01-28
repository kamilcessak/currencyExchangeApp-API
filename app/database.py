import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.user import User

async def init_db():
    mongo_url = os.environ.get("MONGODB_URL")

    if not mongo_url:
        raise ValueError("MONGODB_URL is empty")

    client = AsyncIOMotorClient(mongo_url)
    db = client.get_default_database()

    await init_beanie(database=db, document_models=[User])

    print(f"Connected to database: {db.name}")