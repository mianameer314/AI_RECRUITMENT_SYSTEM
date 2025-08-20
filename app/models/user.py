# User schema definition
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserInDB(BaseModel):
    id: Optional[str]
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True