# Multi-Account Email Setup Guide

This guide explains how to configure multiple email accounts (personal, work, etc.) in the ITS-FRIDAY application.

## Overview

The ITS-FRIDAY application now supports multiple email accounts through:

- **EmailManager**: High-level manager for multiple accounts
- **EmailService**: Individual service per account (used internally)
- **Configuration**: Flexible account configuration system
- **MCP Tools**: Account-specific email operations

## Quick Setup

### 1. Prepare Your Credentials

For each Gmail account you want to add:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials JSON file

### 2. Add Email Accounts

Use the setup helper script:

```bash
# Add personal Gmail account
python setup_email_accounts.py add personal gmail "C:\path\to\personal_credentials.json" "Personal Gmail"

# Add work Gmail account  
python setup_email_accounts.py add work gmail "C:\path\to\work_credentials.json" "Work Gmail" --default

# List all accounts
python setup_email_accounts.py list
```

### 3. Test Your Setup

Run the MCP server and test the tools:

```bash
cd skills
python server.py
```

Use MCP tools like:
- `list_email_accounts()` - See all configured accounts
- `get_unread_emails_from_account(account="personal")` - Get emails from specific account
- `send_email_from_account(to="friend@gmail.com", subject="Hi", body="Hello", account="personal")`

## Configuration Details

### File-Based Configuration

Email accounts are stored in `app/email_accounts.json`:

```json
{
  "personal": {
    "name": "personal",
    "provider": "gmail",
    "display_name": "Personal Gmail",
    "google_credentials_path": "C:\\path\\to\\personal_credentials.json",
    "google_token_path": "C:\\path\\to\\token_personal.json",
    "enabled": true,
    "default_account": false
  },
  "work": {
    "name": "work", 
    "provider": "gmail",
    "display_name": "Work Gmail",
    "google_credentials_path": "C:\\path\\to\\work_credentials.json",
    "google_token_path": "C:\\path\\to\\token_work.json",
    "enabled": true,
    "default_account": true
  }
}
```

### Code-Based Configuration

You can also configure accounts directly in `app/config.py`:

```python
email_accounts: Dict[str, EmailAccountConfig] = Field(
    default_factory=lambda: {
        "personal": EmailAccountConfig(
            name="personal",
            provider="gmail",
            display_name="Personal Gmail Account", 
            google_credentials_path=Path(__file__).parent / "credentials_personal.json",
            google_token_path=Path(__file__).parent / "token_personal.json",
            enabled=True,
            default_account=False
        ),
        "work": EmailAccountConfig(
            name="work",
            provider="gmail",
            display_name="Work Gmail Account",
            google_credentials_path=Path(__file__).parent / "credentials_work.json", 
            google_token_path=Path(__file__).parent / "token_work.json",
            enabled=True,
            default_account=True
        )
    }
)
```

## Using Multiple Accounts

### In MCP Tools

All email MCP tools now support account selection:

```python
# Get unread emails from specific account
result = await get_unread_emails_from_account(account="work", max_results=5)

# Get unread emails from all accounts
result = await get_unread_emails_all_accounts(max_results_per_account=5)

# Send email from specific account  
result = await send_email_from_account(
    to="colleague@company.com",
    subject="Meeting Tomorrow",
    body="Let's meet at 10 AM",
    account="work"
)

# Send from default account (if account not specified)
result = await send_email_from_account(
    to="friend@gmail.com", 
    subject="Hi",
    body="How are you?"
)
```

### In Python Code

```python
from app import email_manager

# Send from specific account
result = await email_manager.send_email(
    to="recipient@example.com",
    subject="Test", 
    body="Hello!",
    account="personal"
)

# Get unread from all accounts
all_unread = email_manager.get_all_unread_messages()

# Get account information
accounts_info = email_manager.get_all_account_info()
```

## Account Management

### Using the Setup Script

```bash
# List all accounts
python setup_email_accounts.py list

# Add new account
python setup_email_accounts.py add myaccount gmail "/path/to/creds.json"

# Set default account
python setup_email_accounts.py set-default personal

# Enable/disable accounts
python setup_email_accounts.py enable myaccount
python setup_email_accounts.py disable myaccount

# Remove account
python setup_email_accounts.py remove myaccount
```

### Programmatically

```python
from app.config import Config

config = Config()

# Get account info
personal_config = config.get_email_account_config("personal")
default_config = config.get_default_email_account()

# List all accounts
all_accounts = config.list_email_accounts(enabled_only=True)
```

## Authentication Flow

Each account maintains its own authentication:

1. **First Run**: OAuth flow opens browser for each account
2. **Token Storage**: Tokens saved to account-specific files
3. **Auto Refresh**: Tokens automatically refreshed when needed
4. **Isolation**: Each account's credentials are separate

### Token File Naming

- Personal account: `token_personal.json`
- Work account: `token_work.json`  
- Custom account: `token_{account_name}.json`

## MCP Tools Reference

### Account Management Tools

- `list_email_accounts()` - List all configured accounts
- `get_unread_emails_from_account(account, max_results, include_body)` - Get unread from specific account
- `get_unread_emails_all_accounts(max_results_per_account)` - Get unread from all accounts
- `send_email_from_account(to, subject, body, account, cc, bcc, html_body)` - Send from specific account

### Legacy Tools (Backward Compatible)

The existing single-account tools still work with the default account:

- `get_weather_now()` - Weather tools (unchanged)
- `get_upcoming_calendar_events()` - Calendar tools (unchanged)
- `list_google_drive_files()` - Drive tools (unchanged)

## Troubleshooting

### Common Issues

1. **"Account not configured"**
   - Check that the account exists in `app/email_accounts.json`
   - Verify the account name is correct

2. **"Credentials file not found"**
   - Check the path to credentials JSON file
   - Ensure the file exists and is readable

3. **"No default account configured"**
   - Set a default account: `python setup_email_accounts.py set-default accountname`
   - Or specify account explicitly in MCP calls

4. **Authentication errors**
   - Delete the token file to re-authenticate
   - Check that credentials file is valid
   - Ensure Gmail API is enabled in Google Cloud Console

### Debug Mode

Enable debug logging in `app/config.py`:

```python
log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("DEBUG", env="LOG_LEVEL")
```

### Validation

Test your setup:

```python
from app import email_manager

# Validate all accounts
results = email_manager.validate_all_accounts()
print(results)

# Get summary
summary = email_manager.get_summary()
print(summary)
```

## Security Considerations

1. **Credential Storage**: Store credentials files securely
2. **Token Files**: Token files contain sensitive data
3. **File Permissions**: Ensure proper file permissions
4. **Backup**: Backup your configuration files
5. **Rotation**: Regularly rotate credentials if needed

## Future Enhancements

Planned features:

1. **Multiple Providers**: Support for Outlook, Exchange, IMAP
2. **Unified Search**: Search across all accounts
3. **Auto-Discovery**: Automatic account detection
4. **Web Interface**: GUI for account management
5. **Sync Features**: Cross-account message synchronization

## Example Configurations

### Basic Setup (Personal + Work)

```json
{
  "personal": {
    "name": "personal",
    "provider": "gmail", 
    "display_name": "Personal Email",
    "google_credentials_path": "credentials_personal.json",
    "google_token_path": "token_personal.json",
    "enabled": true,
    "default_account": true
  },
  "work": {
    "name": "work",
    "provider": "gmail",
    "display_name": "Work Email", 
    "google_credentials_path": "credentials_work.json",
    "google_token_path": "token_work.json",
    "enabled": true,
    "default_account": false
  }
}
```

### Multi-Organization Setup

```json
{
  "main": {
    "name": "main",
    "provider": "gmail",
    "display_name": "Main Account",
    "default_account": true,
    "enabled": true
  },
  "company_a": {
    "name": "company_a", 
    "provider": "gmail",
    "display_name": "Company A Email",
    "enabled": true
  },
  "company_b": {
    "name": "company_b",
    "provider": "gmail", 
    "display_name": "Company B Email",
    "enabled": true
  },
  "personal": {
    "name": "personal",
    "provider": "gmail",
    "display_name": "Personal Email", 
    "enabled": false
  }
}
```

This setup provides a flexible, scalable foundation for managing multiple email accounts in your ITS-FRIDAY application.
