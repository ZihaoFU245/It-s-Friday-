from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
import os
import logging
import json
from typing import List, Optional
from ... import config

class GoogleBaseClient:
    """
    Base client for Google API services with enhanced OAuth 2.0 authentication.
    
    Features:
    - Automatic scope validation and management
    - Token refresh with fallback to re-authentication
    - Support for multiple Google services (Gmail, Calendar, Drive)
    - Graceful handling of scope changes
    """
    
    # Common Google API scopes for reference
    COMMON_SCOPES = {
        'gmail': [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send', 
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.labels'
        ],
        'calendar': [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.readonly'
        ],
        'drive': [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file'
        ]
    }
    
    def __init__(self, scopes: List[str], service_name: Optional[str] = None):
        """
        Initialize the Google Base Client with OAuth authentication.
        
        Args:
            scopes: List of Google API scopes required
            service_name: Optional service name for logging (e.g., 'Gmail', 'Calendar')
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{service_name or 'GoogleClient'}")
        self.creds: Optional[Credentials] = None
        self.scopes = sorted(scopes)  # Sort for consistent comparison
        self.service_name = service_name or "Google API"
        self.token_path = self.config.google_token_path
        self.credentials_path = self.config.google_credentials_path
        
        self.logger.info(f"Initializing {self.service_name} client with scopes: {self.scopes}")
        self._authenticate()
        
    def _authenticate(self):
        """
        Authenticate with Google APIs using OAuth 2.0 flow.
        Handles token validation, refresh, and re-authentication as needed.
        """
        self.logger.debug("Starting authentication process...")
        
        # Step 1: Try to load existing credentials
        if os.path.exists(self.token_path):
            try:
                self._load_existing_credentials()
            except Exception as e:
                self.logger.warning(f"Failed to load existing credentials: {e}")
                self._cleanup_invalid_token()

        # Step 2: Validate and refresh credentials if needed
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self._attempt_token_refresh()
            
            # Step 3: Start OAuth flow if we still don't have valid credentials
            if not self.creds or not self.creds.valid:
                self._start_oauth_flow()

        # Step 4: Save valid credentials
        self._save_credentials()
        self.logger.info(f"{self.service_name} authentication successful")

    def _load_existing_credentials(self):
        """Load and validate existing credentials from token file."""
        self.logger.debug("Loading existing credentials...")
        
        with open(self.token_path, 'r') as f:
            token_data = json.load(f)
            existing_scopes = token_data.get('scopes', [])
            
        # Check if scopes match
        if set(existing_scopes) != set(self.scopes):
            self.logger.info(
                f"Scope mismatch detected. "
                f"Existing: {existing_scopes}, Required: {self.scopes}"
            )
            raise ValueError("Scope mismatch - re-authentication required")
            
        # Load credentials with current scopes
        self.creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        self.logger.debug("Existing credentials loaded successfully")

    def _cleanup_invalid_token(self):
        """Remove invalid token file."""
        if os.path.exists(self.token_path):
            try:
                os.remove(self.token_path)
                self.logger.info("Removed invalid token file")
            except OSError as e:
                self.logger.warning(f"Failed to remove invalid token file: {e}")
        self.creds = None

    def _attempt_token_refresh(self):
        """Attempt to refresh expired credentials."""
        try:
            self.logger.debug("Attempting to refresh expired credentials...")
            self.creds.refresh(Request())
            self.logger.info("Credentials refreshed successfully")
        except RefreshError as e:
            self.logger.warning(f"Failed to refresh credentials: {e}")
            self.creds = None

    def _start_oauth_flow(self):
        """Start the OAuth 2.0 authorization flow."""
        self.logger.info(f"Starting OAuth flow for {self.service_name}...")
        self.logger.info(f"Required scopes: {', '.join(self.scopes)}")
        
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Google API credentials file not found at {self.credentials_path}. "
                "Please download your OAuth 2.0 credentials from Google Cloud Console."
            )
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, self.scopes
            )
            # Use local server for OAuth flow
            self.creds = flow.run_local_server(
                port=0,
                prompt='consent',  # Always show consent screen for scope changes
                open_browser=True
            )
            self.logger.info("OAuth flow completed successfully")
        except Exception as e:
            self.logger.error(f"OAuth flow failed: {e}")
            raise

    def _save_credentials(self):
        """Save valid credentials to token file."""
        try:
            with open(self.token_path, 'w') as f:
                f.write(self.creds.to_json())
            self.logger.debug("Credentials saved successfully")
        except Exception as e:
            self.logger.warning(f"Failed to save credentials: {e}")

    def add_scopes(self, additional_scopes: List[str]) -> bool:
        """
        Add additional scopes to the current authentication.
        This will trigger re-authentication if new scopes are needed.
        
        Args:
            additional_scopes: List of additional scopes to request
            
        Returns:
            True if scopes were added successfully, False otherwise
        """
        new_scopes = sorted(set(self.scopes + additional_scopes))
        
        if new_scopes == self.scopes:
            self.logger.debug("No new scopes to add")
            return True
            
        self.logger.info(f"Adding new scopes: {set(additional_scopes) - set(self.scopes)}")
        
        # Update scopes and re-authenticate
        old_scopes = self.scopes
        self.scopes = new_scopes
        
        try:
            self._cleanup_invalid_token()  # Force re-authentication
            self._authenticate()
            return True
        except Exception as e:
            self.logger.error(f"Failed to add scopes: {e}")
            self.scopes = old_scopes  # Restore old scopes
            return False

    def get_user_info(self) -> dict:
        """
        Get basic user information from the authenticated account.
        
        Returns:
            Dictionary containing user information
        """
        if not self.creds or not self.creds.valid:
            raise RuntimeError("No valid credentials available")
              # Extract user info from token  
        token_info = {}
        try:
            # Try to get user info from token if available
            if hasattr(self.creds, 'id_token') and self.creds.id_token:
                # For now, we'll skip JWT parsing to avoid dependency
                pass
        except Exception:
            pass
                
        return {
            'scopes': self.scopes,
            'service_name': self.service_name,
            'token_valid': self.creds.valid,
            'token_expired': self.creds.expired if hasattr(self.creds, 'expired') else False,
            'user_email': token_info.get('email', 'Unknown'),
            'user_name': token_info.get('name', 'Unknown')
        }