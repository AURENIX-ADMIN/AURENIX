import os
import logging
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from temporalio import activity

# Configuration for Google Workspace
# Scopes needed for Fenix
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

def get_gworkspace_service(service_name: str, version: str, subject: Optional[str] = None):
    """
    Returns a Google Workspace service using a Service Account with Domain-Wide Delegation.
    """
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        logging.warning(f"GOOGLE_APPLICATION_CREDENTIALS not found or invalid at: {creds_path}")
        return None

    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=SCOPES)
        
        if subject:
            # Domain-Wide Delegation: impersonate the user
            creds = creds.with_subject(subject)
            
        return build(service_name, version, credentials=creds)
    except Exception as e:
        logging.error(f"Failed to initialize Google service {service_name}: {e}")
        return None

@activity.defn
async def list_emails(query: str, limit: int = 10, user_email: Optional[str] = None) -> List[dict]:
    activity.logger.info(f"Searching Gmail for: {query} (User: {user_email})")
    
    service = get_gworkspace_service('gmail', 'v1', subject=user_email)
    if not service:
        # Fallback for demo if no credentials
        return [{"id": "mock", "subject": "[DEMO] GOOGLE_APPLICATION_CREDENTIALS MISSING", "from": "fenix@aurenix.ai"}]

    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=limit).execute()
        messages = results.get('messages', [])
        
        email_data = []
        for msg in messages:
            m = service.users().messages().get(userId='me', id=msg['id'], format='minimal').execute()
            headers = m.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
            
            email_data.append({
                "id": m['id'],
                "subject": subject,
                "snippet": m.get('snippet', ''),
                "from": sender
            })
        return email_data
    except Exception as e:
        activity.logger.error(f"Gmail API Error: {e}")
        return [{"error": str(e)}]

@activity.defn
async def list_calendar_events(user_email: Optional[str] = None, limit: int = 5) -> List[dict]:
    activity.logger.info(f"Listing Calendar events (User: {user_email})")
    
    service = get_gworkspace_service('calendar', 'v3', subject=user_email)
    if not service:
        return [{"error": "Credentials missing"}]

    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        results = service.events().list(calendarId='primary', timeMin=now, 
                                      maxResults=limit, singleEvents=True,
                                      orderBy='startTime').execute()
        events = results.get('items', [])
        
        event_data = []
        for event in events:
            event_data.append({
                "id": event['id'],
                "summary": event.get('summary', 'No Title'),
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "link": event.get('htmlLink')
            })
        return event_data
    except Exception as e:
        activity.logger.error(f"Calendar List API Error: {e}")
        return [{"error": str(e)}]

@activity.defn
async def create_calendar_event(summary: str, start_time: str, end_time: str, attendees: List[str], user_email: Optional[str] = None) -> str:
    activity.logger.info(f"Creating Calendar event: {summary} (User: {user_email})")
    
    service = get_gworkspace_service('calendar', 'v3', subject=user_email)
    if not service:
        return "ERROR: Credentials missing"

    event = {
        'summary': summary,
        'start': {'dateTime': start_time},
        'end': {'dateTime': end_time},
        'attendees': [{'email': email} for email in attendees],
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event.get('htmlLink', 'event_created_successfully')
    except Exception as e:
        activity.logger.error(f"Calendar API Error: {e}")
        return f"ERROR: {e}"
