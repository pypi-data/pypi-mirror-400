"""GCP Cloud Functions handler service.

This module provides GCP Cloud Functions management capabilities
including file creation, deletion, listing, and downloading.
"""

import csv
import hashlib
import io
import json
import os
import re
import zipfile
from datetime import datetime
from typing import Optional

try:
    from google.api_core import exceptions as google_exceptions
    from google.auth import exceptions as auth_exceptions
    from google.cloud import functions_v1, functions_v2

    GCP_AVAILABLE = True
except ImportError:
    # GCP libraries not installed - this is expected during development/testing
    GCP_AVAILABLE = False
    google_exceptions = None
    auth_exceptions = None
    functions_v1 = None
    functions_v2 = None

import requests
import yaml
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.services.handler.base import BaseHandlerService
from spartan.utils.filters import FilterUtility, SortUtility


class GCPHandlerService(BaseHandlerService):
    """Service for managing GCP Cloud Functions and handler files."""

    def __init__(
        self,
        name: str = None,
        subscribe: str = None,
        publish: str = None,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """Initialize the GCPHandlerService.

        Args:
            name: Name of the handler
            subscribe: Trigger type to subscribe to (pubsub, storage, firestore)
            publish: Target to publish to (pubsub)
            project_id: GCP project ID (if not provided, reads from environment)
            location: GCP location/region (if not provided, reads from environment)

        Raises:
            ValueError: If project ID is not provided and not found in environment
            ValueError: If GCP credentials are not configured
            ImportError: If GCP libraries are not installed
        """
        super().__init__()
        self.provider = "gcp"
        self.name = name
        self.subscribe = subscribe
        self.publish = publish

        # Get GCP project ID from parameter or environment variables
        # Check in order: parameter, GOOGLE_CLOUD_PROJECT, GCP_PROJECT, GCLOUD_PROJECT
        self.project_id = (
            project_id
            or os.environ.get("GOOGLE_CLOUD_PROJECT")
            or os.environ.get("GCP_PROJECT")
            or os.environ.get("GCLOUD_PROJECT")
        )

        if not self.project_id:
            print(
                "[red]Error: GCP project ID not provided.[/red]\n"
                "[yellow]Set one of these environment variables: "
                "GOOGLE_CLOUD_PROJECT, GCP_PROJECT, GCLOUD_PROJECT[/yellow]\n"
                "[yellow]Or pass --project-id parameter.[/yellow]"
            )
            raise ValueError("GCP project ID is required")

        # Get GCP location from parameter or environment variables
        # Check in order: parameter, GOOGLE_CLOUD_REGION, GCP_REGION, GCLOUD_REGION
        self.location = (
            location
            or os.environ.get("GOOGLE_CLOUD_REGION")
            or os.environ.get("GCP_REGION")
            or os.environ.get("GCLOUD_REGION")
            or "us-central1"  # Default location
        )

        # GCP-specific setup
        # Go up from gcp_handler.py -> handler/ -> services/ to get to spartan/
        self.home_directory = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.current_directory = os.getcwd()
        self.destination_folder = "handlers"

        # Initialize GCP Cloud Functions clients
        if not GCP_AVAILABLE:
            raise ImportError(
                "GCP Cloud Functions libraries not installed. "
                "Install with: pip install google-cloud-functions"
            )

        try:
            self.functions_client_v1 = functions_v1.CloudFunctionsServiceClient()
            self.functions_client_v2 = functions_v2.FunctionServiceClient()
        except auth_exceptions.DefaultCredentialsError:
            print(
                "[red]Error: GCP credentials not configured.[/red]\n"
                "[yellow]Run 'gcloud auth application-default login' "
                "or set GOOGLE_APPLICATION_CREDENTIALS environment variable.[/yellow]"
            )
            raise ValueError(
                "GCP credentials not configured. "
                "Run 'gcloud auth application-default login'"
            )
        except Exception as e:
            print(f"[red]Error initializing GCP Cloud Functions clients: {e}[/red]")
            raise

        # File-related attributes (if name provided)
        if name:
            self.file_name = re.sub(r"\d", "", f"{self.name}.py").lower()
            self.file_path = os.path.join(
                self.current_directory, self.destination_folder, self.file_name
            )
            self.stub_folder = os.path.join(
                self.home_directory, "stubs", "handler", "gcp"
            )
            self.source_stub = self.determine_source_stub()

    def determine_source_stub(self):
        """Determine the appropriate source stub for the handler.

        Returns:
            Path to the appropriate stub template file
        """
        if self.subscribe == "pubsub":
            return os.path.join(self.stub_folder, "pubsub.stub")
        elif self.subscribe == "storage":
            return os.path.join(self.stub_folder, "storage.stub")
        elif self.subscribe == "firestore":
            return os.path.join(self.stub_folder, "firestore.stub")
        elif self.subscribe == "scheduler":
            return os.path.join(self.stub_folder, "scheduler.stub")
        elif self.subscribe == "http" or self.publish:
            return os.path.join(self.stub_folder, "http.stub")
        else:
            return os.path.join(self.stub_folder, "default.stub")

    def list_handlers(  # noqa: C901
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
        """List all GCP Cloud Functions with filtering and sorting.

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
        try:
            # Validate output format
            output_format = self._validate_output_format(output_format)

            # Validate sort field
            valid_sort_fields = ["name", "runtime", "memory", "timeout", "modified"]
            is_valid, error = SortUtility.validate_sort_field(
                sort_by, valid_sort_fields
            )
            if not is_valid:
                print(f"[red]{error}[/red]")
                return

            # Validate sort order
            if sort_order.lower() not in ["asc", "desc"]:
                print(
                    f"[red]Invalid sort order '{sort_order}'. Valid options: asc, desc[/red]"
                )
                return

            # Validate limit
            if limit is not None and limit <= 0:
                print(f"[red]Limit must be a positive integer, got: {limit}[/red]")
                return

            # Validate all filters
            is_valid, error = FilterUtility.validate_all_filters(
                prefix_filter=prefix_filter, regex_filter=regex_match
            )
            if not is_valid:
                print(f"[red]{error}[/red]")
                return

            if output_format == "table":
                print("[blue]Fetching Cloud Functions...[/blue]")

            # Build parent path for listing functions
            parent = f"projects/{self.project_id}/locations/{self.location}"

            # Create ListFunctionsRequest for v2 API
            request = functions_v2.ListFunctionsRequest(parent=parent)

            # Get all functions using pagination
            functions = []
            try:
                # Call functions_client_v2.list_functions() with pagination
                page_result = self.functions_client_v2.list_functions(request=request)

                # Handle pagination
                for function in page_result:
                    functions.append(function)

            except google_exceptions.NotFound:
                print(
                    f"[red]Error: Location '{self.location}' not found in project '{self.project_id}'.[/red]"
                )
                return
            except google_exceptions.PermissionDenied as e:
                print(
                    f"[red]Error: Permission denied accessing GCP Cloud Functions.[/red]\n"
                    f"[yellow]Details: {e}[/yellow]\n"
                    f"[yellow]Required permission: cloudfunctions.functions.list[/yellow]"
                )
                return
            except google_exceptions.GoogleAPICallError as e:
                print(f"[red]GCP API Error: {e}[/red]")
                return

            if not functions:
                self._handle_no_functions_found(output_format)
                return

            # Process function data into common structure
            function_data = []
            for function in functions:
                # Extract function name from full resource path
                # Format: projects/{project}/locations/{location}/functions/{function}
                function_name = function.name.split("/")[-1]

                # Get runtime
                runtime = (
                    function.build_config.runtime
                    if hasattr(function, "build_config")
                    and function.build_config
                    and function.build_config.runtime
                    else "N/A"
                )

                # Get memory (service_config.available_memory for v2)
                memory = (
                    function.service_config.available_memory
                    if hasattr(function, "service_config")
                    and function.service_config
                    and hasattr(function.service_config, "available_memory")
                    else "256Mi"
                )
                # Convert memory from string format like "256Mi" to MB
                if isinstance(memory, str) and memory.endswith("Mi"):
                    memory = int(memory[:-2])
                elif isinstance(memory, str) and memory.endswith("Gi"):
                    memory = int(memory[:-2]) * 1024
                else:
                    memory = 256

                # Get timeout (service_config.timeout_seconds for v2)
                timeout = (
                    function.service_config.timeout_seconds
                    if hasattr(function, "service_config")
                    and function.service_config
                    and hasattr(function.service_config, "timeout_seconds")
                    else 60
                )

                # Get last update time
                update_time = (
                    function.update_time if hasattr(function, "update_time") else None
                )

                function_info = {
                    "name": function_name,
                    "runtime": runtime,
                    "memory": memory,
                    "timeout": timeout,
                    "modified": self._format_date(update_time),
                    "LastModified": update_time,  # Keep original for sorting
                    "description": (
                        function.description if hasattr(function, "description") else ""
                    ),
                    "handler": (
                        function.build_config.entry_point
                        if hasattr(function, "build_config")
                        and function.build_config
                        and hasattr(function.build_config, "entry_point")
                        else "N/A"
                    ),
                    "arn": function.name,  # Full resource name
                    "role": (
                        function.service_config.service_account_email
                        if hasattr(function, "service_config")
                        and function.service_config
                        and hasattr(function.service_config, "service_account_email")
                        else "N/A"
                    ),
                    "package_type": "2nd gen",  # v2 API is 2nd generation
                }
                function_data.append(function_info)

            # Apply filters using the filter utility
            filters = {}
            if prefix_filter:
                filters["prefix"] = {"field": "name", "value": prefix_filter}
            if regex_match:
                filters["regex"] = {"field": "name", "value": regex_match}
            if contains_filter:
                filters["contains"] = {
                    "field": "name",
                    "value": contains_filter,
                    "case_sensitive": False,
                }
            if runtime_filter:
                filters["status"] = {"field": "runtime", "value": runtime_filter}

            if filters:
                function_data = FilterUtility.apply_multiple_filters(
                    function_data, filters
                )

            # Apply sorting
            reverse = sort_order.lower() == "desc"
            if sort_by == "modified":
                function_data = SortUtility.sort_by_date(
                    function_data, "LastModified", reverse=reverse
                )
            elif sort_by == "name":
                function_data = SortUtility.sort_items(
                    function_data, "name", reverse=reverse, case_sensitive=False
                )
            elif sort_by == "runtime":
                function_data = SortUtility.sort_items(
                    function_data, "runtime", reverse=reverse, case_sensitive=False
                )
            elif sort_by == "memory":
                function_data = SortUtility.sort_items(
                    function_data, "memory", reverse=reverse
                )
            elif sort_by == "timeout":
                function_data = SortUtility.sort_items(
                    function_data, "timeout", reverse=reverse
                )

            # Apply limit
            if limit:
                function_data = function_data[:limit]

            # Check if any functions remain after filtering
            if not function_data:
                self._handle_no_functions_after_filter(
                    output_format,
                    prefix_filter,
                    regex_match,
                    contains_filter,
                    runtime_filter,
                )
                return

            # Prepare filter info for display/saving
            applied_filters = {}
            if prefix_filter:
                applied_filters["prefix"] = prefix_filter
            if regex_match:
                applied_filters["regex"] = regex_match
            if contains_filter:
                applied_filters["contains"] = contains_filter
            if runtime_filter:
                applied_filters["runtime"] = runtime_filter
            if limit:
                applied_filters["limit"] = str(limit)

            # Output in requested format
            if output_format == "csv":
                self._print_functions_csv(
                    function_data, show_filters, applied_filters, save_to
                )
            elif output_format == "table":
                self._print_functions_table(
                    function_data, show_filters, applied_filters, sort_by, sort_order
                )
            elif output_format == "json":
                output_data = {
                    "functions": function_data,
                    "count": len(function_data),
                    "sort": {"by": sort_by, "order": sort_order},
                }
                if show_filters and applied_filters:
                    output_data["applied_filters"] = applied_filters

                output_str = json.dumps(output_data, indent=2, default=str)
                if save_to:
                    self._save_to_file(output_str, save_to)
                else:
                    print(output_str)
            elif output_format == "yaml":
                output_data = {
                    "functions": function_data,
                    "count": len(function_data),
                    "sort": {"by": sort_by, "order": sort_order},
                }
                if show_filters and applied_filters:
                    output_data["applied_filters"] = applied_filters

                output_str = yaml.dump(output_data, default_flow_style=False)
                if save_to:
                    self._save_to_file(output_str, save_to)
                else:
                    print(output_str)
            elif output_format == "markdown":
                self._print_functions_markdown(
                    function_data,
                    show_filters,
                    applied_filters,
                    sort_by,
                    sort_order,
                    save_to,
                )

        except Exception as e:
            print(f"[red]Error listing handlers: {e}[/red]")

    def describe_handler(
        self,
        function_name: str,
        output_format: str = "table",
    ) -> None:
        """Describe a specific GCP Cloud Function.

        Args:
            function_name: Name of the function to describe
            output_format: Output format (table, json, yaml, text, markdown)
        """
        try:
            # Validate output format
            output_format = self._validate_output_format(output_format)

            # Build function path: projects/{project_id}/locations/{location}/functions/{name}
            function_path = f"projects/{self.project_id}/locations/{self.location}/functions/{function_name}"

            # Create GetFunctionRequest for v2 API
            request = functions_v2.GetFunctionRequest(name=function_path)

            # Call functions_client_v2.get_function()
            try:
                function = self.functions_client_v2.get_function(request=request)
            except google_exceptions.NotFound:
                print(
                    f"[red]Error: Function '{function_name}' not found in project '{self.project_id}' location '{self.location}'.[/red]"
                )
                return
            except google_exceptions.PermissionDenied as e:
                print(
                    f"[red]Error: Permission denied accessing Cloud Function '{function_name}'.[/red]\n"
                    f"[yellow]Details: {e}[/yellow]\n"
                    f"[yellow]Required permission: cloudfunctions.functions.get[/yellow]"
                )
                return
            except google_exceptions.GoogleAPICallError as e:
                print(f"[red]GCP API Error: {e}[/red]")
                return

            # Extract function information and GCP-specific fields
            function_details = self._extract_function_details(function)

            # Output in requested format
            if output_format == "table":
                self._print_function_details_table(function_details)
            elif output_format == "json":
                print(json.dumps(function_details, indent=2, default=str))
            elif output_format == "yaml":
                try:
                    print(yaml.dump(function_details, default_flow_style=False))
                except Exception as e:
                    print(f"Error generating YAML output: {e}")
                    print(json.dumps(function_details, indent=2, default=str))
            elif output_format == "text":
                self._print_function_details_text(function_details)
            elif output_format == "markdown":
                self._print_function_details_markdown(function_details)

        except Exception as e:
            print(f"[red]Error describing function: {e}[/red]")

    def _extract_function_details(self, function) -> dict:
        """Extract detailed information from a GCP Cloud Function.

        Args:
            function: GCP Cloud Function object

        Returns:
            Dictionary containing function details including GCP-specific fields
        """
        try:
            # Extract function name from full resource path
            function_name = function.name.split("/")[-1]

            # Basic function information
            details = {
                "name": function_name,
                "resource_name": function.name,
                "runtime": (
                    function.build_config.runtime
                    if hasattr(function, "build_config")
                    and function.build_config
                    and hasattr(function.build_config, "runtime")
                    else "N/A"
                ),
                "entry_point": (
                    function.build_config.entry_point
                    if hasattr(function, "build_config")
                    and function.build_config
                    and hasattr(function.build_config, "entry_point")
                    else "N/A"
                ),
            }

            # Memory handling for v2 API
            if (
                hasattr(function, "service_config")
                and function.service_config
                and hasattr(function.service_config, "available_memory")
            ):
                memory = function.service_config.available_memory
                if isinstance(memory, str) and memory.endswith("Mi"):
                    details["memory"] = int(memory[:-2])
                elif isinstance(memory, str) and memory.endswith("Gi"):
                    details["memory"] = int(memory[:-2]) * 1024
                else:
                    details["memory"] = 256
            else:
                details["memory"] = 256

            # Timeout handling for v2 API
            details["timeout"] = (
                function.service_config.timeout_seconds
                if hasattr(function, "service_config")
                and function.service_config
                and hasattr(function.service_config, "timeout_seconds")
                else 60
            )

            details["description"] = (
                function.description if hasattr(function, "description") else ""
            )

            # Timestamps
            if hasattr(function, "update_time") and function.update_time:
                details["updated"] = self._format_date(function.update_time)
                details["updated_raw"] = function.update_time
            else:
                details["updated"] = "N/A"

            # State
            if hasattr(function, "state"):
                # State is an enum, convert to string
                details["state"] = (
                    str(function.state).split(".")[-1] if function.state else "UNKNOWN"
                )
            else:
                details["state"] = "UNKNOWN"

            # Service account
            details["service_account"] = (
                function.service_config.service_account_email
                if hasattr(function, "service_config")
                and function.service_config
                and hasattr(function.service_config, "service_account_email")
                else "N/A"
            )

            # Generation (2nd gen for v2 API)
            details["generation"] = "2nd gen"

            # Build configuration
            build_config = {}
            if hasattr(function, "build_config") and function.build_config:
                if (
                    hasattr(function.build_config, "source")
                    and function.build_config.source
                ):
                    if (
                        hasattr(function.build_config.source, "storage_source")
                        and function.build_config.source.storage_source
                    ):
                        build_config["source_archive_url"] = (
                            f"gs://{function.build_config.source.storage_source.bucket}/{function.build_config.source.storage_source.object}"
                        )
                if (
                    hasattr(function.build_config, "build")
                    and function.build_config.build
                ):
                    build_config["build_id"] = function.build_config.build
            details["build_config"] = build_config if build_config else "N/A"

            # Service configuration
            service_config = {
                "memory": f"{details['memory']}MB",
                "timeout": f"{details['timeout']}s",
                "runtime": details["runtime"],
                "entry_point": details["entry_point"],
            }
            if hasattr(function, "service_config") and function.service_config:
                if hasattr(function.service_config, "max_instance_count"):
                    service_config["max_instances"] = (
                        function.service_config.max_instance_count
                    )
                if hasattr(function.service_config, "min_instance_count"):
                    service_config["min_instances"] = (
                        function.service_config.min_instance_count
                    )
            details["service_config"] = service_config

            # Trigger configuration
            trigger_config = {}
            trigger_type = "UNKNOWN"

            # For v2 API, check event_trigger first
            if hasattr(function, "event_trigger") and function.event_trigger:
                trigger_type = "EVENT"
                if hasattr(function.event_trigger, "event_type"):
                    trigger_config["event_type"] = function.event_trigger.event_type
                    # Determine more specific trigger type from event type
                    if "pubsub" in function.event_trigger.event_type.lower():
                        trigger_type = "PUBSUB"
                    elif "storage" in function.event_trigger.event_type.lower():
                        trigger_type = "STORAGE"
                    elif "firestore" in function.event_trigger.event_type.lower():
                        trigger_type = "FIRESTORE"
                if hasattr(function.event_trigger, "trigger"):
                    trigger_config["trigger"] = function.event_trigger.trigger
            else:
                # Default to HTTP for v2 API
                trigger_type = "HTTP"
                trigger_config["url"] = (
                    f"https://{function.service_config.uri}"
                    if hasattr(function, "service_config")
                    and function.service_config
                    and hasattr(function.service_config, "uri")
                    else "N/A"
                )

            details["trigger_type"] = trigger_type
            details["trigger_config"] = trigger_config if trigger_config else "N/A"

            # Environment variables (mask sensitive values)
            details["environment_variables"] = {}

            # Ingress settings
            if (
                hasattr(function, "service_config")
                and function.service_config
                and hasattr(function.service_config, "ingress_settings")
            ):
                details["ingress_settings"] = (
                    str(function.service_config.ingress_settings).split(".")[-1]
                    if function.service_config.ingress_settings
                    else "ALLOW_ALL"
                )
            else:
                details["ingress_settings"] = "ALLOW_ALL"

            # VPC connector
            if (
                hasattr(function, "service_config")
                and function.service_config
                and hasattr(function.service_config, "vpc_connector")
                and function.service_config.vpc_connector
            ):
                details["vpc_connector"] = function.service_config.vpc_connector
            else:
                details["vpc_connector"] = "N/A"

            # Labels
            details["labels"] = {}

            return details
        except Exception as e:
            # Return minimal details if extraction fails
            function_name = (
                function.name.split("/")[-1] if hasattr(function, "name") else "unknown"
            )
            return {
                "name": function_name,
                "resource_name": getattr(function, "name", "unknown"),
                "runtime": "N/A",
                "entry_point": "N/A",
                "memory": 256,
                "timeout": 60,
                "description": "",
                "updated": "N/A",
                "state": "UNKNOWN",
                "service_account": "N/A",
                "generation": "2nd gen",
                "build_config": "N/A",
                "service_config": {
                    "memory": "256MB",
                    "timeout": "60s",
                    "runtime": "N/A",
                    "entry_point": "N/A",
                },
                "trigger_type": "HTTP",
                "trigger_config": "N/A",
                "environment_variables": {},
                "ingress_settings": "ALLOW_ALL",
                "vpc_connector": "N/A",
                "labels": {},
            }

    def _print_function_details_table(self, details: dict) -> None:
        """Print function details in a formatted table.

        Args:
            details: Dictionary containing function details
        """
        # Create main info table
        table = Table(
            show_header=False,
            box=box.ROUNDED,
            border_style="cyan",
            padding=(0, 1),
        )
        table.add_column("Property", style="bold cyan", no_wrap=True)
        table.add_column("Value", style="white")

        # Basic information
        self.console.print(
            f"\n[bold cyan]Cloud Function: {details['name']}[/bold cyan]\n"
        )

        table.add_row("Resource Name", details["resource_name"])
        table.add_row("Runtime", details["runtime"])
        table.add_row("Entry Point", details["entry_point"])
        table.add_row("Memory", f"{details['memory']}MB")
        table.add_row("Timeout", f"{details['timeout']}s")
        table.add_row("State", details["state"])
        table.add_row("Generation", details["generation"])
        table.add_row("Updated", details["updated"])

        if details["description"]:
            table.add_row("Description", details["description"])

        table.add_row("Service Account", details["service_account"])

        self.console.print(table)

        # Trigger configuration
        if details["trigger_config"] != "N/A":
            self.console.print(
                f"\n[bold cyan]Trigger Configuration ({details['trigger_type']})[/bold cyan]"
            )
            trigger_table = Table(show_header=False, box=box.SIMPLE, border_style="dim")
            trigger_table.add_column("Property", style="cyan")
            trigger_table.add_column("Value", style="white")

            for key, value in details["trigger_config"].items():
                trigger_table.add_row(key, str(value))

            self.console.print(trigger_table)

        # Service configuration
        self.console.print("\n[bold cyan]Service Configuration[/bold cyan]")
        service_table = Table(show_header=False, box=box.SIMPLE, border_style="dim")
        service_table.add_column("Property", style="cyan")
        service_table.add_column("Value", style="white")

        for key, value in details["service_config"].items():
            service_table.add_row(key, str(value))

        self.console.print(service_table)

        # Build configuration
        if details["build_config"] != "N/A":
            self.console.print("\n[bold cyan]Build Configuration[/bold cyan]")
            build_table = Table(show_header=False, box=box.SIMPLE, border_style="dim")
            build_table.add_column("Property", style="cyan")
            build_table.add_column("Value", style="white")

            for key, value in details["build_config"].items():
                if isinstance(value, dict):
                    build_table.add_row(key, json.dumps(value, indent=2))
                else:
                    build_table.add_row(key, str(value))

            self.console.print(build_table)

        # Network settings
        self.console.print("\n[bold cyan]Network Settings[/bold cyan]")
        network_table = Table(show_header=False, box=box.SIMPLE, border_style="dim")
        network_table.add_column("Property", style="cyan")
        network_table.add_column("Value", style="white")

        network_table.add_row("Ingress Settings", details["ingress_settings"])
        network_table.add_row("VPC Connector", details["vpc_connector"])

        self.console.print(network_table)

        # Environment variables
        if details["environment_variables"]:
            self.console.print("\n[bold cyan]Environment Variables[/bold cyan]")
            env_table = Table(show_header=False, box=box.SIMPLE, border_style="dim")
            env_table.add_column("Key", style="cyan")
            env_table.add_column("Value", style="white")

            for key, value in details["environment_variables"].items():
                env_table.add_row(key, value)

            self.console.print(env_table)

        # Labels
        if details["labels"]:
            self.console.print("\n[bold cyan]Labels[/bold cyan]")
            labels_table = Table(show_header=False, box=box.SIMPLE, border_style="dim")
            labels_table.add_column("Key", style="cyan")
            labels_table.add_column("Value", style="white")

            for key, value in details["labels"].items():
                labels_table.add_row(key, value)

            self.console.print(labels_table)

        self.console.print()

    def _print_function_details_text(self, details: dict) -> None:
        """Print function details in plain text format.

        Args:
            details: Dictionary containing function details
        """
        print(f"Cloud Function: {details['name']}")
        print("=" * 60)
        print(f"Resource Name: {details['resource_name']}")
        print(f"Runtime: {details['runtime']}")
        print(f"Entry Point: {details['entry_point']}")
        print(f"Memory: {details['memory']}MB")
        print(f"Timeout: {details['timeout']}s")
        print(f"State: {details['state']}")
        print(f"Generation: {details['generation']}")
        print(f"Updated: {details['updated']}")

        if details["description"]:
            print(f"Description: {details['description']}")

        print(f"Service Account: {details['service_account']}")

        # Trigger configuration
        if details["trigger_config"] != "N/A":
            print(f"\nTrigger Configuration ({details['trigger_type']}):")
            print("-" * 60)
            for key, value in details["trigger_config"].items():
                print(f"  {key}: {value}")

        # Service configuration
        print("\nService Configuration:")
        print("-" * 60)
        for key, value in details["service_config"].items():
            print(f"  {key}: {value}")

        # Build configuration
        if details["build_config"] != "N/A":
            print("\nBuild Configuration:")
            print("-" * 60)
            for key, value in details["build_config"].items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"  {key}: {value}")

        # Network settings
        print("\nNetwork Settings:")
        print("-" * 60)
        print(f"  Ingress Settings: {details['ingress_settings']}")
        print(f"  VPC Connector: {details['vpc_connector']}")

        # Environment variables
        if details["environment_variables"]:
            print("\nEnvironment Variables:")
            print("-" * 60)
            for key, value in details["environment_variables"].items():
                print(f"  {key}: {value}")

        # Labels
        if details["labels"]:
            print("\nLabels:")
            print("-" * 60)
            for key, value in details["labels"].items():
                print(f"  {key}: {value}")

    def _print_function_details_markdown(self, details: dict) -> None:
        """Print function details in Markdown format.

        Args:
            details: Dictionary containing function details
        """
        lines = []
        lines.append(f"# Cloud Function: {details['name']}")
        lines.append("")

        # Basic information
        lines.append("## Basic Information")
        lines.append("")
        lines.append(f"- **Resource Name:** {details['resource_name']}")
        lines.append(f"- **Runtime:** {details['runtime']}")
        lines.append(f"- **Entry Point:** {details['entry_point']}")
        lines.append(f"- **Memory:** {details['memory']}MB")
        lines.append(f"- **Timeout:** {details['timeout']}s")
        lines.append(f"- **State:** {details['state']}")
        lines.append(f"- **Generation:** {details['generation']}")
        lines.append(f"- **Updated:** {details['updated']}")

        if details["description"]:
            lines.append(f"- **Description:** {details['description']}")

        lines.append(f"- **Service Account:** {details['service_account']}")
        lines.append("")

        # Trigger configuration
        if details["trigger_config"] != "N/A":
            lines.append(f"## Trigger Configuration ({details['trigger_type']})")
            lines.append("")
            for key, value in details["trigger_config"].items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        # Service configuration
        lines.append("## Service Configuration")
        lines.append("")
        for key, value in details["service_config"].items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")

        # Build configuration
        if details["build_config"] != "N/A":
            lines.append("## Build Configuration")
            lines.append("")
            for key, value in details["build_config"].items():
                if isinstance(value, dict):
                    lines.append(f"- **{key}:**")
                    for k, v in value.items():
                        lines.append(f"  - **{k}:** {v}")
                else:
                    lines.append(f"- **{key}:** {value}")
            lines.append("")

        # Network settings
        lines.append("## Network Settings")
        lines.append("")
        lines.append(f"- **Ingress Settings:** {details['ingress_settings']}")
        lines.append(f"- **VPC Connector:** {details['vpc_connector']}")
        lines.append("")

        # Environment variables
        if details["environment_variables"]:
            lines.append("## Environment Variables")
            lines.append("")
            for key, value in details["environment_variables"].items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        # Labels
        if details["labels"]:
            lines.append("## Labels")
            lines.append("")
            for key, value in details["labels"].items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        print("\n".join(lines))

    def download_function(
        self,
        function_name: str,
        version: str = "$LATEST",
        output_path: Optional[str] = None,
        extract: bool = False,
        check_integrity: bool = False,
        include_config: bool = False,
    ) -> bool:
        """Download GCP Cloud Function source code.

        Args:
            function_name: Name of the function to download
            version: Function version (GCP: version number)
            output_path: Output file path for the downloaded code
            extract: Whether to extract the ZIP file after download
            check_integrity: Whether to verify download integrity
            include_config: Whether to save function configuration

        Returns:
            True if download was successful, False otherwise
        """
        console = Console()

        try:
            # Subtask 9.1: Implement basic download functionality
            # Build function path: projects/{project_id}/locations/{location}/functions/{name}
            function_path = f"projects/{self.project_id}/locations/{self.location}/functions/{function_name}"

            console.print(f"[blue]Downloading Cloud Function: {function_name}[/blue]")
            console.print(f"[dim]Project: {self.project_id}[/dim]")
            console.print(f"[dim]Location: {self.location}[/dim]")

            # Create GetFunctionRequest for v2 API
            request = functions_v2.GetFunctionRequest(name=function_path)

            # Call get_function() to get function details including download URL
            try:
                function = self.functions_client_v2.get_function(request=request)
            except google_exceptions.NotFound:
                console.print(
                    f"[red]✗ Function '{function_name}' not found in project '{self.project_id}' location '{self.location}'.[/red]"
                )
                return False
            except google_exceptions.PermissionDenied as e:
                console.print(
                    f"[red]✗ Permission denied accessing Cloud Function '{function_name}'.[/red]\n"
                    f"[yellow]Details: {e}[/yellow]\n"
                    f"[yellow]Required permission: cloudfunctions.functions.get[/yellow]"
                )
                return False
            except google_exceptions.GoogleAPICallError as e:
                console.print(f"[red]✗ GCP API Error: {e}[/red]")
                return False

            # Display function information
            console.print(
                f"[dim]Runtime: {function.runtime if function.runtime else 'Unknown'}[/dim]"
            )

            # Get download URL from source_archive_url
            download_url = None
            if hasattr(function, "source_archive_url") and function.source_archive_url:
                download_url = function.source_archive_url
            else:
                console.print(
                    "[red]✗ Function does not have a source archive URL. "
                    "The function may use source repository deployment.[/red]"
                )
                return False

            # Determine output path
            if output_path is None:
                output_path = f"{function_name}.zip"

            # Download source code from URL
            console.print(f"[dim]Downloading from: {download_url}[/dim]")

            try:
                response = requests.get(download_url, stream=True, timeout=30)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                console.print(f"[red]✗ Error downloading function code: {e}[/red]")
                return False

            # Calculate hash if integrity check requested (Subtask 9.3)
            file_hash = None
            gcp_hash = None
            if check_integrity:
                hash_obj = hashlib.sha256()
                # Get the hash from GCP if available
                if hasattr(function, "source_upload_url"):
                    # Note: GCP doesn't provide SHA256 in the same way as AWS
                    # We'll calculate it ourselves and display it
                    pass

            # Save as ZIP file
            try:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            if check_integrity:
                                hash_obj.update(chunk)
            except IOError as e:
                console.print(f"[red]✗ Error writing file '{output_path}': {e}[/red]")
                return False

            # Display hash if integrity check was performed (Subtask 9.3)
            if check_integrity:
                file_hash = hash_obj.hexdigest()
                console.print(f"[dim]SHA256: {file_hash}[/dim]")

            console.print(f"[green]✓ Code downloaded to: {output_path}[/green]")

            # Subtask 9.2: Implement extract functionality
            extract_dir = None
            if extract:
                extract_dir = output_path.replace(".zip", "_extracted")
                try:
                    with zipfile.ZipFile(output_path, "r") as zip_ref:
                        zip_ref.extractall(extract_dir)
                    console.print(f"[green]✓ Code extracted to: {extract_dir}[/green]")
                except zipfile.BadZipFile:
                    console.print(
                        f"[red]✗ Error: Downloaded file is not a valid ZIP file[/red]"
                    )
                    return False
                except IOError as e:
                    console.print(f"[red]✗ Error extracting ZIP file: {e}[/red]")
                    return False

            # Subtask 9.4: Implement config save functionality
            if include_config:
                config_path = output_path.replace(".zip", "_config.json")

                try:
                    # Extract function configuration
                    config_to_save = {
                        "FunctionName": function_name,
                        "ResourceName": function.name,
                        "Runtime": function.runtime if function.runtime else "N/A",
                        "EntryPoint": (
                            function.entry_point
                            if hasattr(function, "entry_point")
                            else "N/A"
                        ),
                        "Description": (
                            function.description
                            if hasattr(function, "description")
                            else ""
                        ),
                        "Timeout": (
                            function.timeout.seconds
                            if hasattr(function, "timeout") and function.timeout
                            else 60
                        ),
                        "MemorySize": (
                            function.available_memory_mb
                            if hasattr(function, "available_memory_mb")
                            else 256
                        ),
                        "ServiceAccount": (
                            function.service_account_email
                            if hasattr(function, "service_account_email")
                            else "N/A"
                        ),
                        "Environment": (
                            dict(function.environment_variables)
                            if hasattr(function, "environment_variables")
                            and function.environment_variables
                            else {}
                        ),
                        "VpcConnector": (
                            function.vpc_connector
                            if hasattr(function, "vpc_connector")
                            and function.vpc_connector
                            else None
                        ),
                        "IngressSettings": (
                            str(function.ingress_settings).split(".")[-1]
                            if hasattr(function, "ingress_settings")
                            and function.ingress_settings
                            else "ALLOW_ALL"
                        ),
                        "Labels": (
                            dict(function.labels)
                            if hasattr(function, "labels") and function.labels
                            else {}
                        ),
                        "SourceArchiveUrl": (
                            function.source_archive_url
                            if hasattr(function, "source_archive_url")
                            and function.source_archive_url
                            else None
                        ),
                        "BuildId": (
                            function.build_id
                            if hasattr(function, "build_id") and function.build_id
                            else None
                        ),
                        "UpdateTime": (
                            self._format_date(function.update_time)
                            if hasattr(function, "update_time") and function.update_time
                            else None
                        ),
                        "Status": (
                            str(function.status).split(".")[-1]
                            if hasattr(function, "status") and function.status
                            else "UNKNOWN"
                        ),
                    }

                    # Add trigger configuration
                    if hasattr(function, "https_trigger") and function.https_trigger:
                        config_to_save["TriggerType"] = "HTTP"
                        config_to_save["TriggerConfig"] = {
                            "url": (
                                function.https_trigger.url
                                if hasattr(function.https_trigger, "url")
                                else "N/A"
                            ),
                            "security_level": (
                                str(function.https_trigger.security_level).split(".")[
                                    -1
                                ]
                                if hasattr(function.https_trigger, "security_level")
                                else "N/A"
                            ),
                        }
                    elif hasattr(function, "event_trigger") and function.event_trigger:
                        config_to_save["TriggerType"] = "EVENT"
                        config_to_save["TriggerConfig"] = {
                            "event_type": (
                                function.event_trigger.event_type
                                if hasattr(function.event_trigger, "event_type")
                                else "N/A"
                            ),
                            "resource": (
                                function.event_trigger.resource
                                if hasattr(function.event_trigger, "resource")
                                else "N/A"
                            ),
                            "service": (
                                function.event_trigger.service
                                if hasattr(function.event_trigger, "service")
                                else "N/A"
                            ),
                        }

                    # Include download metadata
                    download_metadata = {
                        "DownloadedAt": datetime.now().isoformat(),
                        "DownloadedFrom": download_url,
                        "OutputPath": output_path,
                    }

                    if check_integrity and file_hash:
                        download_metadata["SHA256"] = file_hash

                    if extract and extract_dir:
                        download_metadata["ExtractedTo"] = extract_dir

                    config_to_save["DownloadInfo"] = download_metadata

                    # Save as JSON file
                    with open(config_path, "w") as f:
                        json.dump(config_to_save, f, indent=2, default=str)

                    console.print(
                        f"[green]✓ Configuration saved to: {config_path}[/green]"
                    )

                except IOError as e:
                    console.print(f"[red]✗ Error saving configuration file: {e}[/red]")
                    # Don't return False here, download was successful

            # Display summary table
            summary_table = Table(title="Download Summary", box=box.SIMPLE)
            summary_table.add_column("Property", style="cyan")
            summary_table.add_column("Value", style="white")

            summary_table.add_row("Function Name", function_name)
            summary_table.add_row("Project", self.project_id)
            summary_table.add_row("Location", self.location)
            summary_table.add_row("Output Path", output_path)
            summary_table.add_row("Extracted", "Yes" if extract else "No")
            summary_table.add_row("Config Saved", "Yes" if include_config else "No")
            summary_table.add_row("Integrity Check", "Yes" if check_integrity else "No")
            if check_integrity and file_hash:
                summary_table.add_row("SHA256", file_hash[:16] + "...")

            console.print(summary_table)

            return True

        except Exception as e:
            # Subtask 9.5: Implement error handling
            console.print(f"[red]✗ Error downloading function: {e}[/red]")
            return False

    def get_environment_variables(
        self,
        function_name: str,
        format_type: str = "text",
        mask_secrets: bool = True,
        output_file: Optional[str] = None,
        single_key: Optional[str] = None,
    ) -> bool:
        """Get environment variables for a GCP Cloud Function.

        Note: GCP Cloud Functions environment variables are managed differently
        than AWS Lambda. This method provides basic functionality but full
        environment variable management should be done through the GCP Console
        or gcloud CLI.

        Args:
            function_name: Name of the Cloud Function
            format_type: Output format (text, json, yaml, env, markdown)
            mask_secrets: Whether to mask sensitive values
            output_file: Optional file to write output to
            single_key: Get only a specific environment variable

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Build function path
            function_path = f"projects/{self.project_id}/locations/{self.location}/functions/{function_name}"

            # Create GetFunctionRequest for v2 API
            request = functions_v2.GetFunctionRequest(name=function_path)

            # Get function details
            try:
                function = self.functions_client_v2.get_function(request=request)
            except google_exceptions.NotFound:
                print(
                    f"[red]Function '{function_name}' not found in project '{self.project_id}' location '{self.location}'[/red]"
                )
                return False
            except google_exceptions.PermissionDenied as e:
                print(
                    f"[red]Permission denied accessing Cloud Function '{function_name}'[/red]"
                )
                print(f"[yellow]Details: {e}[/yellow]")
                return False
            except google_exceptions.GoogleAPICallError as e:
                print(f"[red]GCP API Error: {e}[/red]")
                return False

            # Extract environment variables
            env_vars = {}
            if hasattr(function, "service_config") and function.service_config:
                if hasattr(function.service_config, "environment_variables"):
                    env_vars = dict(function.service_config.environment_variables)

            if single_key:
                if single_key in env_vars:
                    value = env_vars[single_key]
                    if mask_secrets and self._is_sensitive_value(value):
                        value = "********"
                    print(f"{single_key}={value}")
                else:
                    print(
                        f"[yellow]Environment variable '{single_key}' not found[/yellow]"
                    )
                return True

            if not env_vars:
                print("[yellow]No environment variables found[/yellow]")
                return True

            # Format and display output
            output_content = self._format_env_vars(env_vars, format_type, mask_secrets)

            if output_file:
                with open(output_file, "w") as f:
                    f.write(output_content)
                print(f"[green]✓[/green] Environment variables saved to {output_file}")
            else:
                print(output_content)

            return True

        except Exception as e:
            print(f"[red]Error getting environment variables: {e}[/red]")
            return False

    def _is_sensitive_value(self, value: str) -> bool:
        """Check if a value looks like a sensitive credential."""
        if not value:
            return False

        sensitive_patterns = [
            "password",
            "secret",
            "key",
            "token",
            "credential",
            "auth",
            "api_key",
            "access_key",
            "private",
        ]

        value_lower = value.lower()
        return (
            any(pattern in value_lower for pattern in sensitive_patterns)
            or len(value) > 50
        )

    def _format_env_vars(
        self, env_vars: dict, format_type: str, mask_secrets: bool
    ) -> str:
        """Format environment variables for output."""
        if mask_secrets:
            env_vars = {
                k: "********" if self._is_sensitive_value(v) else v
                for k, v in env_vars.items()
            }

        if format_type == "json":
            import json

            return json.dumps(env_vars, indent=2)
        elif format_type == "yaml":
            import yaml

            return yaml.dump(env_vars, default_flow_style=False)
        elif format_type == "env":
            return "\n".join([f"{k}={v}" for k, v in env_vars.items()])
        elif format_type == "markdown":
            lines = ["# Environment Variables\n"]
            for k, v in env_vars.items():
                lines.append(f"- **{k}**: `{v}`")
            return "\n".join(lines)
        else:  # text format
            lines = []
            for k, v in env_vars.items():
                lines.append(f"{k}={v}")
            return "\n".join(lines)

    def create_handler_file(self) -> None:
        """Create a new handler file from GCP stub template.

        Creates a handler file in the handlers/ directory using the appropriate
        GCP stub template based on the trigger type.

        Raises:
            FileNotFoundError: If the stub template file is not found
            IOError: If there's an error writing the handler file
        """
        console = Console()

        try:
            # Validate that handlers/ directory exists
            handlers_dir = os.path.join(self.current_directory, self.destination_folder)
            if not os.path.exists(handlers_dir):
                console.print(
                    f"[red]Error: Directory '{self.destination_folder}' does not exist.[/red]\n"
                    f"[yellow]Create it with: mkdir {self.destination_folder}[/yellow]"
                )
                return

            # Check if file already exists
            if os.path.exists(self.file_path):
                console.print(
                    f"[yellow]Warning: File '{self.file_name}' already exists at {self.file_path}[/yellow]\n"
                    f"[yellow]Delete it first or choose a different name.[/yellow]"
                )
                return

            # Check if stub template exists
            if not os.path.exists(self.source_stub):
                console.print(
                    f"[red]Error: Stub template not found at {self.source_stub}[/red]\n"
                    f"[yellow]Expected stub templates in: {self.stub_folder}[/yellow]"
                )
                return

            # Read stub template
            try:
                with open(self.source_stub, "r") as stub_file:
                    stub_content = stub_file.read()
            except IOError as e:
                console.print(f"[red]Error reading stub template: {e}[/red]")
                return

            # Write handler file
            try:
                with open(self.file_path, "w") as handler_file:
                    handler_file.write(stub_content)
            except IOError as e:
                console.print(f"[red]Error writing handler file: {e}[/red]")
                return

            # Display success message with details
            console.print(f"[green]✓ Handler file created successfully![/green]")
            console.print(f"[dim]File: {self.file_path}[/dim]")
            console.print(f"[dim]Template: {os.path.basename(self.source_stub)}[/dim]")

            # Display trigger information
            if self.subscribe:
                console.print(f"[dim]Trigger: {self.subscribe}[/dim]")
            if self.publish:
                console.print(f"[dim]Publish to: {self.publish}[/dim]")

            # Display next steps
            console.print("\n[cyan]Next steps:[/cyan]")
            console.print(f"1. Edit the handler: {self.file_path}")
            console.print(f"2. Add your business logic to the handler function")
            console.print(f"3. Deploy to GCP Cloud Functions")

        except Exception as e:
            console.print(f"[red]Error creating handler file: {e}[/red]")

    def delete_handler_file(self) -> None:
        """Delete an existing handler file.

        Deletes a handler file from the handlers/ directory.
        """
        console = Console()

        try:
            # Check if file exists
            if not os.path.exists(self.file_path):
                console.print(
                    f"[yellow]File '{self.file_name}' does not exist at {self.file_path}[/yellow]\n"
                    f"[dim]No deletion needed.[/dim]"
                )
                return

            # Delete the file
            try:
                os.remove(self.file_path)
                console.print(f"[green]✓ Handler file deleted successfully![/green]")
                console.print(f"[dim]Deleted: {self.file_path}[/dim]")
            except PermissionError:
                console.print(
                    f"[red]Error: Permission denied deleting file '{self.file_path}'[/red]\n"
                    f"[yellow]Check file permissions and try again.[/yellow]"
                )
            except OSError as e:
                console.print(f"[red]Error deleting file: {e}[/red]")

        except Exception as e:
            console.print(f"[red]Error deleting handler file: {e}[/red]")

    def _print_functions_table(
        self,
        function_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> None:
        """Print functions in a formatted table."""
        # Show filters if requested
        if show_filters and applied_filters:
            self.console.print(f"[dim]Applied filters: {applied_filters}[/dim]")
            self.console.print()

        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        table.add_column("Function Name", style="bright_blue", no_wrap=False)
        table.add_column("Runtime", style="green")
        table.add_column("Memory", style="yellow", justify="right")
        table.add_column("Timeout", style="yellow", justify="right")
        table.add_column("Modified", style="dim")

        for function in function_data:
            table.add_row(
                function["name"],
                function["runtime"],
                f"{function['memory']}MB",
                f"{function['timeout']}s",
                function["modified"],
            )

        self.console.print(
            f"🔧 [bold]Cloud Functions[/bold] ([bright_yellow]{len(function_data)}[/bright_yellow] found)"
        )
        if sort_by:
            self.console.print(f"[dim]Sorted by: {sort_by} ({sort_order})[/dim]")
        self.console.print()
        self.console.print(table)

    def _handle_no_functions_found(self, output_format: str) -> None:
        """Handle the case when no functions are found."""
        if output_format == "table":
            print(
                f"[yellow]No Cloud Functions found in project '{self.project_id}' location '{self.location}'.[/yellow]"
            )
        elif output_format == "json":
            print(json.dumps({"functions": [], "count": 0}, indent=2))
        elif output_format == "yaml":
            print(yaml.dump({"functions": [], "count": 0}))
        elif output_format == "markdown":
            print(
                f"# Cloud Functions\n\nNo functions found in project '{self.project_id}' location '{self.location}'."
            )
        elif output_format == "csv":
            print(
                "FunctionName,Runtime,Memory,Timeout,Modified,Description,Handler,ARN,Role,PackageType"
            )

    def _handle_no_functions_after_filter(
        self,
        output_format: str,
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        contains_filter: Optional[str],
        runtime_filter: Optional[str],
    ) -> None:
        """Handle the case when no functions remain after filtering."""
        filter_desc = []
        if prefix_filter:
            filter_desc.append(f"prefix '{prefix_filter}'")
        if regex_match:
            filter_desc.append(f"regex '{regex_match}'")
        if contains_filter:
            filter_desc.append(f"contains '{contains_filter}'")
        if runtime_filter:
            filter_desc.append(f"runtime '{runtime_filter}'")

        filter_str = ", ".join(filter_desc)

        if output_format == "table":
            print(
                f"[yellow]No Cloud Functions found matching filters: {filter_str}[/yellow]"
            )
        elif output_format == "json":
            print(
                json.dumps(
                    {"functions": [], "count": 0, "filters": filter_desc}, indent=2
                )
            )
        elif output_format == "yaml":
            print(yaml.dump({"functions": [], "count": 0, "filters": filter_desc}))
        elif output_format == "markdown":
            print(
                f"# Cloud Functions\n\nNo functions found matching filters: {filter_str}"
            )
        elif output_format == "csv":
            print(
                "FunctionName,Runtime,Memory,Timeout,Modified,Description,Handler,ARN,Role,PackageType"
            )

    def _print_functions_csv(
        self,
        function_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        save_to: Optional[str] = None,
    ) -> None:
        """Print functions in CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "FunctionName",
                "Runtime",
                "Memory",
                "Timeout",
                "Modified",
                "Description",
                "Handler",
                "ARN",
                "Role",
                "PackageType",
            ]
        )

        # Write data
        for function in function_data:
            writer.writerow(
                [
                    function["name"],
                    function["runtime"],
                    function["memory"],
                    function["timeout"],
                    function["modified"],
                    function["description"],
                    function["handler"],
                    function["arn"],
                    function["role"],
                    function["package_type"],
                ]
            )

        csv_content = output.getvalue()

        if save_to:
            self._save_to_file(csv_content, save_to)
        else:
            print(csv_content)

    def _print_functions_markdown(
        self,
        function_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        save_to: Optional[str] = None,
    ) -> None:
        """Print functions in Markdown format."""
        lines = []
        lines.append("# Cloud Functions")
        lines.append("")

        if show_filters and applied_filters:
            lines.append(f"**Applied filters:** {applied_filters}")
            lines.append("")

        lines.append(f"**Total:** {len(function_data)} functions")
        lines.append(f"**Sorted by:** {sort_by} ({sort_order})")
        lines.append("")

        # Table header
        lines.append("| Function Name | Runtime | Memory | Timeout | Modified |")
        lines.append("|---------------|---------|--------|---------|----------|")

        # Table rows
        for function in function_data:
            lines.append(
                f"| {function['name']} | {function['runtime']} | "
                f"{function['memory']}MB | {function['timeout']}s | {function['modified']} |"
            )

        markdown_content = "\n".join(lines)

        if save_to:
            self._save_to_file(markdown_content, save_to)
        else:
            print(markdown_content)
