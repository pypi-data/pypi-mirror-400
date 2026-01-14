"""
Folder Operations Module

Contains FolderOperationsMixin with folder-related operations:
- list_folders, search_folders, get_folder, create_folder, delete_folder
"""

from typing import Dict, Any, Optional, TYPE_CHECKING

from googleapiclient.errors import HttpError

from pydrive4.operations.base import FOLDER_MIME_TYPE, DEFAULT_FILE_FIELDS

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


class FolderOperationsMixin:
    """
    Mixin providing folder operations for GoogleDrive.
    
    This mixin expects the class to have:
    - `_service`: Google Drive API service resource
    - `_list_items()`: Helper method from BaseOperationsMixin
    - `_escape_query()`: Helper method from BaseOperationsMixin
    - `_handle_http_error()`: Helper method from BaseOperationsMixin
    """
    
    _service: "Resource"
    
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
            folders = drive.list_folders()
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
            results = drive.search_folders("Projects")
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
            result = drive.get_folder("My Documents")
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
            result = drive.create_folder("New Project")
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
        return self._delete_item(folder_id, permanently)
