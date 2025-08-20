# Authentication logic for login and registration
from fastapi import HTTPException, status
from app.models.user import UserInDB
from app.utils.hashing import hash_password, verify_password
from app.core.jwt import create_access_token
from app.db.mongo import db

class AuthService:
    @staticmethod
    async def register(user_data):
        existing = await db.users.find_one({"username": user_data.username})
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        user_dict = user_data.dict()
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

    #    ✅ Add default role (if not provided)
        user_dict["role"] = user_dict.get("role", "candidate")

        result = await db.users.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        return user_dict

    @staticmethod
    async def authenticate_user(username: str, password: str):
        user = await db.users.find_one({"username": username})
        if not user or not verify_password(password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
