from googleapiclient.discovery import build
from .google_base_client import GoogleBaseClient
import datetime


class CalendarClient(GoogleBaseClient):
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/calendar"]
        super().__init__(scopes)
        self.service = build("calendar", "v3", credentials=self.creds)

    def list_events(self, max_results: int = 10, time_min: datetime.datetime | None = None):
        now = (time_min or datetime.datetime.utcnow()).isoformat() + "Z"
        resp = self.service.events().list(
            calendarId="primary", timeMin=now,
            maxResults=max_results, singleEvents=True, orderBy="startTime"
        ).execute()
        return resp.get("items", [])

    def create_event(self, summary: str, start: str, end: str, timezone: str = "UTC"):
        event = {
            "summary": summary,
            "start": {"dateTime": start, "timeZone": timezone},
            "end": {"dateTime": end, "timeZone": timezone}
        }
        return self.service.events().insert(calendarId="primary", body=event).execute()