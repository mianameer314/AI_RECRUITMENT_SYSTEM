# Job post schema definition
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class JobModel(BaseModel):
    title: str
    description: str
    skills: List[str]
    salary: Optional[str]
    posted_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationModel(BaseModel):
    job_id: str
    user_id: str
    resume_text: Optional[str] = None
    applied_at: datetime = Field(default_factory=datetime.utcnow)
