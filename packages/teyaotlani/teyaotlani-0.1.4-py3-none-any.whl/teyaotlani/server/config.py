"""Server configuration for Teyaotlani.

Provides TOML-based configuration with dataclass validation.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from ..protocol.constants import DEFAULT_MAX_FILE_SIZE, DEFAULT_PORT
from .middleware import AccessControlConfig, RateLimitConfig


@dataclass
class ServerConfig:
    """Configuration for Spartan server.

    Attributes:
        host: Server host address.
        port: Server port (default: 300).
        document_root: Path to directory containing files to serve.

    Examples:
        >>> config = ServerConfig(
        ...     host="localhost",
        ...     port=300,
        ...     document_root=Path("./capsule"),
        ... )
    """

    host: str = "localhost"
    port: int = DEFAULT_PORT
    document_root: Path | str = field(default=".")

    # File serving
    max_file_size: int = DEFAULT_MAX_FILE_SIZE
    enable_directory_listing: bool = False
    index_files: list[str] = field(default_factory=lambda: ["index.gmi", "index.gemini"])

    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_capacity: int = 10
    rate_limit_refill_rate: float = 1.0
    rate_limit_retry_after: int = 30

    # Access control
    enable_access_control: bool = False
    access_control_allow_list: list[str] | None = None
    access_control_deny_list: list[str] | None = None
    access_control_default_allow: bool = True

    # Upload configuration
    enable_upload: bool = False
    upload_dir: Path | str | None = None
    max_upload_size: int = 10 * 1024 * 1024  # 10 MB
    enable_delete: bool = False

    # Logging
    hash_client_ips: bool = True
    log_level: str = "INFO"
    json_logs: bool = False

    def __post_init__(self) -> None:
        """Validate and normalize configuration."""
        # Convert string paths to Path objects
        if isinstance(self.document_root, str):
            self.document_root = Path(self.document_root)

        if isinstance(self.upload_dir, str):
            self.upload_dir = Path(self.upload_dir)

        # Resolve document root
        self.document_root = self.document_root.resolve()

    def validate(self) -> None:
        """Validate configuration at runtime.

        Raises:
            ValueError: If configuration is invalid.
        """
        # Validate port
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid port: {self.port}")

        # Ensure document_root is Path (should be set by __post_init__)
        assert isinstance(self.document_root, Path)

        # Validate document root
        if not self.document_root.exists():
            raise ValueError(f"Document root does not exist: {self.document_root}")
        if not self.document_root.is_dir():
            raise ValueError(f"Document root is not a directory: {self.document_root}")

        # Validate upload config
        if self.enable_upload:
            if self.upload_dir is None:
                raise ValueError("upload_dir is required when enable_upload is True")

    def get_rate_limit_config(self) -> RateLimitConfig | None:
        """Get rate limit configuration if enabled.

        Returns:
            RateLimitConfig if enabled, None otherwise.
        """
        if not self.enable_rate_limiting:
            return None

        return RateLimitConfig(
            capacity=self.rate_limit_capacity,
            refill_rate=self.rate_limit_refill_rate,
            retry_after=self.rate_limit_retry_after,
        )

    def get_access_control_config(self) -> AccessControlConfig | None:
        """Get access control configuration if enabled.

        Returns:
            AccessControlConfig if enabled, None otherwise.
        """
        if not self.enable_access_control:
            return None

        return AccessControlConfig(
            allow_list=self.access_control_allow_list,
            deny_list=self.access_control_deny_list,
            default_allow=self.access_control_default_allow,
        )

    @classmethod
    def from_toml(cls, path: Path) -> "ServerConfig":
        """Load configuration from a TOML file.

        Args:
            path: Path to the TOML configuration file.

        Returns:
            A ServerConfig instance.

        Raises:
            FileNotFoundError: If the config file doesn't exist.
            ValueError: If the config file is invalid.
        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> "ServerConfig":
        """Create config from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            A ServerConfig instance.
        """
        server = data.get("server", {})
        rate_limit = data.get("rate_limit", {})
        access_control = data.get("access_control", {})
        upload = data.get("upload", {})
        logging_config = data.get("logging", {})

        return cls(
            # Server
            host=server.get("host", "localhost"),
            port=server.get("port", DEFAULT_PORT),
            document_root=server.get("document_root", "."),
            max_file_size=server.get("max_file_size", DEFAULT_MAX_FILE_SIZE),
            enable_directory_listing=server.get("enable_directory_listing", False),
            index_files=server.get("index_files", ["index.gmi", "index.gemini"]),
            # Rate limiting
            enable_rate_limiting=rate_limit.get("enabled", True),
            rate_limit_capacity=rate_limit.get("capacity", 10),
            rate_limit_refill_rate=rate_limit.get("refill_rate", 1.0),
            rate_limit_retry_after=rate_limit.get("retry_after", 30),
            # Access control
            enable_access_control=access_control.get("enabled", False),
            access_control_allow_list=access_control.get("allow_list"),
            access_control_deny_list=access_control.get("deny_list"),
            access_control_default_allow=access_control.get("default_allow", True),
            # Upload
            enable_upload=upload.get("enabled", False),
            upload_dir=upload.get("upload_dir"),
            max_upload_size=upload.get("max_upload_size", 10 * 1024 * 1024),
            enable_delete=upload.get("enable_delete", False),
            # Logging
            hash_client_ips=logging_config.get("hash_ips", True),
            log_level=logging_config.get("level", "INFO"),
            json_logs=logging_config.get("json", False),
        )
