# Job CRUD routes
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.v1.users import get_current_user
from app.dependencies.roles import require_admin, require_candidate
from app.schemas.job import JobCreate, JobOut, JobApplication, JobUpdate, PublicJobOut
from app.services.job_service import JobService
import os
import json


router = APIRouter()

@router.post("/seed", summary="Seed sample jobs (admin only)")
async def seed_jobs(user=Depends(require_admin)):
    from app.db.mongo import db  # Ensure db is imported
    await db.jobs.delete_many({})  # 🧹 Wipe old jobs

    jobs = [
        {
            "title": "Backend Developer",
            "description": "Work with FastAPI and MongoDB.",
            "skills": ["FastAPI", "MongoDB", "Python"],
            "salary": "100k",
            "company": "TechCorp",
            "location": "Remote",
            "tags": ["backend", "python"],
            "posted_by": user["username"]
        },
        {
            "title": "Data Scientist",
            "description": "Build data pipelines and ML models.",
            "skills": ["Python", "Pandas", "Scikit-learn"],
            "salary": "120k",
            "company": "DataWorks",
            "location": "New York",
            "tags": ["data", "ml", "python"],
            "posted_by": user["username"]
        }
    ]

    await db.jobs.insert_many(jobs)
    return {"detail": f"{len(jobs)} jobs seeded successfully"}



@router.post("/", response_model=JobOut)
async def post_job(job: JobCreate, user=Depends(require_admin)):
    if user["role"] != "admin":
        raise HTTPException(403, detail="Only admins can post jobs")
    return await JobService.create_job(job, user["username"])

@router.get("/", response_model=list[PublicJobOut])
async def list_jobs(
    keyword: str = Query(None, description="Search by job title or description"),
    location: str = Query(None, description="Filter by job location"),
    limit: int = Query(10, ge=1),
    skip: int = Query(0, ge=0)
):
    jobs = await JobService.list_jobs(keyword, location, skip, limit)
    return jobs


@router.post("/apply")
async def apply_job(app: JobApplication, user=Depends(require_candidate)):
    # Step 1: Locate resume JSON
    resume_path = f"app/uploads/json/{app.resume_id}.json"
    
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Resume not found")

    # Step 2: Read resume text
    with open(resume_path, "r") as f:
        resume_data = json.load(f)

    resume_text = resume_data.get("text", "")

    # Step 3: Apply with resume text
    return await JobService.apply_to_job(app.job_id, user["username"], resume_text)

@router.get("/{job_id}/applications")
async def get_applicants(job_id: str, user=Depends(require_admin)):
    return await JobService.get_applications_by_job(job_id)

@router.put("/{job_id}", response_model=JobOut)
async def update_job(job_id: str, job: JobUpdate, user=Depends(require_admin)):
    return await JobService.update_job(job_id, job, user["username"])

@router.delete("/{job_id}")
async def delete_job(job_id: str, user=Depends(require_admin)):
    return await JobService.delete_job(job_id, user["username"])
