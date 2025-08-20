import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.core.config import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'app/utils/service_account.json'  # path to downloaded credentials
CALENDAR_ID = settings.GOOGLE_CALENDAR_ID  # pass from .env

def create_calendar_event(summary, description, start_time, duration, timezone, attendees, location):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    end_time = start_time + datetime.timedelta(minutes=duration)

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': timezone,
        },
        'attendees': [{'email': email} for email in attendees],
        'reminders': {
            'useDefault': True,
        },
    }

    event_result = service.events().insert(calendarId=CALENDAR_ID, body=event, sendUpdates='all').execute()
    return event_result
