# app/models/resumes.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ResumeBase(BaseModel):
    user_id: str = Field(..., description="ID of the user who uploaded the resume")
    filename: str = Field(..., description="Original file name of the resume")
    text: Optional[str] = Field(None, description="Extracted text from the resume")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ResumeCreate(ResumeBase):
    pass

class ResumeDB(ResumeBase):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
