from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ResumeBase(BaseModel):
    user_id: Optional[str]
    filename: str
    text: str

class ResumeOut(ResumeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
