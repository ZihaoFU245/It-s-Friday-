from .google_base_client import GoogleBaseClient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

class GmailClient(GoogleBaseClient):
    def __init__(self):
        scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send"
        ]
        super().__init__(scopes)
        self.service = build("gmail", "v1", credentials=self.creds)

    def list_messages(self, max_results: int = 10):
        try:
            resp = self.service.users().messages().list(userId="me", maxResults=max_results).execute()
            return resp.get("messages", [])
        except HttpError as error:
            error_details = error.error_details[0] if error.error_details else {}
            error_reason = error_details.get('reason', 'unknown')
            
            if error_reason == 'accessNotConfigured':
                logging.error(f"Gmail API is not enabled. Please enable it at: {error_details.get('extendedHelp', 'Google Cloud Console')}")
                raise Exception(f"Gmail API not enabled. Enable it at Google Cloud Console for project {error.resp.get('project_id', 'your project')}")
            else:
                logging.error(f"Gmail API error: {error}")
                raise error

    def get_message(self, msg_id: str):
        try:
            return self.service.users().messages().get(userId="me", id=msg_id).execute()
        except HttpError as error:
            logging.error(f"Failed to get message {msg_id}: {error}")
            raise error

    def send_message(self, user_id: str, msg_body: dict):
        try:
            return self.service.users().messages().send(userId=user_id, body=msg_body).execute()
        except HttpError as error:
            logging.error(f"Failed to send message: {error}")
            raise error