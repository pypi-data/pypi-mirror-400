"""
Bulk Operations Module

Contains BulkOperationsMixin with bulk/batch operations:
- upload_folder (recursive folder upload)
"""

from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


class BulkOperationsMixin:
    """
    Mixin providing bulk operations for GoogleDrive.
    
    This mixin expects the class to have:
    - `_service`: Google Drive API service resource
    - `create_folder()`: Method from FolderOperationsMixin
    - `upload_file()`: Method from FileOperationsMixin
    """
    
    _service: "Resource"
    
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
            result = drive.upload_folder("./my_project")
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

    def _upload_folder_contents(
        self, local_path: Path, drive_folder_id: str, stats: Dict[str, Any]
    ) -> None:
        """Recursively upload folder contents."""
        for item in local_path.iterdir():
            if item.is_file():
                result = self.upload_file(str(item), drive_folder_id)
                if result["success"]:
                    stats["files_uploaded"] += 1
                else:
                    stats["errors"].append(f"{item.name}: {result.get('error', 'Unknown error')}")
            elif item.is_dir():
                # Create subfolder
                subfolder_result = self.create_folder(item.name, drive_folder_id)
                if subfolder_result["success"]:
                    stats["folders_created"] += 1
                    # Recurse into subfolder
                    self._upload_folder_contents(item, subfolder_result["id"], stats)
                else:
                    stats["errors"].append(f"{item.name}: {subfolder_result.get('error', 'Unknown error')}")
