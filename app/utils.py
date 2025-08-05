from pathlib import Path
import json
import logging
from typing import Dict, Optional, List, Any

from .config import EmailAccountConfig


class EmailConfig:
    """
    Simplified configuration class for email clients.
    Contains only email-related settings, replacing the complex ClientConfig.
    """
    
    def __init__(self, account_config: EmailAccountConfig, base_config=None):
        """
        Initialize with account configuration and optional base config.
        
        Args:
            account_config: Email account configuration
            base_config: Optional base configuration for fallback values
        """
        # Account-specific information
        self.account_name = account_config.name
        self.provider = account_config.provider
        self.display_name = account_config.display_name
        self.enabled = account_config.enabled
        self.default_account = account_config.default_account
        
        # Google-specific settings
        self.google_credentials_path = account_config.google_credentials_path
        self.google_token_path = account_config.google_token_path
        
        # Outlook-specific settings
        self.outlook_tenant_id = account_config.outlook_tenant_id
        self.outlook_client_id = account_config.outlook_client_id
        self.outlook_client_secret = account_config.outlook_client_secret
        
        # IMAP/SMTP settings
        self.imap_server = account_config.imap_server
        self.imap_port = account_config.imap_port
        self.smtp_server = account_config.smtp_server
        self.smtp_port = account_config.smtp_port
        self.username = account_config.username
        self.password = account_config.password
        
        # Basic settings from base config if available
        if base_config:
            self.security_key = getattr(base_config, 'security_key', None)
            self.timeout = getattr(base_config, 'timeout', 10)
            self.log_level = getattr(base_config, 'log_level', 'INFO')
            self.user_agent = getattr(base_config, 'user_agent', None)


class EmailAccountManager:
    """
    Manages email account configuration operations and email client instances.
    
    This class handles loading, saving, creating, and deleting email account
    configurations. It also manages email client creation and lifecycle.
    
    Features:
    - Auto-persistence: All account changes are automatically saved to JSON file
    - Lazy loading: Account configs are cached on init, clients created only when needed
    - Simplified config: Uses single EmailConfig instead of complex ClientConfig
    """
    
    def __init__(self, config=None):
        """
        Initialize the EmailAccountManager.
        
        Args:
            config: Config object containing application settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Cache for account configurations (loaded on init)
        self._account_configs: Dict[str, Any] = {}
        
        # Cache for email client instances (lazy-loaded)
        self._email_clients: Dict[str, Any] = {}
        
        # Available email providers
        self._available_providers: Dict[str, type] = {}
        
        # Path to email accounts JSON file
        self._accounts_file_path = Path(__file__).parent / "email_accounts.json"
        
        self._initialize_default_providers()
        self._load_account_configs()
    
    def _initialize_default_providers(self):
        """Initialize default email providers."""
        try:
            from .modules.email_clients.base_email_client import BaseEmailClient
            from .modules.email_clients.gmail_client_adapter import GmailClientAdapter
            self._available_providers['gmail'] = GmailClientAdapter
            self.logger.info("Initialized default email providers: gmail")
        except ImportError as e:
            self.logger.warning(f"Failed to initialize default providers: {e}")
    
    def _load_account_configs(self):
        """Load account configurations from JSON file on initialization."""
        self._account_configs = self.load_accounts_from_file(self._accounts_file_path)
        self.logger.info(f"Loaded {len(self._account_configs)} account configurations")
    
    def _save_account_configs(self):
        """Auto-save account configurations to JSON file."""
        success = self.save_accounts_to_file(self._account_configs, self._accounts_file_path)
        if success:
            self.logger.info("Account configurations auto-saved successfully")
        else:
            self.logger.error("Failed to auto-save account configurations")
        return success
    
    def register_provider(self, name: str, client_class: type):
        """
        Register a new email provider.
        
        Args:
            name: Provider name (e.g., 'outlook', 'exchange')
            client_class: Client class that implements BaseEmailClient
            
        Raises:
            TypeError: If client_class doesn't implement BaseEmailClient
        """
        try:
            from .modules.email_clients.base_email_client import BaseEmailClient
            if not issubclass(client_class, BaseEmailClient):
                raise TypeError(f"Client class must implement BaseEmailClient interface")
        except ImportError:
            self.logger.warning("BaseEmailClient not available for validation")
        
        self._available_providers[name.lower()] = client_class
        self.logger.info(f"Registered email provider: {name}")
    
    def get_supported_providers(self) -> List[str]:
        """
        Get list of supported email providers.
        
        Returns:
            List of supported provider names
        """
        return list(self._available_providers.keys())
    
    def create_email_client(self, account_name: str):
        """
        Create and cache email client for a specific account (lazy loading).
        
        Args:
            account_name: Name of the email account
            
        Returns:
            BaseEmailClient instance for the account
            
        Raises:
            ValueError: If account is not configured, disabled, or provider not supported
        """
        if account_name in self._email_clients:
            return self._email_clients[account_name]
        
        # Get account config from cache
        account_config = self._account_configs.get(account_name)
        if not account_config:
            raise ValueError(f"Email account '{account_name}' not configured")
        
        if not account_config.enabled:
            raise ValueError(f"Email account '{account_name}' is disabled")
        
        provider = account_config.provider.lower()
        if provider not in self._available_providers:
            available = ', '.join(self._available_providers.keys())
            raise ValueError(f"Unsupported email provider: {provider}. Available: {available}")
        
        client_class = self._available_providers[provider]
        
        # Create client with simplified email configuration
        email_config = self._create_email_config(account_config)
        client = client_class(config=email_config)
        
        # Cache the client
        self._email_clients[account_name] = client
        self.logger.info(f"Created email client for account '{account_name}' ({provider})")
        
        return client
    
    def get_email_client(self, account_name: str):
        """
        Get existing email client or raise exception.
        
        Args:
            account_name: Name of the email account
            
        Returns:
            BaseEmailClient instance for the account
            
        Raises:
            ValueError: If email client not found
        """
        if account_name not in self._email_clients:
            raise ValueError(f"Email client for account '{account_name}' not found. Call create_email_client first.")
        
        return self._email_clients[account_name]
    
    def remove_email_client(self, account_name: str):
        """
        Remove cached email client.
        
        Args:
            account_name: Name of the email account
        """
        if account_name in self._email_clients:
            del self._email_clients[account_name]
            self.logger.info(f"Removed email client for account '{account_name}'")
    
    def clear_all_clients(self):
        """Clear all cached email clients."""
        self._email_clients.clear()
        self.logger.info("Cleared all cached email clients")
    
    def add_account(self, account_config: Any) -> bool:
        """
        Add a new email account with auto-save.
        
        Args:
            account_config: New account configuration to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._account_configs = self.create_account_static(self._account_configs, account_config)
            success = self._save_account_configs()
            if success:
                self.logger.info(f"Added account '{account_config.name}' with auto-save")
            return success
        except Exception as e:
            self.logger.error(f"Failed to add account '{account_config.name}': {e}")
            return False
    
    def delete_account(self, account_name: str) -> bool:
        """
        Delete an email account with auto-save.
        
        Args:
            account_name: Name of account to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if account_name not in self._account_configs:
                self.logger.warning(f"Account '{account_name}' not found for deletion")
                return False
            
            # Remove client from cache if it exists
            self.remove_email_client(account_name)
            
            # Delete from configurations
            self._account_configs = self.delete_account_static(self._account_configs, account_name)
            success = self._save_account_configs()
            if success:
                self.logger.info(f"Deleted account '{account_name}' with auto-save")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete account '{account_name}': {e}")
            return False
    
    def update_account(self, account_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update an email account with auto-save.
        
        Args:
            account_name: Name of account to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if account_name not in self._account_configs:
                self.logger.warning(f"Account '{account_name}' not found for update")
                return False
            
            # Remove client from cache since config is changing
            self.remove_email_client(account_name)
            
            # Update configurations
            self._account_configs = self.update_account_static(self._account_configs, account_name, updates)
            success = self._save_account_configs()
            if success:
                self.logger.info(f"Updated account '{account_name}' with auto-save")
            return success
        except Exception as e:
            self.logger.error(f"Failed to update account '{account_name}': {e}")
            return False
    
    def get_account_config(self, account_name: str) -> Optional[Any]:
        """
        Get account configuration from cache.
        
        Args:
            account_name: Name of the account
            
        Returns:
            Account configuration or None if not found
        """
        return self._account_configs.get(account_name)
    
    def get_all_accounts(self) -> Dict[str, Any]:
        """
        Get all account configurations from cache.
        
        Returns:
            Dictionary of all account configurations
        """
        return self._account_configs.copy()
    
    def list_account_names(self, enabled_only: bool = True) -> List[str]:
        """
        List account names from cache.
        
        Args:
            enabled_only: If True, only return enabled accounts
            
        Returns:
            List of account names
        """
        if enabled_only:
            return [name for name, config in self._account_configs.items() if config.enabled]
        else:
            return list(self._account_configs.keys())
    
    def get_default_account_name(self) -> Optional[str]:
        """
        Get the name of the default email account from cache.
        
        Returns:
            Name of default account, or None if not found
        """
        return self.get_default_account_name_static(self._account_configs)
    
    def _create_email_config(self, account_config):
        """
        Create simplified email configuration for clients.
        
        Args:
            account_config: Configuration for the specific account (EmailAccountConfig)
            
        Returns:
            EmailConfig object with account-specific settings
        """
        return EmailConfig(account_config, self.config)

    @staticmethod
    def load_accounts_from_file(file_path: Path) -> Dict[str, Any]:
        """
        Load email accounts from JSON configuration file.
        
        Args:
            file_path: Path to the email accounts JSON file
            
        Returns:
            Dictionary mapping account names to EmailAccountConfig objects
        """
        if not file_path.exists():
            # Return default configuration if file doesn't exist
            return EmailAccountManager._get_default_accounts()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
            
            # Import here to avoid circular imports
            from .config import EmailAccountConfig
            
            loaded_accounts = {}
            for name, data in accounts_data.items():
                loaded_accounts[name] = EmailAccountConfig(
                    name=data["name"],
                    provider=data["provider"],
                    display_name=data.get("display_name", ""),
                    google_credentials_path=Path(data["google_credentials_path"]) if data.get("google_credentials_path") else None,
                    google_token_path=Path(data["google_token_path"]) if data.get("google_token_path") else None,
                    enabled=data.get("enabled", True),
                    default_account=data.get("default_account", False)
                )
            
            return loaded_accounts
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to load email accounts from {file_path}: {e}")
            # Return default configuration on error
            return EmailAccountManager._get_default_accounts()
    
    @staticmethod
    def save_accounts_to_file(accounts: Dict[str, Any], file_path: Path) -> bool:
        """
        Save email accounts to JSON configuration file.
        
        Args:
            accounts: Dictionary of email account configurations
            file_path: Path to save the configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to serializable format
            accounts_data = {}
            for name, config in accounts.items():
                accounts_data[name] = {
                    "name": config.name,
                    "provider": config.provider,
                    "display_name": config.display_name,
                    "google_credentials_path": str(config.google_credentials_path) if config.google_credentials_path else None,
                    "google_token_path": str(config.google_token_path) if config.google_token_path else None,
                    "enabled": config.enabled,
                    "default_account": config.default_account
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(accounts_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to save email accounts to {file_path}: {e}")
            return False
    
    @staticmethod
    def create_account_static(
        accounts: Dict[str, Any], 
        account_config: Any
    ) -> Dict[str, Any]:
        """
        Create a new email account configuration.
        
        Args:
            accounts: Current accounts dictionary
            account_config: New account configuration to add
            
        Returns:
            Updated accounts dictionary
        """
        # If this is set as default, remove default from others
        if account_config.default_account:
            for existing_config in accounts.values():
                existing_config.default_account = False
        
        # Add the new account
        accounts[account_config.name] = account_config
        
        return accounts
    
    @staticmethod
    def delete_account_static(
        accounts: Dict[str, Any], 
        account_name: str
    ) -> Dict[str, Any]:
        """
        Delete an email account configuration.
        
        Args:
            accounts: Current accounts dictionary
            account_name: Name of account to delete
            
        Returns:
            Updated accounts dictionary
        """
        if account_name in accounts:
            was_default = accounts[account_name].default_account
            del accounts[account_name]
            
            # If we deleted the default account, make the first remaining account default
            if was_default and accounts:
                first_account = next(iter(accounts.values()))
                first_account.default_account = True
        
        return accounts
    
    @staticmethod
    def update_account_static(
        accounts: Dict[str, Any], 
        account_name: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing email account configuration.
        
        Args:
            accounts: Current accounts dictionary
            account_name: Name of account to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated accounts dictionary
        """
        if account_name not in accounts:
            return accounts
        
        config = accounts[account_name]
        
        # Handle default account changes
        if updates.get('default_account', False):
            # Remove default from all other accounts
            for other_config in accounts.values():
                other_config.default_account = False
        
        # Update the configuration
        for field, value in updates.items():
            if hasattr(config, field):
                setattr(config, field, value)
        
        return accounts
    
    @staticmethod
    def validate_account_config(account_config: Any) -> List[str]:
        """
        Validate an email account configuration.
        
        Args:
            account_config: Account configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not account_config.name:
            errors.append("Account name is required")
        
        if not account_config.provider:
            errors.append("Provider is required")
        
        if account_config.provider == "gmail":
            if not account_config.google_credentials_path:
                errors.append("Google credentials path is required for Gmail")
            elif not account_config.google_credentials_path.exists():
                errors.append(f"Google credentials file not found: {account_config.google_credentials_path}")
        
        return errors
    
    @staticmethod
    def _get_default_accounts() -> Dict[str, Any]:
        """
        Get default email account configuration.
        
        Returns:
            Dictionary with default account configuration
        """
        # Import here to avoid circular imports
        from .config import EmailAccountConfig
        
        return {
            "default": EmailAccountConfig(
                name="default",
                provider="gmail",
                display_name="Default Gmail Account",
                google_credentials_path=Path(__file__).parent / "secrets" / "credentials.json",
                google_token_path=Path(__file__).parent / "secrets" / "token.json",
                enabled=True,
                default_account=True
            )
        }
    
    @staticmethod
    def get_default_account_name_static(accounts: Dict[str, Any]) -> Optional[str]:
        """
        Get the name of the default email account.
        
        Args:
            accounts: Dictionary of email accounts
            
        Returns:
            Name of default account, or None if not found
        """
        for name, config in accounts.items():
            if config.default_account and config.enabled:
                return name
        
        # If no explicit default, return first enabled account
        for name, config in accounts.items():
            if config.enabled:
                return name
        
        return None
    
    @staticmethod
    def list_enabled_accounts(accounts: Dict[str, Any]) -> List[str]:
        """
        Get list of enabled account names.
        
        Args:
            accounts: Dictionary of email accounts
            
        Returns:
            List of enabled account names
        """
        return [name for name, config in accounts.items() if config.enabled]


# Additional utility functions
def ensure_directory_exists(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)


def safe_file_operation(operation, *args, **kwargs) -> Any:
    """
    Safely perform a file operation with error handling.
    
    Args:
        operation: File operation function to execute
        *args: Positional arguments for the operation
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Result of the operation, or None if failed
    """
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        logging.getLogger(__name__).error(f"File operation failed: {e}")
        return None


def update_keys(key: str, value: str):
    """
    change the api keys in the .env file
    """
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
        return

    with open(env_path, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[idx] = f"{key}={value}\n"
                f.seek(0)
                f.writelines(lines)
                f.truncate()
                return
        # Key not found, append to end, ensuring newline
        if lines and not lines[-1].endswith('\n'):
            f.write('\n')
        f.write(f"{key}={value}\n")
