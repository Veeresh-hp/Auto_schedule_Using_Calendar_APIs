from datetime import datetime, timedelta
from googleapiclient.discovery import build
from utils.auth import authenticate_google_calendar
import dateutil.parser

def get_calendar_service():
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)
    return service

def list_events(n_events=10):
    """Lists the next n upcoming events."""
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=n_events, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    if not events:
        return "No upcoming events found."
    
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(f"{start}: {event['summary']}")
    
    return "\n".join(event_list)

def create_event(summary, start_time, duration_minutes=60, attendees=None):
    """Creates a new event."""
    service = get_calendar_service()
    
    # Parse start_time if it's a string
    if isinstance(start_time, str):
        start_dt = dateutil.parser.parse(start_time)
    else:
        start_dt = start_time
        
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'UTC', # Adjust as needed or make configurable
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'UTC',
        },
    }
    
    if attendees:
        event['attendees'] = [{'email': email.strip()} for email in attendees.split(',')]

    event = service.events().insert(calendarId='primary', body=event).execute()
    return f"Event created: {event.get('htmlLink')}"

def get_free_slots(date_str, duration_minutes=60):
    """Finds free slots on a given date."""
    # This is a simplified implementation. 
    # In a real production app, you'd query freebusy API.
    # For this demo, we'll just list events and let the LLM figure it out 
    # or implement a basic check if requested.
    # Let's implement a basic freebusy check.
    
    service = get_calendar_service()
    
    try:
        target_date = dateutil.parser.parse(date_str)
    except:
        return "Invalid date format."

    time_min = target_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    time_max = target_date.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'
    
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": "UTC",
        "items": [{"id": "primary"}]
    }
    
    events_result = service.freebusy().query(body=body).execute()
    busy_slots = events_result['calendars']['primary']['busy']
    
    return f"Busy slots for {date_str}: {busy_slots}. Please suggest a time outside these slots."

# Add update and delete as needed
