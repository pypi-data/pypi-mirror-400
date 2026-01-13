"""AWS Lambda handler service.

This module provides AWS Lambda function management capabilities
including file creation, deletion, listing, and downloading.
"""

import base64
import csv
import difflib
import hashlib
import io
import json
import os
import re
import tempfile
import zipfile
from datetime import datetime
from typing import List, Optional, Union

import boto3
import requests
import yaml
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.services.handler.base import BaseHandlerService
from spartan.utils.filters import FilterUtility, SortUtility


class AWSHandlerService(BaseHandlerService):
    """Service for managing AWS Lambda functions and handler files."""

    def __init__(
        self,
        name: str = None,
        subscribe: str = None,
        publish: str = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """Initialize the AWSHandlerService.

        Args:
            name: Name of the handler
            subscribe: SQS queue to subscribe to
            publish: SQS queue to publish to
            region: AWS region
            profile: AWS profile
        """
        super().__init__()
        self.provider = "aws"
        self.name = name
        self.subscribe = subscribe
        self.publish = publish
        # Go up from aws_handler.py -> handler/ -> services/ to get to spartan/
        self.home_directory = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.current_directory = os.getcwd()
        self.destination_folder = "handlers"

        # Only set file attributes if name is provided (for creation/deletion operations)
        if name:
            self.file_name = re.sub(r"\d", "", f"{self.name}.py").lower()
            self.file_path = os.path.join(
                self.current_directory, self.destination_folder, self.file_name
            )
            self.stub_folder = os.path.join(self.home_directory, "stubs", "handler")
            self.source_stub = self.determine_source_stub()

        # AWS client setup for listing operations
        try:
            session = (
                boto3.Session(profile_name=profile) if profile else boto3.Session()
            )
            self.lambda_client = session.client("lambda", region_name=region)
        except NoCredentialsError:
            print(
                "[red]Error: AWS credentials not found. Please configure your AWS credentials.[/red]"
            )
            # Don't raise here as this might be used for file operations only
            self.lambda_client = None
        except Exception as e:
            print(f"[red]Error initializing Lambda client: {e}[/red]")
            self.lambda_client = None

    def determine_source_stub(self):
        """Determine the appropriate source stub for the handler."""
        if self.subscribe and self.publish:
            return os.path.join(self.stub_folder, "sqs_both.stub")
        elif self.subscribe:
            return (
                os.path.join(self.stub_folder, "sqs_subscribe.stub")
                if self.subscribe == "sqs"
                else os.path.join(self.stub_folder, "sns.stub")
            )
        elif self.publish:
            return os.path.join(self.stub_folder, "sqs_publish.stub")
        else:
            print("No specific option chosen.")
            return os.path.join(self.stub_folder, "default.stub")

    def create_handler_file(self):
        """Create a new handler file with appropriate configuration."""
        try:
            if not os.path.exists(
                os.path.join(self.current_directory, self.destination_folder)
            ):
                os.makedirs(
                    os.path.join(self.current_directory, self.destination_folder)
                )
                print(f"Created '{self.destination_folder}' folder.")

            if os.path.exists(self.file_path):
                with open(self.file_path, "r") as dest_file:
                    dest_content = dest_file.read()

                    if "{{ sqs_listen }}" in dest_content and self.subscribe:
                        print(
                            "Destination already has SQS subscription placeholder. Consider updating manually."
                        )
                        return

                    if "{{ sqs_publish }}" in dest_content and self.publish:
                        print(
                            "Destination already has SQS publishing placeholder. Consider updating manually."
                        )
                        return

            with open(self.source_stub, "r") as source_file:
                handler_stub_content = source_file.read()

            # Insert subscribe and publish code if necessary
            handler_stub_content = self.insert_subscribe_publish_code(
                handler_stub_content
            )

            with open(self.file_path, "w") as destination_file:
                destination_file.write(handler_stub_content)

            print(f"File '{self.file_path}' updated successfully.")

        except FileNotFoundError:
            print(f"File '{self.source_stub}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def insert_subscribe_publish_code(self, handler_stub_content):
        """Insert SQS subscribe and publish code into handler stub content."""
        if self.subscribe or (self.subscribe and self.publish):
            handler_stub_content = self.insert_code_block(
                handler_stub_content, "sqs_listen.stub", "{{ sqs_listen }}"
            )

        if self.publish or (self.subscribe and self.publish):
            handler_stub_content = self.insert_code_block(
                handler_stub_content, "sqs_trigger.stub", "{{ sqs_trigger }}"
            )

        return handler_stub_content

    def insert_code_block(self, content, stub_name, placeholder):
        """Insert a code block into content at the specified placeholder."""
        # Construct the pattern string separately to avoid backslash in f-string curly braces
        pattern = r"^( *)" + re.escape(placeholder)
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            indentation = match.group(1)
            with open(os.path.join(self.stub_folder, stub_name), "r") as insert_file:
                code_to_insert = insert_file.read()
            indented_code_to_insert = code_to_insert.replace("\n", "\n" + indentation)
            content = content.replace(placeholder, indented_code_to_insert, 1)
        return content

    def delete_handler_file(self):
        """Delete an existing handler file."""
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
                print(f'File "{self.file_path}" deleted successfully.')
            except Exception as e:
                print(f"An error occurred while trying to delete the file: {e}")
        else:
            print(f'File "{self.file_path}" does not exist. No deletion needed.')

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
        """List all Lambda functions with advanced filtering.

        Args:
            output_format: Output format (table, json, yaml, markdown, csv)
            prefix_filter: Filter functions by name prefix
            regex_match: Filter functions by regex pattern
            contains_filter: Filter functions whose names contain a substring
            runtime_filter: Filter functions by runtime (e.g., python3.11)
            sort_by: Sort by field (name, runtime, memory, timeout, modified)
            sort_order: Sort order (asc, desc)
            limit: Limit the number of results shown
            show_filters: Show which filters were applied in the output
            save_to: Save the results to a file (.json, .yaml, .csv, etc.)
        """
        if not self.lambda_client:
            print(
                "[red]Error: Lambda client not initialized. Please check your AWS credentials.[/red]"
            )
            return

        try:
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
                print("[blue]Fetching Lambda functions...[/blue]")

            # Get all functions using pagination
            functions = []
            paginator = self.lambda_client.get_paginator("list_functions")

            for page in paginator.paginate():
                functions.extend(page.get("Functions", []))

            if not functions:
                self._handle_no_functions_found(output_format)
                return

            # Process function data
            function_data = []
            for function in functions:
                function_info = {
                    "name": function.get("FunctionName", "N/A"),
                    "runtime": function.get("Runtime", "N/A"),
                    "memory": function.get("MemorySize", 0),
                    "timeout": function.get("Timeout", 0),
                    "modified": self._format_date(function.get("LastModified")),
                    "LastModified": function.get(
                        "LastModified"
                    ),  # Keep original for sorting
                    "description": function.get("Description", ""),
                    "handler": function.get("Handler", "N/A"),
                    "arn": function.get("FunctionArn", "N/A"),
                    "role": function.get("Role", "N/A"),
                    "package_type": function.get("PackageType", "N/A"),
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
                    "case_sensitive": "false",
                }
            if runtime_filter:
                filters["exact"] = {"field": "runtime", "value": runtime_filter}

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

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
        except Exception as e:
            print(f"[red]Error listing handlers: {e}[/red]")

    def describe_handler(
        self,
        function_name: str,
        output_format: str = "table",
    ) -> None:
        """Describe a specific Lambda function.

        Args:
            function_name: Name of the function to describe
            output_format: Output format (table, json, yaml, text, markdown)
        """
        # This method needs to be implemented for AWS Lambda
        # For now, we'll add a placeholder
        print(f"[yellow]describe_handler not yet implemented for AWS Lambda[/yellow]")
        pass

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
            f"🔧 [bold]Lambda Functions[/bold] ([bright_yellow]{len(function_data)}[/bright_yellow] found)"
        )
        if sort_by:
            self.console.print(f"[dim]Sorted by: {sort_by} ({sort_order})[/dim]")
        self.console.print()
        self.console.print(table)

    def _handle_no_functions_found(self, output_format: str) -> None:
        """Handle the case when no functions are found."""
        if output_format == "table":
            print("[yellow]No Lambda functions found in the current region.[/yellow]")
        elif output_format == "json":
            print(json.dumps({"functions": [], "count": 0}, indent=2))
        elif output_format == "yaml":
            print(yaml.dump({"functions": [], "count": 0}))
        elif output_format == "markdown":
            print("# Lambda Functions\n\nNo functions found in the current region.")
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

        filter_text = ", ".join(filter_desc)
        message = (
            f"No Lambda functions found matching the specified filters: {filter_text}"
        )

        if output_format == "table":
            print(f"[yellow]{message}[/yellow]")
        elif output_format == "json":
            print(
                json.dumps({"functions": [], "count": 0, "message": message}, indent=2)
            )
        elif output_format == "yaml":
            print(yaml.dump({"functions": [], "count": 0, "message": message}))
        elif output_format == "markdown":
            print(f"# Lambda Functions\n\n{message}")
        elif output_format == "csv":
            print("# " + message)
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
            if show_filters and applied_filters:
                print(f"# Applied filters: {applied_filters}")
            print(csv_content.strip())

    def _print_functions_markdown(
        self,
        function_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        save_to: Optional[str] = None,
    ) -> None:
        """Print functions in markdown format."""
        output_lines = ["# Lambda Functions\n"]

        # Print filter information if any
        if show_filters and applied_filters:
            output_lines.append("## Applied Filters\n")
            for key, value in applied_filters.items():
                output_lines.append(f"- **{key.title()}:** `{value}`")
            output_lines.append("")

        output_lines.append("## Functions\n")
        output_lines.append(
            "| Function Name | Runtime | Memory | Timeout | Modified | Description |"
        )
        output_lines.append(
            "|---------------|---------|--------|---------|----------|-------------|"
        )

        for function in function_data:
            description = (
                function["description"].replace("|", "\\|")
                if function["description"]
                else "N/A"
            )
            output_lines.append(
                f"| {function['name']} | {function['runtime']} | {function['memory']}MB | {function['timeout']}s | {function['modified']} | {description} |"
            )

        output_lines.append(f"\n**Total:** {len(function_data)} function(s)")
        if sort_by:
            output_lines.append(f"**Sorted by:** {sort_by} ({sort_order})")

        markdown_content = "\n".join(output_lines)

        if save_to:
            self._save_to_file(markdown_content, save_to)
        else:
            print(markdown_content)

    def download_function(
        self,
        function_name: str,
        version: str = "$LATEST",
        output_path: Optional[str] = None,
        extract: bool = False,
        check_integrity: bool = False,
        include_config: bool = False,
    ) -> bool:
        """Download Lambda function code and optionally configuration.

        Args:
            function_name: Name of the Lambda function
            version: Version or alias to download (default: $LATEST)
            output_path: Path to save the downloaded code
            extract: Whether to extract the ZIP file
            check_integrity: Whether to verify download integrity
            include_config: Whether to save function configuration

        Returns:
            bool: True if download successful, False otherwise
        """
        console = Console()

        try:
            # Get function details first
            function_response = self.lambda_client.get_function(
                FunctionName=function_name, Qualifier=version
            )

            function_config = function_response["Configuration"]
            code_location = function_response["Code"]["Location"]

            console.print(f"[blue]Downloading Lambda function: {function_name}[/blue]")
            console.print(f"[dim]Version: {version}[/dim]")
            console.print(
                f"[dim]Runtime: {function_config.get('Runtime', 'Unknown')}[/dim]"
            )
            console.print(
                f"[dim]Code Size: {function_config.get('CodeSize', 0)} bytes[/dim]"
            )

            # Determine output path
            if output_path is None:
                output_path = f"{function_name}_{version}.zip".replace("$", "latest")

            # Download the code
            response = requests.get(code_location, stream=True, timeout=30)
            response.raise_for_status()

            # Calculate hash if integrity check requested
            file_hash = None
            if check_integrity:
                hash_obj = hashlib.sha256()

            # Save the ZIP file
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        if check_integrity:
                            hash_obj.update(chunk)

            if check_integrity:
                file_hash = hash_obj.hexdigest()
                console.print(f"[dim]SHA256: {file_hash}[/dim]")

            console.print(f"[green]✓ Code downloaded to: {output_path}[/green]")

            # Extract if requested
            if extract:
                extract_dir = output_path.replace(".zip", "_extracted")
                with zipfile.ZipFile(output_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
                console.print(f"[green]✓ Code extracted to: {extract_dir}[/green]")

            # Save configuration if requested
            if include_config:
                config_path = output_path.replace(".zip", "_config.json")

                # Clean up configuration for saving
                config_to_save = {
                    "FunctionName": function_config["FunctionName"],
                    "FunctionArn": function_config["FunctionArn"],
                    "Runtime": function_config.get("Runtime"),
                    "Handler": function_config.get("Handler"),
                    "Description": function_config.get("Description", ""),
                    "Timeout": function_config.get("Timeout"),
                    "MemorySize": function_config.get("MemorySize"),
                    "Version": function_config.get("Version"),
                    "Environment": function_config.get("Environment", {}),
                    "VpcConfig": function_config.get("VpcConfig", {}),
                    "DeadLetterConfig": function_config.get("DeadLetterConfig", {}),
                    "TracingConfig": function_config.get("TracingConfig", {}),
                    "Layers": function_config.get("Layers", []),
                    "Role": function_config.get("Role"),
                    "CodeSha256": function_config.get("CodeSha256"),
                    "CodeSize": function_config.get("CodeSize"),
                    "LastModified": function_config.get("LastModified"),
                    "ReservedConcurrencyExecutions": function_config.get(
                        "ReservedConcurrencyExecutions"
                    ),
                    "Tags": function_config.get("Tags", {}),
                }

                if check_integrity:
                    config_to_save["DownloadInfo"] = {
                        "SHA256": file_hash,
                        "DownloadedAt": datetime.now().isoformat(),
                        "DownloadedVersion": version,
                    }

                with open(config_path, "w") as f:
                    json.dump(config_to_save, f, indent=2, default=str)

                console.print(f"[green]✓ Configuration saved to: {config_path}[/green]")

            # Display summary table
            summary_table = Table(title="Download Summary", box=box.SIMPLE)
            summary_table.add_column("Property", style="cyan")
            summary_table.add_column("Value", style="white")

            summary_table.add_row("Function Name", function_name)
            summary_table.add_row("Version", version)
            summary_table.add_row("Output Path", output_path)
            summary_table.add_row("Extracted", "Yes" if extract else "No")
            summary_table.add_row("Config Saved", "Yes" if include_config else "No")
            summary_table.add_row("Integrity Check", "Yes" if check_integrity else "No")
            if check_integrity and file_hash:
                summary_table.add_row("SHA256", file_hash[:16] + "...")

            console.print(summary_table)

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "ResourceNotFoundException":
                console.print(f"[red]✗ Function '{function_name}' not found[/red]")
            elif error_code == "InvalidParameterValueException":
                console.print(
                    f"[red]✗ Invalid version '{version}' for function '{function_name}'[/red]"
                )
            else:
                console.print(f"[red]✗ AWS Error ({error_code}): {error_message}[/red]")

            return False

        except Exception as e:
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
        """Get environment variables for a Lambda function.

        Args:
            function_name: Name of the Lambda function
            format_type: Output format (text, json, yaml, env, markdown)
            mask_secrets: Whether to mask sensitive values
            output_file: Optional file to write output to
            single_key: Get only a specific environment variable

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.lambda_client:
            print(
                "[red]Error: Lambda client not initialized. Please check your AWS credentials.[/red]"
            )
            return False

        try:
            response = self.lambda_client.get_function_configuration(
                FunctionName=function_name
            )

            env_vars = response.get("Environment", {}).get("Variables", {})

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

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "ResourceNotFoundException":
                print(f"[red]Function '{function_name}' not found[/red]")
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

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
