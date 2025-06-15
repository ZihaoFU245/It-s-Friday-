from .google_base_client import GoogleBaseClient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone
import base64
import quopri
import email.mime.text
import email.mime.multipart
import email.mime.base
import email.encoders
import mimetypes
import os
from typing import List, Dict, Optional, Union
import json

class GmailClient(GoogleBaseClient):
    """
    Gmail API client for comprehensive email management for a single Google account.

    Features:
        - Send emails (with attachments)
        - Create, update, and manage drafts
        - Fetch and format messages (plain text & HTML)
        - List, search, and filter messages
        - Manage labels and organize emails
        - Mark messages as read/unread
        - Delete and trash messages
        - Sync with Gmail using history API
        - Batch operations for efficiency    Category options: 'PRIMARY', 'PROMOTIONS', 'SOCIAL', 'UPDATES'
    All time filters are in hours (default: 12).
    All methods log errors using the configured logger.
    """
    
    def __init__(self):
        scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.labels"
        ]
        super().__init__(scopes, service_name="Gmail")
        self.service = build("gmail", "v1", credentials=self.creds)
        self.user_id = "me"  # Default to authenticated user

    # ========================================
    # MESSAGE RETRIEVAL AND LISTING METHODS
    # ========================================

    def list_messages(self, max_results: int = 10, query: str = "", label_ids: List[str] = None) -> List[Dict]:
        """
        List message IDs in the user's mailbox with optional query and label filtering.
        
        Args:
            max_results: Maximum number of messages to return (default: 10)
            query: Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')
            label_ids: List of label IDs to filter by
            
        Returns:
            List of message objects with 'id' and 'threadId'
        """
        try:
            params = {
                "userId": self.user_id,
                "maxResults": max_results
            }
            if query:
                params["q"] = query
            if label_ids:
                params["labelIds"] = label_ids
                
            resp = self.service.users().messages().list(**params).execute()
            return resp.get("messages", [])
        except HttpError as error:
            self.logger.error(f"Gmail API error in list_messages: {error}")
            return []

    def get_raw_message(self, msg_id: str, format: str = "full") -> Dict:
        """
        Fetch the raw message by ID.
        
        Args:
            msg_id: The message ID
            format: Message format ('minimal', 'full', 'raw', 'metadata')
            
        Returns:
            Raw message object from Gmail API
        """
        try:
            return self.service.users().messages().get(
                userId=self.user_id, 
                id=msg_id, 
                format=format
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to get message {msg_id}: {error}")
            raise error

    def get_formatted_message(self, raw_msg: Dict) -> Dict:
        """
        Format a raw Gmail API message for display.
        
        Args:
            raw_msg: Raw message object from Gmail API
            
        Returns:
            Dict with id, threadId, snippet, headers, decoded body (text & html), 
            labels, and internal date
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

        # Handle different payload structures
        if payload.get('mimeType') == 'text/plain':
            text_part = payload
            html_part = None
        elif payload.get('mimeType') == 'text/html':
            text_part = None
            html_part = payload
        else:
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

        # Convert internal date to datetime
        internal_date = raw_msg.get('internalDate')
        if internal_date:
            internal_date = datetime.fromtimestamp(int(internal_date) / 1000, tz=timezone.utc)

        return {
            "id": raw_msg.get('id'),
            "threadId": raw_msg.get('threadId'),
            "labelIds": raw_msg.get('labelIds', []),
            "snippet": raw_msg.get('snippet'),
            "historyId": raw_msg.get('historyId'),
            "internalDate": internal_date,
            "sizeEstimate": raw_msg.get('sizeEstimate'),
            "from": header_map.get('from'),
            "to": header_map.get('to'),
            "cc": header_map.get('cc'),
            "bcc": header_map.get('bcc'),
            "subject": header_map.get('subject'),
            "date": header_map.get('date'),
            "content_type": header_map.get('content-type'),
            "message_id": header_map.get('message-id'),
            "in_reply_to": header_map.get('in-reply-to'),
            "references": header_map.get('references'),
            "body": {
                "text": extract_body(text_part),
                "html": extract_body(html_part)
            },
            "attachments": self._extract_attachments(payload)
        }

    def _extract_attachments(self, payload: Dict) -> List[Dict]:
        """Extract attachment information from message payload."""
        attachments = []
        
        def extract_from_parts(parts):
            if not parts:
                return
            for part in parts:
                if part.get('filename'):
                    attachments.append({
                        'filename': part.get('filename'),
                        'mimeType': part.get('mimeType'),
                        'size': part.get('body', {}).get('size', 0),
                        'attachmentId': part.get('body', {}).get('attachmentId')
                    })
                if 'parts' in part:
                    extract_from_parts(part['parts'])
        
        extract_from_parts(payload.get('parts', []))
        return attachments    
    
    def _decode_msg(self, data: str, encoding: str = None) -> str:
        """
        Decode a message body from base64 with robust charset handling.
        
        Args:
            data: Base64 encoded message data
            encoding: Optional encoding hint (e.g., 'quoted-printable')
            
        Returns:
            Decoded message text
        """
        if not data:
            return ""
            
        try:
            # Fix base64 padding if needed
            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            
            # Decode base64
            decoded_bytes = base64.urlsafe_b64decode(data)
            
            # Handle quoted-printable encoding
            if encoding == 'quoted-printable':
                try:
                    decoded_bytes = quopri.decodestring(decoded_bytes)
                except Exception as e:
                    self.logger.warning(f"Failed to decode quoted-printable: {e}")
            
            # Try multiple encoding strategies
            encodings_to_try = ['utf-8', 'utf-8-sig', 'iso-8859-1', 'windows-1252', 'ascii']
            
            for charset in encodings_to_try:
                try:
                    return decoded_bytes.decode(charset)
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Decoding with {charset} failed: {e}")
                    continue
            
            # If all standard encodings fail, try with error handling
            try:
                return decoded_bytes.decode('utf-8', errors='replace')
            except Exception:
                try:
                    return decoded_bytes.decode('latin1', errors='replace')
                except Exception:
                    # Last resort: convert to string representation
                    return f"[Binary content - {len(decoded_bytes)} bytes]"
                    
        except Exception as e:
            self.logger.error(f"Failed to decode message body: {e}")
            return "[Failed to decode message body]"

    def get_attachment(self, msg_id: str, attachment_id: str) -> bytes:
        """
        Download an attachment from a message.
        
        Args:
            msg_id: The message ID
            attachment_id: The attachment ID
            
        Returns:
            Attachment data as bytes
        """
        try:
            attachment = self.service.users().messages().attachments().get(
                userId=self.user_id,
                messageId=msg_id,
                id=attachment_id
            ).execute()
            
            data = attachment['data']
            return base64.urlsafe_b64decode(data)
        except HttpError as error:
            self.logger.error(f"Failed to get attachment {attachment_id}: {error}")
            raise error

    # ========================================
    # EMAIL SENDING METHODS
    # ========================================

    def send_email(self, to: Union[str, List[str]], subject: str, body: str, 
                   cc: Union[str, List[str]] = None, bcc: Union[str, List[str]] = None,
                   attachments: List[str] = None, html_body: str = None) -> Dict:
        """
        Send an email message.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            attachments: List of file paths to attach (optional)
            html_body: HTML body (optional)
            
        Returns:
            Sent message object
        """
        try:
            message = self._create_message(to, subject, body, cc, bcc, attachments, html_body)
            return self.service.users().messages().send(
                userId=self.user_id,
                body=message
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to send email: {error}")
            raise error

    def reply_to_message(self, msg_id: str, body: str, html_body: str = None,
                        reply_all: bool = False, attachments: List[str] = None) -> Dict:
        """
        Reply to an existing message.
        
        Args:
            msg_id: The message ID to reply to
            body: Reply body text
            html_body: Reply HTML body (optional)
            reply_all: Whether to reply to all recipients
            attachments: List of file paths to attach (optional)
            
        Returns:
            Sent reply message object
        """
        try:
            # Get original message to extract headers
            original = self.get_raw_message(msg_id)
            headers = {h['name'].lower(): h['value'] for h in original['payload']['headers']}
            
            # Determine recipients
            to = headers.get('from')
            cc = None
            if reply_all:
                original_to = headers.get('to', '')
                original_cc = headers.get('cc', '')
                cc = f"{original_to},{original_cc}".strip(',')
            
            # Create subject with "Re:" prefix
            original_subject = headers.get('subject', '')
            subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
            
            message = self._create_message(to, subject, body, cc, None, attachments, html_body)
            message['threadId'] = original['threadId']
            
            # Add reference headers
            message_id = headers.get('message-id')
            if message_id:
                references = headers.get('references', '')
                if references:
                    references += f" {message_id}"
                else:
                    references = message_id
                    
                # Add headers to the MIME message
                raw_message = base64.urlsafe_b64decode(message['raw']).decode('utf-8')
                raw_message = raw_message.replace(
                    '\r\n\r\n',
                    f'\r\nIn-Reply-To: {message_id}\r\nReferences: {references}\r\n\r\n',
                    1
                )
                message['raw'] = base64.urlsafe_b64encode(raw_message.encode('utf-8')).decode('utf-8')
            
            return self.service.users().messages().send(
                userId=self.user_id,
                body=message
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to reply to message {msg_id}: {error}")
            raise error

    def _create_message(self, to: Union[str, List[str]], subject: str, body: str,
                       cc: Union[str, List[str]] = None, bcc: Union[str, List[str]] = None,
                       attachments: List[str] = None, html_body: str = None) -> Dict:
        """Create a MIME message object for sending."""
        # Create message container
        if attachments or html_body:
            msg = email.mime.multipart.MIMEMultipart('alternative' if html_body else 'mixed')
        else:
            msg = email.mime.text.MIMEText(body)
            msg['To'] = to if isinstance(to, str) else ', '.join(to)
            msg['Subject'] = subject
            if cc:
                msg['Cc'] = cc if isinstance(cc, str) else ', '.join(cc)
            if bcc:
                msg['Bcc'] = bcc if isinstance(bcc, str) else ', '.join(bcc)
            return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')}

        # Set headers
        msg['To'] = to if isinstance(to, str) else ', '.join(to)
        msg['Subject'] = subject
        if cc:
            msg['Cc'] = cc if isinstance(cc, str) else ', '.join(cc)
        if bcc:
            msg['Bcc'] = bcc if isinstance(bcc, str) else ', '.join(bcc)

        # Add text content
        text_part = email.mime.text.MIMEText(body, 'plain')
        msg.attach(text_part)

        # Add HTML content if provided
        if html_body:
            html_part = email.mime.text.MIMEText(html_body, 'html')
            msg.attach(html_part)

        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                if os.path.isfile(file_path):
                    content_type, _ = mimetypes.guess_type(file_path)
                    if content_type is None:
                        content_type = 'application/octet-stream'
                    
                    main_type, sub_type = content_type.split('/', 1)
                    
                    with open(file_path, 'rb') as fp:
                        attachment = email.mime.base.MIMEBase(main_type, sub_type)
                        attachment.set_payload(fp.read())
                    
                    email.encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(file_path)}"'
                    )
                    msg.attach(attachment)

        return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')}

    # ========================================
    # DRAFT MANAGEMENT METHODS
    # ========================================

    def create_draft(self, to: Union[str, List[str]], subject: str, body: str,
                    cc: Union[str, List[str]] = None, bcc: Union[str, List[str]] = None,
                    attachments: List[str] = None, html_body: str = None) -> Dict:
        """
        Create a draft message.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            attachments: List of file paths to attach (optional)
            html_body: HTML body (optional)
            
        Returns:
            Created draft object
        """
        try:
            message = self._create_message(to, subject, body, cc, bcc, attachments, html_body)
            draft = {'message': message}
            
            return self.service.users().drafts().create(
                userId=self.user_id,
                body=draft
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to create draft: {error}")
            raise error

    def update_draft(self, draft_id: str, to: Union[str, List[str]], subject: str, body: str,
                    cc: Union[str, List[str]] = None, bcc: Union[str, List[str]] = None,
                    attachments: List[str] = None, html_body: str = None) -> Dict:
        """
        Update an existing draft.
        
        Args:
            draft_id: The draft ID to update
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            attachments: List of file paths to attach (optional)
            html_body: HTML body (optional)
            
        Returns:
            Updated draft object
        """
        try:
            message = self._create_message(to, subject, body, cc, bcc, attachments, html_body)
            draft = {'id': draft_id, 'message': message}
            
            return self.service.users().drafts().update(
                userId=self.user_id,
                id=draft_id,
                body=draft
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to update draft {draft_id}: {error}")
            raise error

    def send_draft(self, draft_id: str) -> Dict:
        """
        Send an existing draft.
        
        Args:
            draft_id: The draft ID to send
            
        Returns:
            Sent message object
        """
        try:
            return self.service.users().drafts().send(
                userId=self.user_id,
                body={'id': draft_id}
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to send draft {draft_id}: {error}")
            raise error

    def delete_draft(self, draft_id: str) -> None:
        """
        Delete a draft.
        
        Args:
            draft_id: The draft ID to delete
        """
        try:
            self.service.users().drafts().delete(
                userId=self.user_id,
                id=draft_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to delete draft {draft_id}: {error}")
            raise error

    def list_drafts(self, max_results: int = 10) -> List[Dict]:
        """
        List draft messages.
        
        Args:
            max_results: Maximum number of drafts to return
            
        Returns:
            List of draft objects
        """
        try:
            resp = self.service.users().drafts().list(
                userId=self.user_id,
                maxResults=max_results
            ).execute()
            return resp.get('drafts', [])
        except HttpError as error:
            self.logger.error(f"Failed to list drafts: {error}")
            return []

    def get_draft(self, draft_id: str) -> Dict:
        """
        Get a specific draft by ID.
        
        Args:
            draft_id: The draft ID
            
        Returns:
            Draft object
        """
        try:
            return self.service.users().drafts().get(
                userId=self.user_id,
                id=draft_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to get draft {draft_id}: {error}")
            raise error

    # ========================================
    # MESSAGE MANAGEMENT METHODS
    # ========================================

    def mark_as_read(self, msg_ids: Union[str, List[str]]) -> None:
        """
        Mark message(s) as read by removing the UNREAD label.
        
        Args:
            msg_ids: Message ID(s) to mark as read
        """
        try:
            if isinstance(msg_ids, str):
                msg_ids = [msg_ids]
            
            for msg_id in msg_ids:
                self.service.users().messages().modify(
                    userId=self.user_id,
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to mark messages as read: {error}")
            raise error

    def mark_as_unread(self, msg_ids: Union[str, List[str]]) -> None:
        """
        Mark message(s) as unread by adding the UNREAD label.
        
        Args:
            msg_ids: Message ID(s) to mark as unread
        """
        try:
            if isinstance(msg_ids, str):
                msg_ids = [msg_ids]
            
            for msg_id in msg_ids:
                self.service.users().messages().modify(
                    userId=self.user_id,
                    id=msg_id,
                    body={'addLabelIds': ['UNREAD']}
                ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to mark messages as unread: {error}")
            raise error

    def trash_message(self, msg_id: str) -> Dict:
        """
        Move a message to trash.
        
        Args:
            msg_id: The message ID to trash
            
        Returns:
            Updated message object
        """
        try:
            return self.service.users().messages().trash(
                userId=self.user_id,
                id=msg_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to trash message {msg_id}: {error}")
            raise error

    def untrash_message(self, msg_id: str) -> Dict:
        """
        Remove a message from trash.
        
        Args:
            msg_id: The message ID to untrash
            
        Returns:
            Updated message object
        """
        try:
            return self.service.users().messages().untrash(
                userId=self.user_id,
                id=msg_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to untrash message {msg_id}: {error}")
            raise error

    def delete_message(self, msg_id: str) -> None:
        """
        Permanently delete a message.
        
        Args:
            msg_id: The message ID to delete
        """
        try:
            self.service.users().messages().delete(
                userId=self.user_id,
                id=msg_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to delete message {msg_id}: {error}")
            raise error

    def add_labels(self, msg_id: str, label_ids: List[str]) -> Dict:
        """
        Add labels to a message.
        
        Args:
            msg_id: The message ID
            label_ids: List of label IDs to add
            
        Returns:
            Updated message object
        """
        try:
            return self.service.users().messages().modify(
                userId=self.user_id,
                id=msg_id,
                body={'addLabelIds': label_ids}
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to add labels to message {msg_id}: {error}")
            raise error

    def remove_labels(self, msg_id: str, label_ids: List[str]) -> Dict:
        """
        Remove labels from a message.
        
        Args:
            msg_id: The message ID
            label_ids: List of label IDs to remove
            
        Returns:
            Updated message object
        """
        try:
            return self.service.users().messages().modify(
                userId=self.user_id,
                id=msg_id,
                body={'removeLabelIds': label_ids}
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to remove labels from message {msg_id}: {error}")
            raise error

    # ========================================
    # LABEL MANAGEMENT METHODS
    # ========================================

    def list_labels(self) -> List[Dict]:
        """
        List all labels in the user's mailbox.
        
        Returns:
            List of label objects
        """
        try:
            resp = self.service.users().labels().list(userId=self.user_id).execute()
            return resp.get('labels', [])
        except HttpError as error:
            self.logger.error(f"Failed to list labels: {error}")
            return []

    def create_label(self, name: str, color: Dict = None, visibility: str = 'labelShow') -> Dict:
        """
        Create a new label.
        
        Args:
            name: Label name
            color: Label color settings (optional)
            visibility: Label visibility ('labelHide', 'labelShow', 'labelShowIfUnread')
            
        Returns:
            Created label object
        """
        try:
            label_object = {
                'name': name,
                'labelListVisibility': visibility,
                'messageListVisibility': 'show'
            }
            if color:
                label_object['color'] = color
                
            return self.service.users().labels().create(
                userId=self.user_id,
                body=label_object
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to create label '{name}': {error}")
            raise error

    def update_label(self, label_id: str, name: str = None, color: Dict = None, visibility: str = None) -> Dict:
        """
        Update an existing label.
        
        Args:
            label_id: The label ID to update
            name: New label name (optional)
            color: New label color settings (optional)
            visibility: New label visibility (optional)
            
        Returns:
            Updated label object
        """
        try:
            # Get current label to preserve existing settings
            current_label = self.service.users().labels().get(
                userId=self.user_id,
                id=label_id
            ).execute()
            
            # Update only provided fields
            if name:
                current_label['name'] = name
            if color:
                current_label['color'] = color
            if visibility:
                current_label['labelListVisibility'] = visibility
                
            return self.service.users().labels().update(
                userId=self.user_id,
                id=label_id,
                body=current_label
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to update label {label_id}: {error}")
            raise error

    def delete_label(self, label_id: str) -> None:
        """
        Delete a label.
        
        Args:
            label_id: The label ID to delete
        """
        try:
            self.service.users().labels().delete(
                userId=self.user_id,
                id=label_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to delete label {label_id}: {error}")
            raise error

    # ========================================
    # ADVANCED SEARCH AND FILTERING METHODS
    # ========================================

    def search_messages(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Search for messages using Gmail search syntax.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results to return
            
        Returns:
            List of formatted message objects
        """
        try:
            # Get message IDs matching the query
            msg_ids = self.list_messages(max_results=max_results, query=query)
            
            # Fetch and format each message
            messages = []
            for msg in msg_ids:
                try:
                    raw_msg = self.get_raw_message(msg['id'])
                    formatted_msg = self.get_formatted_message(raw_msg)
                    messages.append(formatted_msg)
                except Exception as e:
                    self.logger.error(f"Failed to fetch message {msg['id']}: {e}")
                    
            return messages
        except HttpError as error:
            self.logger.error(f"Failed to search messages: {error}")
            return []

    def list_unread(self, hours: int = 12, max_results: int = 10, category: str = "PRIMARY") -> List[Dict]:
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
                userId=self.user_id,
                q=query,
                maxResults=max_results
            ).execute()
            return resp.get("messages", []) or []
        except HttpError as error:
            self.logger.error(f"Failed to list unread messages: {error}")
            return []

    def fetch_unread(self, hours: int = 12, max_results: int = 10, category: str = "PRIMARY") -> List[Dict]:
        """
        Fetch unread messages within the last `hours` hours, filtered by Gmail category tab if provided.
        Returns: List[dict] as returned by get_formatted_message
        """
        unread_msgs = self.list_unread(hours=hours, max_results=max_results, category=category)
        results = []
        for msg in unread_msgs:
            msg_id = msg.get('id')
            if not msg_id:
                continue
            try:
                raw_msg = self.get_raw_message(msg_id)
                formatted = self.get_formatted_message(raw_msg)
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
                userId=self.user_id,
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

    # ========================================
    # SYNCHRONIZATION METHODS
    # ========================================

    def get_history(self, start_history_id: str, max_results: int = 100) -> Dict:
        """
        Get message history changes since the specified history ID.
        
        Args:
            start_history_id: History ID to start from
            max_results: Maximum number of history records to return
            
        Returns:
            History response object
        """
        try:
            return self.service.users().history().list(
                userId=self.user_id,
                startHistoryId=start_history_id,
                maxResults=max_results
            ).execute()
        except HttpError as error:
            if error.resp.status == 404:
                self.logger.warning("History ID too old, full sync required")
                return None
            self.logger.error(f"Failed to get history: {error}")
            raise error

    def get_profile(self) -> Dict:
        """
        Get the user's Gmail profile information.
        
        Returns:
            Profile object with email address, messages total, threads total, and history ID
        """
        try:
            return self.service.users().getProfile(userId=self.user_id).execute()
        except HttpError as error:
            self.logger.error(f"Failed to get profile: {error}")
            raise error

    # ========================================
    # THREAD MANAGEMENT METHODS
    # ========================================

    def list_threads(self, max_results: int = 10, query: str = "", label_ids: List[str] = None) -> List[Dict]:
        """
        List conversation threads.
        
        Args:
            max_results: Maximum number of threads to return
            query: Gmail search query
            label_ids: List of label IDs to filter by
            
        Returns:
            List of thread objects
        """
        try:
            params = {
                "userId": self.user_id,
                "maxResults": max_results
            }
            if query:
                params["q"] = query
            if label_ids:
                params["labelIds"] = label_ids
                
            resp = self.service.users().threads().list(**params).execute()
            return resp.get("threads", [])
        except HttpError as error:
            self.logger.error(f"Failed to list threads: {error}")
            return []

    def get_thread(self, thread_id: str) -> Dict:
        """
        Get a conversation thread by ID.
        
        Args:
            thread_id: The thread ID
            
        Returns:
            Thread object with all messages
        """
        try:
            return self.service.users().threads().get(
                userId=self.user_id,
                id=thread_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to get thread {thread_id}: {error}")
            raise error

    def modify_thread(self, thread_id: str, add_label_ids: List[str] = None, 
                     remove_label_ids: List[str] = None) -> Dict:
        """
        Modify labels on a thread.
        
        Args:
            thread_id: The thread ID
            add_label_ids: List of label IDs to add
            remove_label_ids: List of label IDs to remove
            
        Returns:
            Updated thread object
        """
        try:
            body = {}
            if add_label_ids:
                body['addLabelIds'] = add_label_ids
            if remove_label_ids:
                body['removeLabelIds'] = remove_label_ids
                
            return self.service.users().threads().modify(
                userId=self.user_id,
                id=thread_id,
                body=body
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to modify thread {thread_id}: {error}")
            raise error

    def trash_thread(self, thread_id: str) -> Dict:
        """
        Move a thread to trash.
        
        Args:
            thread_id: The thread ID to trash
            
        Returns:
            Updated thread object
        """
        try:
            return self.service.users().threads().trash(
                userId=self.user_id,
                id=thread_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to trash thread {thread_id}: {error}")
            raise error

    def delete_thread(self, thread_id: str) -> None:
        """
        Permanently delete a thread.
        
        Args:
            thread_id: The thread ID to delete
        """
        try:
            self.service.users().threads().delete(
                userId=self.user_id,
                id=thread_id
            ).execute()
        except HttpError as error:
            self.logger.error(f"Failed to delete thread {thread_id}: {error}")
            raise error

    # ========================================
    # LEGACY SEND METHOD (kept for backward compatibility)
    # ========================================

    def send_message(self, user_id: str, msg_body: Dict) -> Dict:
        """Send an email message using the Gmail API (legacy method)."""
        try:
            return self.service.users().messages().send(userId=user_id, body=msg_body).execute()
        except HttpError as error:
            self.logger.error(f"Failed to send message: {error}")
            raise error
