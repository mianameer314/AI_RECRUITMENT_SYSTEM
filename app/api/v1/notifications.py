"""
Notification API endpoints for email notifications
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional

from app.services.email_service import (
    get_email_service, 
    EmailRequest, 
    NotificationRequest,
    send_email_task
)

router = APIRouter()

class TestEmailRequest(BaseModel):
    recipient: EmailStr
    subject: str = "Test Email from AI Recruitment System"

class AnalysisNotificationRequest(BaseModel):
    recipient_email: EmailStr
    recipient_name: str
    resume_id: str
    analysis_data: Dict[str, Any]
    dashboard_url: Optional[str] = "http://localhost:8000/dashboard"

class InterviewInvitationRequest(BaseModel):
    candidate_email: EmailStr
    candidate_name: str
    job_title: str
    interview_details: Dict[str, Any]
    interviewer_name: str
    company_name: Optional[str] = "Our Company"

class StatusUpdateRequest(BaseModel):
    candidate_email: EmailStr
    candidate_name: str
    job_title: str
    status: str
    status_message: str
    recruiter_name: str
    company_name: Optional[str] = "Our Company"
    next_steps: Optional[List[str]] = None
    feedback: Optional[str] = None

@router.post("/send-email")
async def send_custom_email(request: EmailRequest):
    """
    Send custom email using template
    """
    try:
        task = send_email_task.delay(
            recipients=request.recipients,
            subject=request.subject,
            template_name=request.template_name,
            template_data=request.template_data,
            cc=request.cc,
            bcc=request.bcc
        )
        
        return {
            "message": "Email queued for sending",
            "task_id": task.id,
            "recipients": request.recipients
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-email")
async def send_test_email(request: TestEmailRequest):
    """
    Send test email to verify email configuration
    """
    try:
        template_data = {
            "recipient_name": "Test User",
            "message": "This is a test email to verify the email configuration is working correctly.",
            "timestamp": "2024-01-01 12:00:00"
        }
        
        task = send_email_task.delay(
            recipients=[request.recipient],
            subject=request.subject,
            template_name="base.html",
            template_data=template_data
        )
        
        return {
            "message": "Test email queued for sending",
            "task_id": task.id,
            "recipient": request.recipient
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis-notification")
async def send_analysis_notification(request: AnalysisNotificationRequest):
    """
    Send resume analysis completion notification
    """
    try:
        email_service = get_email_service()
        
        task = email_service.send_analysis_notification(
            recipient_email=request.recipient_email,
            recipient_name=request.recipient_name,
            resume_id=request.resume_id,
            analysis_data=request.analysis_data,
            dashboard_url=request.dashboard_url
        )
        
        return {
            "message": "Analysis notification queued for sending",
            "task_id": task.id,
            "recipient": request.recipient_email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interview-invitation")
async def send_interview_invitation(request: InterviewInvitationRequest):
    """
    Send interview invitation email
    """
    try:
        email_service = get_email_service()
        
        task = email_service.send_interview_invitation(
            candidate_email=request.candidate_email,
            candidate_name=request.candidate_name,
            job_title=request.job_title,
            interview_details=request.interview_details,
            interviewer_name=request.interviewer_name,
            company_name=request.company_name
        )
        
        return {
            "message": "Interview invitation queued for sending",
            "task_id": task.id,
            "recipient": request.candidate_email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/status-update")
async def send_status_update(request: StatusUpdateRequest):
    """
    Send application status update email
    """
    try:
        email_service = get_email_service()
        
        task = email_service.send_status_update(
            candidate_email=request.candidate_email,
            candidate_name=request.candidate_name,
            job_title=request.job_title,
            status=request.status,
            status_message=request.status_message,
            recruiter_name=request.recruiter_name,
            company_name=request.company_name,
            next_steps=request.next_steps,
            feedback=request.feedback
        )
        
        return {
            "message": "Status update queued for sending",
            "task_id": task.id,
            "recipient": request.candidate_email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def list_email_templates():
    """
    List available email templates
    """
    try:
        import os
        template_dir = "app/templates/email"
        
        if os.path.exists(template_dir):
            templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
        else:
            templates = []
        
        return {
            "templates": templates,
            "template_directory": template_dir
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_email_config():
    """
    Get email configuration status (without sensitive data)
    """
    try:
        import os
        
        config_status = {
            "mail_server": os.getenv("MAIL_SERVER", "Not configured"),
            "mail_port": os.getenv("MAIL_PORT", "Not configured"),
            "mail_username_configured": bool(os.getenv("MAIL_USERNAME")),
            "mail_password_configured": bool(os.getenv("MAIL_PASSWORD")),
            "mail_from": os.getenv("MAIL_FROM", "Not configured"),
            "mail_from_name": os.getenv("MAIL_FROM_NAME", "AI Recruitment System"),
            "mail_starttls": os.getenv("MAIL_STARTTLS", "True"),
            "mail_ssl_tls": os.getenv("MAIL_SSL_TLS", "False")
        }
        
        return config_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

