"""Request handlers for Spartan server.

This module provides handlers for processing Spartan requests:
- StaticFileHandler: Serves static files from a document root
- UploadHandler: Handles file uploads (Spartan's integrated upload)
"""

from abc import ABC, abstractmethod
from pathlib import Path

from ..content.gemtext import generate_directory_listing
from ..protocol.constants import DEFAULT_MAX_FILE_SIZE, MIME_TYPE_GEMTEXT, MIME_TYPE_PLAIN
from ..protocol.request import SpartanRequest
from ..protocol.response import SpartanResponse
from ..utils.logging import get_logger

logger = get_logger(__name__)


class RequestHandler(ABC):
    """Abstract base class for request handlers."""

    @abstractmethod
    def handle(self, request: SpartanRequest) -> SpartanResponse:
        """Handle a Spartan request and return a response.

        Args:
            request: The incoming request.

        Returns:
            A SpartanResponse.
        """
        pass


class StaticFileHandler(RequestHandler):
    """Handler for serving static files from a document root.

    Features:
    - Path traversal protection
    - Directory index files (index.gmi, index.gemini)
    - Optional directory listings
    - MIME type detection
    - File size limits
    """

    def __init__(
        self,
        document_root: Path | str,
        default_indices: list[str] | None = None,
        enable_directory_listing: bool = False,
        max_file_size: int | None = None,
    ) -> None:
        """Initialize the static file handler.

        Args:
            document_root: Path to the directory to serve files from.
            default_indices: List of index file names to try.
            enable_directory_listing: Whether to generate listings for directories.
            max_file_size: Maximum file size to serve in bytes.

        Raises:
            ValueError: If document_root is invalid.
        """
        self.document_root = Path(document_root).resolve()
        self.default_indices = default_indices or ["index.gmi", "index.gemini"]
        self.enable_directory_listing = enable_directory_listing
        self.max_file_size = max_file_size or DEFAULT_MAX_FILE_SIZE

        if not self.document_root.exists():
            raise ValueError(f"Document root does not exist: {self.document_root}")
        if not self.document_root.is_dir():
            raise ValueError(f"Document root is not a directory: {self.document_root}")

    def handle(self, request: SpartanRequest) -> SpartanResponse:
        """Handle a static file request.

        Args:
            request: The incoming request.

        Returns:
            A SpartanResponse with the file content or error.
        """
        # Build file path
        requested_path = request.path.lstrip("/")
        file_path = (self.document_root / requested_path).resolve()

        # Path traversal protection
        if not self._is_safe_path(file_path):
            logger.warning(
                "path_traversal_attempt",
                path=request.path,
                resolved=str(file_path),
            )
            return SpartanResponse.client_error("Not found")

        # Handle directories
        if file_path.is_dir():
            return self._handle_directory(file_path, request.path)

        # Handle files
        if not file_path.exists():
            return SpartanResponse.client_error("Not found")

        if not file_path.is_file():
            return SpartanResponse.client_error("Not found")

        return self._serve_file(file_path)

    def _is_safe_path(self, file_path: Path) -> bool:
        """Check if file path is within document root.

        Args:
            file_path: The resolved file path.

        Returns:
            True if safe, False if path traversal attempt.
        """
        try:
            file_path.relative_to(self.document_root)
            return True
        except ValueError:
            return False

    def _handle_directory(self, dir_path: Path, request_path: str) -> SpartanResponse:
        """Handle a directory request.

        Args:
            dir_path: The directory path.
            request_path: The original request path.

        Returns:
            A SpartanResponse with index file or directory listing.
        """
        # Try index files
        for index_name in self.default_indices:
            index_path = dir_path / index_name
            if index_path.exists() and index_path.is_file():
                return self._serve_file(index_path)

        # No index found - check if directory listing enabled
        if self.enable_directory_listing:
            listing = generate_directory_listing(dir_path, request_path)
            return SpartanResponse.success(MIME_TYPE_GEMTEXT, listing)

        return SpartanResponse.client_error("Not found")

    def _serve_file(self, file_path: Path) -> SpartanResponse:
        """Serve a file.

        Args:
            file_path: The file path to serve.

        Returns:
            A SpartanResponse with file content.
        """
        try:
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return SpartanResponse.server_error("File too large")

            # Determine MIME type
            mime_type = self._get_mime_type(file_path)

            # Read and serve
            if mime_type.startswith("text/"):
                content = file_path.read_text(encoding="utf-8")
            else:
                content = file_path.read_bytes()

            return SpartanResponse.success(mime_type, content)

        except PermissionError:
            logger.warning("permission_denied", path=str(file_path))
            return SpartanResponse.client_error("Not found")
        except UnicodeDecodeError:
            # Fall back to binary for text files that fail to decode
            content = file_path.read_bytes()
            return SpartanResponse.success(MIME_TYPE_PLAIN, content)
        except Exception as e:
            logger.error("file_read_error", path=str(file_path), error=str(e))
            return SpartanResponse.server_error("Server error")

    def _get_mime_type(self, file_path: Path) -> str:
        """Determine MIME type from file extension.

        Args:
            file_path: The file path.

        Returns:
            The MIME type string.
        """
        suffix = file_path.suffix.lower()

        mime_map = {
            ".gmi": MIME_TYPE_GEMTEXT,
            ".gemini": MIME_TYPE_GEMTEXT,
            ".txt": MIME_TYPE_PLAIN,
            ".md": MIME_TYPE_PLAIN,
            ".py": MIME_TYPE_PLAIN,
            ".json": "application/json",
            ".xml": "application/xml",
            ".html": "text/html",
            ".css": "text/css",
            ".js": "text/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".pdf": "application/pdf",
        }

        return mime_map.get(suffix, MIME_TYPE_PLAIN)


class UploadHandler(RequestHandler):
    """Handler for file uploads.

    Spartan integrates upload into the core protocol (content-length > 0),
    unlike Gemini which uses the separate Titan protocol.
    """

    def __init__(
        self,
        upload_dir: Path | str,
        max_size: int = 10 * 1024 * 1024,
        allowed_types: list[str] | None = None,
        enable_delete: bool = False,
    ) -> None:
        """Initialize the upload handler.

        Args:
            upload_dir: Directory to store uploads.
            max_size: Maximum upload size in bytes.
            allowed_types: List of allowed MIME types (None = all).
            enable_delete: Whether to allow delete (zero-byte upload).
        """
        self.upload_dir = Path(upload_dir).resolve()
        self.max_size = max_size
        self.allowed_types = allowed_types
        self.enable_delete = enable_delete

        # Create upload directory if needed
        if not self.upload_dir.exists():
            self.upload_dir.mkdir(parents=True, exist_ok=True)

    def handle(self, request: SpartanRequest) -> SpartanResponse:
        """Handle an upload request.

        Args:
            request: The incoming request with content.

        Returns:
            A SpartanResponse indicating success or failure.
        """
        # Size validation
        if request.content_length > self.max_size:
            return SpartanResponse.client_error(
                f"Upload exceeds maximum size ({self.max_size} bytes)"
            )

        # Delete request (zero-byte upload)
        if request.content_length == 0:
            if self.enable_delete:
                return self._handle_delete(request.path)
            return SpartanResponse.client_error("Delete not enabled")

        # Path validation
        target = (self.upload_dir / request.path.lstrip("/")).resolve()
        if not self._is_safe_path(target):
            return SpartanResponse.client_error("Invalid path")

        # Save file
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(request.content)

            logger.info(
                "upload_completed",
                path=request.path,
                size=request.content_length,
            )

            body = (
                f"# Upload Successful\n\n"
                f"Uploaded {request.content_length} bytes to {request.path}\n\n"
                f"=> {request.path} View uploaded file\n"
            )
            return SpartanResponse.success(MIME_TYPE_GEMTEXT, body)

        except PermissionError:
            return SpartanResponse.server_error("Permission denied")
        except Exception as e:
            logger.error("upload_error", path=request.path, error=str(e))
            return SpartanResponse.server_error(f"Upload failed: {e}")

    def _handle_delete(self, path: str) -> SpartanResponse:
        """Handle a delete request.

        Args:
            path: The path to delete.

        Returns:
            A SpartanResponse indicating success or failure.
        """
        target = (self.upload_dir / path.lstrip("/")).resolve()

        if not self._is_safe_path(target):
            return SpartanResponse.client_error("Not found")

        if not target.exists():
            return SpartanResponse.client_error("Not found")

        try:
            target.unlink()
            logger.info("delete_completed", path=path)
            return SpartanResponse.success(
                MIME_TYPE_GEMTEXT,
                f"# Deleted\n\nResource '{path}' has been removed.\n",
            )
        except Exception as e:
            logger.error("delete_error", path=path, error=str(e))
            return SpartanResponse.server_error(f"Delete failed: {e}")

    def _is_safe_path(self, file_path: Path) -> bool:
        """Check if file path is within upload directory.

        Args:
            file_path: The resolved file path.

        Returns:
            True if safe, False if path traversal attempt.
        """
        try:
            file_path.relative_to(self.upload_dir)
            return True
        except ValueError:
            return False


class CombinedHandler(RequestHandler):
    """Handler that combines static file serving with upload handling.

    Routes requests based on content_length:
    - content_length == 0: Serve static file
    - content_length > 0: Handle upload
    """

    def __init__(
        self,
        static_handler: StaticFileHandler,
        upload_handler: UploadHandler | None = None,
    ) -> None:
        """Initialize the combined handler.

        Args:
            static_handler: Handler for static file requests.
            upload_handler: Optional handler for upload requests.
        """
        self.static_handler = static_handler
        self.upload_handler = upload_handler

    def handle(self, request: SpartanRequest) -> SpartanResponse:
        """Route request to appropriate handler.

        Args:
            request: The incoming request.

        Returns:
            A SpartanResponse.
        """
        if request.is_upload:
            if self.upload_handler:
                return self.upload_handler.handle(request)
            return SpartanResponse.client_error("Uploads not enabled")

        return self.static_handler.handle(request)
