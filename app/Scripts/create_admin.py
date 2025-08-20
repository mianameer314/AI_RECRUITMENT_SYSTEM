import asyncio
from passlib.context import CryptContext
from bson import ObjectId
from app.db.mongo import get_db  # Uses your existing db connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_initial_admin():
    db = await get_db()
    users_collection = db["users"]

    # Check if admin already exists
    existing_admin = await users_collection.find_one({"role": "admin"})
    if existing_admin:
        print("⚠️ Admin already exists:", existing_admin["username"])
        return

    admin_user = {
        "_id": str(ObjectId()),
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin"
    }

    await users_collection.insert_one(admin_user)
    print("✅ Admin user created successfully!")
