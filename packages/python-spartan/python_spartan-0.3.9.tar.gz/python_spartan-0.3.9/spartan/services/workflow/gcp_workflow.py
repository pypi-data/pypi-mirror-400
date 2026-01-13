"""GCP Workflows service implementation.

This module contains the GCPWorkflowService class for managing
Google Cloud Platform Workflows.
"""

import json
import os
from datetime import datetime
from typing import Optional

import yaml
from google.api_core import exceptions as google_exceptions
from google.auth import exceptions as auth_exceptions
from google.cloud import workflows_v1
from google.cloud.workflows import executions_v1
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.services.workflow.base import BaseWorkflowService
from spartan.utils.filters import FilterUtility, SortUtility


class GCPWorkflowService(BaseWorkflowService):
    """Service class for managing GCP Workflows.

    This class provides methods to interact with Google Cloud Platform Workflows,
    including listing workflows, describing workflow definitions, executing workflows,
    and viewing execution logs.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """Initialize the GCPWorkflowService with GCP Workflows clients.

        Args:
            project_id: GCP project ID. If None, checks environment variables in order:
                       GOOGLE_CLOUD_PROJECT, GCP_PROJECT, GCLOUD_PROJECT
            location: GCP location (e.g., 'us-central1'). If None, checks environment
                     variables in order: GOOGLE_CLOUD_REGION, GCP_REGION, GCLOUD_REGION
                     Defaults to 'us-central1' if not found.

        Raises:
            ValueError: If project_id is not provided and not found in environment.
            google.auth.exceptions.DefaultCredentialsError: If GCP credentials are not configured.
        """
        self.provider = "gcp"

        # Get project ID from parameter or environment variables
        self.project_id = (
            project_id
            or os.environ.get("GOOGLE_CLOUD_PROJECT")
            or os.environ.get("GCP_PROJECT")
            or os.environ.get("GCLOUD_PROJECT")
        )
        if not self.project_id:
            print(
                "[red]Error: GCP project ID not provided.[/red]\n"
                "[yellow]Set one of these environment variables: GOOGLE_CLOUD_PROJECT, GCP_PROJECT, GCLOUD_PROJECT[/yellow]\n"
                "[yellow]Or pass --project-id parameter.[/yellow]"
            )
            raise ValueError("GCP project ID is required")

        # Get location from parameter or environment variables
        self.location = (
            location
            or os.environ.get("GOOGLE_CLOUD_REGION")
            or os.environ.get("GCP_REGION")
            or os.environ.get("GCLOUD_REGION")
            or "us-central1"  # Default fallback
        )
        self.console = Console()

        # Initialize GCP Workflows clients
        try:
            self.workflows_client = workflows_v1.WorkflowsClient()
            self.executions_client = executions_v1.ExecutionsClient()
        except auth_exceptions.DefaultCredentialsError:
            print(
                "[red]Error: GCP credentials not configured.[/red]\n"
                "[yellow]Suggestion: Run 'gcloud auth application-default login' "
                "or set GOOGLE_APPLICATION_CREDENTIALS environment variable.[/yellow]"
            )
            raise
        except Exception as e:
            print(f"[red]Error initializing GCP Workflows clients: {e}[/red]")
            raise

    def list_workflows(
        self,
        output_format: str = "table",
        prefix_filter: Optional[str] = None,
        regex_match: Optional[str] = None,
        contains_filter: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        limit: Optional[int] = None,
        show_filters: bool = False,
        save_to: Optional[str] = None,
        interactive: bool = False,
    ) -> None:
        """List all GCP Workflows with advanced filtering.

        Args:
            output_format: Output format (table, json, yaml, markdown, csv)
            prefix_filter: Filter workflows by name prefix
            regex_match: Filter workflows by regex pattern
            contains_filter: Filter workflows whose names contain a substring
            sort_by: Sort by field (name, creationDate)
            sort_order: Sort order (asc, desc)
            limit: Limit the number of results shown
            show_filters: Show which filters were applied in the output
            save_to: Save the results to a file
            interactive: Enable interactive mode for workflow selection
        """
        try:
            output_format = self._validate_output_format(output_format)

            # Validate sort field
            valid_sort_fields = ["name", "creationDate"]
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
                print("[blue]Fetching GCP Workflows...[/blue]")

            # Build parent path for listing workflows
            parent = f"projects/{self.project_id}/locations/{self.location}"

            # Get all workflows using pagination
            workflows = []
            request = workflows_v1.ListWorkflowsRequest(parent=parent)

            try:
                page_result = self.workflows_client.list_workflows(request=request)
                for workflow in page_result:
                    workflows.append(workflow)
            except google_exceptions.NotFound:
                print(
                    f"[red]Error: Location '{self.location}' not found in project '{self.project_id}'.[/red]"
                )
                return
            except google_exceptions.PermissionDenied as e:
                print(
                    f"[red]Error: Permission denied accessing GCP Workflows.[/red]\n"
                    f"[yellow]Details: {e}[/yellow]"
                )
                return

            if not workflows:
                self._handle_no_workflows_found(output_format)
                return

            # Process workflow data
            workflow_data = []
            for workflow in workflows:
                # Extract workflow name from full resource name
                # Format: projects/{project}/locations/{location}/workflows/{workflow}
                workflow_name = workflow.name.split("/")[-1]

                # Parse creation time
                create_time = workflow.create_time
                created_str = self._format_date(create_time)

                workflow_info = {
                    "name": workflow_name,
                    "state": workflow.state.name if workflow.state else "UNKNOWN",
                    "created": created_str,
                    "creationDate": create_time,  # Keep original for sorting
                    "revision_id": workflow.revision_id,
                    "resource_name": workflow.name,
                    "update_time": self._format_date(workflow.update_time),
                }
                workflow_data.append(workflow_info)

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

            if filters:
                workflow_data = FilterUtility.apply_multiple_filters(
                    workflow_data, filters
                )

            # Apply sorting
            reverse = sort_order.lower() == "desc"
            if sort_by == "creationDate":
                workflow_data = SortUtility.sort_by_date(
                    workflow_data, "creationDate", reverse=reverse
                )
            else:
                case_sensitive = False if sort_by == "name" else True
                workflow_data = SortUtility.sort_items(
                    workflow_data,
                    sort_by,
                    reverse=reverse,
                    case_sensitive=case_sensitive,
                )

            # Apply limit
            if limit:
                workflow_data = workflow_data[:limit]

            # Check if any workflows remain after filtering
            if not workflow_data:
                self._handle_no_workflows_after_filter(
                    output_format, prefix_filter, regex_match, contains_filter
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
            if limit:
                applied_filters["limit"] = str(limit)

            # Output in requested format
            if output_format == "csv":
                self._print_workflows_csv(
                    workflow_data, show_filters, applied_filters, save_to
                )
            elif output_format == "table":
                self._print_workflows_table(
                    workflow_data, show_filters, applied_filters, sort_by, sort_order
                )
            elif output_format == "json":
                output_data = {
                    "workflows": workflow_data,
                    "count": len(workflow_data),
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
                    "workflows": workflow_data,
                    "count": len(workflow_data),
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
                self._print_workflows_markdown(
                    workflow_data,
                    show_filters,
                    applied_filters,
                    sort_by,
                    sort_order,
                    save_to,
                )

        except google_exceptions.GoogleAPICallError as e:
            print(f"[red]GCP API Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error listing workflows: {e}[/red]")

    def _validate_output_format(self, output_format: str) -> str:
        """Validate and normalize output format."""
        valid_formats = ["table", "json", "yaml", "markdown", "csv", "text"]
        output_format = output_format.lower()
        if output_format not in valid_formats:
            print(
                f"[red]Invalid output format '{output_format}'. Valid formats: {', '.join(valid_formats)}[/red]"
            )
            raise ValueError(f"Invalid output format: {output_format}")
        return output_format

    def _format_date(self, date_obj: Optional[datetime]) -> str:
        """Format date object to readable format."""
        if not date_obj:
            return "N/A"
        try:
            if hasattr(date_obj, "strftime"):
                return date_obj.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                return str(date_obj)
        except Exception:
            return str(date_obj)

    def _print_workflows_table(
        self,
        workflow_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> None:
        """Print workflows in a formatted table."""
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
        table.add_column("Name", style="bright_blue", no_wrap=False)
        table.add_column("State", style="green", no_wrap=True)
        table.add_column("Revision ID", style="magenta", no_wrap=True)
        table.add_column("Created", style="dim")
        table.add_column("Updated", style="dim")

        for workflow in workflow_data:
            table.add_row(
                workflow["name"],
                workflow["state"],
                workflow["revision_id"],
                workflow["created"],
                workflow["update_time"],
            )

        self.console.print(
            f"📋 [bold]GCP Workflows[/bold] ([bright_yellow]{len(workflow_data)}[/bright_yellow] found)"
        )
        if sort_by:
            self.console.print(f"[dim]Sorted by: {sort_by} ({sort_order})[/dim]")
        self.console.print()
        self.console.print(table)

    def _handle_no_workflows_found(self, output_format: str) -> None:
        """Handle the case when no workflows are found."""
        if output_format == "table":
            print(
                f"[yellow]No GCP Workflows found in project '{self.project_id}' location '{self.location}'.[/yellow]"
            )
        elif output_format == "json":
            print(json.dumps({"workflows": [], "count": 0}, indent=2))
        elif output_format == "yaml":
            print(yaml.dump({"workflows": [], "count": 0}))
        elif output_format == "text":
            print(
                f"No GCP Workflows found in project '{self.project_id}' location '{self.location}'."
            )
        elif output_format == "markdown":
            print(
                f"# GCP Workflows\n\nNo workflows found in project '{self.project_id}' location '{self.location}'."
            )

    def _handle_no_workflows_after_filter(
        self,
        output_format: str,
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        contains_filter: Optional[str],
    ) -> None:
        """Handle the case when no workflows remain after filtering."""
        filter_desc = []
        if prefix_filter:
            filter_desc.append(f"prefix '{prefix_filter}'")
        if regex_match:
            filter_desc.append(f"regex '{regex_match}'")
        if contains_filter:
            filter_desc.append(f"contains '{contains_filter}'")

        filter_text = ", ".join(filter_desc)
        message = f"No workflows found matching the specified filters: {filter_text}"

        if output_format == "table":
            print(f"[yellow]{message}[/yellow]")
        elif output_format == "json":
            print(
                json.dumps({"workflows": [], "count": 0, "message": message}, indent=2)
            )
        elif output_format == "yaml":
            print(yaml.dump({"workflows": [], "count": 0, "message": message}))
        elif output_format == "text":
            print(message)
        elif output_format == "markdown":
            print(f"# GCP Workflows\n\n{message}")

    def _print_workflows_csv(
        self,
        workflow_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        save_to: Optional[str] = None,
    ) -> None:
        """Print workflows in CSV format."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            ["Name", "State", "Revision ID", "Created", "Updated", "Resource Name"]
        )

        # Write data
        for workflow in workflow_data:
            writer.writerow(
                [
                    workflow["name"],
                    workflow["state"],
                    workflow["revision_id"],
                    workflow["created"],
                    workflow["update_time"],
                    workflow["resource_name"],
                ]
            )

        csv_content = output.getvalue()
        if save_to:
            self._save_to_file(csv_content, save_to)
        else:
            print(csv_content)

    def _print_workflows_markdown(
        self,
        workflow_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        save_to: Optional[str] = None,
    ) -> None:
        """Print workflows in Markdown format."""
        lines = []
        lines.append("# GCP Workflows\n")

        if show_filters and applied_filters:
            lines.append("## Applied Filters\n")
            for key, value in applied_filters.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("\n")

        lines.append(f"**Total workflows**: {len(workflow_data)}\n")
        lines.append(f"**Sorted by**: {sort_by} ({sort_order})\n")
        lines.append("\n## Workflows\n")
        lines.append("| Name | State | Revision ID | Created | Updated |")
        lines.append("|------|-------|-------------|---------|---------|")

        for workflow in workflow_data:
            lines.append(
                f"| {workflow['name']} | {workflow['state']} | {workflow['revision_id']} | "
                f"{workflow['created']} | {workflow['update_time']} |"
            )

        markdown_content = "\n".join(lines)
        if save_to:
            self._save_to_file(markdown_content, save_to)
        else:
            print(markdown_content)

    def _save_to_file(self, content: str, file_path: str) -> None:
        """Save content to a file."""
        try:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"[green]✓ Results saved to {file_path}[/green]")
        except Exception as e:
            print(f"[red]Error saving to file: {e}[/red]")

    def describe_workflow(
        self,
        name: str,
        output_format: str = "table",
    ) -> None:
        """Describe a specific GCP Workflow.

        Args:
            name: Workflow name
            output_format: Output format (table, json, yaml, text, markdown)
        """
        try:
            output_format = self._validate_output_format(output_format)

            # Build workflow path
            workflow_path = (
                f"projects/{self.project_id}/locations/{self.location}/workflows/{name}"
            )

            # Get workflow details
            try:
                request = workflows_v1.GetWorkflowRequest(name=workflow_path)
                workflow = self.workflows_client.get_workflow(request=request)
            except google_exceptions.NotFound:
                print(
                    f"[red]Error: Workflow '{name}' not found in project '{self.project_id}' location '{self.location}'.[/red]"
                )
                return
            except google_exceptions.PermissionDenied as e:
                print(
                    f"[red]Error: Permission denied accessing workflow '{name}'.[/red]\n"
                    f"[yellow]Details: {e}[/yellow]"
                )
                return

            # Extract workflow information
            workflow_name = workflow.name.split("/")[-1]
            workflow_info = {
                "name": workflow_name,
                "resource_name": workflow.name,
                "state": workflow.state.name if workflow.state else "UNKNOWN",
                "revision_id": workflow.revision_id,
                "created": self._format_date(workflow.create_time),
                "updated": self._format_date(workflow.update_time),
                "source_contents": (
                    workflow.source_contents if workflow.source_contents else "N/A"
                ),
            }

            # Output in requested format
            if output_format == "json":
                output_str = json.dumps(workflow_info, indent=2, default=str)
                print(output_str)
            elif output_format == "yaml":
                # For YAML, include the workflow definition
                output_data = {
                    "metadata": {
                        "name": workflow_info["name"],
                        "resource_name": workflow_info["resource_name"],
                        "state": workflow_info["state"],
                        "revision_id": workflow_info["revision_id"],
                        "created": workflow_info["created"],
                        "updated": workflow_info["updated"],
                    },
                    "definition": workflow_info["source_contents"],
                }
                output_str = yaml.dump(output_data, default_flow_style=False)
                print(output_str)
            elif output_format == "text":
                print(f"Workflow: {workflow_info['name']}")
                print(f"State: {workflow_info['state']}")
                print(f"Revision ID: {workflow_info['revision_id']}")
                print(f"Created: {workflow_info['created']}")
                print(f"Updated: {workflow_info['updated']}")
                print(f"\nDefinition:\n{workflow_info['source_contents']}")
            elif output_format == "markdown":
                lines = []
                lines.append(f"# Workflow: {workflow_info['name']}\n")
                lines.append("## Metadata\n")
                lines.append(f"- **State**: {workflow_info['state']}")
                lines.append(f"- **Revision ID**: {workflow_info['revision_id']}")
                lines.append(f"- **Created**: {workflow_info['created']}")
                lines.append(f"- **Updated**: {workflow_info['updated']}")
                lines.append(f"- **Resource Name**: {workflow_info['resource_name']}")
                lines.append("\n## Workflow Definition\n")
                lines.append("```yaml")
                lines.append(workflow_info["source_contents"])
                lines.append("```")
                print("\n".join(lines))
            else:  # table format
                self._print_workflow_details_table(workflow_info)

        except google_exceptions.GoogleAPICallError as e:
            print(f"[red]GCP API Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error describing workflow: {e}[/red]")

    def _print_workflow_details_table(self, workflow_info: dict) -> None:
        """Print workflow details in a formatted table."""
        self.console.print(
            f"\n[bold cyan]Workflow: {workflow_info['name']}[/bold cyan]\n"
        )

        # Metadata table
        metadata_table = Table(
            show_header=False,
            box=box.SIMPLE,
            border_style="dim",
        )
        metadata_table.add_column("Property", style="cyan")
        metadata_table.add_column("Value", style="white")

        metadata_table.add_row("State", workflow_info["state"])
        metadata_table.add_row("Revision ID", workflow_info["revision_id"])
        metadata_table.add_row("Created", workflow_info["created"])
        metadata_table.add_row("Updated", workflow_info["updated"])
        metadata_table.add_row("Resource Name", workflow_info["resource_name"])

        self.console.print(metadata_table)
        self.console.print("\n[bold]Workflow Definition:[/bold]\n")
        self.console.print(workflow_info["source_contents"])

    def run_workflow(
        self,
        workflow_name: str,
        input_data: Optional[str] = None,
        input_file: Optional[str] = None,
        execution_name: Optional[str] = None,
        skip_confirmation: bool = False,
    ) -> None:
        """Execute a GCP Workflow.

        Args:
            workflow_name: Name of the workflow to execute
            input_data: Execution input as JSON string
            input_file: Path to JSON file containing execution input
            execution_name: Custom execution name
            skip_confirmation: Skip confirmation prompt
        """
        try:
            # Build workflow path
            workflow_path = f"projects/{self.project_id}/locations/{self.location}/workflows/{workflow_name}"

            # Verify workflow exists
            try:
                request = workflows_v1.GetWorkflowRequest(name=workflow_path)
                workflow = self.workflows_client.get_workflow(request=request)
            except google_exceptions.NotFound:
                print(f"[red]Error: Workflow '{workflow_name}' not found.[/red]")
                return
            except google_exceptions.PermissionDenied as e:
                print(
                    f"[red]Error: Permission denied accessing workflow '{workflow_name}'.[/red]\n"
                    f"[yellow]Details: {e}[/yellow]"
                )
                return

            # Handle input data
            execution_input = None
            if input_file:
                try:
                    with open(input_file, "r") as f:
                        execution_input = f.read()
                except FileNotFoundError:
                    print(f"[red]Error: Input file '{input_file}' not found.[/red]")
                    return
                except Exception as e:
                    print(f"[red]Error reading input file: {e}[/red]")
                    return
            elif input_data:
                execution_input = input_data

            # Validate JSON if input provided
            if execution_input:
                try:
                    json.loads(execution_input)
                except json.JSONDecodeError as e:
                    print(f"[red]Error: Invalid JSON input: {e}[/red]")
                    return

            # Confirmation prompt
            if not skip_confirmation:
                print(f"\n[yellow]About to execute workflow: {workflow_name}[/yellow]")
                if execution_input:
                    print(
                        f"[yellow]With input: {execution_input[:100]}{'...' if len(execution_input) > 100 else ''}[/yellow]"
                    )
                response = input("Continue? (y/N): ")
                if response.lower() != "y":
                    print("[yellow]Execution cancelled.[/yellow]")
                    return

            # Generate execution name if not provided
            if not execution_name:
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                execution_name = f"execution-{timestamp}"

            # Create execution
            try:
                parent = workflow_path
                execution = executions_v1.Execution()
                if execution_input:
                    execution.argument = execution_input

                request = executions_v1.CreateExecutionRequest(
                    parent=parent,
                    execution=execution,
                )

                execution_result = self.executions_client.create_execution(
                    request=request
                )

                print(f"[green]✓ Execution started successfully![/green]")
                print(
                    f"[cyan]Execution Name: {execution_result.name.split('/')[-1]}[/cyan]"
                )
                print(f"[cyan]Resource Name: {execution_result.name}[/cyan]")
                print(f"[cyan]State: {execution_result.state.name}[/cyan]")

            except google_exceptions.GoogleAPICallError as e:
                print(f"[red]Error creating execution: {e}[/red]")
                return

        except Exception as e:
            print(f"[red]Error running workflow: {e}[/red]")

    def list_executions(
        self,
        workflow_name: str,
        status_filter: str = "ALL",
        max_results: int = 50,
        output_format: str = "table",
    ) -> None:
        """List executions for a GCP Workflow.

        Args:
            workflow_name: Name of the workflow
            status_filter: Filter by status (ALL, ACTIVE, SUCCEEDED, FAILED, CANCELLED)
            max_results: Maximum number of executions to return
            output_format: Output format (table, json, yaml, text, markdown)
        """
        try:
            output_format = self._validate_output_format(output_format)

            # Build workflow path
            workflow_path = f"projects/{self.project_id}/locations/{self.location}/workflows/{workflow_name}"

            # Verify workflow exists
            try:
                request = workflows_v1.GetWorkflowRequest(name=workflow_path)
                workflow = self.workflows_client.get_workflow(request=request)
            except google_exceptions.NotFound:
                print(f"[red]Error: Workflow '{workflow_name}' not found.[/red]")
                return

            # List executions
            try:
                parent = workflow_path
                request = executions_v1.ListExecutionsRequest(
                    parent=parent,
                    page_size=max_results,
                )

                executions = []
                page_result = self.executions_client.list_executions(request=request)

                for execution in page_result:
                    # Apply status filter
                    if status_filter != "ALL" and execution.state.name != status_filter:
                        continue

                    execution_info = {
                        "name": execution.name.split("/")[-1],
                        "resource_name": execution.name,
                        "state": execution.state.name,
                        "start_time": self._format_date(execution.start_time),
                        "end_time": (
                            self._format_date(execution.end_time)
                            if execution.end_time
                            else "N/A"
                        ),
                        "duration": self._calculate_duration(
                            execution.start_time, execution.end_time
                        ),
                    }
                    executions.append(execution_info)

                    if len(executions) >= max_results:
                        break

                if not executions:
                    print(
                        f"[yellow]No executions found for workflow '{workflow_name}'.[/yellow]"
                    )
                    return

                # Sort by start time (descending)
                executions.sort(key=lambda x: x["start_time"], reverse=True)

                # Output in requested format
                if output_format == "json":
                    output_data = {
                        "workflow": workflow_name,
                        "executions": executions,
                        "count": len(executions),
                    }
                    print(json.dumps(output_data, indent=2, default=str))
                elif output_format == "yaml":
                    output_data = {
                        "workflow": workflow_name,
                        "executions": executions,
                        "count": len(executions),
                    }
                    print(yaml.dump(output_data, default_flow_style=False))
                elif output_format == "table":
                    self._print_executions_table(workflow_name, executions)
                elif output_format == "text":
                    print(f"Executions for workflow: {workflow_name}\n")
                    for exec_info in executions:
                        print(f"Name: {exec_info['name']}")
                        print(f"State: {exec_info['state']}")
                        print(f"Start: {exec_info['start_time']}")
                        print(f"End: {exec_info['end_time']}")
                        print(f"Duration: {exec_info['duration']}")
                        print()

            except google_exceptions.GoogleAPICallError as e:
                print(f"[red]Error listing executions: {e}[/red]")
                return

        except Exception as e:
            print(f"[red]Error listing executions: {e}[/red]")

    def _calculate_duration(self, start_time, end_time) -> str:
        """Calculate duration between start and end time."""
        if not start_time or not end_time:
            return "N/A"
        try:
            duration = end_time - start_time
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except Exception:
            return "N/A"

    def _print_executions_table(self, workflow_name: str, executions: list) -> None:
        """Print executions in a formatted table."""
        self.console.print(
            f"\n[bold cyan]Executions for: {workflow_name}[/bold cyan]\n"
        )

        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        table.add_column("Name", style="bright_blue", no_wrap=False)
        table.add_column("State", style="white", no_wrap=True)
        table.add_column("Start Time", style="dim")
        table.add_column("End Time", style="dim")
        table.add_column("Duration", style="magenta")

        for execution in executions:
            # Color code the state
            state = execution["state"]
            if state == "SUCCEEDED":
                state_display = f"[green]{state}[/green]"
            elif state == "FAILED":
                state_display = f"[red]{state}[/red]"
            elif state == "ACTIVE":
                state_display = f"[yellow]{state}[/yellow]"
            else:
                state_display = state

            table.add_row(
                execution["name"],
                state_display,
                execution["start_time"],
                execution["end_time"],
                execution["duration"],
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(executions)} executions[/dim]")

    def get_execution_logs(
        self,
        execution_id: str,
        workflow_name: Optional[str] = None,
        output_format: str = "table",
        show_input: bool = False,
        show_output: bool = False,
        show_states: bool = False,
        show_state_io: bool = False,
        state_filter: Optional[str] = None,
        show_diff: bool = False,
        limit: Optional[int] = None,
        save_to: Optional[str] = None,
        follow: bool = False,
    ) -> None:
        """Get detailed logs for a GCP Workflow execution.

        Args:
            execution_id: Execution ID or full resource name
            workflow_name: Workflow name (optional, used to construct full resource path if execution_id is just an ID)
            output_format: Output format (table, json, yaml, text, markdown)
            show_input: Show full input passed into the execution
            show_output: Show final output of the execution
            show_states: Display state transition events
            show_state_io: Show detailed input/output mapping per state
            state_filter: Focus debug output on a specific state by name
            show_diff: Highlight key differences between input and output
            limit: Limit number of state events displayed
            save_to: Save detailed execution report to file
            follow: Stream logs in real-time for running executions
        """
        try:
            output_format = self._validate_output_format(output_format)

            # Build execution path if only ID provided
            if not execution_id.startswith("projects/"):
                if workflow_name:
                    # Construct full resource name from workflow name and execution ID
                    execution_id = f"projects/{self.project_id}/locations/{self.location}/workflows/{workflow_name}/executions/{execution_id}"
                else:
                    print("[red]Error: For GCP, please provide either:[/red]")
                    print("[yellow]  1. Full execution resource name, or[/yellow]")
                    print("[yellow]  2. Execution ID with --workflow flag[/yellow]")
                    print()
                    print("[cyan]Example:[/cyan]")
                    print(
                        f"[dim]  spartan workflow execution {execution_id} --workflow <workflow-name>[/dim]"
                    )
                    return

            # Get execution details
            try:
                request = executions_v1.GetExecutionRequest(name=execution_id)
                execution = self.executions_client.get_execution(request=request)
            except google_exceptions.NotFound:
                print(f"[red]Error: Execution '{execution_id}' not found.[/red]")
                return
            except google_exceptions.PermissionDenied as e:
                print(
                    f"[red]Error: Permission denied accessing execution.[/red]\n"
                    f"[yellow]Details: {e}[/yellow]"
                )
                return

            # Extract execution information
            execution_info = {
                "name": execution.name.split("/")[-1],
                "resource_name": execution.name,
                "workflow": execution.name.split("/workflows/")[-1].split(
                    "/executions/"
                )[0],
                "state": execution.state.name,
                "start_time": self._format_date(execution.start_time),
                "end_time": (
                    self._format_date(execution.end_time)
                    if execution.end_time
                    else "N/A"
                ),
                "duration": self._calculate_duration(
                    execution.start_time, execution.end_time
                ),
                "argument": execution.argument if execution.argument else "N/A",
                "result": execution.result if execution.result else "N/A",
                "error": execution.error.payload if execution.error else None,
            }

            # Output in requested format
            if output_format == "json":
                output_data = execution_info.copy()
                if show_input:
                    output_data["input_details"] = execution_info["argument"]
                if show_output:
                    output_data["output_details"] = execution_info["result"]
                print(json.dumps(output_data, indent=2, default=str))
            elif output_format == "yaml":
                output_data = execution_info.copy()
                if show_input:
                    output_data["input_details"] = execution_info["argument"]
                if show_output:
                    output_data["output_details"] = execution_info["result"]
                print(yaml.dump(output_data, default_flow_style=False))
            elif output_format == "table":
                self._print_execution_logs_table(
                    execution_info, show_input, show_output
                )
            elif output_format == "text":
                print(f"Execution: {execution_info['name']}")
                print(f"Workflow: {execution_info['workflow']}")
                print(f"State: {execution_info['state']}")
                print(f"Start: {execution_info['start_time']}")
                print(f"End: {execution_info['end_time']}")
                print(f"Duration: {execution_info['duration']}")
                if show_input:
                    print(f"\nInput:\n{execution_info['argument']}")
                if show_output:
                    print(f"\nOutput:\n{execution_info['result']}")
                if execution_info["error"]:
                    print(f"\nError:\n{execution_info['error']}")

        except google_exceptions.GoogleAPICallError as e:
            print(f"[red]GCP API Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error getting execution logs: {e}[/red]")

    def _print_execution_logs_table(
        self, execution_info: dict, show_input: bool, show_output: bool
    ) -> None:
        """Print execution logs in a formatted table with comprehensive view.

        This displays:
        1. Execution summary section with metadata
        2. Execution logs table with state transitions
        3. Error details if execution failed
        """
        # Print header
        self.console.print(
            f"🔄 [bold]GCP Workflow Execution[/bold] ([bright_yellow]{execution_info['name']}[/bright_yellow])"
        )
        self.console.print()

        # Execution Summary Section
        summary_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        summary_table.add_column("Property", style="cyan", no_wrap=True)
        summary_table.add_column("Value", style="white")

        # Color code the state
        state = execution_info["state"]
        if state == "SUCCEEDED":
            state_display = "[green]SUCCEEDED[/green]"
        elif state == "FAILED":
            state_display = "[red]FAILED[/red]"
        elif state == "ACTIVE":
            state_display = "[blue]ACTIVE[/blue]"
        elif state == "CANCELLED":
            state_display = "[yellow]CANCELLED[/yellow]"
        else:
            state_display = f"[dim]{state}[/dim]"

        summary_table.add_row("Name", execution_info["name"])
        summary_table.add_row("Status", state_display)
        summary_table.add_row("Workflow", execution_info["workflow"])
        summary_table.add_row("Started", execution_info["start_time"])
        summary_table.add_row("Stopped", execution_info["end_time"] or "Still running")
        summary_table.add_row("Duration", execution_info["duration"])
        summary_table.add_row("Resource Name", execution_info["resource_name"])

        if execution_info["error"]:
            summary_table.add_row("Error", f"[red]{execution_info['error']}[/red]")

        self.console.print(summary_table)

        # Show input if requested
        if show_input and execution_info["argument"] != "N/A":
            self.console.print("\n[bold]📥 Input Payload:[/bold]")
            try:
                input_json = json.loads(execution_info["argument"])
                self.console.print(json.dumps(input_json, indent=2))
            except json.JSONDecodeError:
                self.console.print(execution_info["argument"])

        # Show output if requested
        if show_output and execution_info["result"] != "N/A":
            self.console.print("\n[bold]📤 Output Result:[/bold]")
            try:
                output_json = json.loads(execution_info["result"])
                self.console.print(json.dumps(output_json, indent=2))
            except json.JSONDecodeError:
                self.console.print(execution_info["result"])

        # Execution Logs Table Section
        # Get workflow steps to display state transitions
        self.console.print("\n[bold]📋 Execution Logs:[/bold]")

        # Create logs table with detailed step information
        logs_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        logs_table.add_column("ID", style="dim", justify="right", no_wrap=True)
        logs_table.add_column("State", style="white", no_wrap=True)
        logs_table.add_column("Routine", style="cyan", no_wrap=True)
        logs_table.add_column("Step", style="green", no_wrap=True)
        logs_table.add_column("Step Type", style="magenta", no_wrap=True)
        logs_table.add_column("Create Time", style="yellow")
        logs_table.add_column("Update Time", style="yellow")

        # Fetch step entries from GCP Workflows API
        try:
            # List step entries for this execution
            parent = execution_info["resource_name"]

            try:
                # Use the executions client to list step entries
                # Note: We need to use the REST API or gRPC client that supports stepEntries
                # The executions_v1 client should have this capability
                request = executions_v1.ListStepEntriesRequest(
                    parent=parent,
                    page_size=100,  # Get up to 100 steps
                )

                step_entries = []
                page_result = self.executions_client.list_step_entries(request=request)

                for step_entry in page_result:
                    step_entries.append(step_entry)

                # Display step entries if we have them
                if step_entries:
                    for step_entry in step_entries:
                        # Extract step information
                        entry_id = (
                            step_entry.entry_id
                            if hasattr(step_entry, "entry_id")
                            else "N/A"
                        )
                        step_state = (
                            step_entry.state.name
                            if hasattr(step_entry, "state")
                            else "UNKNOWN"
                        )
                        routine = (
                            step_entry.routine
                            if hasattr(step_entry, "routine")
                            else "main"
                        )
                        step_name = (
                            step_entry.step if hasattr(step_entry, "step") else "N/A"
                        )
                        step_type = (
                            step_entry.step_type.name
                            if hasattr(step_entry, "step_type")
                            else "UNKNOWN"
                        )
                        create_time = (
                            self._format_date(step_entry.create_time)
                            if hasattr(step_entry, "create_time")
                            else "N/A"
                        )
                        update_time = (
                            self._format_date(step_entry.update_time)
                            if hasattr(step_entry, "update_time")
                            else "N/A"
                        )

                        # Color code the state
                        if step_state == "STATE_SUCCEEDED":
                            state_display = "[green]Succeeded[/green]"
                        elif step_state == "STATE_FAILED":
                            state_display = "[red]Failed[/red]"
                        elif step_state == "STATE_IN_PROGRESS":
                            state_display = "[blue]In Progress[/blue]"
                        else:
                            state_display = step_state.replace("STATE_", "").title()

                        # Format step type for display
                        step_type_display = (
                            step_type.replace("STEP_", "")
                            .lower()
                            .replace("_", " ")
                            .title()
                        )

                        logs_table.add_row(
                            str(entry_id),
                            state_display,
                            routine,
                            step_name,
                            step_type_display,
                            create_time,
                            update_time,
                        )

                    self.console.print(logs_table)
                    self.console.print(
                        f"\n[dim]Total: {len(step_entries)} step(s)[/dim]"
                    )
                else:
                    # No step entries available, show basic execution state
                    self._add_basic_execution_row(
                        logs_table, state, execution_info, state_display
                    )
                    self.console.print(logs_table)
                    self._show_console_link(execution_info, state)

            except AttributeError:
                # list_step_entries method not available in this version of the client
                self._add_basic_execution_row(
                    logs_table, state, execution_info, state_display
                )
                self.console.print(logs_table)
                self.console.print(
                    f"\n[dim]💡 Note: Step-by-step logs require google-cloud-workflows-executions >= 1.14.0[/dim]"
                )
                self._show_console_link(execution_info, state)

            except google_exceptions.PermissionDenied:
                # User doesn't have permission to list step entries
                self._add_basic_execution_row(
                    logs_table, state, execution_info, state_display
                )
                self.console.print(logs_table)
                self.console.print(
                    f"\n[yellow]Note: Permission denied to list step entries. Showing basic execution info.[/yellow]"
                )
                self._show_console_link(execution_info, state)

            except Exception as e:
                # Other error fetching step entries
                self._add_basic_execution_row(
                    logs_table, state, execution_info, state_display
                )
                self.console.print(logs_table)
                self.console.print(
                    f"\n[dim]Note: Could not retrieve step entries: {e}[/dim]"
                )
                self._show_console_link(execution_info, state)

            # Show error details if present
            if execution_info["error"]:
                self.console.print(f"\n[bold red]Error Details:[/bold red]")
                self.console.print(f"[red]{execution_info['error']}[/red]")

        except Exception as e:
            # Fallback to basic execution info
            self._add_basic_execution_row(
                logs_table, state, execution_info, state_display
            )
            self.console.print(logs_table)
            self.console.print(
                f"[dim]Note: Could not retrieve execution logs: {e}[/dim]"
            )

    def _add_basic_execution_row(
        self, table: Table, state: str, execution_info: dict, state_display: str
    ) -> None:
        """Add a basic execution row to the logs table when detailed steps are not available."""
        if state == "ACTIVE":
            table.add_row(
                "1",
                "[blue]Running[/blue]",
                "main",
                "execution",
                "Workflow",
                execution_info["start_time"],
                "In Progress",
            )
        elif state == "SUCCEEDED":
            table.add_row(
                "1",
                "[green]Succeeded[/green]",
                "main",
                "execution",
                "Workflow",
                execution_info["start_time"],
                execution_info["end_time"],
            )
        elif state == "FAILED":
            table.add_row(
                "1",
                "[red]Failed[/red]",
                "main",
                "execution",
                "Workflow",
                execution_info["start_time"],
                execution_info["end_time"],
            )
        elif state == "CANCELLED":
            table.add_row(
                "1",
                "[yellow]Cancelled[/yellow]",
                "main",
                "execution",
                "Workflow",
                execution_info["start_time"],
                execution_info["end_time"],
            )
        else:
            table.add_row(
                "1",
                state_display,
                "main",
                "execution",
                "Workflow",
                execution_info["start_time"],
                execution_info["end_time"] or "N/A",
            )

    def _show_console_link(self, execution_info: dict, state: str) -> None:
        """Show a link to the GCP Console for detailed step information."""
        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            self.console.print(
                f"\n[dim]💡 Detailed step-by-step logs available in GCP Console:[/dim]"
            )
            # Extract project, location, workflow from resource name
            parts = execution_info["resource_name"].split("/")
            if len(parts) >= 8:
                project = parts[1]
                location = parts[3]
                workflow = parts[5]
                exec_id = parts[7]
                console_url = f"https://console.cloud.google.com/workflows/workflow/{location}/{workflow}/execution/{exec_id}?project={project}"
                self.console.print(f"[dim]   {console_url}[/dim]")

    def export_workflow(
        self,
        workflow_name: str,
        revision_id: Optional[str] = None,
    ) -> dict:
        """Export a workflow definition with metadata.

        Args:
            workflow_name: Name of the workflow to export
            revision_id: Specific revision to export (optional, defaults to latest)

        Returns:
            Dict containing:
                - source_contents: Workflow YAML/JSON code
                - metadata: Export metadata (name, timestamp, revision, etc.)
                - revision_id: The revision ID that was exported
                - workflow_name: The workflow name

        Raises:
            google.api_core.exceptions.NotFound: Workflow not found
            google.api_core.exceptions.PermissionDenied: Insufficient permissions
            google.auth.exceptions.DefaultCredentialsError: GCP credentials not configured
        """
        try:
            # Build workflow path
            workflow_path = f"projects/{self.project_id}/locations/{self.location}/workflows/{workflow_name}"

            # Get workflow details
            request = workflows_v1.GetWorkflowRequest(name=workflow_path)
            workflow = self.workflows_client.get_workflow(request=request)

            # Extract source contents and revision ID
            source_contents = (
                workflow.source_contents if workflow.source_contents else ""
            )
            exported_revision_id = workflow.revision_id

            # Generate export metadata
            from datetime import datetime

            metadata = {
                "workflow_name": workflow_name,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "revision_id": exported_revision_id,
                "project_id": self.project_id,
                "location": self.location,
            }

            # Return structured dictionary
            return {
                "workflow_name": workflow_name,
                "source_contents": source_contents,
                "revision_id": exported_revision_id,
                "metadata": metadata,
            }

        except google_exceptions.NotFound:
            raise
        except google_exceptions.PermissionDenied:
            raise
        except auth_exceptions.DefaultCredentialsError:
            raise
        except Exception as e:
            raise Exception(f"Error exporting workflow: {e}")

    def workflow_exists(
        self,
        workflow_name: str,
    ) -> bool:
        """Check if a workflow exists.

        Args:
            workflow_name: Name of the workflow

        Returns:
            True if workflow exists, False otherwise
        """
        try:
            # Build workflow path
            workflow_path = f"projects/{self.project_id}/locations/{self.location}/workflows/{workflow_name}"

            # Try to get the workflow
            request = workflows_v1.GetWorkflowRequest(name=workflow_path)
            self.workflows_client.get_workflow(request=request)

            # If we get here, workflow exists
            return True

        except google_exceptions.NotFound:
            # Workflow doesn't exist
            return False
        except Exception:
            # For other errors, re-raise them
            raise

    def validate_workflow_definition(
        self,
        source_contents: str,
    ) -> tuple:
        """Validate a workflow definition without creating/updating.

        Args:
            source_contents: Workflow YAML/JSON code

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if valid, False otherwise
            - error_message: Error description if invalid, None if valid
        """
        # Check if source_contents is empty
        if not source_contents or not source_contents.strip():
            return (False, "Workflow definition is empty")

        # Try to parse as YAML first
        try:
            yaml.safe_load(source_contents)
            # If YAML parsing succeeds, it's valid
            return (True, None)
        except yaml.YAMLError as e:
            # YAML parsing failed, try JSON
            try:
                json.loads(source_contents)
                # If JSON parsing succeeds, it's valid
                return (True, None)
            except json.JSONDecodeError as json_e:
                # Both YAML and JSON parsing failed
                return (False, f"Invalid YAML/JSON syntax: {str(e)}")
        except Exception as e:
            return (False, f"Validation error: {str(e)}")

    def import_workflow(
        self,
        workflow_name: str,
        source_contents: str,
        description: Optional[str] = None,
        service_account: Optional[str] = None,
        labels: Optional[dict] = None,
    ) -> dict:
        """Import a workflow definition (create or update).

        Args:
            workflow_name: Name of the workflow
            source_contents: Workflow YAML/JSON code
            description: Workflow description (optional)
            service_account: Service account email (optional)
            labels: Workflow labels (optional)

        Returns:
            Dict containing:
                - operation: The operation name
                - workflow_name: The workflow name
                - action: 'created' or 'updated'
                - revision_id: The new revision ID

        Raises:
            google.api_core.exceptions.InvalidArgument: Invalid workflow definition
            google.api_core.exceptions.PermissionDenied: Insufficient permissions
        """
        try:
            # Check if workflow exists
            exists = self.workflow_exists(workflow_name)

            # Build workflow path
            parent = f"projects/{self.project_id}/locations/{self.location}"
            workflow_path = f"{parent}/workflows/{workflow_name}"

            if exists:
                # Update existing workflow
                workflow = workflows_v1.Workflow(
                    name=workflow_path,
                    source_contents=source_contents,
                )

                if description:
                    workflow.description = description
                if service_account:
                    workflow.service_account = service_account
                if labels:
                    workflow.labels = labels

                request = workflows_v1.UpdateWorkflowRequest(
                    workflow=workflow,
                )

                operation = self.workflows_client.update_workflow(request=request)
                action = "updated"
            else:
                # Create new workflow
                workflow = workflows_v1.Workflow(
                    source_contents=source_contents,
                )

                if description:
                    workflow.description = description
                if service_account:
                    workflow.service_account = service_account
                if labels:
                    workflow.labels = labels

                request = workflows_v1.CreateWorkflowRequest(
                    parent=parent,
                    workflow=workflow,
                    workflow_id=workflow_name,
                )

                operation = self.workflows_client.create_workflow(request=request)
                action = "created"

            # Wait for operation to complete
            result = operation.result()

            # Extract revision ID from the result
            revision_id = (
                result.revision_id if hasattr(result, "revision_id") else "unknown"
            )

            # Return structured dictionary
            return {
                "workflow_name": workflow_name,
                "action": action,
                "revision_id": revision_id,
                "operation_name": (
                    operation.operation.name
                    if hasattr(operation, "operation")
                    else "unknown"
                ),
            }

        except google_exceptions.InvalidArgument:
            raise
        except google_exceptions.PermissionDenied:
            raise
        except Exception as e:
            raise Exception(f"Error importing workflow: {e}")

    def get_workflow_diff(
        self,
        workflow_name: str,
        new_source_contents: str,
    ) -> Optional[str]:
        """Get a diff between current and new workflow definition.

        Args:
            workflow_name: Name of the workflow
            new_source_contents: New workflow YAML/JSON code

        Returns:
            Unified diff string if workflow exists, None if workflow doesn't exist
        """
        import difflib

        try:
            # Check if workflow exists
            if not self.workflow_exists(workflow_name):
                return None

            # Get current workflow definition
            workflow_path = f"projects/{self.project_id}/locations/{self.location}/workflows/{workflow_name}"
            request = workflows_v1.GetWorkflowRequest(name=workflow_path)
            workflow = self.workflows_client.get_workflow(request=request)

            current_source_contents = (
                workflow.source_contents if workflow.source_contents else ""
            )

            # Check if there are any differences
            if current_source_contents.strip() == new_source_contents.strip():
                return None

            # Generate unified diff
            old_lines = current_source_contents.splitlines(keepends=True)
            new_lines = new_source_contents.splitlines(keepends=True)

            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile="current",
                tofile="new",
                lineterm="",
            )

            diff_str = "".join(diff)

            # Return None if diff is empty (no changes)
            return diff_str if diff_str else None

        except google_exceptions.NotFound:
            return None
        except Exception:
            # For other errors, re-raise them
            raise
