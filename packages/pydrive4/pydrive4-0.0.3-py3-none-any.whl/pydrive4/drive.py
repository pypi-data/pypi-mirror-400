"""
PyDrive4 Drive Module

Main GoogleDrive class that combines all operation mixins
for a complete Google Drive API v3 client.
"""

from typing import Optional, Dict, Any

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from pydrive4.auth import GoogleAuth
from pydrive4.operations.base import BaseOperationsMixin
from pydrive4.operations.files import FileOperationsMixin
from pydrive4.operations.folders import FolderOperationsMixin
from pydrive4.operations.bulk import BulkOperationsMixin
from pydrive4.operations.sharing import SharingOperationsMixin


class GoogleDrive(
    BaseOperationsMixin,
    FileOperationsMixin,
    FolderOperationsMixin,
    BulkOperationsMixin,
    SharingOperationsMixin,
):
    """
    Main client for Google Drive API v3 operations.

    Provides easy-to-use methods for:
    - Listing files and folders
    - Searching files and folders
    - Creating folders
    - Uploading and downloading files
    - Sharing files and folders
    - Deleting items (trash or permanent)

    Args:
        credentials_name (str, optional): Path to credentials JSON file.
            - If not provided: auto-detects from current directory
            - For OAuth2: client_secrets.json from Google Cloud Console
            - For service account: service_account.json key file
        service_account (bool, optional): Use service account authentication.
            - True: force service account mode (for automation/servers)
            - False: force OAuth2 mode (opens browser for auth)
            - None: auto-detect based on filename
        token_file (str): Path to cache OAuth2 tokens. Default: "token.json"
        readonly (bool): Request read-only Drive access. Default: False
        auth (GoogleAuth, optional): Pre-configured GoogleAuth instance.

    What is service_account?
        Service accounts are special Google accounts for server-to-server
        authentication. They don't require user interaction (no browser popup).
        
        Use service_account=True when:
        - Running automated scripts or bots
        - Running on servers without a browser
        - You want to use a dedicated Drive (not user's personal drive)

    Example:
        ```python
        from pydrive4 import GoogleDrive

        # Auto-detect credentials (easiest!)
        drive = GoogleDrive()

        # With explicit OAuth2 credentials
        drive = GoogleDrive(credentials_name="client_secrets.json")

        # With service account (for automation)
        drive = GoogleDrive(
            credentials_name="service_account.json",
            service_account=True
        )

        # List files
        files = drive.list_files()
        ```
    """

    def __init__(
        self,
        credentials_name: Optional[str] = None,
        service_account: Optional[bool] = None,
        token_file: str = "token.json",
        readonly: bool = False,
        auth: Optional[GoogleAuth] = None,
    ) -> None:
        """
        Initialize GoogleDrive.

        Args:
            credentials_name: Path to credentials JSON file.
                - If None: auto-detects from current directory
                - For OAuth2: client_secrets.json from Google Cloud Console
                - For service account: service account key JSON file
            service_account: Use service account authentication.
                - True: force service account mode
                - False: force OAuth2 mode  
                - None (default): auto-detect based on filename
            token_file: Path to store/load OAuth2 tokens. Default: "token.json"
            readonly: If True, request read-only access. Default: False
            auth: Pre-configured GoogleAuth instance. If provided, other args are ignored.

        Raises:
            InvalidCredentialsError: If credentials file is not found or invalid.
            AuthenticationError: If authentication fails.
        """
        if auth:
            self._auth = auth
        else:
            self._auth = GoogleAuth(
                credentials_file=credentials_name,
                token_file=token_file,
                service_account=service_account,
                readonly=readonly,
            )
            self._auth.authenticate()

        self._service: Resource = self._auth.get_drive_service()

    @property
    def service(self) -> Resource:
        """Get the underlying Google Drive API service."""
        return self._service

    @property
    def auth(self) -> GoogleAuth:
        """Get the authentication handler."""
        return self._auth

    def _delete_item(self, item_id: str, permanently: bool = False) -> Dict[str, Any]:
        """Internal method to delete or trash a file or folder."""
        try:
            if permanently:
                self._service.files().delete(fileId=item_id).execute()
            else:
                # Move to trash
                self._service.files().update(
                    fileId=item_id, body={"trashed": True}
                ).execute()

            return {
                "success": True,
                "permanently_deleted": permanently,
            }
        except HttpError as e:
            if e.resp.status == 404:
                return {
                    "success": False,
                    "error": f"Item not found: {item_id}",
                }
            return self._handle_http_error(e)


# Alias for backwards compatibility
GoogleDriveClient = GoogleDrive
