"""Base handler service module.

This module provides the abstract base class for handler services that manage
serverless functions across different cloud providers (AWS Lambda, GCP Cloud Functions).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.console import Console


class BaseHandlerService(ABC):
    """Abstract base class for handler services.

    This class defines the common interface that all handler service implementations
    must follow, ensuring consistent behavior across different cloud providers.
    """

    def __init__(self):
        """Initialize the base handler service."""
        self.provider: Optional[str] = None  # Set by subclasses
        self.console = Console()

    @abstractmethod
    def list_handlers(
        self,
        output_format: str = "table",
        prefix_filter: Optional[str] = None,
        regex_match: Optional[str] = None,
        contains_filter: Optional[str] = None,
        runtime_filter: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        limit: Optional[int] = None,
        show_filters: bool = False,
        save_to: Optional[str] = None,
    ) -> None:
        """List all serverless functions with filtering and sorting.

        Args:
            output_format: Output format (table, json, yaml, markdown, csv)
            prefix_filter: Filter by name prefix
            regex_match: Filter by regex pattern
            contains_filter: Filter by substring
            runtime_filter: Filter by runtime
            sort_by: Field to sort by (name, runtime, memory, timeout, modified)
            sort_order: Sort order (asc, desc)
            limit: Maximum number of results to return
            show_filters: Whether to show applied filters in output
            save_to: File path to save output
        """
        pass

    @abstractmethod
    def describe_handler(
        self,
        function_name: str,
        output_format: str = "table",
    ) -> None:
        """Describe a specific serverless function.

        Args:
            function_name: Name of the function to describe
            output_format: Output format (table, json, yaml, text, markdown)
        """
        pass

    @abstractmethod
    def download_function(
        self,
        function_name: str,
        version: str = "$LATEST",
        output_path: Optional[str] = None,
        extract: bool = False,
        check_integrity: bool = False,
        include_config: bool = False,
    ) -> bool:
        """Download function source code.

        Args:
            function_name: Name of the function to download
            version: Function version (AWS: $LATEST, GCP: version number)
            output_path: Output file path for the downloaded code
            extract: Whether to extract the ZIP file after download
            check_integrity: Whether to verify download integrity
            include_config: Whether to save function configuration

        Returns:
            True if download was successful, False otherwise
        """
        pass

    @abstractmethod
    def create_handler_file(self) -> None:
        """Create a new handler file from stub template.

        Creates a handler file in the handlers/ directory using the appropriate
        stub template based on the trigger type and cloud provider.
        """
        pass

    @abstractmethod
    def delete_handler_file(self) -> None:
        """Delete an existing handler file.

        Deletes a handler file from the handlers/ directory.
        """
        pass

    # Common utility methods (implemented in base class)

    def _validate_output_format(self, output_format: str) -> str:
        """Validate and normalize output format.

        Args:
            output_format: The output format to validate

        Returns:
            The normalized output format (lowercase)

        Raises:
            ValueError: If the output format is invalid
        """
        valid_formats = ["table", "json", "yaml", "markdown", "csv", "text"]
        output_format = output_format.lower()
        if output_format not in valid_formats:
            self.console.print(
                f"[red]Invalid output format '{output_format}'. "
                f"Valid formats: {', '.join(valid_formats)}[/red]"
            )
            raise ValueError(f"Invalid output format: {output_format}")
        return output_format

    def _format_date(self, date_obj: Optional[Any]) -> str:
        """Format date object to readable format.

        Args:
            date_obj: Date object to format (datetime, string, or None)

        Returns:
            Formatted date string in YYYY-MM-DD HH:MM:SS format,
            or "N/A" if date_obj is None
        """
        if date_obj is None:
            return "N/A"

        # If it's already a string, return it
        if isinstance(date_obj, str):
            return date_obj

        # If it's a datetime object, format it
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")

        # Try to convert to datetime if it has a ToDatetime method (protobuf)
        if hasattr(date_obj, "ToDatetime"):
            dt = date_obj.ToDatetime()
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        # Fallback: convert to string
        return str(date_obj)

    def _save_to_file(self, content: str, file_path: str) -> None:
        """Save content to a file.

        Args:
            content: Content to save
            file_path: Path to the file

        Raises:
            PermissionError: If permission is denied
            IOError: If file write fails
        """
        try:
            with open(file_path, "w") as f:
                f.write(content)
            self.console.print(f"[green]✓ File saved to {file_path}[/green]")
        except PermissionError:
            self.console.print(
                f"[red]Error: Permission denied writing to {file_path}[/red]"
            )
            raise
        except IOError as e:
            self.console.print(f"[red]Error: Failed to write file: {e}[/red]")
            raise
