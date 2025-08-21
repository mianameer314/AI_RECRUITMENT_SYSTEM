# app/api/v1/resumes.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import magic
from datetime import datetime

from app.db.mongo import db
from app.dependencies.roles import require_admin
from app.services.resume_service import parse_resume_task
from app.services.llm_service import get_resume_analysis, trigger_resume_analysis
from app.dependencies.auth import get_current_user

router = APIRouter()

UPLOAD_DIR = "app/uploads/resumes"


class AnalysisRequest(BaseModel):
    job_description: Optional[str] = ""
    provider: Optional[str] = "gemini"


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user_data: dict = Depends(get_current_user)
):
    # Validate MIME type
    mime = magic.Magic(mime=True)
    file_content_peek = await file.read(1024)
    file_type = mime.from_buffer(file_content_peek)
    await file.seek(0)

    if file_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Generate unique filename
    resume_id = f"resume_{uuid.uuid4()}"
    filename = f"{resume_id}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Save metadata to MongoDB
    await db.resumes.insert_one({
        "resume_id": resume_id,
        "user_id": current_user_data["id"],
        "filename": filename,
        "status": "uploaded",
        "created_at": datetime.utcnow()
    })

    # Trigger async parsing task
    parse_resume_task.delay(file_path)

    return {
        "message": "File uploaded successfully",
        "file_name": filename,
        "resume_id": resume_id
    }


@router.post("/analyze/{resume_id}", status_code=status.HTTP_202_ACCEPTED)
async def analyze_resume(
    resume_id: str,
    request: AnalysisRequest,
    current_admin_user_data: dict = Depends(require_admin)
):
    try:
        admin_user_id = current_admin_user_data["id"]

        # Update resume status in DB
        await db.resumes.update_one(
            {"resume_id": resume_id},
            {"$set": {
                "status": "analysis_started",
                "job_description": request.job_description,
                "provider": request.provider,
                "analysis_requested_by": admin_user_id,
                "analysis_requested_at": datetime.utcnow()
            }}
        )

        # Trigger background task
        task_id = trigger_resume_analysis(
            resume_id=resume_id,
            job_description=request.job_description,
            provider=request.provider,
            admin_user_id=admin_user_id
        )

        return {
            "message": "Analysis has been started and you will be notified via email upon completion.",
            "task_id": task_id,
            "resume_id": resume_id,
            "provider": request.provider,
            "email_sent": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{resume_id}")
async def get_analysis(resume_id: str, current_admin_user_data: dict = Depends(require_admin)):
    try:
        analysis = get_resume_analysis(resume_id)

        if not analysis:
            # Check DB if metadata exists
            resume_meta = await db.resumes.find_one({"resume_id": resume_id})
            if not resume_meta:
                raise HTTPException(status_code=404, detail="Resume not found in database.")
            raise HTTPException(status_code=404, detail="Analysis not found. Please trigger analysis first.")

        return {
            "resume_id": resume_id,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_resumes(current_user_data: dict = Depends(get_current_user)):
    try:
        query = {}
        if current_user_data.get("role") != "admin":
            query["user_id"] = current_user_data["id"]

        resumes_cursor = db.resumes.find(query)
        resumes = []
        async for r in resumes_cursor:
            resumes.append({
                "resume_id": r.get("resume_id") or str(r.get("_id")),
                "filename": r.get("filename", ""),
                "status": r.get("status", "unknown"),
                "provider": r.get("provider", None),
                "job_description": r.get("job_description", None),
                "created_at": r.get("created_at")
            })

        return {"resumes": resumes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
