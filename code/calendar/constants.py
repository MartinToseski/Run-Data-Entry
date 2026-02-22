"""
Google Calendar API constants and configuration.
"""

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

DEADLINE_KEYWORDS = [
    "deadline",
    "submit",
    "exam",
    "due",
    "assignment",
    "task",
    "homework",
    "report",
    "lab",
    "laboratory",
    "midterm",
    "final",
    "presentation",
    "prepare"
]

CLASS_CALENDAR_NAME = "KTU Classes"
WORK_CALENDAR_NAME = "Meetings / Activities"