# app/api/v1/users.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from app.core.jwt import create_access_token, decode_access_token
from app.db.mongo import db, get_db
from app.dependencies.roles import require_admin
from app.models.user import UserInDB # Keep this import, it might be used elsewhere for model definitions
from app.schemas.user import AdminUserCreate, PublicUserCreate, UserLogin, UserOut
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
router = APIRouter()
auth_service = AuthService()

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: dict = Depends(require_admin)):
    # Assuming require_admin correctly returns a dict from get_current_user
    return current_user

@router.post("/create_user", response_model=UserOut)
async def Only_Admins_CreateUser(user_create_data: AdminUserCreate, current_user_data: dict = Depends(get_current_user)):
    # 🐛 FIXED: Access 'role' using dictionary key lookup
    if current_user_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users with custom roles")

    # Allow roles like 'admin' or 'interviewer'
    # Renamed 'user' to 'user_create_data' to avoid conflict with 'current_user_data' if any.
    return await auth_service.register(user_create_data)

@router.post("/register", response_model=UserOut)
async def candidate_register(user_data: PublicUserCreate):
    new_user = await AuthService.register(user_data, force_role="candidate", allow_custom_role=False)
    # 🐛 FIXED: Return the Pydantic model directly for response_model compliance.
    # FastAPI will automatically serialize it to JSON.
    return new_user

@router.post("/login")
async def login_user(user_in: UserLogin, db_connection=Depends(get_db)): # 🐛 FIXED: Renamed db to db_connection
    # Ensure AuthService.authenticate_user uses the global 'db' or is passed 'db_connection' if needed.
    # Assuming AuthService handles database interaction itself.
    user = await AuthService.authenticate_user(user_in.username, user_in.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user["username"], "role": user.get("role", "candidate")})
    return {"access_token": token, "token_type": "bearer"}
