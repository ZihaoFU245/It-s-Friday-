# Gmail Client Integration Guide

## Quick Start

### 1. Install Dependencies

Make sure you have the required dependencies installed:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Set Up Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure the OAuth consent screen
6. Download the credentials file and save it as `credentials.json` in your project

### 3. Basic Usage

```python
from app.modules.google_clients.gmail_client import GmailClient

# Initialize (will open browser for first-time authentication)
client = GmailClient()

# Get your profile
profile = client.get_profile()
print(f"Connected as: {profile['emailAddress']}")

# Send a test email to yourself
client.send_email(
    to=profile['emailAddress'],
    subject="Test from Gmail Client",
    body="Hello! This email was sent using the Gmail Client."
)
```

### 4. Run Examples

```bash
# Run the examples script
python gmail_client_examples.py

# Run tests (mock tests - safe without credentials)
python app/testing/test_email.py
```

## Key Features Summary

| Feature | Method | Description |
|---------|---------|-------------|
| **Send Email** | `send_email()` | Send emails with attachments, HTML, CC/BCC |
| **Create Draft** | `create_draft()` | Create draft messages |
| **Search** | `search_messages()` | Search with Gmail syntax |
| **Read Messages** | `get_formatted_message()` | Get formatted message content |
| **Manage Labels** | `create_label()`, `add_labels()` | Create and apply labels |
| **Mark Read/Unread** | `mark_as_read()`, `mark_as_unread()` | Change read status |
| **Reply** | `reply_to_message()` | Reply to existing messages |
| **Attachments** | `get_attachment()` | Download email attachments |
| **Threads** | `get_thread()` | Manage conversation threads |
| **Sync** | `get_history()` | Incremental synchronization |

## Error Handling

The client includes comprehensive error handling. Always wrap operations in try-catch blocks:

```python
from googleapiclient.errors import HttpError

try:
    result = client.send_email("test@example.com", "Subject", "Body")
    print(f"Email sent: {result['id']}")
except HttpError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Next Steps

1. **Read the full documentation**: `GMAIL_CLIENT_README.md`
2. **Run the examples**: `gmail_client_examples.py`
3. **Run the tests**: `app/testing/test_email.py`
4. **Integrate into your application**: Use the client in your own code

For detailed API reference and advanced usage, see the complete documentation.
