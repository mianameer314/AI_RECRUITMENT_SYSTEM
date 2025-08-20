# Analytics endpoints
from fastapi import APIRouter, Depends
from app.services.dashboard_service import DashboardService
from app.dependencies.roles import require_admin

router = APIRouter()

@router.get("/stats/overview")
async def overview(user=Depends(require_admin)):
    return await DashboardService.get_overview()

@router.get("/stats/jobs-per-location")
async def jobs_per_location(user=Depends(require_admin)):
    return await DashboardService.get_jobs_per_location()

@router.get("/stats/applications-per-job")
async def applications_per_job(user=Depends(require_admin)):
    return await DashboardService.get_applications_per_job()

@router.get("/stats/daily-applications")
async def daily_applications(user=Depends(require_admin)):
    return await DashboardService.get_daily_applications()

@router.get("/stats/most-applied-jobs")
async def most_applied_jobs(user=Depends(require_admin)):
    return await DashboardService.get_most_applied_jobs()

@router.get("/stats/most-active-candidates")
async def most_active_candidates(user=Depends(require_admin)):
    return await DashboardService.get_most_active_candidates()

@router.get("/stats/application-status-breakdown")
async def status_breakdown(user=Depends(require_admin)):
    return await DashboardService.get_applications_status_breakdown()

@router.get("/stats/recent-activity")
async def recent_activity(user=Depends(require_admin)):
    return await DashboardService.get_recent_activity()

@router.get("/total-jobs")
async def total_jobs_public():
    return {"total_jobs": 100}

@router.get("/total-applications")
async def total_applications_public():
    return {"total_applications": 50}

@router.get("/jobs-by-location")
async def jobs_by_location_public():
    return {"location1": 10, "location2": 20}

@router.get("/applications-per-job")
async def applications_per_job_public():
    return [{"job_id": 1, "applications": 5}, {"job_id": 2, "applications": 10}]
