"""OAuth authentication management."""

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from gchat.utils.errors import AuthenticationError, ConfigurationError, NetworkError
from gchat.utils.network import retry_on_network_error
from gchat.utils.paths import get_account_dir, get_credentials_file, get_token_file

# OAuth scopes for Google Chat
SCOPES = [
    "https://www.googleapis.com/auth/chat.spaces.readonly",
    "https://www.googleapis.com/auth/chat.messages.readonly",
    "https://www.googleapis.com/auth/chat.messages.create",
]


class AuthManager:
    """Handles OAuth authentication flow and token management."""

    def __init__(self, account_name: str):
        self.account_name = account_name
        self.account_dir = get_account_dir(account_name)
        self.credentials_path = get_credentials_file(account_name)
        self.token_path = get_token_file(account_name)

    def get_credentials(self) -> Credentials:
        """Get valid credentials, refreshing or re-authenticating if needed."""
        creds = self._load_credentials()

        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            try:

                def _refresh() -> None:
                    creds.refresh(Request())

                retry_on_network_error(_refresh, context="refreshing credentials")
                self._save_credentials(creds)
                return creds
            except NetworkError:
                raise  # Re-raise network errors with their helpful messages
            except Exception as e:
                raise AuthenticationError(
                    f"Failed to refresh credentials: {e}. Try re-authenticating."
                )

        # Need to run OAuth flow
        raise AuthenticationError(
            f"No valid credentials for account '{self.account_name}'. "
            "Run 'gchat account add' to authenticate."
        )

    def authenticate(self) -> Credentials:
        """Run OAuth flow to get new credentials."""
        if not self.credentials_path.exists():
            raise ConfigurationError(
                f"No credentials.json found for account '{self.account_name}'. "
                f"Please provide OAuth credentials from Google Cloud Console."
            )

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path),
                scopes=SCOPES,
            )

            creds = flow.run_local_server(
                host="localhost",
                port=0,  # Use any available port
                authorization_prompt_message=(
                    "Opening browser for Google authentication...\n"
                    "If browser doesn't open, visit: {url}"
                ),
                success_message="Authentication successful! You can close this window.",
                open_browser=True,
            )

            self._save_credentials(creds)
            return creds

        except Exception as e:
            raise AuthenticationError(f"OAuth flow failed: {e}")

    def is_authenticated(self) -> bool:
        """Check if valid credentials exist."""
        try:
            creds = self._load_credentials()
            if creds and creds.valid:
                return True
            if creds and creds.expired and creds.refresh_token:

                def _refresh() -> None:
                    creds.refresh(Request())

                retry_on_network_error(_refresh, context="checking authentication")
                self._save_credentials(creds)
                return True
            return False
        except Exception:
            return False

    def revoke(self) -> None:
        """Delete stored credentials."""
        if self.token_path.exists():
            self.token_path.unlink()

    def setup_credentials_file(self, credentials_path: Path | str) -> None:
        """Copy or link credentials.json to the account directory."""
        source = Path(credentials_path)
        if not source.exists():
            raise ConfigurationError(f"Credentials file not found: {source}")

        # Ensure account directory exists
        self.account_dir.mkdir(parents=True, exist_ok=True)

        # Copy the credentials file
        with open(source) as f:
            creds_data = json.load(f)

        with open(self.credentials_path, "w") as f:
            json.dump(creds_data, f, indent=2)

    def _load_credentials(self) -> Credentials | None:
        """Load credentials from token.json."""
        if not self.token_path.exists():
            return None

        try:
            return Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
        except Exception:
            return None

    def _save_credentials(self, creds: Credentials) -> None:
        """Save credentials to token.json."""
        self.account_dir.mkdir(parents=True, exist_ok=True)

        creds_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes) if creds.scopes else SCOPES,
        }

        with open(self.token_path, "w") as f:
            json.dump(creds_data, f, indent=2)
