from .google_base_client import GoogleBaseClient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone
import base64
import quopri

class GmailClient(GoogleBaseClient):
    """
    Gmail API client for sending, retrieving, and searching emails for a single Google account.

    Features:
        - Send emails
        - Fetch and format messages (plain text & HTML)
        - List unread messages (with time and category filters)
        - Count unread messages (with time and category filters)

    Category options: 'PRIMARY', 'PROMOTIONS', 'SOCIAL', 'UPDATES'
    All time filters are in hours (default: 12).
    All methods log errors using the configured logger.
    """
    def __init__(self):
        scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send"
        ]
        super().__init__(scopes)
        self.service = build("gmail", "v1", credentials=self.creds)

    def list_messages(self, max_results: int = 10) -> list[dict]:
        """List message IDs in the user's mailbox (default: 10)."""
        try:
            resp = self.service.users().messages().list(userId="me", maxResults=max_results).execute()
            return resp.get("messages", [])
        except HttpError as error:
            self.logger.error(f"Gmail API error in list_messages: {error}")
            return []

    def get_raw_message(self, msg_id: str) -> dict:
        """Fetch the raw message by ID."""
        try:
            return self.service.users().messages().get(userId="me", id=msg_id).execute()
        except HttpError as error:
            self.logger.error(f"Failed to get message {msg_id}: {error}")
            raise error

    def get_formatted_messgae(self, raw_msg: dict) -> dict:
        """
        Format a raw Gmail API message for display.
        Returns a dict with id, threadId, snippet, headers, and decoded body (text & html).
        """
        payload = raw_msg.get('payload', {})
        headers = payload.get('headers', [])
        header_map = {h['name'].lower(): h['value'] for h in headers}

        def find_part(parts, mime_type):
            if not parts:
                return None
            for part in parts:
                if part.get('mimeType') == mime_type:
                    return part
                if 'parts' in part:
                    found = find_part(part['parts'], mime_type)
                    if found:
                        return found
            return None

        text_part = find_part(payload.get('parts', []), 'text/plain')
        html_part = find_part(payload.get('parts', []), 'text/html')

        def extract_body(part):
            if not part:
                return None
            body = part.get('body', {})
            data = body.get('data')
            if not data:
                return None
            encoding = None
            for h in part.get('headers', []):
                if h['name'].lower() == 'content-transfer-encoding':
                    encoding = h['value'].lower()
            return self._decode_msg(data, encoding)

        return {
            "id": raw_msg.get('id'),
            "threadId": raw_msg.get('threadId'),
            "snippet": raw_msg.get('snippet'),
            "from": header_map.get('from'),
            "to": header_map.get('to'),
            "subject": header_map.get('subject'),
            "date": header_map.get('date'),
            "content_type": header_map.get('content-type'),
            "body": {
                "text": extract_body(text_part),
                "html": extract_body(html_part)
            }
        }

    def _decode_msg(self, data: str, encoding: str = None) -> str:
        """Decode a message body from base64 and handle quoted-printable if needed."""
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        try:
            decoded_bytes = base64.urlsafe_b64decode(data)
            if encoding == 'quoted-printable':
                decoded_bytes = quopri.decodestring(decoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to decode message body: {e}")
            try:
                return decoded_bytes.decode('latin1', errors='replace')
            except Exception:
                return "[Unreadable message body]"

    def send_message(self, user_id: str, msg_body: dict) -> dict:
        """Send an email message using the Gmail API."""
        try:
            return self.service.users().messages().send(userId=user_id, body=msg_body).execute()
        except HttpError as error:
            self.logger.error(f"Failed to send message: {error}")
            raise error

    def list_unread(self, hours: int = 12, max_results: int = 10, category: str = "PRIMARY") -> list[dict]:
        """
        List unread message IDs received within the last `hours` hours, optionally filtered by Gmail category tab.
        category: one of 'PRIMARY', 'PROMOTIONS', 'SOCIAL', 'UPDATES' (case-insensitive)
        """
        now = datetime.now(timezone.utc)
        after_time = now - timedelta(hours=hours)
        after_unix = int(after_time.timestamp())
        query = f'is:unread after:{after_unix}'
        cat_map = {
            'PRIMARY': 'category:primary',
            'PROMOTIONS': 'category:promotions',
            'SOCIAL': 'category:social',
            'UPDATES': 'category:updates',
        }
        cat_key = cat_map.get((category or "PRIMARY").upper())
        if cat_key:
            query += f' {cat_key}'
        try:
            resp = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results
            ).execute()
            return resp.get("messages", []) or []
        except HttpError as error:
            self.logger.error(f"Failed to list unread messages: {error}")
            return []

    def fetch_unread(self, hours: int = 12, max_results: int = 10, category: str = "PRIMARY") -> list[dict]:
        """
        Fetch unread messages within the last `hours` hours, filtered by Gmail category tab if provided.
        Returns: List[dict] as returned by get_formatted_messgae
        """
        unread_msgs = self.list_unread(hours=hours, max_results=max_results, category=category)
        results = []
        for msg in unread_msgs:
            msg_id = msg.get('id')
            if not msg_id:
                continue
            try:
                raw_msg = self.get_raw_message(msg_id)
                formatted = self.get_formatted_messgae(raw_msg)
                results.append(formatted)
            except Exception as e:
                self.logger.error(f"Failed to fetch/format message {msg_id}: {e}")
        return results

    def count_unread(self, hours: int = 12, category: str = "PRIMARY") -> int:
        """
        Return the number of unread emails in the given category and time range.
        """
        now = datetime.now(timezone.utc)
        after_time = now - timedelta(hours=hours)
        after_unix = int(after_time.timestamp())
        query = f'is:unread after:{after_unix}'
        cat_map = {
            'PRIMARY': 'category:primary',
            'PROMOTIONS': 'category:promotions',
            'SOCIAL': 'category:social',
            'UPDATES': 'category:updates',
        }
        cat_key = cat_map.get((category or "PRIMARY").upper())
        if cat_key:
            query += f' {cat_key}'
        try:
            resp = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=1
            ).execute()
            if isinstance(resp, dict) and "resultSizeEstimate" in resp:
                return resp["resultSizeEstimate"]
            else:
                self.logger.error(f"Unexpected response in count_unread: {resp}")
                return 0
        except HttpError as error:
            self.logger.error(f"Failed to count unread messages: {error}")
            return 0