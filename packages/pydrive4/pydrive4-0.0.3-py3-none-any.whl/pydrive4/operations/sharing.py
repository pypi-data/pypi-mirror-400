"""
Sharing Operations Module

Contains SharingOperationsMixin with permission/sharing operations:
- share, unshare, list_permissions, get_share_link
"""

from typing import Dict, Any, Optional, List, Literal, TYPE_CHECKING

from googleapiclient.errors import HttpError

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


# Share role types
ShareRole = Literal["reader", "writer", "commenter"]


class SharingOperationsMixin:
    """
    Mixin providing sharing/permission operations for GoogleDrive.
    
    This mixin expects the class to have:
    - `_service`: Google Drive API service resource
    - `_handle_http_error()`: Helper method from BaseOperationsMixin
    """
    
    _service: "Resource"
    
    def share(
        self,
        file_id: str,
        *,
        public: bool = False,
        email: Optional[str] = None,
        role: ShareRole = "reader",
        notify: bool = True,
    ) -> Dict[str, Any]:
        """
        Share a file or folder with others.

        Args:
            file_id: ID of the file/folder to share.
            public: If True, make publicly accessible (anyone with link).
            email: Email address to share with (mutually exclusive with public).
            role: Permission role - "reader", "writer", or "commenter".
            notify: If True, send email notification (only for email shares).

        Returns:
            Dict containing:
                - success: bool
                - permission: Created permission metadata
                - link: Shareable link (if public)

        Example:
            # Make public (anyone with link can view)
            drive.share("file_id", public=True)

            # Share with specific person
            drive.share("file_id", email="user@example.com", role="writer")
        """
        try:
            if public and email:
                return {
                    "success": False,
                    "error": "Cannot use both 'public' and 'email' - choose one",
                }
            
            if not public and not email:
                return {
                    "success": False,
                    "error": "Must specify either 'public=True' or 'email'",
                }

            # Build permission body
            if public:
                permission_body = {
                    "type": "anyone",
                    "role": role,
                }
            else:
                permission_body = {
                    "type": "user",
                    "role": role,
                    "emailAddress": email,
                }

            # Create permission
            permission = (
                self._service.permissions()
                .create(
                    fileId=file_id,
                    body=permission_body,
                    sendNotificationEmail=notify if email else False,
                    fields="id, type, role, emailAddress",
                )
                .execute()
            )

            result = {
                "success": True,
                "permission": permission,
            }

            # Get shareable link for public shares
            if public:
                file_metadata = (
                    self._service.files()
                    .get(fileId=file_id, fields="webViewLink")
                    .execute()
                )
                result["link"] = file_metadata.get("webViewLink")

            return result

        except HttpError as e:
            if e.resp.status == 404:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}",
                }
            return self._handle_http_error(e)

    def unshare(
        self,
        file_id: str,
        *,
        email: Optional[str] = None,
        permission_id: Optional[str] = None,
        remove_public: bool = False,
    ) -> Dict[str, Any]:
        """
        Remove sharing permissions from a file or folder.

        Args:
            file_id: ID of the file/folder.
            email: Email address to remove access from.
            permission_id: Specific permission ID to remove.
            remove_public: If True, remove public (anyone) access.

        Returns:
            Dict containing:
                - success: bool
                - removed_count: Number of permissions removed

        Example:
            # Remove public access
            drive.unshare("file_id", remove_public=True)

            # Remove access for specific user
            drive.unshare("file_id", email="user@example.com")
        """
        try:
            removed_count = 0

            if permission_id:
                # Remove specific permission
                self._service.permissions().delete(
                    fileId=file_id, permissionId=permission_id
                ).execute()
                removed_count = 1
            else:
                # List permissions to find matching ones
                permissions = self.list_permissions(file_id)
                if not permissions["success"]:
                    return permissions

                for perm in permissions["permissions"]:
                    should_remove = False
                    
                    if remove_public and perm.get("type") == "anyone":
                        should_remove = True
                    elif email and perm.get("emailAddress", "").lower() == email.lower():
                        should_remove = True

                    if should_remove and perm.get("id") != "owner":
                        try:
                            self._service.permissions().delete(
                                fileId=file_id, permissionId=perm["id"]
                            ).execute()
                            removed_count += 1
                        except HttpError:
                            pass  # Skip if can't remove (e.g., owner permission)

            return {
                "success": True,
                "removed_count": removed_count,
            }

        except HttpError as e:
            if e.resp.status == 404:
                return {
                    "success": False,
                    "error": f"File or permission not found",
                }
            return self._handle_http_error(e)

    def list_permissions(self, file_id: str) -> Dict[str, Any]:
        """
        List all permissions for a file or folder.

        Args:
            file_id: ID of the file/folder.

        Returns:
            Dict containing:
                - success: bool
                - permissions: List of permission objects
                - count: Number of permissions

        Example:
            perms = drive.list_permissions("file_id")
            for p in perms["permissions"]:
                print(f"{p.get('emailAddress', 'anyone')}: {p['role']}")
        """
        try:
            response = (
                self._service.permissions()
                .list(
                    fileId=file_id,
                    fields="permissions(id, type, role, emailAddress, displayName)",
                )
                .execute()
            )

            permissions = response.get("permissions", [])

            return {
                "success": True,
                "permissions": permissions,
                "count": len(permissions),
            }

        except HttpError as e:
            if e.resp.status == 404:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}",
                }
            return self._handle_http_error(e)

    def get_share_link(self, file_id: str) -> Dict[str, Any]:
        """
        Get the shareable web link for a file or folder.

        Args:
            file_id: ID of the file/folder.

        Returns:
            Dict containing:
                - success: bool
                - link: Web view link
                - is_public: Whether the file is publicly shared

        Example:
            result = drive.get_share_link("file_id")
            print(f"Link: {result['link']}")
        """
        try:
            file_metadata = (
                self._service.files()
                .get(fileId=file_id, fields="webViewLink, webContentLink")
                .execute()
            )

            # Check if file is public
            permissions = self.list_permissions(file_id)
            is_public = any(
                p.get("type") == "anyone" 
                for p in permissions.get("permissions", [])
            )

            return {
                "success": True,
                "link": file_metadata.get("webViewLink"),
                "download_link": file_metadata.get("webContentLink"),
                "is_public": is_public,
            }

        except HttpError as e:
            if e.resp.status == 404:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}",
                }
            return self._handle_http_error(e)

    def _make_public(self, file_id: str) -> bool:
        """
        Internal method to make a file publicly accessible.
        Used by upload_file and create_folder when public=True.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._service.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"},
            ).execute()
            return True
        except HttpError:
            return False
