from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path
from typing import Union, Literal, Dict, List, Optional
import logging
import logging.config
import sys
import os

class EmailAccountConfig(BaseSettings):
    """Configuration for a single email account."""
    name: str = Field(..., description="Account name (e.g., 'personal', 'work')")
    provider: str = Field("gmail", description="Email provider (gmail, outlook, etc.)")
    display_name: str = Field("", description="Display name for the account")
    
    # Google-specific settings
    google_credentials_path: Optional[Path] = Field(None, description="Path to Google credentials JSON")
    google_token_path: Optional[Path] = Field(None, description="Path to Google token JSON")
    
    # Outlook-specific settings (for future use)
    outlook_tenant_id: Optional[str] = Field(None, description="Outlook tenant ID")
    outlook_client_id: Optional[str] = Field(None, description="Outlook client ID")
    outlook_client_secret: Optional[str] = Field(None, description="Outlook client secret")
    
    # IMAP/SMTP settings (for future use)
    imap_server: Optional[str] = Field(None, description="IMAP server address")
    imap_port: Optional[int] = Field(None, description="IMAP server port")
    smtp_server: Optional[str] = Field(None, description="SMTP server address")
    smtp_port: Optional[int] = Field(None, description="SMTP server port")
    username: Optional[str] = Field(None, description="Email username")
    password: Optional[str] = Field(None, description="Email password")
    
    # Account-specific settings
    enabled: bool = Field(True, description="Whether this account is enabled")
    default_account: bool = Field(False, description="Whether this is the default account")

class Config(BaseSettings):
    """
    Application configuration class using Pydantic BaseSettings.
    Loads environment variables and provides default values for all key settings.

    Attributes:
        security_key (str|None): Security key for the application.
        weather_api_key (str|None): API key for weather service.
        weather_url (str): Base URL for weather API.
        lang (str): Default language for weather API.
        timeout (int): Timeout for API requests (seconds).
        temp_unit (str): Temperature unit ('c' or 'f').
        google_credentials_path (Path): Path to Google API credentials JSON.
        google_token_path (Path): Path to Google API token JSON.
        log_level (str): Logging level ('DEBUG', 'INFO', etc.).
        log_path (Path): Path to log file.
        log_max_size (int): Maximum log file size in MB before rotation.
        log_counts (int): Number of rotated log files to keep.
        log_format (str): Format string for log messages.

    Methods:
        validate_log_path: Ensures log directory exists and returns absolute path.
        logging_config: Returns a logging configuration dictionary for dictConfig.
        configure_logging: Configures the logging system using current settings.
    """
    # Security
    security_key: Union[None, str] = Field(None, env="SECURITY_KEY")

    # Weather
    weather_api_key: Union[None, str] = Field(None, env="WEATHER_API_KEY")
    weather_url: str = Field("http://api.weatherapi.com/v1", env="WEATHER_URL")
    lang: str = Field("en", env="LANG")
    timeout: int = Field(10, env="TIMEOUT")
    temp_unit: str = Field("c", env="TEMP_UNIT")    
    
    # PLATFORM & Location
    platform: str = Field(default_factory=lambda: os.environ.get("PLATFORM", "local"), env="PLATFORM")
    location: Union[None, str] = Field(default=None, env="LOCATION")

    # Email Accounts Configuration (DEPRECATED - Now managed by EmailAccountManager)
    # This field is kept for backward compatibility but is no longer used
    email_accounts: Dict[str, EmailAccountConfig] = Field(
        default_factory=dict,
        description="DEPRECATED: Email accounts are now managed by EmailAccountManager"
    )
    
    # Default email account name (for backward compatibility)
    default_email_account: str = Field("default", env="DEFAULT_EMAIL_ACCOUNT")

    # logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", env="LOG_LEVEL")
    log_path: Path = Field(Path(__file__).parent / "logs" / "app.log", env="LOG_PATH")
    log_max_size: int = Field(10, description="max log file size in MB", env="LOG_MAX_SIZE")
    log_counts: int = Field(10, description="number of logs will be kept", env="LOG_COUNTS")
    log_format: str = Field(
        "%(acstime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        env="LOG_FORMAT"
    )
    # for web accessing
    user_agent: Union[None, str] = Field(None, env="USER-AGENT")

    BASE_DIR: Path = Path(__file__).resolve().parent
    db_path: str = f"sqlite:///{(BASE_DIR / 'db/app.db').resolve()}"
 
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding='utf-8'
    )

    def __init__(self, **kwargs):
        """Initialize config. Email accounts are now managed by EmailAccountManager."""
        super().__init__(**kwargs)

    @field_validator('log_path')
    def validate_log_path(cls, value: Path) -> Path:
        """Ensure log directory exists and return absolute path"""
        value = value.absolute()
        value.parent.mkdir(parents=True, exist_ok=True)
        return value

    @property
    def logging_config(self) -> dict:
        """Generate logging configuration dictionary with dynamic formatter detail based on log level."""
        # More detailed format for DEBUG/ERROR/CRITICAL
        detailed_format = (
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
        )
        # Simpler format for INFO/WARNING
        simple_format = "%(asctime)s [%(levelname)s] %(message)s"
        # Use detailed format for DEBUG, ERROR, CRITICAL
        if self.log_level in ("DEBUG", "ERROR", "CRITICAL"):
            fmt = detailed_format
        else:
            fmt = simple_format
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': fmt,
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.log_level,
                    'formatter': 'standard',
                    'stream': sys.stdout
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': self.log_level,
                    'formatter': 'standard',
                    'filename': str(self.log_path),
                    'maxBytes': self.log_max_size * 1024 * 1024,  # Convert MB to bytes
                    'backupCount': self.log_counts,
                    'encoding': 'utf8'
                },
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['console', 'file'],
                    'level': self.log_level,
                    'propagate': False
                },
            }
        }
    
    def configure_logging(self) -> None:
        """Configure the logging system using the settings defined in the class."""
        logging.config.dictConfig(self.logging_config)
    
    def configure_fastapi_logging(self) -> None:
        """Configure verbose logging for FastAPI application"""
        logging.config.dictConfig(self.logging_config)
        logging.captureWarnings(True)
    
    def configure_mcp_logging(self) -> None:
        """Configure minimal logging for MCP server to prevent JSON-RPC parsing issues"""
        # This must be done BEFORE importing any modules that might log
        logging.basicConfig(level=logging.CRITICAL, format='%(message)s')
        
        # Suppress all MCP-related verbose logging
        loggers_to_suppress = [
            "fastmcp",
            "mcp",
            "mcp.server", 
            "mcp.server.lowlevel",
            "mcp.server.lowlevel.server",
            "asyncio",
            "urllib3",
            "requests"
        ]
        
        for logger_name in loggers_to_suppress:
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)
        # Completely disable debug and info logging for all loggers
        logging.disable(logging.DEBUG)
        logging.disable(logging.INFO)
    
    # DEPRECATED METHODS - Kept for backward compatibility
    # These methods now delegate to EmailAccountManager
    
    def get_email_account_config(self, account_name: str) -> Optional[EmailAccountConfig]:
        """
        DEPRECATED: Get configuration for a specific email account.
        Use EmailAccountManager.get_account_config() instead.
        """
        from .utils import EmailAccountManager
        # Create a temporary manager to access accounts
        manager = EmailAccountManager(self)
        return manager.get_account_config(account_name)
    
    def get_default_email_account(self) -> Optional[EmailAccountConfig]:
        """
        DEPRECATED: Get the default email account configuration.
        Use EmailAccountManager.get_default_account_name() instead.
        """
        from .utils import EmailAccountManager
        # Create a temporary manager to access accounts
        manager = EmailAccountManager(self)
        default_name = manager.get_default_account_name()
        return manager.get_account_config(default_name) if default_name else None
    
    def list_email_accounts(self, enabled_only: bool = True) -> List[EmailAccountConfig]:
        """
        DEPRECATED: List all configured email accounts.
        Use EmailAccountManager.list_account_names() instead.
        """
        from .utils import EmailAccountManager
        # Create a temporary manager to access accounts
        manager = EmailAccountManager(self)
        account_names = manager.list_account_names(enabled_only)
        return [manager.get_account_config(name) for name in account_names if manager.get_account_config(name)]
