# Job application endpoints
from fastapi import APIRouter, Depends
from app.services.job_service import JobService
from app.dependencies.roles import require_admin

router = APIRouter()

@router.get("/job/{job_id}/applicants")
async def get_applicants(job_id: str, user=Depends(require_admin)):
    return await JobService.get_applications_by_job(job_id)
