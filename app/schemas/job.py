from pydantic import BaseModel, Field
from typing import List, Optional

class JobCreate(BaseModel):
    title: str
    description: str
    location: Optional[str]
    salary: Optional[str]
    skills: Optional[List[str]] = []
    company: str  # ✅ Add this
    location: str  # ✅ Add this
    tags: List[str]  # ✅ Add this

class JobOut(JobCreate):
    id: str = Field(..., alias="_id") 
    posted_by: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {}
        from_attributes = True

class PublicJobOut(JobCreate):
    id: str = Field(..., alias="_id") 
    posted_by: str

    class Config:
        allow_population_by_field_name = True
        from_attributes = True

class JobApplication(BaseModel):
    job_id: str
    resume_id: str

class JobUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    location: Optional[str]
    salary: Optional[str]
    skills: Optional[List[str]]
    company: Optional[str]  # ✅ Add this
    tags: Optional[List[str]]  # ✅ Add this
    
