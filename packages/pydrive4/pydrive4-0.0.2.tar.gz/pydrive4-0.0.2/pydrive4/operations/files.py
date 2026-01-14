"""
File Operations Module

Contains FileOperationsMixin with file-related operations:
- list_files, search_files, upload_file, download_file, delete_file
"""

import io
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from pydrive4.operations.base import FOLDER_MIME_TYPE, DEFAULT_FILE_FIELDS

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


class FileOperationsMixin:
    """
    Mixin providing file operations for GoogleDrive.
    
    This mixin expects the class to have:
    - `_service`: Google Drive API service resource
    - `_list_items()`: Helper method from BaseOperationsMixin
    - `_escape_query()`: Helper method from BaseOperationsMixin
    - `_handle_http_error()`: Helper method from BaseOperationsMixin
    - `_find_file_by_name()`: Helper method from BaseOperationsMixin
    """
    
    _service: "Resource"
    
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
            files = drive.list_files()
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
            results = drive.search_files("report")
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
            result = drive.upload_file("document.pdf", folder_id="abc123")
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
            result = drive.download_file("abc123", "downloaded.pdf")
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
        return self._delete_item(file_id, permanently)
