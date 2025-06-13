from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import logging
from ... import config

class GoogleBaseClient:
    def __init__(self, scopes: list[str]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.creds: Credentials | None = None
        self.scopes = scopes
        self.token_path = self.config.google_token_path
        self.credentials_path = self.config.google_credentials_path
        self._authenticate()

    def _authenticate(self):
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes
                )
                self.creds = flow.run_local_server(port=0)  # opens browser → consent screen

            # save credentials
            with open(self.token_path, 'w') as f:
                f.write(self.creds.to_json())