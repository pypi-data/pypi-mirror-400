"""Configuration service for Spartan CLI.

This module provides a singleton service for managing Spartan CLI configuration.
It discovers, parses, and validates .spartan configuration files, making provider
values accessible throughout the application.

The ConfigService class implements the singleton pattern to ensure configuration
consistency across the entire application. It automatically discovers configuration
files by traversing up the directory tree from the current working directory.

Configuration File Format:
    The .spartan file uses INI format with a [default] section:

    [default]
    provider = aws

    Supported providers: 'aws', 'gcp'

Discovery Process:
    1. Start from current working directory (or specified path)
    2. Check for .spartan file in current directory
    3. If not found, move to parent directory
    4. Repeat until file is found, home directory is reached, or filesystem root
    5. If no file found, use default provider ('gcp')

Usage:
    >>> from spartan.services.config import ConfigService
    >>>
    >>> # Get singleton instance
    >>> config = ConfigService.get_instance()
    >>>
    >>> # Get configured provider
    >>> provider = config.get_provider()
    >>> print(provider)  # 'aws' or 'gcp'
    >>>
    >>> # Get config file path
    >>> path = config.get_config_path()
    >>> if path:
    ...     print(f"Using config from: {path}")
    >>>
    >>> # Reload configuration
    >>> config.reload()

Error Handling:
    The module defines several exception classes for different error scenarios:

    - ConfigError: Base exception for all configuration errors
    - ConfigParseError: Invalid INI syntax in configuration file
    - ConfigValidationError: Invalid configuration values (e.g., unsupported provider)
    - ConfigPermissionError: Cannot read configuration file due to permissions

    Example:
        >>> try:
        ...     config = ConfigService.get_instance()
        ...     provider = config.get_provider()
        ... except ConfigValidationError as e:
        ...     print(f"Invalid configuration: {e}")
        ... except ConfigPermissionError as e:
        ...     print(f"Permission denied: {e}")
        ... except ConfigError as e:
        ...     print(f"Configuration error: {e}")

Thread Safety:
    The ConfigService singleton implementation is thread-safe using a lock
    to prevent race conditions during initialization.

Attributes:
    ConfigService._instance: The singleton instance (class attribute)
    ConfigService._lock: Thread lock for singleton initialization (class attribute)
"""

import configparser
import threading
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigError(Exception):
    """Base exception for configuration errors.

    This is the base class for all configuration-related exceptions.
    Catch this exception to handle any configuration error generically.

    Example:
        >>> try:
        ...     config = ConfigService.get_instance()
        ... except ConfigError as e:
        ...     print(f"Configuration error: {e}")
    """

    pass


class ConfigParseError(ConfigError):
    """Raised when configuration file cannot be parsed.

    This exception is raised when the .spartan file contains invalid INI
    syntax that cannot be parsed by Python's configparser.

    Attributes:
        The exception message includes the line number (when available)
        and a description of the syntax error.

    Example:
        >>> try:
        ...     config.parse_config_file('/path/to/.spartan')
        ... except ConfigParseError as e:
        ...     print(f"Parse error: {e}")
    """

    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration values are invalid.

    This exception is raised when the configuration file is syntactically
    valid but contains invalid values (e.g., unsupported provider).

    Attributes:
        The exception message lists all validation errors found in the
        configuration file.

    Example:
        >>> try:
        ...     config.parse_config_file('/path/to/.spartan')
        ... except ConfigValidationError as e:
        ...     print(f"Validation error: {e}")
    """

    pass


class ConfigPermissionError(ConfigError):
    """Raised when configuration file cannot be read due to permissions.

    This exception is raised when the .spartan file exists but cannot
    be read due to insufficient file permissions.

    Attributes:
        The exception message includes the file path and suggests checking
        file permissions.

    Example:
        >>> try:
        ...     config.parse_config_file('/path/to/.spartan')
        ... except ConfigPermissionError as e:
        ...     print(f"Permission error: {e}")
    """

    pass


class ConfigService:
    """Singleton service for managing Spartan CLI configuration.

    This service discovers .spartan configuration files by traversing up the
    directory tree, parses them using INI format, validates the provider value,
    and provides access to configuration throughout the application.

    Example:
        >>> config = ConfigService.get_instance()
        >>> provider = config.get_provider()
        >>> print(provider)  # 'aws' or 'gcp'
    """

    _instance: Optional["ConfigService"] = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize the configuration service (private).

        This constructor is private and should not be called directly.
        Use get_instance() to access the singleton instance.
        """
        self._config: configparser.ConfigParser = configparser.ConfigParser()
        self._config_path: Optional[str] = None
        self._provider: str = "gcp"  # Default provider

        # Discover and load configuration on initialization
        self._load_configuration()

    @classmethod
    def get_instance(cls) -> "ConfigService":
        """Get or create the singleton instance.

        Returns:
            ConfigService: The singleton configuration service instance.

        Example:
            >>> config = ConfigService.get_instance()
            >>> provider = config.get_provider()
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def discover_config_file(self, start_path: Optional[str] = None) -> Optional[str]:
        """Discover .spartan file by traversing up from start_path.

        Searches for a .spartan configuration file starting from the given path
        (or current working directory) and traversing upward through parent
        directories until the file is found, the filesystem root is reached,
        or the user's home directory is reached.

        Args:
            start_path: Starting directory (defaults to current working directory).

        Returns:
            Path to .spartan file or None if not found.

        Example:
            >>> config = ConfigService.get_instance()
            >>> path = config.discover_config_file()
            >>> if path:
            ...     print(f"Found config at: {path}")
        """
        # Start from provided path or current working directory
        if start_path is None:
            current = Path.cwd()
        else:
            current = Path(start_path).resolve()

        home = Path.home()

        # Traverse upward through parent directories
        while True:
            config_file = current / ".spartan"

            # Check if .spartan file exists in current directory
            if config_file.exists():
                return str(config_file)

            # Stop at home directory
            if current == home:
                break

            # Stop at filesystem root
            if current == current.parent:
                break

            # Move to parent directory
            current = current.parent

        return None

    def parse_config_file(self, config_path: str) -> Dict[str, Any]:
        """Parse the .spartan configuration file.

        Reads and parses the configuration file using INI format, extracts
        the provider value, and validates the configuration.

        Args:
            config_path: Path to the configuration file.

        Returns:
            Dictionary of configuration values.

        Raises:
            ConfigParseError: If file cannot be parsed due to invalid INI syntax.
            ConfigValidationError: If configuration values are invalid.
            ConfigPermissionError: If file cannot be read due to permissions.

        Example:
            >>> config = ConfigService.get_instance()
            >>> config_data = config.parse_config_file('/path/to/.spartan')
            >>> print(config_data['provider'])  # 'aws' or 'gcp'
        """
        config_parser = configparser.ConfigParser()
        errors = []

        try:
            # Read the configuration file
            config_parser.read(config_path)

            # Handle empty files - return defaults
            if not config_parser.sections():
                return {"provider": "gcp"}

            # Extract provider value from [default] section
            # If [default] section is missing, use default provider
            if not config_parser.has_section("default"):
                return {"provider": "gcp"}

            # Get provider value, default to 'gcp' if missing
            provider = config_parser.get("default", "provider", fallback="gcp")

            # Validate the provider value and collect errors
            if not self.validate_provider(provider):
                errors.append(
                    f"Invalid provider '{provider}' in configuration. "
                    f"Valid options are: 'aws', 'gcp'."
                )

            # If there are validation errors, raise them all together
            if errors:
                raise ConfigValidationError("\n".join(errors))

            return {"provider": provider}

        except PermissionError as e:
            raise ConfigPermissionError(
                f"Cannot read configuration file '{config_path}': Permission denied. "
                f"Please check file permissions."
            ) from e
        except configparser.Error as e:
            # Extract line number if available
            line_info = f"line {e.lineno}" if hasattr(e, "lineno") else "unknown line"
            raise ConfigParseError(
                f"Invalid configuration file syntax at {line_info}: {str(e)}. "
                f"Please check INI format."
            ) from e

    def validate_provider(self, provider: str) -> bool:
        """Validate that provider is either 'aws' or 'gcp'.

        Args:
            provider: Provider string to validate.

        Returns:
            True if valid (provider is 'aws' or 'gcp'), False otherwise.

        Example:
            >>> config = ConfigService.get_instance()
            >>> config.validate_provider('aws')  # True
            >>> config.validate_provider('azure')  # False
        """
        return provider in ("aws", "gcp")

    def _load_configuration(self) -> None:
        """Load configuration from disk (internal method).

        Discovers the configuration file, parses it if found, and caches
        the provider value. Uses default provider ('gcp') if no file is found.
        """
        # Discover configuration file
        config_path = self.discover_config_file()

        if config_path:
            # Parse and validate configuration file
            config_data = self.parse_config_file(config_path)
            self._provider = config_data["provider"]
            self._config_path = config_path
        else:
            # Use defaults when no config file found
            self._provider = "gcp"
            self._config_path = None

    def get_provider(self) -> str:
        """Get the configured cloud provider.

        Returns:
            Provider string ('aws' or 'gcp').

        Example:
            >>> config = ConfigService.get_instance()
            >>> provider = config.get_provider()
            >>> print(provider)  # 'aws' or 'gcp'
        """
        return self._provider

    def get_config_path(self) -> Optional[str]:
        """Get the path to the loaded configuration file.

        Returns:
            Path to config file or None if using defaults.

        Example:
            >>> config = ConfigService.get_instance()
            >>> path = config.get_config_path()
            >>> if path:
            ...     print(f"Using config from: {path}")
            ... else:
            ...     print("Using default configuration")
        """
        return self._config_path

    def reload(self) -> None:
        """Reload configuration from disk.

        Clears the cached configuration and re-runs discovery and parsing.
        Useful when the configuration file has been modified.

        Example:
            >>> config = ConfigService.get_instance()
            >>> config.reload()  # Re-read configuration from disk
        """
        # Clear cached configuration
        self._config = configparser.ConfigParser()
        self._config_path = None
        self._provider = "gcp"

        # Re-run discovery and parsing
        self._load_configuration()
