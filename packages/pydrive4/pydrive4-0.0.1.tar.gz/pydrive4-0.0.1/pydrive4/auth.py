"""
PyDrive4 Authentication Module

Handles authentication with Google Drive API v3 using:
- Application Default Credentials (ADC) - automatic/recommended
- Service Account credentials (JSON key file)
- OAuth2 Client credentials (interactive browser-based)
- Environment variable GOOGLE_APPLICATION_CREDENTIALS
- Token caching and automatic refresh
"""

import json
import os
from pathlib import Path
from typing import Optional, List

import google.auth
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource

from pydrive4.exceptions import AuthenticationError, InvalidCredentialsError


# Default scopes for Google Drive access
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/drive",  # Full access to Drive
]

# Read-only scope alternative
READONLY_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
]

# Common credential file names for auto-detection
AUTO_DETECT_OAUTH_FILES = [
    "client_secrets.json",
    "credentials.json",
    "client_secret.json",
    "oauth_credentials.json",
]

AUTO_DETECT_SERVICE_ACCOUNT_FILES = [
    "service_account.json",
    "service_account_key.json",
    "sa_credentials.json",
]


def _auto_detect_credentials() -> tuple[Optional[str], bool]:
    """
    Auto-detect credentials file in current directory.
    
    Returns:
        Tuple of (credentials_path, is_service_account)
    """
    from glob import glob
    
    # First check for service account files
    for filename in AUTO_DETECT_SERVICE_ACCOUNT_FILES:
        if Path(filename).exists():
            return filename, True
    
    # Then check for OAuth2 files (exact names)
    for filename in AUTO_DETECT_OAUTH_FILES:
        if Path(filename).exists():
            return filename, False
    
    # Check for client_secret_*.json pattern (Google's default download name)
    client_secret_files = glob("client_secret_*.json")
    if client_secret_files:
        return client_secret_files[0], False
    
    return None, False


class GoogleAuth:
    """
    Handles Google Drive API authentication.

    Supports multiple authentication methods (in order of recommendation):
    
    1. **Application Default Credentials (ADC)** - Automatic, recommended
       - Uses `gcloud auth application-default login`
       - Or `GOOGLE_APPLICATION_CREDENTIALS` environment variable
       - Works on Google Cloud (GCE, Cloud Run, etc.) automatically
    
    2. **Service Account** - For servers/automation
       - Uses a service account JSON key file
       - No user interaction needed
    
    3. **OAuth2 Client Credentials** - For desktop/personal apps
       - Uses client_secrets.json
       - Opens browser for authorization (first time only)

    Args:
        credentials_file (str, optional): Path to credentials JSON file.
            If not provided, uses ADC or auto-detects from current directory.
        token_file (str): Path to cache OAuth2 tokens. Default: "token.json"
        scopes (list, optional): Custom OAuth2 scopes.
        service_account (bool, optional): Force service account auth.
            - True: force service account mode
            - False: force OAuth2 mode
            - None: auto-detect
        readonly (bool): Use read-only scopes. Default: False
        use_adc (bool): Try Application Default Credentials first. Default: True

    Example:
        ```python
        # Method 1: Application Default Credentials (easiest for GCP)
        # First run: gcloud auth application-default login
        auth = GoogleAuth()
        auth.authenticate()

        # Method 2: Auto-detect from current directory
        # Place client_secrets.json or service_account.json in directory
        auth = GoogleAuth()
        auth.authenticate()

        # Method 3: Explicit OAuth2 credentials
        auth = GoogleAuth(credentials_file="client_secrets.json")
        auth.authenticate()

        # Method 4: Explicit service account
        auth = GoogleAuth(
            credentials_file="service_account.json",
            service_account=True
        )
        auth.authenticate()
        ```
    """

    def __init__(
        self,
        credentials_file: Optional[str] = None,
        token_file: str = "token.json",
        scopes: Optional[List[str]] = None,
        service_account: Optional[bool] = None,
        readonly: bool = False,
        use_adc: bool = True,
    ):
        """
        Initialize GoogleAuth.

        Args:
            credentials_file: Path to credentials JSON file.
                - If None and use_adc=True: tries Application Default Credentials
                - If None and use_adc=False: auto-detects from current directory
            token_file: Path to store/load OAuth2 tokens. Default: "token.json"
            scopes: Custom OAuth2 scopes. Default: full Drive access.
            service_account: Use service account authentication.
                - True: force service account mode
                - False: force OAuth2 mode
                - None: auto-detect based on filename or ADC
            readonly: If True, request read-only access. Default: False
            use_adc: Try Application Default Credentials first. Default: True
        """
        self._service_account_mode: bool = False
        self._use_adc = use_adc
        self._adc_available = False
        
        # Auto-detect credentials if not provided
        if credentials_file is None:
            detected_file, detected_is_sa = _auto_detect_credentials()
            if detected_file:
                credentials_file = detected_file
                if service_account is None:
                    self._service_account_mode = detected_is_sa
        
        self.credentials_file = credentials_file
        self.token_file = token_file
        self._credentials: Optional[Credentials] = None
        self._drive_service: Optional[Resource] = None

        # Set service account mode
        if service_account is not None:
            self._service_account_mode = service_account
        elif credentials_file and not self._service_account_mode:
            # Try to detect from filename
            filename = Path(credentials_file).name.lower()
            if "service" in filename or "sa_" in filename:
                self._service_account_mode = True

        # Set scopes
        if readonly:
            self.scopes = READONLY_SCOPES
        elif scopes:
            self.scopes = scopes
        else:
            self.scopes = DEFAULT_SCOPES

    @property
    def credentials(self) -> Optional[Credentials]:
        """Get the current credentials object."""
        return self._credentials

    @property
    def is_authenticated(self) -> bool:
        """Check if authentication is valid and not expired."""
        if self._credentials is None:
            return False
        if hasattr(self._credentials, "expired"):
            return not self._credentials.expired
        return True

    @property
    def is_service_account(self) -> bool:
        """Check if using service account authentication."""
        return self._service_account_mode

    @property
    def is_adc(self) -> bool:
        """Check if using Application Default Credentials."""
        return self._adc_available

    def authenticate(self) -> "GoogleAuth":
        """
        Perform authentication using the best available method.

        Order of attempts:
        1. Application Default Credentials (if use_adc=True)
        2. Service Account (if service_account=True or detected)
        3. OAuth2 flow

        Returns:
            self for method chaining

        Raises:
            AuthenticationError: If all authentication methods fail
            InvalidCredentialsError: If credentials file is invalid or not found
        """
        # Try ADC first if enabled and no explicit credentials file
        if self._use_adc and not self.credentials_file:
            try:
                self._authenticate_adc()
                return self
            except Exception:
                # ADC not available, continue with other methods
                pass

        # Use explicit authentication method
        if self._service_account_mode:
            self._authenticate_service_account()
        else:
            self._authenticate_oauth2()

        return self

    def _authenticate_adc(self) -> None:
        """
        Authenticate using Application Default Credentials.
        
        This is the recommended method for:
        - Google Cloud environments (GCE, Cloud Run, etc.)
        - Local development with `gcloud auth application-default login`
        - Environments with GOOGLE_APPLICATION_CREDENTIALS set
        """
        try:
            credentials, project = google.auth.default(scopes=self.scopes)
            self._credentials = credentials
            self._adc_available = True
        except google.auth.exceptions.DefaultCredentialsError as e:
            raise AuthenticationError(
                f"Application Default Credentials not available: {e}"
            )

    def _authenticate_service_account(self) -> None:
        """Authenticate using a service account JSON key file."""
        if not self.credentials_file:
            raise InvalidCredentialsError(
                message="Service account credentials file is required. "
                "Download from: https://console.cloud.google.com/iam-admin/serviceaccounts"
            )

        credentials_path = Path(self.credentials_file)
        if not credentials_path.exists():
            raise InvalidCredentialsError(
                credentials_path=str(credentials_path),
                message=f"Service account file not found: {credentials_path}"
            )

        try:
            self._credentials = service_account.Credentials.from_service_account_file(
                str(credentials_path),
                scopes=self.scopes
            )
            self._service_account_mode = True
        except json.JSONDecodeError as e:
            raise InvalidCredentialsError(
                credentials_path=str(credentials_path),
                message=f"Invalid JSON in credentials file: {e}"
            )
        except Exception as e:
            raise AuthenticationError(f"Service account authentication failed: {e}")

    def _authenticate_oauth2(self) -> None:
        """Authenticate using OAuth2 flow with user interaction."""
        creds = None

        # Try to load existing token
        token_path = Path(self.token_file)
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path), self.scopes)
            except Exception:
                # Token file is invalid, will need to re-authenticate
                creds = None

        # If no valid credentials, perform OAuth2 flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    # Refresh failed, need to re-authenticate
                    creds = None

            if not creds:
                if not self.credentials_file:
                    raise InvalidCredentialsError(
                        message="No credentials available. Choose one of these methods:\n"
                        "\n"
                        "  Method 1: Application Default Credentials (ADC)\n"
                        "    → Run: gcloud auth application-default login\n"
                        "\n"
                        "  Method 2: Service Account (for automation)\n"
                        "    → Place 'service_account.json' in current directory\n"
                        "\n"
                        "  Method 3: OAuth2 (for personal use)\n"
                        "    → Place 'client_secrets.json' in current directory\n"
                        "\n"
                        "  Get credentials: https://console.cloud.google.com/apis/credentials"
                    )

                credentials_path = Path(self.credentials_file)
                if not credentials_path.exists():
                    raise InvalidCredentialsError(
                        credentials_path=str(credentials_path),
                        message=f"Credentials file not found: {credentials_path}"
                    )

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path),
                        self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    raise AuthenticationError(f"OAuth2 authentication failed: {e}")

            # Save the credentials for future use
            try:
                with open(token_path, "w") as token:
                    token.write(creds.to_json())
            except Exception:
                # Non-fatal: just can't cache the token
                pass

        self._credentials = creds

    def get_drive_service(self) -> Resource:
        """
        Get the Google Drive API service object.

        Returns:
            Google Drive API service resource

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.is_authenticated:
            raise AuthenticationError("Not authenticated. Call authenticate() first.")

        if self._drive_service is None:
            self._drive_service = build("drive", "v3", credentials=self._credentials)

        return self._drive_service

    def revoke(self) -> None:
        """
        Revoke the current credentials and remove cached token.
        """
        self._credentials = None
        self._drive_service = None
        self._adc_available = False

        # Remove cached token file
        token_path = Path(self.token_file)
        if token_path.exists():
            try:
                token_path.unlink()
            except Exception:
                pass

    def refresh(self) -> bool:
        """
        Attempt to refresh the current credentials.

        Returns:
            True if refresh was successful, False otherwise
        """
        if self._credentials is None:
            return False

        try:
            if hasattr(self._credentials, "refresh"):
                self._credentials.refresh(Request())
                return True
        except Exception:
            pass

        return False


# Convenience function for quick authentication
def authenticate(
    credentials_file: Optional[str] = None,
    service_account: Optional[bool] = None,
    readonly: bool = False,
) -> GoogleAuth:
    """
    Quick authenticate and return GoogleAuth instance.
    
    This is a convenience function for simple use cases.
    
    Args:
        credentials_file: Optional path to credentials JSON
        service_account: Force service account mode
        readonly: Use read-only access
    
    Returns:
        Authenticated GoogleAuth instance
    
    Example:
        ```python
        from pydrive4 import authenticate
        
        auth = authenticate()  # Uses ADC or auto-detect
        drive = auth.get_drive_service()
        ```
    """
    auth = GoogleAuth(
        credentials_file=credentials_file,
        service_account=service_account,
        readonly=readonly,
    )
    auth.authenticate()
    return auth
