"""
PyDrive4 Client Module

Main GoogleDriveClient class for interacting with Google Drive API v3.
Provides simplified methods for common file and folder operations.
"""

import io
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from googleapiclient.discovery import Resource
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from pydrive4.auth import GoogleAuth
from pydrive4.exceptions import (
    AuthenticationError,
    FileNotFoundError,
    FolderNotFoundError,
    UploadError,
    DownloadError,
    ApiError,
)


# Google Drive MIME type for folders
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

# Default fields to retrieve for file/folder metadata
DEFAULT_FILE_FIELDS = "id, name, mimeType, size, createdTime, modifiedTime, parents, trashed"
DEFAULT_LIST_FIELDS = f"nextPageToken, files({DEFAULT_FILE_FIELDS})"


class GoogleDrive:
    """
    Main client for Google Drive API v3 operations.

    Provides easy-to-use methods for:
    - Listing files and folders
    - Searching files and folders
    - Creating folders
    - Uploading and downloading files
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
        from pydrive4 import GoogleDriveClient

        # Auto-detect credentials (easiest!)
        client = GoogleDriveClient()

        # With explicit OAuth2 credentials
        client = GoogleDriveClient(credentials_name="client_secrets.json")

        # With service account (for automation)
        client = GoogleDriveClient(
            credentials_name="service_account.json",
            service_account=True
        )

        # List files
        files = client.list_files()
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
        Initialize GoogleDriveClient.

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

    # =========================================================================
    # LIST OPERATIONS
    # =========================================================================

    def list_files(
        self, folder_id: Optional[str] = None, trashed: bool = False
    ) -> Dict[str, Any]:
        """
        List all files (non-folders) in a folder.

        Args:
            folder_id: ID of the folder to list. None for root folder.
            trashed: If True, list trashed files only. Default False.

        Returns:
            Dict containing:
                - success: bool
                - files: List of file metadata dicts
                - count: Number of files found

        Example:
            files = client.list_files()
            for f in files['files']:
                print(f"File: {f['name']} ({f['id']})")
        """
        try:
            parent = folder_id or "root"
            query_parts = [
                f"'{parent}' in parents",
                f"mimeType != '{FOLDER_MIME_TYPE}'",
                f"trashed = {str(trashed).lower()}",
            ]
            query = " and ".join(query_parts)

            files = self._list_items(query)

            return {
                "success": True,
                "files": files,
                "count": len(files),
            }
        except HttpError as e:
            return self._handle_http_error(e)

    def list_folders(
        self, parent_id: Optional[str] = None, trashed: bool = False
    ) -> Dict[str, Any]:
        """
        List all folders in a parent folder.

        Args:
            parent_id: ID of the parent folder. None for root folder.
            trashed: If True, list trashed folders only. Default False.

        Returns:
            Dict containing:
                - success: bool
                - folders: List of folder metadata dicts
                - count: Number of folders found

        Example:
            folders = client.list_folders()
            for f in folders['folders']:
                print(f"Folder: {f['name']} ({f['id']})")
        """
        try:
            parent = parent_id or "root"
            query_parts = [
                f"'{parent}' in parents",
                f"mimeType = '{FOLDER_MIME_TYPE}'",
                f"trashed = {str(trashed).lower()}",
            ]
            query = " and ".join(query_parts)

            folders = self._list_items(query)

            return {
                "success": True,
                "folders": folders,
                "count": len(folders),
            }
        except HttpError as e:
            return self._handle_http_error(e)

    # =========================================================================
    # SEARCH OPERATIONS
    # =========================================================================

    def search_files(
        self, query_text: str, folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for files by name.

        Args:
            query_text: Text to search for in file names.
            folder_id: Optional folder ID to limit search scope.

        Returns:
            Dict containing:
                - success: bool
                - files: List of matching file metadata dicts
                - count: Number of matches found

        Example:
            results = client.search_files("report")
            print(f"Found {results['count']} files matching 'report'")
        """
        try:
            query_parts = [
                f"name contains '{self._escape_query(query_text)}'",
                f"mimeType != '{FOLDER_MIME_TYPE}'",
                "trashed = false",
            ]

            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")

            query = " and ".join(query_parts)
            files = self._list_items(query)

            return {
                "success": True,
                "files": files,
                "count": len(files),
            }
        except HttpError as e:
            return self._handle_http_error(e)

    def search_folders(
        self, query_text: str, parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for folders by name.

        Args:
            query_text: Text to search for in folder names.
            parent_id: Optional parent folder ID to limit search scope.

        Returns:
            Dict containing:
                - success: bool
                - folders: List of matching folder metadata dicts
                - count: Number of matches found

        Example:
            results = client.search_folders("Projects")
            print(f"Found {results['count']} folders matching 'Projects'")
        """
        try:
            query_parts = [
                f"name contains '{self._escape_query(query_text)}'",
                f"mimeType = '{FOLDER_MIME_TYPE}'",
                "trashed = false",
            ]

            if parent_id:
                query_parts.append(f"'{parent_id}' in parents")

            query = " and ".join(query_parts)
            folders = self._list_items(query)

            return {
                "success": True,
                "folders": folders,
                "count": len(folders),
            }
        except HttpError as e:
            return self._handle_http_error(e)

    # =========================================================================
    # FOLDER OPERATIONS
    # =========================================================================

    def get_folder(
        self, folder_name: str, parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a folder by its exact name.

        Args:
            folder_name: Exact name of the folder to find.
            parent_id: Optional parent folder ID to search within.

        Returns:
            Dict containing:
                - success: bool
                - folder: Folder metadata dict (if found)
                - found: bool indicating if folder was found

        Example:
            result = client.get_folder("My Documents")
            if result['found']:
                print(f"Folder ID: {result['folder']['id']}")
        """
        try:
            parent = parent_id or "root"
            query_parts = [
                f"name = '{self._escape_query(folder_name)}'",
                f"mimeType = '{FOLDER_MIME_TYPE}'",
                f"'{parent}' in parents",
                "trashed = false",
            ]
            query = " and ".join(query_parts)

            folders = self._list_items(query)

            if folders:
                return {
                    "success": True,
                    "folder": folders[0],
                    "found": True,
                }
            else:
                return {
                    "success": True,
                    "folder": None,
                    "found": False,
                }
        except HttpError as e:
            return self._handle_http_error(e)

    def create_folder(
        self, folder_name: str, parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new folder.

        Args:
            folder_name: Name for the new folder.
            parent_id: Optional parent folder ID. None for root.

        Returns:
            Dict containing:
                - success: bool
                - folder: Created folder metadata dict
                - id: ID of the created folder

        Example:
            result = client.create_folder("New Project")
            print(f"Created folder with ID: {result['id']}")
        """
        try:
            file_metadata = {
                "name": folder_name,
                "mimeType": FOLDER_MIME_TYPE,
            }

            if parent_id:
                file_metadata["parents"] = [parent_id]

            folder = (
                self._service.files()
                .create(body=file_metadata, fields=DEFAULT_FILE_FIELDS)
                .execute()
            )

            return {
                "success": True,
                "folder": folder,
                "id": folder["id"],
            }
        except HttpError as e:
            return self._handle_http_error(e)

    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================

    def upload_file(
        self, file_path: str, folder_id: Optional[str] = None, overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Upload a file to Google Drive.

        Args:
            file_path: Local path to the file to upload.
            folder_id: Optional destination folder ID. None for root.
            overwrite: If True, overwrite existing file with same name.

        Returns:
            Dict containing:
                - success: bool
                - file: Uploaded file metadata dict
                - id: ID of the uploaded file
                - overwritten: bool indicating if an existing file was replaced

        Example:
            result = client.upload_file("document.pdf", folder_id="abc123")
            print(f"Uploaded file ID: {result['id']}")
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                }

            file_name = path.name
            parent = folder_id or "root"
            overwritten = False

            # Check for existing file if overwrite is enabled
            existing_file_id = None
            if overwrite:
                existing = self._find_file_by_name(file_name, parent)
                if existing:
                    existing_file_id = existing["id"]
                    overwritten = True

            # Prepare file metadata
            file_metadata = {"name": file_name}
            if not existing_file_id:
                file_metadata["parents"] = [parent]

            # Create media upload
            media = MediaFileUpload(
                str(path),
                resumable=True,
            )

            # Upload or update
            if existing_file_id:
                # Update existing file
                file = (
                    self._service.files()
                    .update(
                        fileId=existing_file_id,
                        body=file_metadata,
                        media_body=media,
                        fields=DEFAULT_FILE_FIELDS,
                    )
                    .execute()
                )
            else:
                # Create new file
                file = (
                    self._service.files()
                    .create(
                        body=file_metadata,
                        media_body=media,
                        fields=DEFAULT_FILE_FIELDS,
                    )
                    .execute()
                )

            return {
                "success": True,
                "file": file,
                "id": file["id"],
                "overwritten": overwritten,
            }
        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}",
            }

    def download_file(
        self, file_id: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download a file from Google Drive.

        Args:
            file_id: ID of the file to download.
            output_path: Optional local path for the downloaded file.
                        If None, uses the file's name in current directory.

        Returns:
            Dict containing:
                - success: bool
                - path: Path where file was saved
                - size: Size of downloaded file in bytes

        Example:
            result = client.download_file("abc123", "downloaded.pdf")
            print(f"Downloaded to: {result['path']}")
        """
        try:
            # Get file metadata first
            file_metadata = (
                self._service.files()
                .get(fileId=file_id, fields="name, mimeType, size")
                .execute()
            )

            # Determine output path
            if output_path:
                save_path = Path(output_path)
            else:
                save_path = Path(file_metadata["name"])

            # Download the file
            request = self._service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Write to file
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(file_handle.getvalue())

            return {
                "success": True,
                "path": str(save_path),
                "size": len(file_handle.getvalue()),
            }
        except HttpError as e:
            if e.resp.status == 404:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}",
                }
            return self._handle_http_error(e)
        except Exception as e:
            return {
                "success": False,
                "error": f"Download failed: {str(e)}",
            }

    def upload_folder(
        self, folder_path: str, parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an entire folder to Google Drive recursively.

        Args:
            folder_path: Local path to the folder to upload.
            parent_id: Optional destination parent folder ID. None for root.

        Returns:
            Dict containing:
                - success: bool
                - folder: Created root folder metadata dict
                - files_uploaded: Number of files uploaded
                - folders_created: Number of folders created
                - errors: List of any errors encountered

        Example:
            result = client.upload_folder("./my_project")
            print(f"Uploaded {result['files_uploaded']} files")
        """
        try:
            path = Path(folder_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"Folder not found: {folder_path}",
                }

            if not path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {folder_path}",
                }

            stats = {
                "files_uploaded": 0,
                "folders_created": 0,
                "errors": [],
            }

            # Create root folder
            root_result = self.create_folder(path.name, parent_id)
            if not root_result["success"]:
                return root_result

            root_folder = root_result["folder"]
            stats["folders_created"] += 1

            # Upload contents recursively
            self._upload_folder_contents(path, root_folder["id"], stats)

            return {
                "success": True,
                "folder": root_folder,
                "files_uploaded": stats["files_uploaded"],
                "folders_created": stats["folders_created"],
                "errors": stats["errors"],
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Folder upload failed: {str(e)}",
            }

    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================

    def delete_item(self, item_id: str, permanently: bool = False) -> Dict[str, Any]:
        """
        Delete or trash a file or folder.

        Args:
            item_id: ID of the item to delete.
            permanently: If True, delete permanently. If False, move to trash.

        Returns:
            Dict containing:
                - success: bool
                - permanently_deleted: bool indicating deletion type

        Example:
            # Move to trash
            drive.delete_item("abc123")

            # Delete permanently
            drive.delete_item("abc123", permanently=True)
        """
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

    def delete_file(self, file_id: str, permanently: bool = False) -> Dict[str, Any]:
        """
        Delete or trash a file.

        Args:
            file_id: ID of the file to delete.
            permanently: If True, delete permanently. If False, move to trash.

        Returns:
            Dict containing:
                - success: bool
                - permanently_deleted: bool indicating deletion type

        Example:
            # Move file to trash
            drive.delete_file("file_id_here")

            # Delete file permanently
            drive.delete_file("file_id_here", permanently=True)
        """
        return self.delete_item(file_id, permanently)

    def delete_folder(self, folder_id: str, permanently: bool = False) -> Dict[str, Any]:
        """
        Delete or trash a folder and all its contents.

        Args:
            folder_id: ID of the folder to delete.
            permanently: If True, delete permanently. If False, move to trash.

        Returns:
            Dict containing:
                - success: bool
                - permanently_deleted: bool indicating deletion type

        Warning:
            Deleting a folder also deletes all files and subfolders inside it!

        Example:
            # Move folder to trash
            drive.delete_folder("folder_id_here")

            # Delete folder permanently (cannot be recovered!)
            drive.delete_folder("folder_id_here", permanently=True)
        """
        return self.delete_item(folder_id, permanently)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _list_items(self, query: str, max_results: int = 1000) -> List[Dict[str, Any]]:
        """List items matching a query, handling pagination."""
        items = []
        page_token = None

        while True:
            response = (
                self._service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields=DEFAULT_LIST_FIELDS,
                    pageToken=page_token,
                    pageSize=min(max_results - len(items), 100),
                )
                .execute()
            )

            items.extend(response.get("files", []))
            page_token = response.get("nextPageToken")

            if not page_token or len(items) >= max_results:
                break

        return items[:max_results]

    def _find_file_by_name(
        self, name: str, parent_id: str
    ) -> Optional[Dict[str, Any]]:
        """Find a file by exact name in a specific folder."""
        query = (
            f"name = '{self._escape_query(name)}' "
            f"and '{parent_id}' in parents "
            f"and mimeType != '{FOLDER_MIME_TYPE}' "
            f"and trashed = false"
        )

        files = self._list_items(query, max_results=1)
        return files[0] if files else None

    def _upload_folder_contents(
        self, local_path: Path, drive_folder_id: str, stats: Dict[str, Any]
    ) -> None:
        """Recursively upload folder contents."""
        for item in local_path.iterdir():
            try:
                if item.is_dir():
                    # Create subfolder and recurse
                    result = self.create_folder(item.name, drive_folder_id)
                    if result["success"]:
                        stats["folders_created"] += 1
                        self._upload_folder_contents(item, result["id"], stats)
                    else:
                        stats["errors"].append(f"Failed to create folder: {item}")
                else:
                    # Upload file
                    result = self.upload_file(str(item), drive_folder_id)
                    if result["success"]:
                        stats["files_uploaded"] += 1
                    else:
                        stats["errors"].append(f"Failed to upload file: {item}")
            except Exception as e:
                stats["errors"].append(f"Error processing {item}: {str(e)}")

    def _escape_query(self, text: str) -> str:
        """Escape special characters in query strings."""
        return text.replace("\\", "\\\\").replace("'", "\\'")

    def _handle_http_error(self, error: HttpError) -> Dict[str, Any]:
        """Convert HttpError to standardized error response."""
        return {
            "success": False,
            "error": str(error),
            "status_code": error.resp.status if hasattr(error, "resp") else None,
        }
