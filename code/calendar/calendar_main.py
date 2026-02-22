import datetime
import os.path
from dateutil import parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
deadline_keywords = ["deadline", "submit", "exam", "due", "assignment", "task", "homework", "report", "lab", "laboratory", "midterm", "final", "presentation", "prepare"]
CLASS_CALENDAR = "KTU Classes"
WORK_CALENDAR = "Meetings / Activities"


def is_deadline(event):
    summary = event.get("summary", "").lower()
    return any(keyword in summary for keyword in deadline_keywords)


def get_calendar_id(service, calendar_name):
    calendars = service.calendarList().list().execute()
    for calendar in calendars["items"]:
        if calendar_name == calendar["summary"]:
            return calendar["id"]
    return None


def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service


def get_today_window():
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start.isoformat(), end.isoformat()


def get_next_3_days_window():
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=3)
    return start.isoformat(), end.isoformat()


def get_today_events(service, calendar_id):
    start, end = get_today_window()
    events = (
        service.events()
        .list(calendarId=calendar_id, timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime")
        .execute()
        .get("items", [])
    )
    return events


def process_daily_events(events):
    duration = 0
    before_10am = False
    after_5pm = False

    for event in events:
        if "dateTime" not in event["start"]:
            continue

        start = parser.isoparse(event["start"]["dateTime"])
        end = parser.isoparse(event["end"]["dateTime"])

        duration = round((end - start).total_seconds() / 3600.0, 1)

        if start.hour < 10:
            before_10am = True
        if start.hour > 17:
            after_5pm = True

    return {
        "duration_sum": duration,
        "morning_activity": before_10am,
        "evening_activity": after_5pm
    }


def get_upcoming_deadlines(service, calendar_id):
    start, end = get_next_3_days_window()
    events = (
        service.events()
        .list(calendarId=calendar_id, timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime")
        .execute()
        .get("items", [])
    )
    events = [event for event in events if is_deadline(event)]
    return events


def extract_calendar_stats():
    service = authenticate()

    class_calendar_id = get_calendar_id(service, CLASS_CALENDAR)
    work_calendar_id = get_calendar_id(service, WORK_CALENDAR)

    classes_today = get_today_events(service, class_calendar_id)
    work_today = get_today_events(service, work_calendar_id)

    classes_stats = process_daily_events(classes_today)
    work_stats = process_daily_events(work_today)

    upcoming_deadlines = get_upcoming_deadlines(service, work_calendar_id)

    return {
        "class_hours": classes_stats["duration_sum"],
        "work_hours": work_stats["duration_sum"],
        "before_10am": classes_stats["morning_activity"] or work_stats["morning_activity"],
        "after_5pm": classes_stats["evening_activity"] or work_stats["evening_activity"],
        "upcoming_deadline_next_three_days": len(upcoming_deadlines) > 0
    }


def main():
    try:
        print(extract_calendar_stats())
    except HttpError as e:
        print(e)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(e)