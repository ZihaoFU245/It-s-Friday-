from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path
from typing import Union, Literal
import logging
import logging.config
import sys

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

    # Google API
    google_credentials_path: Path = Field(Path(__file__).parent / "credentials.json", env="GOOGLE_CREDENTIALS_PATH")
    google_token_path: Path = Field(Path(__file__).parent / "token.json", env="GOOGLE_TOKEN_PATH")

    # logging ocnfiguration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", env="LOG_LEVEL")
    log_path: Path = Field(Path(__file__).parent / "logs" / "app.log", env="LOG_PATH")
    log_max_size: int = Field(10, description="max log file size in MB", env="LOG_MAX_SIZE")
    log_counts: int = Field(10, description="number of logs will be kept", env="LOG_COUNTS")
    log_format: str = Field(
        "%(acstime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        env="LOG_FORMAT"
    )
 
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding='utf-8'
    )

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
        """Configure logging system using the current settings"""
        logging.config.dictConfig(self.logging_config)
        logging.captureWarnings(True)

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

if __name__ == "__main__":
    config = Config()
    print(config.weather_api_key)
    print(config.test_key)
