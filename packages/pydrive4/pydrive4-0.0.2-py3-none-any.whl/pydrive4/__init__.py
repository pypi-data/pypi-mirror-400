"""
PyDrive4 - A simplified Google Drive API v3 wrapper library.

PyDrive4 makes it easy to interact with Google Drive from Python.
It wraps the google-api-python-client to provide a clean, intuitive API
for common file and folder operations.

Example:
    ```python
    from pydrive4 import GoogleAuth, GoogleDrive

    # Authenticate
    auth = GoogleAuth()
    auth.authenticate()

    # Create Drive client
    drive = GoogleDrive(auth=auth)

    # Or simpler - auto-authenticate
    drive = GoogleDrive()

    # List files
    files = drive.list_files()

    # Upload a file
    result = drive.upload_file("document.pdf")
    ```

Authentication Methods:
    1. Application Default Credentials (recommended):
       Run `gcloud auth application-default login` first
    
    2. Auto-detect from current directory:
       Place client_secrets.json or service_account.json in your folder
    
    3. Explicit credentials file:
       GoogleDrive(credentials_name="path/to/creds.json")
"""

from pydrive4.drive import GoogleDrive, GoogleDriveClient
from pydrive4.auth import GoogleAuth, authenticate
from pydrive4.exceptions import (
    PyDrive4Error,
    AuthenticationError,
    FileNotFoundError,
    FolderNotFoundError,
    UploadError,
    DownloadError,
    ApiError,
    InvalidCredentialsError,
    PermissionError,
    enable_clean_errors,
    disable_clean_errors,
)

# Auto-enable clean error messages
enable_clean_errors()

__version__ = "0.1.0"
__author__ = "PyDrive4 Contributors"

__all__ = [
    # Main classes
    "GoogleDrive",
    "GoogleDriveClient",  # Alias for backwards compatibility
    "GoogleAuth",
    # Convenience functions
    "authenticate",
    # Exceptions
    "PyDrive4Error",
    "AuthenticationError",
    "FileNotFoundError",
    "FolderNotFoundError",
    "UploadError",
    "DownloadError",
    "ApiError",
    "InvalidCredentialsError",
    "PermissionError",
    # Error display control
    "enable_clean_errors",
    "disable_clean_errors",
]
