# Job-related business logic
from fastapi import HTTPException
from app.db.mongo import db
from bson import ObjectId
from datetime import datetime

from app.schemas.job import JobOut

class JobService:
    @staticmethod
    async def create_job(data, username):
        job = data.dict()
        job["posted_by"] = username
        result = await db.jobs.insert_one(job)
        job["_id"] = str(result.inserted_id)  # ✅ Use alias _id for Pydantic mapping
        return JobOut(**job)


    @staticmethod
    async def list_jobs(keyword=None, location=None, skip=0, limit=10):
        from app.schemas.job import PublicJobOut
        query = {}
        if keyword:
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}}
            ]
        if location:
            query["location"] = {"$regex": location, "$options": "i"}

        jobs_cursor = db.jobs.find(query).skip(skip).limit(limit)
        jobs = []
        async for job in jobs_cursor:
            job["_id"] = str(job["_id"])  # ✅ Convert ObjectId to string
            jobs.append(PublicJobOut(**job))
        return jobs



    @staticmethod
    async def apply_to_job(job_id, user_id, resume_text=None):
        application = {
            "job_id": job_id,
            "user_id": user_id,
            "resume_text": resume_text,
            "created_at": datetime.utcnow()
        }
        result = await db.applications.insert_one(application)
        application["_id"] = str(result.inserted_id)
        return application

    @staticmethod
    async def get_applications_by_job(job_id):
        apps_cursor = db.applications.find({"job_id": job_id})
        apps = []
        async for app in apps_cursor:
            app["_id"] = str(app["_id"])  # Convert ObjectId to string
            apps.append(app)
        return apps
    
    

    @staticmethod
    async def update_job(job_id: str, job_data, username: str):
        result = await db.jobs.update_one(
            {"_id": ObjectId(job_id), "posted_by": username},
            {"$set": job_data.dict(exclude_unset=True)}
        )
        if result.matched_count == 0:
            raise HTTPException(404, detail="Job not found or unauthorized")
        return await db.jobs.find_one({"_id": ObjectId(job_id)})

    @staticmethod
    async def delete_job(job_id: str, username: str):
        result = await db.jobs.delete_one(
            {"_id": ObjectId(job_id), "posted_by": username}
        )
        if result.deleted_count == 0:
            raise HTTPException(404, detail="Job not found or unauthorized")
        return {"detail": "Job deleted"}

