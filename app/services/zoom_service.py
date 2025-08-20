"""
Zoom Integration Service for AI Recruitment System
Handles Zoom API authentication, meeting creation, and management
"""

from pyzoom import ZoomClient
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.workers.celery_worker import celery_app
import requests
from urllib.parse import urlencode
import base64


class ZoomConfig:
    """Zoom API configuration settings"""
    
    def __init__(self):
        # Server-to-Server OAuth credentials
        self.ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID", "")
        self.ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID", "")
        self.ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET", "")
        
        # Alternative: JWT credentials (deprecated but still supported)
        self.ZOOM_API_KEY = os.getenv("ZOOM_API_KEY", "")
        self.ZOOM_API_SECRET = os.getenv("ZOOM_API_SECRET", "")
        
        # Zoom API endpoints
        self.ZOOM_API_BASE_URL = "https://api.zoom.us/v2"
        self.ZOOM_OAUTH_URL = "https://zoom.us/oauth/token"
        
        # Default meeting settings
        self.DEFAULT_TIMEZONE = "UTC"
        self.DEFAULT_DURATION = 60  # minutes


class ZoomService:
    """Service for integrating with Zoom API"""
    
    def __init__(self):
        self.config = ZoomConfig()
        self.access_token = None
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Zoom API authentication"""
        
        # Try Server-to-Server OAuth first (recommended)
        if all([self.config.ZOOM_ACCOUNT_ID, self.config.ZOOM_CLIENT_ID, self.config.ZOOM_CLIENT_SECRET]):
            self._setup_server_to_server_oauth()
        
        # Fallback to JWT (deprecated)
        elif all([self.config.ZOOM_API_KEY, self.config.ZOOM_API_SECRET]):
            self._setup_jwt_auth()
        
        else:
            print("Warning: Zoom credentials not configured. Using mock service.")
            self.auth_method = "mock"
    
    def _setup_server_to_server_oauth(self):
        """Setup Server-to-Server OAuth authentication"""
        try:
            # Get access token
            self.access_token = self._get_access_token()
            self.auth_method = "oauth"
            print("✅ Zoom Server-to-Server OAuth configured")
            
        except Exception as e:
            print(f"❌ Zoom Server-to-Server OAuth setup failed: {e}")
            self.auth_method = "mock"
    
    def _setup_jwt_auth(self):
        """Setup JWT authentication (deprecated)"""
        try:
            self.zoom_client = ZoomClient(
                api_key=self.config.ZOOM_API_KEY,
                api_secret=self.config.ZOOM_API_SECRET
            )
            self.auth_method = "jwt"
            print("✅ Zoom JWT authentication configured")
            
        except Exception as e:
            print(f"❌ Zoom JWT setup failed: {e}")
            self.auth_method = "mock"
    
    def _get_access_token(self) -> str:
        """Get access token for Server-to-Server OAuth"""
        
        # Prepare credentials
        credentials = f"{self.config.ZOOM_CLIENT_ID}:{self.config.ZOOM_CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Request headers
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Request data
        data = {
            "grant_type": "account_credentials",
            "account_id": self.config.ZOOM_ACCOUNT_ID
        }
        
        # Make request
        response = requests.post(
            self.config.ZOOM_OAUTH_URL,
            headers=headers,
            data=urlencode(data)
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"Failed to get access token: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")
    
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request to Zoom"""
        
        if self.auth_method == "mock":
            return self._mock_api_response(method, endpoint, data)
        
        url = f"{self.config.ZOOM_API_BASE_URL}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code in [200, 201, 204]:
            try:
                return response.json()
            except json.JSONDecodeError:
                # Handle cases where response is successful but not JSON (e.g., 204 No Content)
                return {}
        else:
            # Log the full error response for debugging
            print(f"Zoom API error: {response.status_code} - {response.text}")
            raise Exception(f"Zoom API error: {response.status_code} - {response.text}")
    
    def _mock_api_response(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Mock API responses for development/testing"""
        
        if "/meetings" in endpoint and method.upper() == "POST":
            # Mock meeting creation
            return {
                "id": 123456789,
                "host_id": "mock_host_id",
                "topic": data.get("topic", "Mock Interview"),
                "type": 2,
                "start_time": data.get("start_time", "2024-01-01T10:00:00Z"),
                "duration": data.get("duration", 60),
                "timezone": data.get("timezone", "UTC"),
                "password": "123456",
                "join_url": "https://zoom.us/j/123456789?pwd=mock_password",
                "start_url": "https://zoom.us/s/123456789?mock_start_token",
                "settings": {
                    "host_video": True,
                    "participant_video": True,
                    "join_before_host": False,
                    "mute_upon_entry": True,
                    "waiting_room": True
                },
                "success": True
            }
        
        elif "/meetings/" in endpoint and method.upper() == "GET":
            # Mock meeting details
            meeting_id = endpoint.split("/")[-1]
            return {
                "id": int(meeting_id),
                "topic": "Mock Interview",
                "type": 2,
                "status": "waiting",
                "start_time": "2024-01-01T10:00:00Z",
                "duration": 60,
                "join_url": f"https://zoom.us/j/{meeting_id}?pwd=mock_password",
                "password": "123456"
            }
        
        elif "/meetings/" in endpoint and method.upper() == "PATCH":
            # Mock meeting update
            return {"success": True}
        
        elif "/meetings/" in endpoint and method.upper() == "DELETE":
            # Mock meeting deletion
            return {"success": True}
        
        else:
            return {"mock": True, "method": method, "endpoint": endpoint}
    
    def create_meeting(
        self,
        topic: str,
        start_time: datetime,
        duration: int = 60,
        timezone: str = "UTC",
        password: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Zoom meeting
        
        Args:
            topic: Meeting topic/title
            start_time: Meeting start time
            duration: Meeting duration in minutes
            timezone: Meeting timezone
            password: Meeting password (optional)
            settings: Additional meeting settings
            
        Returns:
            Meeting details including join URL and meeting ID
        """
        
        # Default settings
        default_settings = {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "waiting_room": True,
            "use_pmi": False,
            "approval_type": 0,  # Automatically approve
            "audio": "both",  # Both telephony and VoIP
            "auto_recording": "none"
        }
        
        if settings:
            default_settings.update(settings)
        
        # Prepare meeting data
        meeting_data = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration": duration,
            "timezone": timezone,
            "settings": default_settings
        }
        
        if password:
            meeting_data["password"] = password
        
        # Create meeting via API
        try:
            response = self._make_api_request("POST", "/users/me/meetings", meeting_data)
            
            print(f"✅ Zoom meeting created: {response.get('id')}")
            
            return {
                "meeting_id": response.get("id"),
                "topic": response.get("topic"),
                "start_time": response.get("start_time"),
                "duration": response.get("duration"),
                "timezone": response.get("timezone"),
                "join_url": response.get("join_url"),
                "start_url": response.get("start_url"),
                "password": response.get("password"),
                "settings": response.get("settings", {}),
                "status": "created"
            }
            
        except Exception as e:
            print(f"❌ Error creating Zoom meeting: {e}")
            raise e
    
    def get_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Get meeting details"""
        
        try:
            response = self._make_api_request("GET", f"/meetings/{meeting_id}")
            
            return {
                "meeting_id": response.get("id"),
                "topic": response.get("topic"),
                "start_time": response.get("start_time"),
                "duration": response.get("duration"),
                "status": response.get("status"),
                "join_url": response.get("join_url"),
                "password": response.get("password")
            }
            
        except Exception as e:
            print(f"❌ Error getting Zoom meeting: {e}")
            raise e
    
    def update_meeting(
        self,
        meeting_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update meeting details"""
        
        try:
            response = self._make_api_request("PATCH", f"/meetings/{meeting_id}", updates)
            
            print(f"✅ Zoom meeting updated: {meeting_id}")
            
            return {
                "meeting_id": meeting_id,
                "updated": True,
                "changes": updates
            }
            
        except Exception as e:
            print(f"❌ Error updating Zoom meeting: {e}")
            raise e
    
    def delete_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Delete/cancel meeting"""
        
        try:
            self._make_api_request("DELETE", f"/meetings/{meeting_id}")
            
            print(f"✅ Zoom meeting deleted: {meeting_id}")
            
            return {
                "meeting_id": meeting_id,
                "deleted": True
            }
            
        except Exception as e:
            print(f"❌ Error deleting Zoom meeting: {e}")
            raise e
    
    def list_meetings(self, user_id: str = "me") -> List[Dict[str, Any]]:
        """List user's meetings"""
        
        try:
            response = self._make_api_request("GET", f"/users/{user_id}/meetings")
            
            meetings = []
            for meeting in response.get("meetings", []):
                meetings.append({
                    "meeting_id": meeting.get("id"),
                    "topic": meeting.get("topic"),
                    "start_time": meeting.get("start_time"),
                    "duration": meeting.get("duration"),
                    "status": meeting.get("status"),
                    "join_url": meeting.get("join_url")
                })
            
            return meetings
            
        except Exception as e:
            print(f"❌ Error listing Zoom meetings: {e}")
            raise e


# Celery tasks for async Zoom operations
@celery_app.task
def create_interview_meeting_task(
    candidate_name: str,
    interviewer_name: str,
    job_title: str,
    start_time: str,  # ISO format string
    duration: int = 60,
    timezone: str = "UTC"
):
    """
    Celery task for creating interview meetings
    """
    
    try:
        zoom_service = ZoomService()
        
        # Parse start time
        start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        # Create meeting topic
        topic = f"Interview: {candidate_name} - {job_title}"
        
        # Create meeting
        meeting = zoom_service.create_meeting(
            topic=topic,
            start_time=start_datetime,
            duration=duration,
            timezone=timezone,
            settings={
                "waiting_room": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "host_video": True,
                "participant_video": True
            }
        )
        
        # Store meeting details
        meeting_data = {
            "candidate_name": candidate_name,
            "interviewer_name": interviewer_name,
            "job_title": job_title,
            "meeting_details": meeting,
            "created_at": datetime.now().isoformat()
        }
        
        # Save to file (in production, save to database)
        meeting_file = f"app/uploads/json/meeting_{meeting['meeting_id']}.json"
        with open(meeting_file, 'w') as f:
            json.dump(meeting_data, f, indent=2)
        
        print(f"✅ Interview meeting created for {candidate_name}")
        
        return {
            "success": True,
            "meeting_id": meeting["meeting_id"],
            "join_url": meeting["join_url"],
            "password": meeting["password"],
            "topic": meeting["topic"]
        }
        
    except Exception as e:
        error_msg = f"Error creating interview meeting: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


@celery_app.task
def update_meeting_task(meeting_id: str, updates: Dict[str, Any]):
    """Celery task for updating meetings"""
    
    try:
        zoom_service = ZoomService()
        result = zoom_service.update_meeting(meeting_id, updates)
        
        print(f"✅ Meeting {meeting_id} updated")
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "updates": updates
        }
        
    except Exception as e:
        error_msg = f"Error updating meeting {meeting_id}: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


@celery_app.task
def cancel_meeting_task(meeting_id: str):
    """Celery task for canceling meetings"""
    
    try:
        zoom_service = ZoomService()
        result = zoom_service.delete_meeting(meeting_id)
        
        print(f"✅ Meeting {meeting_id} canceled")
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "canceled": True
        }
        
    except Exception as e:
        error_msg = f"Error canceling meeting {meeting_id}: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
    



# Utility functions
def get_zoom_service():
    """Get Zoom service instance"""
    return ZoomService()


def get_meeting_details(meeting_id: str) -> Optional[Dict[str, Any]]:
    """Get stored meeting details"""
    meeting_file = f"app/uploads/json/meeting_{meeting_id}.json"
    
    if os.path.exists(meeting_file):
        with open(meeting_file, 'r') as f:
            return json.load(f)
    
    return None


def schedule_interview(
    candidate_name: str,
    candidate_email: str,
    interviewer_name: str,
    job_title: str,
    start_time: datetime,
    duration: int = 60,
    timezone: str = "UTC"
) -> str:
    """
    Schedule an interview with Zoom meeting creation
    
    Returns:
        Task ID for the meeting creation task
    """
    
    task = create_interview_meeting_task.delay(
        candidate_name=candidate_name,
        interviewer_name=interviewer_name,
        job_title=job_title,
        start_time=start_time.isoformat(),
        duration=duration,
        timezone=timezone
    )
    
    return task.id

