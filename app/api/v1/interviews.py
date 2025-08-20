"""
Interview API endpoints for Zoom integration and interview scheduling
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.workers.celery_worker import celery_app
from app.services.google_calender_service import create_calendar_event
import os
from datetime import timedelta

from app.services.zoom_service import (
    get_zoom_service,
    schedule_interview,
    get_meeting_details,
    create_interview_meeting_task,
    update_meeting_task,
    cancel_meeting_task
)
from app.services.email_service import get_email_service

router = APIRouter()

class InterviewScheduleRequest(BaseModel):
    candidate_name: str
    candidate_email: EmailStr
    interviewer_name: str
    interviewer_email: Optional[EmailStr] = None
    job_title: str
    start_time: datetime
    end_time: datetime
    duration: Optional[int] = 60
    timezone: Optional[str] = "UTC"
    send_email: Optional[bool] = True
    location: str = "Online (Zoom)"

class MeetingCreateRequest(BaseModel):
    topic: str
    start_time: datetime
    duration: Optional[int] = 60
    timezone: Optional[str] = "UTC"
    password: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class MeetingUpdateRequest(BaseModel):
    topic: Optional[str] = None
    start_time: Optional[datetime] = None
    duration: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None

@router.post("/schedule")
async def schedule_interview_endpoint(request: InterviewScheduleRequest):
    try:
        task_id = schedule_interview(
            candidate_name=request.candidate_name,
            candidate_email=request.candidate_email,
            interviewer_name=request.interviewer_name,
            job_title=request.job_title,
            start_time=request.start_time,
            duration=request.duration,
            timezone=request.timezone
        )

        response = {
            "message": "Interview scheduled successfully",
            "task_id": task_id,
            "candidate_name": request.candidate_name,
            "job_title": request.job_title,
            "start_time": request.start_time.isoformat(),
            "duration": request.duration
        }

        # --- Wait for the Zoom meeting to be created ---
        meeting_result = celery_app.AsyncResult(task_id).get(timeout=30)

        zoom_link = meeting_result["join_url"] if meeting_result.get("success") else "N/A"
        meeting_id = meeting_result.get("meeting_id", "N/A")
        passcode = meeting_result.get("password", "N/A")

        # --- Add Google Calendar Event ---
        try:
            calendar_id = request.calendar_id or os.getenv("GOOGLE_CALENDAR_ID")
            end_time = request.start_time + timedelta(minutes=request.duration)

            calendar_link = create_calendar_event(
                summary=f"Interview: {request.candidate_name} for {request.job_title}",
                description=f"Interview with {request.candidate_name}. Zoom link: {zoom_link}",
                start_time=request.start_time,
                end_time=end_time,
                attendees=[request.candidate_email, request.interviewer_email] if request.interviewer_email else [request.candidate_email],
                calendar_id=calendar_id
            )
            response["calendar_link"] = calendar_link
        except Exception as cal_err:
            response["calendar_error"] = str(cal_err)

        # --- Send Email ---
        if request.send_email:
            try:
                email_service = get_email_service()
                interview_details = {
                    "date": request.start_time.strftime("%Y-%m-%d"),
                    "time": request.start_time.strftime("%H:%M"),
                    "duration": request.duration,
                    "type": "Video Interview",
                    "zoom_link": zoom_link,
                    "meeting_id": meeting_id,
                    "passcode": passcode
                }

                email_task = email_service.send_interview_invitation(
                    candidate_email=request.candidate_email,
                    candidate_name=request.candidate_name,
                    job_title=request.job_title,
                    interview_details=interview_details,
                    interviewer_name=request.interviewer_name
                )

                response["email_task_id"] = email_task.id
                response["email_sent"] = True
            except Exception as e:
                response["email_error"] = str(e)
                response["email_sent"] = False

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/meetings/{meeting_id}")
async def update_meeting(meeting_id: str, request: MeetingUpdateRequest):
    """
    Update meeting details
    """
    try:
        # Prepare updates
        updates = {}
        
        if request.topic:
            updates["topic"] = request.topic
        
        if request.start_time:
            updates["start_time"] = request.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        if request.duration:
            updates["duration"] = request.duration
        
        if request.settings:
            updates["settings"] = request.settings
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        # Update meeting
        task = update_meeting_task.delay(meeting_id, updates)
        
        return {
            "message": "Meeting update queued",
            "task_id": task.id,
            "meeting_id": meeting_id,
            "updates": updates
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/meetings/{meeting_id}")
async def cancel_meeting(meeting_id: str):
    """
    Cancel/delete meeting
    """
    try:
        task = cancel_meeting_task.delay(meeting_id)
        
        return {
            "message": "Meeting cancellation queued",
            "task_id": task.id,
            "meeting_id": meeting_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meetings")
async def list_meetings():
    """
    List all meetings
    """
    try:
        zoom_service = get_zoom_service()
        meetings = zoom_service.list_meetings()
        
        return {
            "meetings": meetings,
            "count": len(meetings)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_zoom_config():
    """
    Get Zoom configuration status (without sensitive data)
    """
    try:
        import os
        
        config_status = {
            "account_id_configured": bool(os.getenv("ZOOM_ACCOUNT_ID")),
            "client_id_configured": bool(os.getenv("ZOOM_CLIENT_ID")),
            "client_secret_configured": bool(os.getenv("ZOOM_CLIENT_SECRET")),
            "api_key_configured": bool(os.getenv("ZOOM_API_KEY")),
            "api_secret_configured": bool(os.getenv("ZOOM_API_SECRET")),
            "auth_method": "Server-to-Server OAuth" if all([
                os.getenv("ZOOM_ACCOUNT_ID"),
                os.getenv("ZOOM_CLIENT_ID"),
                os.getenv("ZOOM_CLIENT_SECRET")
            ]) else "JWT" if all([
                os.getenv("ZOOM_API_KEY"),
                os.getenv("ZOOM_API_SECRET")
            ]) else "Mock"
        }
        
        return config_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-meeting")
async def create_test_meeting():
    """
    Create a test meeting to verify Zoom integration
    """
    try:
        from datetime import datetime, timedelta
        
        # Create test meeting for 1 hour from now
        start_time = datetime.now() + timedelta(hours=1)
        
        zoom_service = get_zoom_service()
        meeting = zoom_service.create_meeting(
            topic="Test Meeting - AI Recruitment System",
            start_time=start_time,
            duration=30,
            timezone="UTC",
            settings={
                "waiting_room": True,
                "join_before_host": False,
                "mute_upon_entry": True
            }
        )
        
        return {
            "message": "Test meeting created successfully",
            "meeting": meeting,
            "note": "This is a test meeting to verify Zoom integration"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stored-meetings")
async def list_stored_meetings():
    """
    List all stored meeting details from local files
    """
    try:
        import os
        import json
        
        meetings = []
        upload_dir = "app/uploads/json"
        
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename.startswith("meeting_") and filename.endswith(".json"):
                    meeting_id = filename.replace("meeting_", "").replace(".json", "")
                    
                    try:
                        with open(os.path.join(upload_dir, filename), 'r') as f:
                            meeting_data = json.load(f)
                            
                        meetings.append({
                            "meeting_id": meeting_id,
                            "candidate_name": meeting_data.get("candidate_name"),
                            "job_title": meeting_data.get("job_title"),
                            "interviewer_name": meeting_data.get("interviewer_name"),
                            "created_at": meeting_data.get("created_at"),
                            "meeting_details": meeting_data.get("meeting_details", {})
                        })
                        
                    except Exception as e:
                        print(f"Error reading meeting file {filename}: {e}")
        
        return {
            "stored_meetings": meetings,
            "count": len(meetings)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))