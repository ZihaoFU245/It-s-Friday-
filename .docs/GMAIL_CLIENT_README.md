# Gmail Client Documentation

## Overview

The `GmailClient` is a comprehensive Python wrapper for the Gmail API that provides full email application functionality without a GUI. It's designed for backend email operations and includes all the features you'd expect from a modern email client.

## Features

### Core Email Operations
- ✅ **Send emails** with attachments, HTML content, CC/BCC
- ✅ **Reply to messages** with threading support
- ✅ **Retrieve and format messages** (plain text & HTML)
- ✅ **Search emails** with Gmail's powerful search syntax
- ✅ **Download attachments** from messages

### Draft Management
- ✅ **Create drafts** with full formatting and attachments
- ✅ **Update existing drafts**
- ✅ **Send drafts**
- ✅ **Delete drafts**
- ✅ **List all drafts**

### Message Management
- ✅ **Mark messages as read/unread**
- ✅ **Move messages to trash**
- ✅ **Permanently delete messages**
- ✅ **Add/remove labels** from messages
- ✅ **Organize emails** by categories (Primary, Promotions, Social, Updates)

### Label Management
- ✅ **Create custom labels**
- ✅ **Update label properties**
- ✅ **Delete labels**
- ✅ **List all labels**

### Advanced Features
- ✅ **Thread management** (conversation handling)
- ✅ **History synchronization** for efficient updates
- ✅ **Batch operations** for better performance
- ✅ **Full Gmail search** syntax support
- ✅ **Comprehensive error handling**

## Installation and Setup

### Prerequisites

1. **Google Cloud Project** with Gmail API enabled
2. **OAuth 2.0 credentials** (client_secret.json)
3. **Python dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

### Configuration

1. **Enable Gmail API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Gmail API for your project
   - Create OAuth 2.0 credentials
   - Download the credentials file as `credentials.json`

2. **Set up authentication**:
   - Place `credentials.json` in your project directory
   - The client will handle the OAuth flow automatically
   - A `token.json` file will be created after first authentication

3. **Configure scopes** (handled automatically by the client):
   ```python
   scopes = [
       "https://www.googleapis.com/auth/gmail.readonly",
       "https://www.googleapis.com/auth/gmail.send",
       "https://www.googleapis.com/auth/gmail.compose",
       "https://www.googleapis.com/auth/gmail.modify",
       "https://www.googleapis.com/auth/gmail.labels"
   ]
   ```

## Usage Examples

### Basic Usage

```python
from app.modules.google_clients.gmail_client import GmailClient

# Initialize the client
client = GmailClient()

# Get user profile
profile = client.get_profile()
print(f"Email: {profile['emailAddress']}")
```

### Sending Emails

```python
# Send a simple email
result = client.send_email(
    to="recipient@example.com",
    subject="Hello from Gmail Client",
    body="This is a test email!"
)

# Send email with HTML and attachments
result = client.send_email(
    to=["recipient1@example.com", "recipient2@example.com"],
    cc="cc@example.com",
    bcc="bcc@example.com",
    subject="Rich Email with Attachment",
    body="Plain text version",
    html_body="<h1>HTML Version</h1><p>This is <b>rich</b> content!</p>",
    attachments=["/path/to/file.pdf", "/path/to/image.jpg"]
)
```

### Managing Drafts

```python
# Create a draft
draft = client.create_draft(
    to="recipient@example.com",
    subject="Draft Email",
    body="This is a draft message"
)

# Update the draft
client.update_draft(
    draft_id=draft['id'],
    to="recipient@example.com",
    subject="Updated Draft Email",
    body="This is the updated draft message"
)

# Send the draft
client.send_draft(draft['id'])

# Or delete it
client.delete_draft(draft['id'])
```

### Reading Emails

```python
# List recent messages
messages = client.list_messages(max_results=10)

# Get a specific message
raw_message = client.get_raw_message(messages[0]['id'])
formatted_message = client.get_formatted_message(raw_message)

print(f"From: {formatted_message['from']}")
print(f"Subject: {formatted_message['subject']}")
print(f"Body: {formatted_message['body']['text']}")

# Download attachments
for attachment in formatted_message['attachments']:
    data = client.get_attachment(
        formatted_message['id'], 
        attachment['attachmentId']
    )
    with open(attachment['filename'], 'wb') as f:
        f.write(data)
```

### Searching Emails

```python
# Search with Gmail syntax
unread_emails = client.search_messages("is:unread")
emails_from_sender = client.search_messages("from:important@example.com")
recent_emails = client.search_messages("newer_than:7d")

# Count unread emails by category
primary_unread = client.count_unread(category="PRIMARY")
promotions_unread = client.count_unread(category="PROMOTIONS")
```

### Managing Labels

```python
# List all labels
labels = client.list_labels()

# Create a new label
label = client.create_label("Important Projects")

# Add label to messages
client.add_labels("message_id", [label['id']])

# Remove labels from messages
client.remove_labels("message_id", ["SPAM"])
```

### Message Operations

```python
# Mark as read/unread
client.mark_as_read("message_id")
client.mark_as_unread("message_id")

# Move to trash
client.trash_message("message_id")

# Permanently delete
client.delete_message("message_id")
```

### Thread Management

```python
# List conversation threads
threads = client.list_threads(max_results=10)

# Get full thread with all messages
thread = client.get_thread(threads[0]['id'])

# Modify thread labels
client.modify_thread(
    thread_id="thread_id",
    add_label_ids=["IMPORTANT"],
    remove_label_ids=["INBOX"]
)
```

### Replying to Messages

```python
# Reply to a message
reply = client.reply_to_message(
    msg_id="original_message_id",
    body="Thank you for your email!",
    reply_all=False  # Set to True to reply to all recipients
)
```

### Synchronization

```python
# Get current state
profile = client.get_profile()
current_history_id = profile['historyId']

# Later, check for changes
history = client.get_history(start_history_id=current_history_id)
if history:
    # Process changes
    for record in history.get('history', []):
        print(f"History record: {record}")
```

## API Reference

### Class: GmailClient

#### Constructor
```python
GmailClient()
```
Initializes the Gmail client with proper authentication and scopes.

#### Message Retrieval Methods

- `list_messages(max_results=10, query="", label_ids=None)` - List messages with optional filtering
- `get_raw_message(msg_id, format="full")` - Get raw message data
- `get_formatted_message(raw_msg)` - Format message for display
- `get_attachment(msg_id, attachment_id)` - Download attachment data

#### Email Sending Methods

- `send_email(to, subject, body, cc=None, bcc=None, attachments=None, html_body=None)` - Send email
- `reply_to_message(msg_id, body, html_body=None, reply_all=False, attachments=None)` - Reply to message

#### Draft Management Methods

- `create_draft(to, subject, body, cc=None, bcc=None, attachments=None, html_body=None)` - Create draft
- `update_draft(draft_id, to, subject, body, cc=None, bcc=None, attachments=None, html_body=None)` - Update draft
- `send_draft(draft_id)` - Send existing draft
- `delete_draft(draft_id)` - Delete draft
- `list_drafts(max_results=10)` - List all drafts
- `get_draft(draft_id)` - Get specific draft

#### Message Management Methods

- `mark_as_read(msg_ids)` - Mark messages as read
- `mark_as_unread(msg_ids)` - Mark messages as unread
- `trash_message(msg_id)` - Move to trash
- `untrash_message(msg_id)` - Remove from trash
- `delete_message(msg_id)` - Permanently delete
- `add_labels(msg_id, label_ids)` - Add labels
- `remove_labels(msg_id, label_ids)` - Remove labels

#### Label Management Methods

- `list_labels()` - List all labels
- `create_label(name, color=None, visibility="labelShow")` - Create label
- `update_label(label_id, name=None, color=None, visibility=None)` - Update label
- `delete_label(label_id)` - Delete label

#### Search and Filtering Methods

- `search_messages(query, max_results=50)` - Search with Gmail syntax
- `list_unread(hours=12, max_results=10, category="PRIMARY")` - List unread messages
- `fetch_unread(hours=12, max_results=10, category="PRIMARY")` - Fetch formatted unread messages
- `count_unread(hours=12, category="PRIMARY")` - Count unread messages

#### Synchronization Methods

- `get_history(start_history_id, max_results=100)` - Get message history
- `get_profile()` - Get user profile information

#### Thread Management Methods

- `list_threads(max_results=10, query="", label_ids=None)` - List threads
- `get_thread(thread_id)` - Get thread details
- `modify_thread(thread_id, add_label_ids=None, remove_label_ids=None)` - Modify thread labels
- `trash_thread(thread_id)` - Move thread to trash
- `delete_thread(thread_id)` - Permanently delete thread

## Testing

### Running Tests

The project includes comprehensive tests:

```bash
# Run mock tests (safe, no credentials needed)
python app/testing/test_email.py

# Run specific test categories
python -m unittest app.testing.test_email.TestGmailClient.test_send_email_basic
```

### Test Categories

1. **Mock Tests** - Safe tests using mocked API responses
2. **Integration Tests** - Tests requiring real Gmail credentials (disabled by default)
3. **Workflow Tests** - Complete email workflows

### Example Usage Script

Run the included examples:

```bash
python gmail_client_examples.py
```

## Error Handling

The client includes comprehensive error handling:

```python
from googleapiclient.errors import HttpError

try:
    client = GmailClient()
    result = client.send_email("test@example.com", "Subject", "Body")
except HttpError as e:
    if e.resp.status == 403:
        print("Permission denied - check your scopes")
    elif e.resp.status == 404:
        print("Resource not found")
    else:
        print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### Performance
- Use `list_messages()` with queries to filter results server-side
- Implement pagination for large result sets
- Use history API for incremental synchronization
- Cache formatted messages to avoid repeated API calls

### Security
- Store credentials securely
- Use minimal required scopes
- Implement proper error handling
- Validate input parameters

### Rate Limiting
- The Gmail API has rate limits (250 quota units per user per second)
- Implement exponential backoff for retries
- Consider using batch requests for multiple operations

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure `credentials.json` is properly configured
   - Check that Gmail API is enabled in Google Cloud Console
   - Verify OAuth consent screen is properly configured

2. **Permission Errors**
   - Ensure all required scopes are included
   - Re-authenticate if scopes have changed
   - Check that the user has granted all permissions

3. **Quota Exceeded**
   - Implement rate limiting in your application
   - Use batch operations when possible
   - Consider requesting higher quotas if needed

### Debug Mode

Enable logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = GmailClient()
# Now all API calls will be logged
```

## Contributing

When contributing to the Gmail client:

1. Add comprehensive tests for new features
2. Update this documentation
3. Follow existing code style and patterns
4. Ensure backward compatibility
5. Add appropriate error handling

## License

This Gmail client is part of the its-Friday project. Please refer to the project's license for usage terms.
