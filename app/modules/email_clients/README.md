# Email Service Architecture Documentation

## Overview

The Email Service provides a unified, provider-agnostic interface for email operations. This architecture allows seamless integration with multiple email providers (Gmail, Outlook, Exchange, etc.) without requiring code changes in the application layer.

## Architecture Components

### 1. BaseEmailClient (Abstract Interface)
**File**: `app/modules/email_clients/base_email_client.py`

Defines the standard interface that all email client implementations must follow. This ensures consistency across different providers.

**Key Features**:
- Standardized method signatures
- Comprehensive error handling patterns
- Provider capability detection
- Consistent return value formats

### 2. Provider-Specific Adapters
**Files**: 
- `app/modules/email_clients/gmail_client_adapter.py`
- `app/modules/email_clients/outlook_client_adapter.py` (placeholder)

These adapters implement the BaseEmailClient interface for specific email providers.

**Gmail Adapter Features**:
- Wraps the existing GmailClient
- Translates Gmail-specific data to standard format
- Handles Gmail-specific features (labels, threads, etc.)
- Provides error handling and logging

### 3. EmailService (High-Level API)
**File**: `app/services/email_service.py`

Provides the main interface for application code. Handles provider selection, configuration, and service-level features.

**Key Features**:
- Provider-agnostic operations
- Automatic provider detection
- Email validation
- Async/sync operation support
- Comprehensive logging and metadata

### 4. Factory Pattern
**File**: `app/modules/email_clients/__init__.py`

Implements factory pattern for creating email clients dynamically.

## Usage Examples

### Basic Usage

```python
from app.services.email_service import EmailService

# Initialize with Gmail (default)
email_service = EmailService(config: Config)

# Send email
result = await email_service.send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="Hello World!"
)

# Get unread messages
messages = email_service.get_unread_messages(max_results=10)

# Search messages
results = email_service.search_messages("from:important@company.com")
```

### Provider Switching

```python
# Start with Gmail
gmail_service = EmailService(config: Config, provider="gmail")

# Switch to Outlook (when implemented)
outlook_service = EmailService(config: Config, provider="outlook")

# Same API works for both providers
gmail_messages = gmail_service.get_unread_messages()
outlook_messages = outlook_service.get_unread_messages()
```

### Multi-Provider Support

```python
# Use multiple providers simultaneously
providers = {
    'personal': EmailService(config: Config, provider="gmail"),
    'work': EmailService(config: Config, provider="outlook")
}

# Send from different accounts
await providers['personal'].send_email(to="friend@gmail.com", ...)
await providers['work'].send_email(to="colleague@company.com", ...)
```

## Adding New Email Providers

### Step 1: Implement BaseEmailClient

```python
from app.modules.email_clients.base_email_client import BaseEmailClient

class NewProviderAdapter(BaseEmailClient):
    def __init__(self, config=None):
        super().__init__()
        # Initialize provider-specific client
        
    def send_email(self, to, subject, body, **kwargs):
        # Implement using provider's API
        pass
        
    def get_message(self, message_id):
        # Implement message retrieval
        pass
        
    # Implement all other required methods...
```

### Step 2: Register Provider

```python
# In __init__.py or dynamically
from app.modules.email_clients import add_email_provider
add_email_provider('new_provider', NewProviderAdapter)
```

### Step 3: Use New Provider

```python
service = EmailService(config: Config, provider="new_provider")
```

## Provider Capabilities

Each provider can declare its capabilities:

```python
def supports_feature(self, feature: str) -> bool:
    capabilities = {
        'html_email': True,
        'attachments': True, 
        'threading': False,  # Provider doesn't support threading
        'labels': True,
        'folders': False,    # Uses labels instead
        'search': True,
        'drafts': True
    }
    return capabilities.get(feature, False)
```

The EmailService automatically adapts based on these capabilities.

## Data Flow

```
Application Code
       ↓
EmailService (Provider-agnostic API)
       ↓
BaseEmailClient Interface
       ↓
Provider-Specific Adapter (Gmail/Outlook/etc.)
       ↓
Provider API (Gmail API, Graph API, etc.)
```

## Error Handling

### Standardized Error Responses

All methods return consistent error formats:

```python
{
    'success': False,
    'error': 'Error description',
    'provider': 'gmail',
    'service': 'EmailService'
}
```

### Provider-Specific Error Handling

Each adapter handles provider-specific errors and translates them to standard formats.

## Configuration

### Gmail Configuration
```python
gmail_config = {
    'credentials_path': 'path/to/credentials.json',
    'token_path': 'path/to/token.json',
    'scopes': ['gmail.readonly', 'gmail.send']
}
```

### Outlook Configuration (Future)
```python
outlook_config = {
    'tenant_id': 'your-tenant-id',
    'client_id': 'your-client-id',
    'client_secret': 'your-client-secret',
    'scopes': ['Mail.Read', 'Mail.Send']
}
```

## Testing Strategy

### Unit Tests
- Test each adapter independently
- Mock provider APIs
- Test error conditions

### Integration Tests
- Test with real provider APIs
- Verify cross-provider consistency
- Test provider switching

### Example Test Structure
```python
class TestEmailService:
    def test_gmail_send_email(self):
        service = EmailService(config={}, provider="gmail")
        # Test Gmail-specific functionality
        
    def test_outlook_send_email(self):
        service = EmailService(config={}, provider="outlook")
        # Test Outlook-specific functionality
        
    def test_provider_switching(self):
        # Test switching between providers
```

## Performance Considerations

### Lazy Initialization
- Email clients are initialized only when needed
- Reduces startup time and resource usage

### Caching
- Provider capabilities are cached
- Profile information can be cached
- Message metadata can be cached

### Async Support
- All sending operations support async/await
- Retrieval operations are optimized for batch processing

## Security Considerations

### Authentication
- Each provider handles its own authentication
- Credentials are managed separately per provider
- Token refresh is handled automatically

### Data Privacy
- No sensitive data is logged
- Provider responses can be sanitized
- Configurable logging levels

## Migration Guide

### From Direct Gmail Usage
```python
# Before
gmail_client = GmailClient()
result = gmail_client.send_email(...)

# After  
email_service = EmailService(config={}, provider="gmail")
result = await email_service.send_email(...)
```

### Benefits of Migration
1. **Provider Independence**: Easy to switch providers
2. **Consistent API**: Same methods work across providers
3. **Enhanced Features**: Email validation, metadata, logging
4. **Future-Proof**: Easy to add new providers
5. **Better Error Handling**: Standardized error responses

## Future Enhancements

### Planned Features
1. **Multi-Account Support**: Handle multiple accounts per provider
2. **Unified Search**: Search across multiple providers
3. **Message Synchronization**: Sync messages between providers
4. **Advanced Filtering**: Provider-agnostic filtering
5. **Batch Operations**: Efficient bulk operations
6. **Real-time Notifications**: Push notifications from providers

### Additional Providers
1. **Microsoft Exchange**: Enterprise email support
2. **IMAP/SMTP**: Generic email protocol support
3. **Yahoo Mail**: Consumer email support
4. **ProtonMail**: Privacy-focused email
5. **Custom SMTP**: Custom email server support

## Best Practices

### For Application Developers
1. Always use EmailService instead of direct provider clients
2. Handle async operations properly
3. Check provider capabilities before using advanced features
4. Use consistent error handling patterns

### For Provider Implementers
1. Follow the BaseEmailClient interface exactly
2. Provide comprehensive error handling
3. Implement capability detection accurately
4. Include provider-specific optimizations
5. Add comprehensive logging

## Troubleshooting

### Common Issues
1. **Authentication Failures**: Check provider credentials
2. **Feature Not Supported**: Check provider capabilities
3. **Rate Limiting**: Implement exponential backoff
4. **Network Issues**: Handle timeouts gracefully

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

email_service = EmailService(config: Config, provider="gmail")
# Detailed logging will show all operations
```

This architecture provides a solid foundation for email operations while maintaining flexibility for future enhancements and provider additions.
