from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


# Shared fields
class UserBase(BaseModel):
    email: EmailStr
    username: str


# Public registration (auth/register) → always candidate
class PublicUserCreate(UserBase):
    password: str
    role: Literal["candidate"] = Field(default="candidate", example="candidate")


# Admin registration (admin/register) → default shown as admin
class AdminUserCreate(UserBase):
    password: str
    role: Literal["admin", "interviewer", "candidate"] = Field(default="admin", example="admin")


# Used when allowing full flexibility
class UserCreate(UserBase):
    password: str
    role: str


# Login schema
class UserLogin(BaseModel):
    username: str
    password: str


# Output model
class UserOut(UserBase):
    id: str
    role: str


# Token model
class Token(BaseModel):
    access_token: str
    token_type: str
