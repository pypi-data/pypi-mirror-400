from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings

client: AsyncMongoClient | None = None
db = None


async def init_db():
    global client, db
    client = AsyncMongoClient(settings.DATABASE_URI)
    db = client[settings.DB_NAME]
    await init_beanie(database=db, document_models=[])


async def close_db():
    global client
    if client:
        await client.close()
