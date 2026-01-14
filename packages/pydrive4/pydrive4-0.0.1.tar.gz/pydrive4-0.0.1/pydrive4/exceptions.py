"""
PyDrive4 Exceptions Module

Custom exception classes for handling various error scenarios
in Google Drive API operations.
"""

import sys


class PyDrive4Error(Exception):
    """Base exception for all PyDrive4 errors."""

    def __init__(self, message: str = "An error occurred in PyDrive4"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"PyDrive4Error: {self.message}"


class AuthenticationError(PyDrive4Error):
    """Raised when authentication fails or credentials are invalid."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)

    def __str__(self) -> str:
        return f"AuthenticationError: {self.message}"


class FileNotFoundError(PyDrive4Error):
    """Raised when a requested file is not found in Google Drive."""

    def __init__(self, file_id: str = "", message: str = ""):
        if not message:
            message = f"File not found: {file_id}" if file_id else "File not found"
        self.file_id = file_id
        super().__init__(message)

    def __str__(self) -> str:
        return f"FileNotFoundError: {self.message}"


class FolderNotFoundError(PyDrive4Error):
    """Raised when a requested folder is not found in Google Drive."""

    def __init__(self, folder_id: str = "", folder_name: str = "", message: str = ""):
        if not message:
            if folder_name:
                message = f"Folder not found: {folder_name}"
            elif folder_id:
                message = f"Folder not found with ID: {folder_id}"
            else:
                message = "Folder not found"
        self.folder_id = folder_id
        self.folder_name = folder_name
        super().__init__(message)

    def __str__(self) -> str:
        return f"FolderNotFoundError: {self.message}"


class UploadError(PyDrive4Error):
    """Raised when a file upload operation fails."""

    def __init__(self, file_path: str = "", message: str = ""):
        if not message:
            message = f"Failed to upload file: {file_path}" if file_path else "Upload failed"
        self.file_path = file_path
        super().__init__(message)

    def __str__(self) -> str:
        return f"UploadError: {self.message}"


class DownloadError(PyDrive4Error):
    """Raised when a file download operation fails."""

    def __init__(self, file_id: str = "", message: str = ""):
        if not message:
            message = f"Failed to download file: {file_id}" if file_id else "Download failed"
        self.file_id = file_id
        super().__init__(message)

    def __str__(self) -> str:
        return f"DownloadError: {self.message}"


class ApiError(PyDrive4Error):
    """Raised when the Google Drive API returns an error."""

    def __init__(self, status_code: int = 0, message: str = "", reason: str = ""):
        if not message:
            message = f"API Error ({status_code}): {reason}" if reason else f"API Error: {status_code}"
        self.status_code = status_code
        self.reason = reason
        super().__init__(message)

    def __str__(self) -> str:
        return f"ApiError: {self.message}"


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials file is invalid or malformed."""

    def __init__(self, credentials_path: str = "", message: str = ""):
        if not message:
            message = f"Credentials file not found: {credentials_path}" if credentials_path else "Invalid credentials"
        self.credentials_path = credentials_path
        super().__init__(message)

    def __str__(self) -> str:
        return f"InvalidCredentialsError: {self.message}"


class PermissionError(PyDrive4Error):
    """Raised when the user doesn't have permission to perform an operation."""

    def __init__(self, item_id: str = "", operation: str = "", message: str = ""):
        if not message:
            if operation and item_id:
                message = f"Permission denied: Cannot {operation} item {item_id}"
            else:
                message = "Permission denied"
        self.item_id = item_id
        self.operation = operation
        super().__init__(message)

    def __str__(self) -> str:
        return f"PermissionError: {self.message}"


def _pydrive4_exception_handler(exc_type, exc_value, exc_traceback):
    """Custom exception handler that shows clean one-line errors for PyDrive4 exceptions."""
    if issubclass(exc_type, PyDrive4Error):
        # Print clean one-line error for PyDrive4 exceptions
        print(f"\n❌ {exc_value}", file=sys.stderr)
        sys.exit(1)
    else:
        # Use default handler for other exceptions
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def enable_clean_errors():
    """
    Enable clean, one-line error messages for PyDrive4 exceptions.
    
    Call this at the start of your script to get cleaner error output:
    
        from pydrive4 import enable_clean_errors
        enable_clean_errors()
    """
    sys.excepthook = _pydrive4_exception_handler


def disable_clean_errors():
    """Disable clean errors and restore default exception handling."""
    sys.excepthook = sys.__excepthook__
