"""
Comprehensive test suite for Gmail Client functionality.

This test suite covers all major features of the Gmail client including:
- Message retrieval and formatting
- Email sending with attachments
- Draft management
- Label management
- Message operations (mark read/unread, trash, delete)
- Search functionality
- Thread management
- Synchronization features

Note: These tests require actual Gmail API credentials and will interact with a real Gmail account.
For production use, consider using mock objects or a test Gmail account.
"""

import unittest
import tempfile
import os
import time
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
import sys
import json
import base64

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.modules.google_clients.gmail_client import GmailClient
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the Gmail client module is available and dependencies are installed")
    sys.exit(1)


class TestGmailClient(unittest.TestCase):
    """Test suite for Gmail Client functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that will be used across multiple tests."""
        # Create a mock Gmail client for testing
        cls.client = None
        cls.mock_service = Mock()
        cls.test_files_created = []
        
    @classmethod
    def tearDownClass(cls):
        """Clean up any test files created during testing."""
        for file_path in cls.test_files_created:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to clean up test file {file_path}: {e}")
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock Gmail client without calling the real initialization
        self.client = GmailClient.__new__(GmailClient)  # Create instance without calling __init__
        
        # Manually set up the required attributes
        self.client.service = self.mock_service
        self.client.user_id = "me"
        self.client.logger = Mock()
        self.client.creds = Mock()  # Mock credentials

    def tearDown(self):
        """Clean up after each test method."""
        # Reset all mock call counts to avoid interference between tests
        self.mock_service.reset_mock()

    def create_test_file(self, content="Test file content", suffix=".txt"):
        """Create a temporary test file and return its path."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        self.test_files_created.append(temp_file.name)
        return temp_file.name

    def create_mock_message(self, msg_id="test123", from_email="test@example.com", 
                           subject="Test Subject", body_text="Test body"):
        """Create a mock Gmail message object for testing."""
        return {
            'id': msg_id,
            'threadId': f'thread_{msg_id}',
            'labelIds': ['INBOX', 'UNREAD'],
            'snippet': body_text[:50],
            'historyId': '12345',
            'internalDate': str(int(datetime.now(timezone.utc).timestamp() * 1000)),
            'sizeEstimate': 1234,
            'payload': {
                'headers': [
                    {'name': 'From', 'value': from_email},
                    {'name': 'To', 'value': 'recipient@example.com'},
                    {'name': 'Subject', 'value': subject},
                    {'name': 'Date', 'value': 'Mon, 15 Jun 2025 10:00:00 +0000'},
                    {'name': 'Message-ID', 'value': f'<{msg_id}@example.com>'}
                ],
                'mimeType': 'text/plain',
                'body': {
                    'data': self.encode_base64(body_text)
                }
            }
        }

    def encode_base64(self, text):
        """Helper to encode text as base64 URL-safe."""
        return base64.urlsafe_b64encode(text.encode('utf-8')).decode('utf-8')

    # ========================================
    # MESSAGE RETRIEVAL TESTS
    # ========================================

    def test_list_messages_basic(self):
        """Test basic message listing functionality."""
        # Mock the API response
        mock_response = {
            'messages': [
                {'id': 'msg1', 'threadId': 'thread1'},
                {'id': 'msg2', 'threadId': 'thread2'}
            ]
        }
        self.mock_service.users().messages().list().execute.return_value = mock_response
        
        # Test the method
        messages = self.client.list_messages(max_results=2)
        
        # Assertions
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['id'], 'msg1')
        self.assertEqual(messages[1]['id'], 'msg2')
          # Verify API was called correctly
        self.mock_service.users().messages().list.assert_called_with(
            userId='me', maxResults=2
        )

    def test_list_messages_with_query(self):
        """Test message listing with search query."""
        mock_response = {'messages': [{'id': 'msg1', 'threadId': 'thread1'}]}
        self.mock_service.users().messages().list().execute.return_value = mock_response
        
        messages = self.client.list_messages(query="is:unread", max_results=5)
        
        # Verify the query parameter was passed
        call_args = self.mock_service.users().messages().list.call_args[1]
        self.assertIn('q', call_args)
        self.assertEqual(call_args['q'], "is:unread")

    def test_get_raw_message(self):
        """Test retrieving a raw message by ID."""
        mock_message = self.create_mock_message()
        self.mock_service.users().messages().get().execute.return_value = mock_message
        result = self.client.get_raw_message("test123")
        
        self.assertEqual(result['id'], 'test123')
        self.mock_service.users().messages().get.assert_called_with(
            userId='me', id='test123', format='full'
        )

    def test_get_formatted_message(self):
        """Test message formatting functionality."""
        mock_message = self.create_mock_message()
        
        formatted = self.client.get_formatted_message(mock_message)
        
        # Check that all expected fields are present
        expected_fields = ['id', 'threadId', 'from', 'to', 'subject', 'body', 'attachments']
        for field in expected_fields:
            self.assertIn(field, formatted)
        
        # Check specific values
        self.assertEqual(formatted['id'], 'test123')
        self.assertEqual(formatted['from'], 'test@example.com')
        self.assertEqual(formatted['subject'], 'Test Subject')
        self.assertIsInstance(formatted['body'], dict)
        self.assertIn('text', formatted['body'])

    def test_decode_message_body(self):
        """Test message body decoding."""
        test_text = "Hello, this is a test message!"
        encoded = self.encode_base64(test_text)
        
        decoded = self.client._decode_msg(encoded)
        
        self.assertEqual(decoded, test_text)

    def test_extract_attachments(self):
        """Test attachment extraction from message payload."""
        payload_with_attachment = {
            'parts': [
                {
                    'filename': 'test.pdf',
                    'mimeType': 'application/pdf',
                    'body': {
                        'size': 1024,
                        'attachmentId': 'att123'
                    }
                }
            ]
        }
        
        attachments = self.client._extract_attachments(payload_with_attachment)
        
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]['filename'], 'test.pdf')
        self.assertEqual(attachments[0]['mimeType'], 'application/pdf')

    # ========================================
    # EMAIL SENDING TESTS
    # ========================================

    def test_send_email_basic(self):
        """Test basic email sending functionality."""
        mock_response = {'id': 'sent123', 'threadId': 'thread123'}
        self.mock_service.users().messages().send().execute.return_value = mock_response
        result = self.client.send_email(
            to="recipient@example.com",
            subject="Test Subject",
            body="Test message body"
        )
        
        self.assertEqual(result['id'], 'sent123')
        # Verify the API was called with the correct structure
        call_args = self.mock_service.users().messages().send.call_args
        self.assertEqual(call_args[1]['userId'], 'me')
        self.assertIn('body', call_args[1])
        self.assertIn('raw', call_args[1]['body'])

    def test_send_email_with_attachments(self):
        """Test sending email with file attachments."""
        # Create test attachment file
        test_file = self.create_test_file("Test attachment content", ".txt")
        
        mock_response = {'id': 'sent123', 'threadId': 'thread123'}
        self.mock_service.users().messages().send().execute.return_value = mock_response
        
        result = self.client.send_email(
            to="recipient@example.com",
            subject="Test with Attachment",
            body="Message with attachment",
            attachments=[test_file]
        )
        
        self.assertEqual(result['id'], 'sent123')

    def test_send_email_with_html(self):
        """Test sending email with HTML body."""
        mock_response = {'id': 'sent123', 'threadId': 'thread123'}
        self.mock_service.users().messages().send().execute.return_value = mock_response
        
        result = self.client.send_email(
            to="recipient@example.com",
            subject="HTML Test",
            body="Plain text body",
            html_body="<h1>HTML Body</h1><p>This is HTML content</p>"
        )
        
        self.assertEqual(result['id'], 'sent123')

    def test_reply_to_message(self):
        """Test replying to an existing message."""        # Mock the get_raw_message method directly to avoid deep mock chain issues
        original_message = {
            'id': 'test123',
            'threadId': 'thread_test123',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'To', 'value': 'recipient@example.com'},
                    {'name': 'Subject', 'value': 'Original Subject'},
                    {'name': 'Message-ID', 'value': '<original@example.com>'}
                ]
            }
        }
        
        # Patch the get_raw_message method directly
        with patch.object(self.client, 'get_raw_message', return_value=original_message):
            # Mock send response
            mock_response = {'id': 'reply123', 'threadId': 'thread_test123'}
            self.mock_service.users().messages().send().execute.return_value = mock_response
            
            result = self.client.reply_to_message(
                msg_id="test123",
                body="This is my reply"
            )
            
            self.assertEqual(result['id'], 'reply123')

    # ========================================
    # DRAFT MANAGEMENT TESTS
    # ========================================

    def test_create_draft(self):
        """Test creating a draft message."""
        mock_response = {'id': 'draft123', 'message': {'id': 'msg123'}}
        self.mock_service.users().drafts().create().execute.return_value = mock_response
        
        result = self.client.create_draft(
            to="recipient@example.com",
            subject="Draft Subject",
            body="Draft body"
        )
        self.assertEqual(result['id'], 'draft123')
        # Verify the API was called with correct parameters
        call_args = self.mock_service.users().drafts().create.call_args
        self.assertEqual(call_args[1]['userId'], 'me')
        self.assertIn('body', call_args[1])
        self.assertIn('message', call_args[1]['body'])

    def test_update_draft(self):
        """Test updating an existing draft."""
        mock_response = {'id': 'draft123', 'message': {'id': 'msg123'}}
        self.mock_service.users().drafts().update().execute.return_value = mock_response
        
        result = self.client.update_draft(
            draft_id="draft123",
            to="recipient@example.com",
            subject="Updated Subject",
            body="Updated body"
        )
        
        self.assertEqual(result['id'], 'draft123')
        # Verify the API was called with correct parameters
        self.mock_service.users().drafts().update.assert_called_with(
            userId='me', id='draft123', body=unittest.mock.ANY
        )

    def test_send_draft(self):
        """Test sending an existing draft."""
        mock_response = {'id': 'sent123', 'threadId': 'thread123'}
        self.mock_service.users().drafts().send().execute.return_value = mock_response
        
        result = self.client.send_draft("draft123")
        
        self.assertEqual(result['id'], 'sent123')
        # Verify the API was called correctly
        self.mock_service.users().drafts().send.assert_called_with(
            userId='me', body={'id': 'draft123'}
        )

    def test_delete_draft(self):
        """Test deleting a draft."""
        self.mock_service.users().drafts().delete().execute.return_value = {}
        
        # Should not raise an exception
        self.client.delete_draft("draft123")
        
        # Verify the API was called correctly
        self.mock_service.users().drafts().delete.assert_called_with(
            userId='me', id='draft123'
        )

    def test_list_drafts(self):
        """Test listing draft messages."""
        mock_response = {
            'drafts': [
                {'id': 'draft1', 'message': {'id': 'msg1'}},
                {'id': 'draft2', 'message': {'id': 'msg2'}}
            ]
        }
        self.mock_service.users().drafts().list().execute.return_value = mock_response
        
        drafts = self.client.list_drafts()
        
        self.assertEqual(len(drafts), 2)
        self.assertEqual(drafts[0]['id'], 'draft1')

    # ========================================
    # MESSAGE MANAGEMENT TESTS
    # ========================================

    def test_mark_as_read(self):
        """Test marking messages as read."""
        self.mock_service.users().messages().modify().execute.return_value = {}
        
        self.client.mark_as_read("msg123")
        
        # Verify the modify call was made with correct parameters
        call_args = self.mock_service.users().messages().modify.call_args[1]
        self.assertIn('removeLabelIds', call_args['body'])
        self.assertIn('UNREAD', call_args['body']['removeLabelIds'])

    def test_mark_as_unread(self):
        """Test marking messages as unread."""
        self.mock_service.users().messages().modify().execute.return_value = {}
        
        self.client.mark_as_unread("msg123")
        
        # Verify the modify call was made with correct parameters
        call_args = self.mock_service.users().messages().modify.call_args[1]
        self.assertIn('addLabelIds', call_args['body'])
        self.assertIn('UNREAD', call_args['body']['addLabelIds'])

    def test_trash_message(self):
        """Test moving a message to trash."""
        mock_response = {'id': 'msg123', 'labelIds': ['TRASH']}
        self.mock_service.users().messages().trash().execute.return_value = mock_response
        
        result = self.client.trash_message("msg123")
        
        self.assertEqual(result['id'], 'msg123')
        # Verify the API was called correctly
        self.mock_service.users().messages().trash.assert_called_with(
            userId='me', id='msg123'
        )

    def test_delete_message(self):
        """Test permanently deleting a message."""
        self.mock_service.users().messages().delete().execute.return_value = {}
        
        # Should not raise an exception
        self.client.delete_message("msg123")
        
        # Verify the API was called correctly
        self.mock_service.users().messages().delete.assert_called_with(
            userId='me', id='msg123'
        )

    def test_add_labels(self):
        """Test adding labels to a message."""
        mock_response = {'id': 'msg123', 'labelIds': ['INBOX', 'IMPORTANT']}
        self.mock_service.users().messages().modify().execute.return_value = mock_response
        
        result = self.client.add_labels("msg123", ["IMPORTANT"])
        
        self.assertEqual(result['id'], 'msg123')
        
        # Verify the modify call was made with correct parameters
        call_args = self.mock_service.users().messages().modify.call_args[1]
        self.assertIn('addLabelIds', call_args['body'])
        self.assertIn('IMPORTANT', call_args['body']['addLabelIds'])

    # ========================================
    # LABEL MANAGEMENT TESTS
    # ========================================

    def test_list_labels(self):
        """Test listing all labels."""
        mock_response = {
            'labels': [
                {'id': 'INBOX', 'name': 'INBOX', 'type': 'system'},
                {'id': 'label1', 'name': 'Custom Label', 'type': 'user'}
            ]
        }
        self.mock_service.users().labels().list().execute.return_value = mock_response
        
        labels = self.client.list_labels()
        
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0]['name'], 'INBOX')
        self.assertEqual(labels[1]['name'], 'Custom Label')

    def test_create_label(self):
        """Test creating a new label."""
        mock_response = {'id': 'label123', 'name': 'New Label'}
        self.mock_service.users().labels().create().execute.return_value = mock_response
        
        result = self.client.create_label("New Label")
        
        self.assertEqual(result['name'], 'New Label')
        # Verify the API was called correctly
        self.mock_service.users().labels().create.assert_called_with(
            userId='me', body={'name': 'New Label', 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        )

    def test_update_label(self):
        """Test updating an existing label."""
        # Mock getting current label
        current_label = {'id': 'label123', 'name': 'Old Name', 'labelListVisibility': 'labelShow'}
        self.mock_service.users().labels().get().execute.return_value = current_label
        
        # Mock update response
        updated_label = {'id': 'label123', 'name': 'New Name', 'labelListVisibility': 'labelShow'}
        self.mock_service.users().labels().update().execute.return_value = updated_label
        
        result = self.client.update_label("label123", name="New Name")
        
        self.assertEqual(result['name'], 'New Name')

    def test_delete_label(self):
        """Test deleting a label."""
        self.mock_service.users().labels().delete().execute.return_value = {}
        
        # Should not raise an exception
        self.client.delete_label("label123")
        
        # Verify the API was called correctly
        self.mock_service.users().labels().delete.assert_called_with(
            userId='me', id='label123'
        )

    # ========================================
    # SEARCH AND FILTERING TESTS
    # ========================================

    def test_search_messages(self):
        """Test searching for messages with a query."""
        # Mock list response
        mock_list_response = {
            'messages': [
                {'id': 'msg1', 'threadId': 'thread1'},
                {'id': 'msg2', 'threadId': 'thread2'}
            ]
        }
        self.mock_service.users().messages().list().execute.return_value = mock_list_response
        
        # Mock individual message responses
        mock_msg1 = self.create_mock_message("msg1", "sender1@example.com", "Subject 1")
        mock_msg2 = self.create_mock_message("msg2", "sender2@example.com", "Subject 2")
        self.mock_service.users().messages().get().execute.side_effect = [mock_msg1, mock_msg2]
        
        results = self.client.search_messages("from:sender1@example.com")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], 'msg1')
        self.assertEqual(results[1]['id'], 'msg2')

    def test_fetch_unread(self):
        """Test fetching unread messages."""
        # Mock list response
        mock_list_response = {
            'messages': [{'id': 'unread1', 'threadId': 'thread1'}]
        }
        self.mock_service.users().messages().list().execute.return_value = mock_list_response
        
        # Mock message response
        mock_message = self.create_mock_message("unread1")
        self.mock_service.users().messages().get().execute.return_value = mock_message
        
        results = self.client.fetch_unread(hours=24, category="PRIMARY")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 'unread1')

    def test_count_unread(self):
        """Test counting unread messages."""
        mock_response = {'resultSizeEstimate': 5}
        self.mock_service.users().messages().list().execute.return_value = mock_response
        
        count = self.client.count_unread(hours=12, category="PRIMARY")
        
        self.assertEqual(count, 5)

    # ========================================
    # SYNCHRONIZATION TESTS
    # ========================================

    def test_get_history(self):
        """Test getting message history."""
        mock_response = {
            'history': [
                {'id': '12345', 'messages': [{'id': 'msg1'}]},
                {'id': '12346', 'messages': [{'id': 'msg2'}]}
            ]
        }
        self.mock_service.users().history().list().execute.return_value = mock_response
        
        result = self.client.get_history("12340")
        
        self.assertIn('history', result)
        self.assertEqual(len(result['history']), 2)

    def test_get_profile(self):
        """Test getting user profile."""
        mock_response = {
            'emailAddress': 'user@example.com',
            'messagesTotal': 1000,
            'threadsTotal': 500,
            'historyId': '12345'
        }
        self.mock_service.users().getProfile().execute.return_value = mock_response
        
        profile = self.client.get_profile()
        
        self.assertEqual(profile['emailAddress'], 'user@example.com')
        self.assertEqual(profile['messagesTotal'], 1000)

    # ========================================
    # THREAD MANAGEMENT TESTS
    # ========================================

    def test_list_threads(self):
        """Test listing conversation threads."""
        mock_response = {
            'threads': [
                {'id': 'thread1', 'snippet': 'First conversation'},
                {'id': 'thread2', 'snippet': 'Second conversation'}
            ]
        }
        self.mock_service.users().threads().list().execute.return_value = mock_response
        
        threads = self.client.list_threads(max_results=2)
        
        self.assertEqual(len(threads), 2)
        self.assertEqual(threads[0]['id'], 'thread1')

    def test_get_thread(self):
        """Test getting a specific thread."""
        mock_response = {
            'id': 'thread123',
            'messages': [
                self.create_mock_message("msg1"),
                self.create_mock_message("msg2")
            ]
        }
        self.mock_service.users().threads().get().execute.return_value = mock_response
        
        thread = self.client.get_thread("thread123")
        
        self.assertEqual(thread['id'], 'thread123')
        self.assertEqual(len(thread['messages']), 2)

    def test_trash_thread(self):
        """Test moving a thread to trash."""
        mock_response = {'id': 'thread123', 'labelIds': ['TRASH']}
        self.mock_service.users().threads().trash().execute.return_value = mock_response
        
        result = self.client.trash_thread("thread123")
        
        self.assertEqual(result['id'], 'thread123')

    # ========================================
    # ERROR HANDLING TESTS
    # ========================================

    def test_http_error_handling(self):
        """Test proper handling of HTTP errors."""
        # Mock an HTTP error
        error_response = Mock()
        error_response.status = 404
        http_error = HttpError(error_response, b'Not found')
        
        self.mock_service.users().messages().get().execute.side_effect = http_error
        
        with self.assertRaises(HttpError):
            self.client.get_raw_message("nonexistent")

    def test_history_404_handling(self):
        """Test handling of 404 errors in history (indicating full sync needed)."""
        error_response = Mock()
        error_response.status = 404
        http_error = HttpError(error_response, b'History ID too old')
        
        self.mock_service.users().history().list().execute.side_effect = http_error
        
        result = self.client.get_history("old_history_id")
        
        # Should return None for 404 errors (indicating full sync needed)
        self.assertIsNone(result)

    # ========================================
    # INTEGRATION-STYLE TESTS
    # ========================================

    def test_email_workflow(self):
        """Test a complete email workflow: create draft, update, send."""
        # Mock create draft
        mock_draft = {'id': 'draft123', 'message': {'id': 'msg123'}}
        self.mock_service.users().drafts().create().execute.return_value = mock_draft
        
        # Mock update draft
        updated_draft = {'id': 'draft123', 'message': {'id': 'msg123'}}
        self.mock_service.users().drafts().update().execute.return_value = updated_draft
        
        # Mock send draft
        sent_message = {'id': 'sent123', 'threadId': 'thread123'}
        self.mock_service.users().drafts().send().execute.return_value = sent_message
        
        # Execute workflow
        draft = self.client.create_draft("recipient@example.com", "Test", "Body")
        self.assertEqual(draft['id'], 'draft123')
        
        updated = self.client.update_draft("draft123", "recipient@example.com", "Updated Test", "Updated Body")
        self.assertEqual(updated['id'], 'draft123')
        
        sent = self.client.send_draft("draft123")
        self.assertEqual(sent['id'], 'sent123')


class TestGmailClientIntegration(unittest.TestCase):
    """
    Integration tests that require actual Gmail API access.
    These tests will send real emails and fetch real data for verification.
    """
    
    TEST_EMAIL = "shengwxnw@gmail.com"
    VERIFICATION_LOG_PATH = "testing/need_verify/README.MD"
    
    @classmethod
    def setUpClass(cls):
        """Set up the real Gmail client for integration testing."""
        try:
            cls.client = GmailClient()
            cls.test_results = []
            cls.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n🔧 Integration test session started at {cls.start_time}")
            print(f"📧 Test emails will be sent to: {cls.TEST_EMAIL}")
        except Exception as e:
            print(f"❌ Failed to initialize Gmail client: {e}")
            raise unittest.SkipTest("Gmail authentication failed")

    @classmethod
    def tearDownClass(cls):
        """Clean up and write verification log."""
        if hasattr(cls, 'test_results') and cls.test_results:
            cls._write_verification_log()

    @classmethod
    def _write_verification_log(cls):
        """Write test results to verification log for human review."""
        os.makedirs(os.path.dirname(cls.VERIFICATION_LOG_PATH), exist_ok=True)
        
        log_content = f"""# Gmail Client Integration Test Results
## Test Session: {cls.start_time}
## Test Target Email: {cls.TEST_EMAIL}

### 🧪 Test Results Summary
Total Tests: {len(cls.test_results)}
Passed: {sum(1 for r in cls.test_results if r['status'] == 'PASS')}
Failed: {sum(1 for r in cls.test_results if r['status'] == 'FAIL')}

### 📋 Detailed Results

"""
        
        for i, result in enumerate(cls.test_results, 1):
            status_emoji = "✅" if result['status'] == 'PASS' else "❌"
            log_content += f"""#### Test {i}: {result['test_name']} {status_emoji}
- **Status**: {result['status']}
- **Description**: {result['description']}
- **Timestamp**: {result['timestamp']}
"""
            
            if result.get('email_id'):
                log_content += f"- **Email ID**: `{result['email_id']}`\n"
            if result.get('details'):
                log_content += f"- **Details**: {result['details']}\n"
            if result.get('verification_needed'):
                log_content += f"- **⚠️ Verification Needed**: {result['verification_needed']}\n"
                
            log_content += "\n"

        log_content += f"""
### 🔍 Manual Verification Checklist
Please verify the following in your email inbox ({cls.TEST_EMAIL}):

1. **Email Delivery**: Check if test emails were received
2. **Content Accuracy**: Verify email subjects and bodies match test data
3. **Attachments**: Confirm any attachments were properly delivered
4. **Threading**: Check if reply emails are properly threaded
5. **Labels**: Verify if any labels were applied correctly

### 📊 Performance Metrics
- Test session duration: {(datetime.now() - datetime.strptime(cls.start_time, "%Y-%m-%d %H:%M:%S")).total_seconds():.2f} seconds
- Average email send time: {cls._calculate_avg_send_time():.2f} seconds

---
*Generated by Gmail Client Integration Test Suite*
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        with open(cls.VERIFICATION_LOG_PATH, 'w', encoding='utf-8') as f:
            f.write(log_content)
            
        print(f"\n📝 Verification log written to: {cls.VERIFICATION_LOG_PATH}")

    @classmethod
    def _calculate_avg_send_time(cls):
        """Calculate average email send time from test results."""
        send_times = [r.get('send_time', 0) for r in cls.test_results if r.get('send_time')]
        return sum(send_times) / len(send_times) if send_times else 0

    def _log_test_result(self, test_name: str, status: str, description: str, **kwargs):
        """Log a test result for verification."""
        result = {
            'test_name': test_name,
            'status': status,
            'description': description,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **kwargs
        }
        self.__class__.test_results.append(result)

    def test_01_authentication_and_profile(self):
        """Test real Gmail authentication and profile retrieval."""
        try:
            profile = self.client.get_profile()
            
            self.assertIn('emailAddress', profile)
            self.assertIn('messagesTotal', profile)
            
            user_email = profile['emailAddress']
            total_messages = profile['messagesTotal']
            
            self._log_test_result(
                "Authentication & Profile",
                "PASS",
                f"Successfully authenticated as {user_email} with {total_messages} total messages",
                details=f"Profile data: {json.dumps(profile, indent=2)}"
            )
            
            print(f"✅ Authenticated as: {user_email}")
            
        except Exception as e:
            self._log_test_result(
                "Authentication & Profile",
                "FAIL", 
                f"Authentication failed: {str(e)}"
            )
            self.fail(f"Authentication test failed: {e}")

    def test_02_send_basic_test_email(self):
        """Send a basic test email to verify email sending functionality."""
        try:
            start_time = time.time()
            
            subject = f"🧪 Gmail Client Test - Basic Email {datetime.now().strftime('%H:%M:%S')}"
            body = f"""Hello!

This is a test email sent by the Gmail Client integration test suite.

Test Details:
- Test: Basic Email Sending
- Timestamp: {datetime.now().isoformat()}
- Test ID: test_02_basic
- Purpose: Verify basic email sending functionality

If you received this email, the basic sending functionality is working correctly!

Best regards,
Gmail Client Test Suite
"""
            
            result = self.client.send_email(
                to=self.TEST_EMAIL,
                subject=subject,
                body=body
            )
            
            send_time = time.time() - start_time
            
            self.assertIn('id', result)
            email_id = result['id']
            
            self._log_test_result(
                "Basic Email Send",
                "PASS",
                f"Successfully sent basic test email",
                email_id=email_id,
                send_time=send_time,
                verification_needed=f"Check inbox for email with subject: '{subject}'"
            )
            
            print(f"✅ Basic email sent successfully (ID: {email_id})")
            
        except Exception as e:
            self._log_test_result(
                "Basic Email Send",
                "FAIL",
                f"Failed to send basic email: {str(e)}"
            )
            self.fail(f"Basic email send test failed: {e}")

    def test_03_send_html_email(self):
        """Send an HTML email to test rich content support."""
        try:
            start_time = time.time()
            
            subject = f"🎨 Gmail Client Test - HTML Email {datetime.now().strftime('%H:%M:%S')}"
            plain_body = "This email should display as HTML if your client supports it."
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Gmail Client Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #4285f4; color: white; padding: 20px; border-radius: 8px; }}
        .content {{ margin: 20px 0; }}
        .highlight {{ background: #fff3cd; padding: 10px; border-left: 4px solid #856404; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Gmail Client HTML Test</h1>
        <p>Integration Test Suite</p>
    </div>
    
    <div class="content">
        <h2>Test Information</h2>
        <ul>
            <li><strong>Test Type:</strong> HTML Email Support</li>
            <li><strong>Timestamp:</strong> {datetime.now().isoformat()}</li>
            <li><strong>Test ID:</strong> test_03_html</li>
        </ul>
        
        <div class="highlight">
            <h3>🎯 Verification Points</h3>
            <p>If you can see this formatted content with:</p>
            <ul>
                <li>Blue header background</li>
                <li>Styled fonts and spacing</li>
                <li>This highlighted yellow box</li>
            </ul>
            <p>Then HTML email support is working correctly!</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by Gmail Client Test Suite • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
            
            result = self.client.send_email(
                to=self.TEST_EMAIL,
                subject=subject,
                body=plain_body,
                html_body=html_body
            )
            
            send_time = time.time() - start_time
            
            self.assertIn('id', result)
            email_id = result['id']
            
            self._log_test_result(
                "HTML Email Send",
                "PASS",
                f"Successfully sent HTML test email",
                email_id=email_id,
                send_time=send_time,
                verification_needed=f"Check inbox for HTML email with subject: '{subject}' - verify HTML rendering"
            )
            
            print(f"✅ HTML email sent successfully (ID: {email_id})")
            
        except Exception as e:
            self._log_test_result(
                "HTML Email Send",
                "FAIL",
                f"Failed to send HTML email: {str(e)}"
            )
            self.fail(f"HTML email send test failed: {e}")

    def test_04_send_email_with_attachment(self):
        """Send an email with a file attachment."""
        try:
            start_time = time.time()
            
            # Create a test attachment
            test_content = f"""Gmail Client Test Attachment
=============================

This is a test file attachment sent by the Gmail Client integration test suite.

Test Details:
- Test ID: test_04_attachment
- Timestamp: {datetime.now().isoformat()}
- File Type: Plain Text (.txt)
- Purpose: Verify attachment handling

If you can download and read this file, attachment functionality is working correctly!

Test Data:
- Random number: {time.time()}
- Test iteration: 1
- Environment: Integration Test
"""
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_content)
                attachment_path = f.name
            
            try:
                subject = f"📎 Gmail Client Test - Attachment {datetime.now().strftime('%H:%M:%S')}"
                body = f"""Hello!

This email contains a test attachment to verify the Gmail Client's attachment handling capability.

Attachment Details:
- Filename: gmail_client_test.txt
- Content: Test data and verification information
- Size: Approximately {len(test_content)} bytes

Please download and verify the attachment content.

Test timestamp: {datetime.now().isoformat()}

Best regards,
Gmail Client Test Suite
"""
                
                result = self.client.send_email(
                    to=self.TEST_EMAIL,
                    subject=subject,
                    body=body,
                    attachments=[attachment_path]
                )
                
                send_time = time.time() - start_time
                
                self.assertIn('id', result)
                email_id = result['id']
                
                self._log_test_result(
                    "Email with Attachment",
                    "PASS",
                    f"Successfully sent email with attachment",
                    email_id=email_id,
                    send_time=send_time,
                    verification_needed=f"Check inbox for email with subject: '{subject}' - verify attachment can be downloaded"
                )
                
                print(f"✅ Email with attachment sent successfully (ID: {email_id})")
                
            finally:
                # Clean up temporary file
                if os.path.exists(attachment_path):
                    os.unlink(attachment_path)
                    
        except Exception as e:
            self._log_test_result(
                "Email with Attachment",
                "FAIL",
                f"Failed to send email with attachment: {str(e)}"
            )
            self.fail(f"Email with attachment test failed: {e}")

    def test_05_fetch_recent_emails(self):
        """Fetch recent emails to verify retrieval functionality."""
        try:
            # Fetch recent emails
            messages = self.client.list_messages(max_results=5, query="is:unread")
            
            self.assertIsInstance(messages, list)
            
            email_details = []
            for msg in messages[:3]:  # Process first 3 messages
                try:
                    formatted_msg = self.client.get_formatted_message(
                        self.client.get_raw_message(msg['id'])
                    )
                    
                    email_details.append({
                        'id': msg['id'],
                        'subject': formatted_msg.get('subject', 'No Subject')[:50],
                        'from': formatted_msg.get('from', 'Unknown Sender'),
                        'snippet': formatted_msg.get('snippet', '')[:100]
                    })
                except Exception as e:
                    print(f"⚠️ Error processing message {msg['id']}: {e}")
            
            self._log_test_result(
                "Recent Email Fetch",
                "PASS",
                f"Successfully fetched {len(messages)} recent emails",
                details=f"Sample emails: {json.dumps(email_details, indent=2)}",
                verification_needed="Review the fetched email details for accuracy"
            )
            
            print(f"✅ Fetched {len(messages)} recent emails")
            
        except Exception as e:
            self._log_test_result(
                "Recent Email Fetch", 
                "FAIL",
                f"Failed to fetch recent emails: {str(e)}"
            )
            self.fail(f"Recent email fetch test failed: {e}")

    def test_06_draft_workflow(self):
        """Test draft creation, update, and sending workflow."""
        try:
            # Create draft
            subject = f"📝 Gmail Client Test - Draft Workflow {datetime.now().strftime('%H:%M:%S')}"
            initial_body = f"""This is a draft email created by the Gmail Client test suite.

Initial draft timestamp: {datetime.now().isoformat()}
Test ID: test_06_draft
"""
            
            draft_result = self.client.create_draft(
                to=self.TEST_EMAIL,
                subject=subject,
                body=initial_body
            )
            
            self.assertIn('id', draft_result)
            draft_id = draft_result['id']
            
            # Update draft
            updated_body = f"""{initial_body}

DRAFT UPDATED!
Update timestamp: {datetime.now().isoformat()}
Status: Ready to send

This draft was successfully updated by the Gmail Client test suite.
"""
            
            update_result = self.client.update_draft(
                draft_id=draft_id,
                to=self.TEST_EMAIL,
                subject=subject + " [UPDATED]",
                body=updated_body
            )
            
            # Send draft
            start_time = time.time()
            send_result = self.client.send_draft(draft_id)
            send_time = time.time() - start_time
            
            self.assertIn('id', send_result)
            email_id = send_result['id']
            
            self._log_test_result(
                "Draft Workflow",
                "PASS",
                f"Successfully completed draft workflow: create → update → send",
                email_id=email_id,
                send_time=send_time,
                verification_needed=f"Check inbox for email with subject: '{subject} [UPDATED]' - verify it shows as updated content"
            )
            
            print(f"✅ Draft workflow completed successfully (Final ID: {email_id})")
            
        except Exception as e:
            self._log_test_result(
                "Draft Workflow",
                "FAIL",
                f"Draft workflow failed: {str(e)}"
            )
            self.fail(f"Draft workflow test failed: {e}")

    def test_07_label_management(self):
        """Test label creation and management."""
        try:
            # Create a test label
            test_label_name = f"GmailClientTest_{int(time.time())}"
            
            label_result = self.client.create_label(test_label_name)
            self.assertIn('id', label_result)
            label_id = label_result['id']
            
            # List labels to verify creation
            labels = self.client.list_labels()
            label_names = [label.get('name', '') for label in labels]
            self.assertIn(test_label_name, label_names)
            
            # Clean up - delete the test label
            self.client.delete_label(label_id)
            
            self._log_test_result(
                "Label Management",
                "PASS",
                f"Successfully created and deleted test label: {test_label_name}",
                details=f"Label ID: {label_id}, Total labels found: {len(labels)}"
            )
            
            print(f"✅ Label management test completed (Label: {test_label_name})")
            
        except Exception as e:
            self._log_test_result(
                "Label Management",
                "FAIL",
                f"Label management failed: {str(e)}"
            )
            self.fail(f"Label management test failed: {e}")

    def test_08_search_functionality(self):
        """Test email search functionality with various queries."""
        try:
            search_queries = [
                "from:noreply",
                "subject:test",
                "is:unread",
                "has:attachment"
            ]
            
            search_results = {}
            for query in search_queries:
                try:
                    results = self.client.search_messages(query, max_results=5)
                    search_results[query] = len(results)
                except Exception as e:
                    search_results[query] = f"Error: {str(e)}"
            
            # At least one search should return results or handle gracefully
            successful_searches = sum(1 for v in search_results.values() if isinstance(v, int))
            
            self._log_test_result(
                "Search Functionality",
                "PASS" if successful_searches > 0 else "FAIL",
                f"Tested {len(search_queries)} search queries, {successful_searches} successful",
                details=f"Search results: {json.dumps(search_results, indent=2)}"
            )
            
            print(f"✅ Search functionality tested ({successful_searches}/{len(search_queries)} successful)")
            
        except Exception as e:
            self._log_test_result(
                "Search Functionality",
                "FAIL",
                f"Search functionality failed: {str(e)}"
            )
            self.fail(f"Search functionality test failed: {e}")

    def test_09_performance_metrics(self):
        """Test performance and collect metrics."""
        try:
            metrics = {}
            
            # Test message listing performance
            start_time = time.time()
            messages = self.client.list_messages(max_results=10)
            metrics['list_messages_time'] = time.time() - start_time
            
            # Test profile retrieval performance  
            start_time = time.time()
            profile = self.client.get_profile()
            metrics['get_profile_time'] = time.time() - start_time
            
            # Test label listing performance
            start_time = time.time()
            labels = self.client.list_labels()
            metrics['list_labels_time'] = time.time() - start_time
            
            metrics['total_messages'] = len(messages)
            metrics['total_labels'] = len(labels)
            metrics['user_email'] = profile.get('emailAddress', 'Unknown')
            
            self._log_test_result(
                "Performance Metrics",
                "PASS",
                f"Collected performance metrics successfully",
                details=f"Metrics: {json.dumps(metrics, indent=2)}"
            )
            
            print(f"✅ Performance metrics collected")
            
        except Exception as e:
            self._log_test_result(
                "Performance Metrics",
                "FAIL",
                f"Performance metrics collection failed: {str(e)}"
            )
            self.fail(f"Performance metrics test failed: {e}")

    def test_10_reply_to_email_from_target(self):
        """Find an email from shengwxnw@gmail.com and reply to it."""
        try:
            target_sender = "shengwxnw@gmail.com"
            
            # Search for emails from the target sender
            search_query = f"from:{target_sender}"
            messages = self.client.search_messages(search_query, max_results=10)
            
            if not messages:
                self._log_test_result(
                    "Reply to Target Email",
                    "FAIL",
                    f"No emails found from {target_sender} to reply to",
                    verification_needed=f"Ensure there are emails from {target_sender} in the inbox"
                )
                self.fail(f"No emails found from {target_sender} to reply to")
                return
            
            # Get the most recent email from the target sender
            target_message = messages[0]
            msg_id = target_message['id']
            
            # Get the original message details
            raw_message = self.client.get_raw_message(msg_id)
            formatted_message = self.client.get_formatted_message(raw_message)
            
            original_subject = formatted_message.get('subject', 'No Subject')
            original_from = formatted_message.get('from', 'Unknown Sender')
            original_snippet = formatted_message.get('snippet', '')[:100]
            
            # Prepare reply content
            reply_subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
            reply_body = f"""Hello!

This is an automated reply generated by the Gmail Client integration test suite.

Reply Details:
- Test ID: test_10_reply
- Timestamp: {datetime.now().isoformat()}
- Original Message ID: {msg_id}
- Original Subject: {original_subject}
- Original Snippet: {original_snippet[:50]}...

This reply was sent to verify that the Gmail Client's reply functionality is working correctly.

If you receive this message, it means:
✅ The Gmail client can successfully search for emails
✅ The Gmail client can retrieve message details
✅ The Gmail client can send replies with proper threading

Test completed successfully!

Best regards,
Gmail Client Test Suite
"""
            
            # Send the reply
            start_time = time.time()
            reply_result = self.client.reply_to_message(
                msg_id=msg_id,
                body=reply_body
            )
            send_time = time.time() - start_time
            
            self.assertIn('id', reply_result)
            reply_email_id = reply_result['id']
            
            self._log_test_result(
                "Reply to Target Email",
                "PASS",
                f"Successfully replied to email from {target_sender}",
                email_id=reply_email_id,
                send_time=send_time,
                details=f"Original message: '{original_subject}' from {original_from}",
                verification_needed=f"Check {target_sender} inbox for reply email - verify it's properly threaded with original message"
            )
            
            print(f"✅ Reply sent successfully to {target_sender} (Reply ID: {reply_email_id})")
            print(f"   Original subject: {original_subject}")
            print(f"   Send time: {send_time:.2f} seconds")
            
        except Exception as e:
            self._log_test_result(
                "Reply to Target Email",
                "FAIL",
                f"Failed to reply to email from {target_sender}: {str(e)}"
            )
            self.fail(f"Reply to target email test failed: {e}")

def run_mock_tests():
    """Run only the mock tests (safe to run without credentials)."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGmailClient)
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def run_integration_tests():
    """Run integration tests (requires real Gmail credentials)."""
    print("\n🔧 Gmail Client Integration Test Suite")
    print("=" * 50)
    print("⚠️  WARNING: This will attempt to connect to Gmail API with real credentials!")
    print(f"📧 Test emails will be sent to: {TestGmailClientIntegration.TEST_EMAIL}")
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Integration tests cancelled by user")
        return
    
    print("\n🚀 Running integration tests...")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGmailClientIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n📊 Integration Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
    else:
        print("❌ Some integration tests failed")
    
    print(f"\n📝 Check {TestGmailClientIntegration.VERIFICATION_LOG_PATH} for detailed verification log")
    
    return result


if __name__ == '__main__':
    print("Gmail Client Test Suite")
    print("=" * 50)
    print()
    
    # Ask user which tests to run
    choice = input("Choose test type:\n1. Mock tests (safe, no credentials needed)\n2. Integration tests (requires Gmail credentials)\n3. All tests\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        print("\nRunning mock tests...")
        result = run_mock_tests()
    elif choice == '2':
        print("\nRunning integration tests...")
        result = run_integration_tests()
    elif choice == '3':
        print("\nRunning all tests...")
        unittest.main(verbosity=2)
    else:
        print("Invalid choice. Running mock tests by default...")
        result = run_mock_tests()
    
    if hasattr(result, 'wasSuccessful'):
        sys.exit(0 if result.wasSuccessful() else 1)
