# app/api/v1/resumes.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import magic
from bson import ObjectId 

from app.db.mongo import db
from app.dependencies.roles import require_admin
# from app.models import user # ⚠️ Consider removing or fixing if 'app.models.user' is not a module
from app.services.resume_service import parse_resume_task
from app.services.llm_service import get_resume_analysis, trigger_resume_analysis
from app.schemas.user import UserOut
from app.dependencies.auth import get_current_user # 🐛 FIXED: Import get_current_user from app.dependencies.auth

# ⚠️ POTENTIAL CONFLICT: If your main app imports both users.py and resumes.py,
# both might define 'router = APIRouter()'. Consider renaming this one.
# For example: router_resumes = APIRouter()
router = APIRouter() 

UPLOAD_DIR = "app/uploads/resumes"

class AnalysisRequest(BaseModel):
    job_description: Optional[str] = ""
    provider: Optional[str] = "gemini"

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user_data: dict = Depends(get_current_user) # 🐛 FIXED: Consistent parameter naming
):
    # Validate MIME type
    mime = magic.Magic(mime=True)
    file_content_peek = await file.read(1024) # Read a small chunk to determine MIME type
    file_type = mime.from_buffer(file_content_peek)
    await file.seek(0) # Reset file pointer to the beginning

    if file_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Generate unique filename
    filename = f"resume_{uuid.uuid4()}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Trigger parsing task
    parse_resume_task.delay(file_path)

    # Extract resume ID
    resume_id = filename.replace(".pdf", "")

    # Save metadata to MongoDB
    await db.resumes.insert_one({
        "resume_id": resume_id,
        "user_id": current_user_data["id"] # Access 'id' using dictionary key lookup
    })

    return {
        "message": "File uploaded successfully",
        "file_name": filename,
        "resume_id": resume_id
    }

@router.post("/analyze/{resume_id}", status_code=status.HTTP_202_ACCEPTED)
async def analyze_resume(resume_id: str, request: AnalysisRequest, current_admin_user_data: dict = Depends(require_admin)): # 🐛 FIXED: Consistent parameter naming
    try:
        # Pass the admin user ID to the background task
        admin_user_id = current_admin_user_data["id"] # Access 'id' using dictionary key lookup
        
        # Trigger the analysis task, which now also handles the email notification
        task_id = trigger_resume_analysis(
            resume_id=resume_id,
            job_description=request.job_description,
            provider=request.provider,
            admin_user_id=admin_user_id # Pass admin_user_id to the task
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
async def get_analysis(resume_id: str, current_admin_user_data: dict = Depends(require_admin)): # 🐛 FIXED: Consistent parameter naming
    try:
        analysis = get_resume_analysis(resume_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found. Please trigger analysis first.")
        
        return {
            "resume_id": resume_id,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_resumes(current_user_data: dict = Depends(get_current_user)): # 🐛 FIXED: Consistent parameter naming
    try:
        resumes = []

        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if filename.endswith('.pdf'):
                    resume_id = filename.replace('.pdf', '')

                    parsed = os.path.exists(f"app/uploads/json/{resume_id}.json")
                    analyzed = os.path.exists(f"app/uploads/json/{resume_id}_analysis.json")

                    resumes.append({
                        "resume_id": resume_id,
                        "filename": filename,
                        "parsed": parsed,
                        "analyzed": analyzed
                    })

        return {"resumes": resumes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
