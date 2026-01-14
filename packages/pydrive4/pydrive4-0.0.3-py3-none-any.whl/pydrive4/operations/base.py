"""
Base Operations Module

Contains shared constants, types, and helper methods used by all operation mixins.
"""

from typing import Dict, Any, List, TYPE_CHECKING

from googleapiclient.errors import HttpError

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


# Google Drive MIME type for folders
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

# Default fields to retrieve for file/folder metadata
DEFAULT_FILE_FIELDS = "id, name, mimeType, size, createdTime, modifiedTime, parents, trashed"
DEFAULT_LIST_FIELDS = f"nextPageToken, files({DEFAULT_FILE_FIELDS})"


class BaseOperationsMixin:
    """
    Base mixin providing shared helper methods for all operations.
    
    This mixin expects the class to have a `_service` attribute
    that is a Google Drive API service resource.
    """
    
    _service: "Resource"
    
    def _list_items(self, query: str, max_results: int = 1000) -> List[Dict[str, Any]]:
        """List items matching a query, handling pagination."""
        items = []
        page_token = None
        
        while True:
            response = self._service.files().list(
                q=query,
                spaces="drive",
                fields=DEFAULT_LIST_FIELDS,
                pageToken=page_token,
                pageSize=min(100, max_results - len(items)),
            ).execute()
            
            items.extend(response.get("files", []))
            page_token = response.get("nextPageToken")
            
            if not page_token or len(items) >= max_results:
                break
        
        return items
    
    def _find_file_by_name(self, name: str, parent_id: str) -> Dict[str, Any] | None:
        """Find a file by exact name in a specific folder."""
        escaped_name = self._escape_query(name)
        query = f"name = '{escaped_name}' and '{parent_id}' in parents and trashed = false"
        
        items = self._list_items(query, max_results=1)
        return items[0] if items else None
    
    def _escape_query(self, text: str) -> str:
        """Escape special characters in query strings."""
        return text.replace("\\", "\\\\").replace("'", "\\'")
    
    def _handle_http_error(self, error: HttpError) -> Dict[str, Any]:
        """Convert HttpError to standardized error response."""
        return {
            "success": False,
            "error": f"API error ({error.resp.status}): {error._get_reason()}",
        }
