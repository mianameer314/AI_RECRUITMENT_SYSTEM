# app/services/email_service.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List, Dict, Any, Optional
import os
from jinja2 import Environment, FileSystemLoader
from app.workers.celery_worker import celery_app
import asyncio


class EmailConfig:
    # ... (no changes needed here) ...
    """Email configuration settings"""
    
    def __init__(self):
        self.MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
        self.MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
        self.MAIL_FROM = os.getenv("MAIL_FROM", self.MAIL_USERNAME)
        self.MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
        self.MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        self.MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "AI Recruitment System")
        self.MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
        self.MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
        
        # Template directory
        self.TEMPLATE_FOLDER = "app/templates/email"
        
        # Ensure template directory exists
        os.makedirs(self.TEMPLATE_FOLDER, exist_ok=True)


class EmailService:
    # ... (the rest of the class is fine, but the methods below are modified) ...
    """Service for sending emails with templates"""
    
    def __init__(self):
        self.config = EmailConfig()
        self._setup_mail_config()
        self._setup_templates()
    
    def _setup_mail_config(self):
        """Setup FastMail configuration"""
        self.conf = ConnectionConfig(
            MAIL_USERNAME=self.config.MAIL_USERNAME,
            MAIL_PASSWORD=self.config.MAIL_PASSWORD,
            MAIL_FROM=self.config.MAIL_FROM,
            MAIL_PORT=self.config.MAIL_PORT,
            MAIL_SERVER=self.config.MAIL_SERVER,
            MAIL_FROM_NAME=self.config.MAIL_FROM_NAME,
            MAIL_STARTTLS=self.config.MAIL_STARTTLS,
            MAIL_SSL_TLS=self.config.MAIL_SSL_TLS,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        
        self.fastmail = FastMail(self.conf)
    
    def _setup_templates(self):
        """Setup Jinja2 template environment"""
        self.template_env = Environment(
            loader=FileSystemLoader(self.config.TEMPLATE_FOLDER)
        )
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default email templates"""
        
        # Base template
        base_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .content {
            background-color: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }
        .button {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
        }
        .score {
            background-color: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .score.high { background-color: #d4edda; }
        .score.medium { background-color: #fff3cd; }
        .score.low { background-color: #f8d7da; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Recruitment System</h1>
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    <div class="footer">
        <p>This is an automated message from the AI Recruitment System.</p>
        <p>Please do not reply to this email.</p>
    </div>
</body>
</html>
        """
        
        # Resume analysis notification template
        analysis_template = """
{% extends "base.html" %}
{% block content %}
<h2>Resume Analysis Complete</h2>

<p>Hello {{ recipient_name }},</p>

<p>The AI analysis for resume <strong>{{ resume_id }}</strong> has been completed.</p>

<div class="score {{ score_class }}">
    <h3>Overall Score: {{ overall_score }}/100</h3>
    <p><strong>Summary:</strong> {{ summary }}</p>
    <p><strong>Analyzed By:</strong> {{ provider|capitalize }}</p>
</div>

<h3>Key Highlights:</h3>
<ul>
    {% for strength in strengths %}
    <li>{{ strength }}</li>
    {% endfor %}
</ul>

{% if job_match_score %}
<div class="score">
    <h3>Job Match Score: {{ job_match_score }}/100</h3>
    <p>{{ fit_assessment }}</p>
</div>
{% endif %}

<p>
    <a href="{{ dashboard_url }}" class="button">View Full Analysis</a>
</p>

<p>Best regards,<br>AI Recruitment Team</p>
{% endblock %}
        """
        
        # Interview invitation template
        interview_template = """
{% extends "base.html" %}
{% block content %}
<h2>Interview Invitation</h2>

<p>Dear {{ candidate_name }},</p>

<p>Congratulations! We are pleased to invite you for an interview for the position of <strong>{{ job_title }}</strong>.</p>

<h3>Interview Details:</h3>
<ul>
    <li><strong>Date:</strong> {{ interview_date }}</li>
    <li><strong>Time:</strong> {{ interview_time }}</li>
    <li><strong>Duration:</strong> {{ duration }} minutes</li>
    <li><strong>Type:</strong> {{ interview_type }}</li>
</ul>

{% if zoom_link %}
<div class="score">
    <h3>Zoom Meeting Details:</h3>
    <p><strong>Meeting ID:</strong> {{ meeting_id }}</p>
    <p><strong>Passcode:</strong> {{ passcode }}</p>
    <p>
        <a href="{{ zoom_link }}" class="button">Join Zoom Meeting</a>
    </p>
</div>
{% endif %}

<h3>What to Expect:</h3>
<ul>
    <li>Technical discussion about your experience</li>
    <li>Questions about the role and company</li>
    <li>Opportunity to ask questions</li>
</ul>

<p>Please confirm your attendance by replying to this email.</p>

<p>We look forward to speaking with you!</p>

<p>Best regards,<br>{{ interviewer_name }}<br>{{ company_name }}</p>
{% endblock %}
        """
        
        # Application status update template
        status_template = """
{% extends "base.html" %}
{% block content %}
<h2>Application Status Update</h2>

<p>Dear {{ candidate_name }},</p>

<p>We wanted to update you on the status of your application for the position of <strong>{{ job_title }}</strong>.</p>

<div class="score">
    <h3>Status: {{ status }}</h3>
    <p>{{ status_message }}</p>
</div>

{% if next_steps %}
<h3>Next Steps:</h3>
<ul>
    {% for step in next_steps %}
    <li>{{ step }}</li>
    {% endfor %}
</ul>
{% endif %}

{% if feedback %}
<h3>Feedback:</h3>
<p>{{ feedback }}</p>
{% endif %}

<p>Thank you for your interest in joining our team.</p>

<p>Best regards,<br>{{ recruiter_name }}<br>{{ company_name }}</p>
{% endblock %}
        """
        
        # Save templates
        templates = {
            "base.html": base_template,
            "analysis_notification.html": analysis_template,
            "interview_invitation.html": interview_template,
            "status_update.html": status_template
        }
        
        for filename, content in templates.items():
            template_path = os.path.join(self.config.TEMPLATE_FOLDER, filename)
            if not os.path.exists(template_path):
                with open(template_path, 'w') as f:
                    f.write(content)
    
    async def send_email(
        self,
        recipients: List[EmailStr],
        subject: str,
        template_name: str,
        template_data: Dict[str, Any],
        cc: Optional[List[EmailStr]] = None,
        bcc: Optional[List[EmailStr]] = None
    ) -> bool:
        """
        Send email using template
        """
        
        try:
            # Render template
            template = self.template_env.get_template(template_name)
            html_content = template.render(**template_data, subject=subject)
            
            # Create message
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_content,
                subtype=MessageType.html,
                cc=cc or [],
                bcc=bcc or []
            )
            
            # Send email
            await self.fastmail.send_message(message)
            
            print(f"✅ Email sent successfully to {recipients}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False
    
    def send_analysis_notification(
        self,
        recipient_email: str,
        recipient_name: str,
        resume_id: str,
        analysis_data: Dict[str, Any],
        dashboard_url: str = "http://localhost:8000/dashboard"
    ):
        """Send resume analysis notification"""
        
        # Determine score class for styling
        overall_score = analysis_data.get('overall_score', 0)
        if overall_score >= 80:
            score_class = "high"
        elif overall_score >= 60:
            score_class = "medium"
        else:
            score_class = "low"
        
        template_data = {
            "recipient_name": recipient_name,
            "resume_id": resume_id,
            "overall_score": overall_score,
            "score_class": score_class,
            "summary": analysis_data.get('summary', 'Analysis completed'),
            "strengths": analysis_data.get('strengths', []),
            "job_match_score": analysis_data.get('job_match_score'),
            "fit_assessment": analysis_data.get('fit_assessment', ''),
            "provider": analysis_data.get('provider', "unknown"),
            "dashboard_url": dashboard_url
        }
        
        return send_email_task.delay(
            recipients=[recipient_email],
            subject=f"Resume Analysis Complete - {resume_id}",
            template_name="analysis_notification.html",
            template_data=template_data
        )
    
    def send_interview_invitation(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        interview_details: Dict[str, Any],
        interviewer_name: str,
        company_name: str = "Our Company"
    ):
        """Send interview invitation"""
        
        template_data = {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "interview_date": interview_details.get('date'),
            "interview_time": interview_details.get('time'),
            "duration": interview_details.get('duration', 60),
            "interview_type": interview_details.get('type', 'Video Interview'),
            "zoom_link": interview_details.get('zoom_link'),
            "meeting_id": interview_details.get('meeting_id'),
            "passcode": interview_details.get('passcode'),
            "interviewer_name": interviewer_name,
            "company_name": company_name
        }
        
        return send_email_task.delay(
            recipients=[candidate_email],
            subject=f"Interview Invitation - {job_title}",
            template_name="interview_invitation.html",
            template_data=template_data
        )
    
    def send_status_update(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        status: str,
        status_message: str,
        recruiter_name: str,
        company_name: str = "Our Company",
        next_steps: Optional[List[str]] = None,
        feedback: Optional[str] = None
    ):
        """Send application status update"""
        
        template_data = {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "status": status,
            "status_message": status_message,
            "next_steps": next_steps or [],
            "feedback": feedback,
            "recruiter_name": recruiter_name,
            "company_name": company_name
        }
        
        return send_email_task.delay(
            recipients=[candidate_email],
            subject=f"Application Status Update - {job_title}",
            template_name="status_update.html",
            template_data=template_data
        )


# Celery tasks for async email sending
@celery_app.task
def send_email_task(
    recipients: List[str],
    subject: str,
    template_name: str,
    template_data: Dict[str, Any],
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
):
    """
    Celery task for sending emails asynchronously
    """
    
    try:
        email_service = EmailService()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            email_service.send_email(
                recipients=recipients,
                subject=subject,
                template_name=template_name,
                template_data=template_data,
                cc=cc,
                bcc=bcc
            )
        )
        
        loop.close()
        
        return {
            "success": result,
            "recipients": recipients,
            "subject": subject
        }
        
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


# Utility functions
def get_email_service():
    """Get email service instance"""
    return EmailService()


# Email validation
class EmailRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    template_name: str
    template_data: Dict[str, Any]
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None


class NotificationRequest(BaseModel):
    recipient_email: EmailStr
    recipient_name: str
    notification_type: str
    data: Dict[str, Any]