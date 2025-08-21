# Authentication logic for login and registration
from fastapi import HTTPException, status
from app.models.user import UserInDB
from app.utils.hashing import hash_password, verify_password
from app.core.jwt import create_access_token
from app.db.mongo import db

class AuthService:
    @staticmethod
    async def register(user_data, force_role=None, allow_custom_role=True):
        user_dict = user_data.dict()
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

        # Determine role based on args
        if force_role:
            user_dict["role"] = force_role
        else:
            user_dict["role"] = user_dict.get("role", "candidate")

        # You can add logic for allow_custom_role if needed
        if not allow_custom_role:
            user_dict["role"] = "candidate"

        existing = await db.users.find_one({"username": user_dict["username"]})
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        result = await db.users.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        return user_dict


    @staticmethod
    async def authenticate_user(username: str, password: str):
        user = await db.users.find_one({"username": username})
        if not user or not verify_password(password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
