"""
Email Clients Module

This module provides standardized email client implementations for different providers.
All clients implement the BaseEmailClient interface for consistent usage.
"""

from .base_email_client import BaseEmailClient
from .gmail_client_adapter import GmailClientAdapter
# from .outlook_client_adapter import OutlookClientAdapter  # Uncomment when fully implemented

# Available email client implementations
AVAILABLE_CLIENTS = {
    'gmail': GmailClientAdapter,
    # Future implementations (uncomment when ready):
    # 'outlook': OutlookClientAdapter,
    # 'exchange': ExchangeClientAdapter,
    # 'imap': IMAPClientAdapter,
}

def create_email_client(provider: str, config=None, **kwargs) -> BaseEmailClient:
    """
    Factory function to create email clients by provider name.
    
    Args:
        provider: Email provider name ('gmail', 'outlook', etc.)
        config: Configuration object (Config class instance)
        **kwargs: Provider-specific configuration options
        
    Returns:
        BaseEmailClient implementation for the specified provider
        
    Raises:
        ValueError: If provider is not supported
        
    Example:
        # Create Gmail client
        gmail_client = create_email_client('gmail', config)
        
        # Create Outlook client (when implemented)
        # outlook_client = create_email_client('outlook', config, tenant_id='...', client_id='...')
    """
    provider = provider.lower()
    
    if provider not in AVAILABLE_CLIENTS:
        available = ', '.join(AVAILABLE_CLIENTS.keys())
        raise ValueError(f"Unsupported email provider: {provider}. Available: {available}")
    
    client_class = AVAILABLE_CLIENTS[provider]
    
    # Pass config as first argument if provided, otherwise just use kwargs
    if config is not None:
        return client_class(config=config, **kwargs)
    else:
        return client_class(**kwargs)

def get_supported_providers() -> list:
    """
    Get list of supported email providers.
    
    Returns:
        List of supported provider names
    """
    return list(AVAILABLE_CLIENTS.keys())

def add_email_provider(name: str, client_class: type):
    """
    Dynamically add a new email provider.
    
    Args:
        name: Provider name (e.g., 'outlook', 'exchange')
        client_class: Client class that implements BaseEmailClient
        
    Raises:
        TypeError: If client_class doesn't implement BaseEmailClient
        
    Example:
        # Add Outlook provider when implementation is ready
        from .outlook_client_adapter import OutlookClientAdapter
        add_email_provider('outlook', OutlookClientAdapter)
    """
    if not issubclass(client_class, BaseEmailClient):
        raise TypeError(f"Client class must implement BaseEmailClient interface")
    
    AVAILABLE_CLIENTS[name.lower()] = client_class

__all__ = [
    'BaseEmailClient',
    'GmailClientAdapter', 
    'create_email_client',
    'get_supported_providers',
    'add_email_provider',
    'AVAILABLE_CLIENTS'
]
