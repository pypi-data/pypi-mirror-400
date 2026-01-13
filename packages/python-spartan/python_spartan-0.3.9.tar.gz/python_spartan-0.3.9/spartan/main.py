"""Spartan CLI - The swiss army knife for serverless development."""

import json
import os
import subprocess
import sys
from typing import List, Optional

import boto3
import botocore
import typer
from alembic.config import Config
from google.api_core import exceptions as google_exceptions
from google.auth import exceptions as auth_exceptions
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.services.application import ApplicationService
from spartan.services.config import ConfigError, ConfigService
from spartan.services.debug import DebugService
from spartan.services.ecs import ECSService
from spartan.services.handler import AWSHandlerService, GCPHandlerService
from spartan.services.layer import LayerService
from spartan.services.logs import LogsService
from spartan.services.migrate import MigrateService
from spartan.services.model import ModelService
from spartan.services.motivate import MotivateService
from spartan.services.notebook import NotebookService
from spartan.services.request import RequestService
from spartan.services.response import ResponseService
from spartan.services.route import RouteService
from spartan.services.service import ServiceService

DEBUG_OPTIONS = [
    "Python File",
    "Python File with Arguments",
    "Module",
    "FastAPI",
    "Quit",
]

JOB_OPTIONS = [
    "DDB to S3",
    "S3 to DDB",
    "S3 to S3",
    "DDB to DDB",
    "DB to S3",
    "S3 to DB",
    "DB to DB",
    "Quit",
]


alembic_cfg = Config("alembic.ini")
app = typer.Typer(no_args_is_help=True)


def select_option(prompt: str, choices: list) -> str | None:
    """Display a menu of choices and return the selected option.

    Built-in alternative to questionary.select()
    """
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")

    while True:
        try:
            selection = input("\nEnter your choice (number): ").strip()
            choice_index = int(selection) - 1
            if 0 <= choice_index < len(choices):
                return choices[choice_index]
            else:
                print(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None


def register_commands():  # noqa: C901
    """Register all CLI commands and sub-applications."""
    # NEW: Create scaffold command group for code generation
    scaffold_app = typer.Typer(no_args_is_help=True)
    app.add_typer(
        scaffold_app,
        name="scaffold",
        help="Generate code scaffolding (models, routes, services, DTOs).",
    )

    # Other command groups (non-scaffold related)
    handler_app = typer.Typer(no_args_is_help=True)
    app.add_typer(
        handler_app,
        name="handler",
        help="Manages the creation of handler in the application.",
    )

    # Create env subcommand under handler
    handler_env_app = typer.Typer(no_args_is_help=True)
    handler_app.add_typer(
        handler_env_app,
        name="env",
        help="Manage Lambda function environment variables.",
    )

    migrate_app = typer.Typer(no_args_is_help=True)
    app.add_typer(
        migrate_app,
        name="migrate",
        help="Manages database changes, like updates, rollbacks, and making new tables.",
    )

    db_app = typer.Typer(no_args_is_help=True)
    app.add_typer(db_app, name="db", help="Prepare your database tables.")

    container_app = typer.Typer(no_args_is_help=True)
    app.add_typer(container_app, name="container", help="Manage container resources.")

    debug_app = typer.Typer(no_args_is_help=True)
    app.add_typer(
        debug_app, name="debug", help="Generate VS Code launch configurations."
    )

    job_app = typer.Typer(no_args_is_help=True)
    app.add_typer(job_app, name="job", help="Generate AWS Glue job scripts.")

    @job_app.command("generate", help="Generate AWS Glue job scripts")
    def job_generate():
        """Generate AWS Glue job scripts based on selected template."""
        option = select_option("Select job type:", JOB_OPTIONS)
        if not option or option == "Quit":
            typer.echo("Operation cancelled.")
            return

        # Map job options to stub files
        stub_mapping = {
            "DDB to S3": "ddb_s3.stub",
            "S3 to DDB": "s3_ddb.stub",
            "S3 to S3": "s3_s3.stub",
            "DDB to DDB": "ddb_ddb.stub",
            "DB to S3": "db_s3.stub",
            "S3 to DB": "s3_db.stub",
            "DB to DB": "db_db.stub",
        }

        stub_file = stub_mapping.get(option)
        if not stub_file:
            typer.echo(f"Unsupported job option: {option}")
            return

        # Create jobs directory if it doesn't exist
        jobs_dir = os.path.join(os.getcwd(), "jobs")
        if not os.path.exists(jobs_dir):
            try:
                os.makedirs(jobs_dir)
                typer.echo("Created jobs directory.")
            except OSError as e:
                if e.errno == 17:  # File exists error - another process created it
                    pass  # Continue, directory exists now
                else:
                    typer.echo(f"Error creating jobs directory: {e}")
                    return

        # Generate script filename
        script_name = stub_file.replace(".stub", ".py")
        script_path = os.path.join(jobs_dir, script_name)

        # Check if script already exists
        if os.path.exists(script_path):
            typer.echo(f"Script '{script_path}' already exists. Skipping creation.")
            return

        # Read stub file and create script
        home_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        stub_path = os.path.join(home_directory, "spartan", "stubs", "job", stub_file)

        if not os.path.exists(stub_path):
            typer.echo(f"Stub file '{stub_path}' not found.")
            return

        try:
            with open(stub_path, "r") as f:
                content = f.read()

            with open(script_path, "w") as f:
                f.write(content)

            typer.echo(f"Generated job script: {script_path}")
        except Exception as e:
            typer.echo(f"Error generating job script: {e}")

    parquet_app = typer.Typer(no_args_is_help=True)
    app.add_typer(
        parquet_app, name="parquet", help="Convert and analyze Parquet files."
    )

    note_app = typer.Typer(no_args_is_help=True)
    app.add_typer(
        note_app, name="notebook", help="Manage notebook projects and configurations."
    )

    layer_app = typer.Typer(no_args_is_help=True)
    app.add_typer(layer_app, name="layer", help="Manage AWS Lambda layers.")

    logs_app = typer.Typer(no_args_is_help=True)
    app.add_typer(
        logs_app,
        name="logs",
        help="Access and stream AWS CloudWatch logs across multiple services.",
    )

    config_app = typer.Typer(no_args_is_help=True)
    app.add_typer(
        config_app,
        name="config",
        help="Manage Spartan CLI configuration.",
    )

    # ========================================================================================
    # SCAFFOLD COMMANDS - New unified code generation commands
    # ========================================================================================

    @scaffold_app.command("model", help="Generate a model class")
    def scaffold_model(
        name: Optional[str] = typer.Option(
            None, "--name", "-n", help="Name of the model class"
        ),
        path: Optional[str] = typer.Option(
            None, "--path", "-p", help="Output path for the model file"
        ),
        template: Optional[str] = typer.Option(
            None, "--template", "-t", help="Custom template to use"
        ),
        force: bool = typer.Option(
            False, "--force", "-f", help="Overwrite existing files"
        ),
        interactive: bool = typer.Option(
            False, "--interactive", "-i", help="Prompt for name if not provided"
        ),
    ):
        """Generate a model class for data structures and database entities."""
        if not name:
            if interactive:
                name = typer.prompt("Model name")
            else:
                print(
                    "[red]✗[/red] Error: Model name is required. Use --name or --interactive flag."
                )
                raise typer.Exit(1)

        try:
            service = ModelService(name)
            service.create_model_file()
            print(f"[green]✓[/green] Model '{name}' created successfully!")
        except Exception as e:
            print(f"[red]✗[/red] Error creating model: {e}")
            raise typer.Exit(1)

    @scaffold_app.command("service", help="Generate a service class")
    def scaffold_service(
        name: Optional[str] = typer.Option(
            None, "--name", "-n", help="Name of the service class"
        ),
        path: Optional[str] = typer.Option(
            None, "--path", "-p", help="Output path for the service file"
        ),
        template: Optional[str] = typer.Option(
            None, "--template", "-t", help="Custom template to use"
        ),
        force: bool = typer.Option(
            False, "--force", "-f", help="Overwrite existing files"
        ),
        interactive: bool = typer.Option(
            False, "--interactive", "-i", help="Prompt for name if not provided"
        ),
    ):
        """Generate a service class for business logic and data processing."""
        if not name:
            if interactive:
                name = typer.prompt("Service name")
            else:
                print(
                    "[red]✗[/red] Error: Service name is required. Use --name or --interactive flag."
                )
                raise typer.Exit(1)

        try:
            service = ServiceService(name)
            service.create_service_file()
            print(f"[green]✓[/green] Service '{name}' created successfully!")
        except Exception as e:
            print(f"[red]✗[/red] Error creating service: {e}")
            raise typer.Exit(1)

    @scaffold_app.command("route", help="Generate a route class")
    def scaffold_route(
        name: Optional[str] = typer.Option(
            None, "--name", "-n", help="Name of the route class"
        ),
        method: Optional[str] = typer.Option(
            None, "--method", "-m", help="HTTP method (GET, POST, PUT, DELETE)"
        ),
        path: Optional[str] = typer.Option(
            None, "--path", "-p", help="Output path for the route file"
        ),
        template: Optional[str] = typer.Option(
            None, "--template", "-t", help="Custom template to use"
        ),
        force: bool = typer.Option(
            False, "--force", "-f", help="Overwrite existing files"
        ),
        interactive: bool = typer.Option(
            False, "--interactive", "-i", help="Prompt for name if not provided"
        ),
    ):
        """Generate a route class for API endpoints and URL handling."""
        if not name:
            if interactive:
                name = typer.prompt("Route name")
            else:
                print(
                    "[red]✗[/red] Error: Route name is required. Use --name or --interactive flag."
                )
                raise typer.Exit(1)

        try:
            route = RouteService(name)
            route.create_route_file()
            print(f"[green]✓[/green] Route '{name}' created successfully!")
        except Exception as e:
            print(f"[red]✗[/red] Error creating route: {e}")
            raise typer.Exit(1)

    @scaffold_app.command("request", help="Generate a request/input DTO class")
    def scaffold_request(
        name: Optional[str] = typer.Option(
            None, "--name", "-n", help="Name of the request DTO class"
        ),
        path: Optional[str] = typer.Option(
            None, "--path", "-p", help="Output path for the request file"
        ),
        template: Optional[str] = typer.Option(
            None, "--template", "-t", help="Custom template to use"
        ),
        force: bool = typer.Option(
            False, "--force", "-f", help="Overwrite existing files"
        ),
        interactive: bool = typer.Option(
            False, "--interactive", "-i", help="Prompt for name if not provided"
        ),
    ):
        """Generate a request DTO class for input validation and data transfer."""
        if not name:
            if interactive:
                name = typer.prompt("Request DTO name")
            else:
                print(
                    "[red]✗[/red] Error: Request name is required. Use --name or --interactive flag."
                )
                raise typer.Exit(1)

        try:
            service = RequestService(name)
            service.create_request_file()
            print(f"[green]✓[/green] Request DTO '{name}' created successfully!")
        except Exception as e:
            print(f"[red]✗[/red] Error creating request: {e}")
            raise typer.Exit(1)

    @scaffold_app.command("response", help="Generate a response/output DTO class")
    def scaffold_response(
        name: Optional[str] = typer.Option(
            None, "--name", "-n", help="Name of the response DTO class"
        ),
        path: Optional[str] = typer.Option(
            None, "--path", "-p", help="Output path for the response file"
        ),
        template: Optional[str] = typer.Option(
            None, "--template", "-t", help="Custom template to use"
        ),
        force: bool = typer.Option(
            False, "--force", "-f", help="Overwrite existing files"
        ),
        interactive: bool = typer.Option(
            False, "--interactive", "-i", help="Prompt for name if not provided"
        ),
    ):
        """Generate a response DTO class for structured API responses."""
        if not name:
            if interactive:
                name = typer.prompt("Response DTO name")
            else:
                print(
                    "[red]✗[/red] Error: Response name is required. Use --name or --interactive flag."
                )
                raise typer.Exit(1)

        try:
            service = ResponseService(name)
            service.create_response_file()
            print(f"[green]✓[/green] Response DTO '{name}' created successfully!")
        except Exception as e:
            print(f"[red]✗[/red] Error creating response: {e}")
            raise typer.Exit(1) @ scaffold_app.command(
                "list", help="List available scaffold templates"
            )

    def scaffold_list():
        """List all available scaffold templates and their descriptions."""
        print("\n[bold cyan]Available Scaffold Templates:[/bold cyan]\n")

        templates = [
            (
                "model",
                "Generate a model class for data structures and database entities",
            ),
            (
                "service",
                "Generate a service class for business logic and data processing",
            ),
            ("route", "Generate a route class for API endpoints and URL handling"),
            ("request", "Generate a request DTO class for input validation"),
            ("response", "Generate a response DTO class for structured API responses"),
        ]

        for template_name, description in templates:
            print(f"  [green]{template_name:12}[/green] {description}")

        print(
            "\n[dim]Use 'spartan scaffold <template> --help' for template-specific options.[/dim]"
        )

    @handler_app.command(
        "create",
        help="Create a new handler file with optional subscribe and publish options.",
    )
    def handler_create(
        name: str,
        subscribe: str = typer.Option(
            None,
            "--subscribe",
            "-s",
            help="Subscribe/trigger option (AWS: sqs, sns; GCP: pubsub, storage, firestore)",
        ),
        publish: str = typer.Option(
            None, "--publish", "-p", help="Publish option (AWS: sqs; GCP: pubsub)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
    ):
        """Create a new handler file with appropriate template for the configured cloud provider.

        AWS Examples:
        spartan handler create my-handler                           # Default handler
        spartan handler create my-handler --subscribe sqs           # SQS subscriber
        spartan handler create my-handler --publish sqs             # SQS publisher
        spartan handler create my-handler --subscribe sns           # SNS subscriber

        GCP Examples:
        spartan handler create my-handler                           # Default handler
        spartan handler create my-handler --subscribe pubsub        # Pub/Sub subscriber
        spartan handler create my-handler --subscribe storage       # Cloud Storage trigger
        spartan handler create my-handler --subscribe firestore     # Firestore trigger
        spartan handler create my-handler --publish pubsub          # Pub/Sub publisher
        """
        try:
            # Get provider from config
            config = ConfigService.get_instance()
            provider = config.get_provider()

            # Instantiate appropriate service based on provider
            if provider == "gcp":
                handler_service = GCPHandlerService(
                    name=name,
                    subscribe=subscribe,
                    publish=publish,
                    project_id=project_id,
                )
            else:  # default to AWS
                handler_service = AWSHandlerService(
                    name=name,
                    subscribe=subscribe,
                    publish=publish,
                )

            handler_service.create_handler_file()
        except Exception as e:
            print(f"Error creating handler: {e}")

    @handler_app.command("delete", help="Delete an existing handler file.")
    def handler_delete(name: str):
        """Delete a local handler file (provider-agnostic operation).

        Examples:
        spartan handler delete my-handler
        """
        try:
            # Get provider from config for consistency, though delete is provider-agnostic
            config = ConfigService.get_instance()
            provider = config.get_provider()

            # Instantiate appropriate service based on provider
            # Note: delete_handler_file is provider-agnostic, but we use the
            # provider-specific service for consistency
            if provider == "gcp":
                handler_service = GCPHandlerService(name=name)
            else:  # default to AWS
                handler_service = AWSHandlerService(name=name)

            handler_service.delete_handler_file()
        except Exception as e:
            print(f"Error deleting handler: {e}")

    @handler_app.command(
        "list",
        help="List serverless functions with advanced filtering, sorting, and output options.",
    )
    def handler_list(
        # Filter options
        prefix: Optional[str] = typer.Option(
            None, "--prefix", help="Filter functions by name prefix"
        ),
        match: Optional[str] = typer.Option(
            None, "--match", help="Filter functions by regex pattern"
        ),
        contains: Optional[str] = typer.Option(
            None, "--contains", help="Filter functions whose names contain a substring"
        ),
        runtime: Optional[str] = typer.Option(
            None, "--runtime", help="Filter functions by runtime (e.g., python3.11)"
        ),
        # Sort options
        sort: Optional[str] = typer.Option(
            "name", "--sort", help="Sort by: name, runtime, memory, timeout, modified"
        ),
        order: Optional[str] = typer.Option(
            "asc", "--order", help="Sort order: asc or desc"
        ),
        # Output options
        output: Optional[str] = typer.Option(
            "table", "--output", help="Output format: table, json, yaml, markdown, csv"
        ),
        # Cloud provider options
        location: Optional[str] = typer.Option(
            None, "--location", help="Cloud provider region (AWS) or location (GCP)"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
        # Advanced options
        limit: Optional[int] = typer.Option(
            None, "--limit", help="Limit the number of results shown"
        ),
        show_filters: bool = typer.Option(
            False, "--show-filters", help="Show applied filters in output"
        ),
        save_to: Optional[str] = typer.Option(
            None, "--save-to", help="Save results to file (.json, .yaml, .csv, etc.)"
        ),
    ):
        """List serverless functions with comprehensive filtering, sorting, and output options.

        FILTERING OPTIONS:
        --prefix TEXT       Filter by name prefix (e.g., --prefix "prod-")
        --match TEXT        Filter by regex pattern (e.g., --match "api.*service")
        --contains TEXT     Filter by substring (e.g., --contains "lambda")
        --runtime TEXT      Filter by runtime (e.g., --runtime "python3.11")

        SORTING OPTIONS:
        --sort TEXT         Sort by: name, runtime, memory, timeout, modified
        --order TEXT        Sort order: asc (ascending) or desc (descending)

        OUTPUT OPTIONS:
        --output TEXT       Output format: table (default), json, yaml, markdown, csv
        --save-to TEXT      Save results to file (format determined by extension)

        CLOUD PROVIDER OPTIONS:
        --location TEXT     Cloud provider region (AWS) or location (GCP)
        --profile TEXT      AWS CLI profile (AWS only)
        --project-id TEXT   GCP project ID (GCP only)

        ADVANCED OPTIONS:
        --limit INTEGER     Limit number of results displayed
        --show-filters      Show which filters were applied
        --help              Show this help message

        Examples:
        spartan handler list                                    # Basic table output
        spartan handler list --prefix "prod-" --sort memory --order desc
        spartan handler list --runtime python3.11 --output json
        spartan handler list --contains "api" --save-to functions.csv
        spartan handler list --match ".*service.*" --show-filters
        spartan handler list --project-id my-gcp-project --location us-central1  # GCP
        """
        try:
            # Get provider from config
            config = ConfigService.get_instance()
            provider = config.get_provider()

            # Instantiate appropriate service based on provider
            if provider == "gcp":
                handler_service = GCPHandlerService(
                    project_id=project_id,
                    location=location,
                )
            else:  # default to AWS
                handler_service = AWSHandlerService(
                    region=location,  # Use location parameter for region
                    profile=profile,
                )

            # Call service method
            handler_service.list_handlers(
                output_format=output,
                prefix_filter=prefix,
                regex_match=match,
                contains_filter=contains,
                runtime_filter=runtime,
                sort_by=sort,
                sort_order=order,
                limit=limit,
                show_filters=show_filters,
                save_to=save_to,
            )
        except Exception as e:
            print(f"[red]Error listing handlers: {e}[/red]")

    @handler_app.command(
        "describe",
        help="Describe a specific serverless function with detailed information.",
    )
    def handler_describe(
        function_name: str = typer.Argument(
            ..., help="The name or ARN of the function to describe."
        ),
        output: Optional[str] = typer.Option(
            "table", "--output", help="Output format: table, json, yaml, text, markdown"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="Cloud provider region (AWS) or location (GCP)"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
    ):
        """Describe a specific serverless function with detailed information including environment variables.

        Examples:
        spartan handler describe my-function                           # AWS Lambda
        spartan handler describe my-function --project-id my-project   # GCP Cloud Function
        spartan handler describe my-function --output json             # JSON output
        """
        try:
            # Get provider from config
            config = ConfigService.get_instance()
            provider = config.get_provider()

            # Instantiate appropriate service based on provider
            if provider == "gcp":
                handler_service = GCPHandlerService(
                    project_id=project_id,
                    location=location,
                )
            else:  # default to AWS
                handler_service = AWSHandlerService(
                    region=location,
                    profile=profile,
                )

            # Call service method
            handler_service.describe_handler(
                function_name=function_name,
                output_format=output,
            )
        except Exception as e:
            print(f"[red]Error describing handler: {e}[/red]")

    @handler_app.command("download")
    def handler_download(
        name: str = typer.Option(
            ..., "--name", "-n", help="Name of the function to download"
        ),
        version: str = typer.Option(
            "$LATEST",
            "--version",
            "-v",
            help="Version or alias to download (default: $LATEST, AWS only)",
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output path for the downloaded code"
        ),
        extract: bool = typer.Option(
            False, "--extract", "-e", help="Extract the ZIP file after download"
        ),
        check_integrity: bool = typer.Option(
            False,
            "--check-integrity",
            "-c",
            help="Verify download integrity with SHA256",
        ),
        include_config: bool = typer.Option(
            False, "--include-config", "-i", help="Save function configuration as JSON"
        ),
        location: Optional[str] = typer.Option(
            None,
            "--location",
            "-l",
            help="Cloud provider region (AWS) or location (GCP)",
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", "-p", help="AWS CLI profile (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
    ):
        """Download serverless function code and optionally configuration.

        Examples:
        spartan handler download --name my-function                           # AWS Lambda
        spartan handler download --name my-function --extract                 # Extract after download
        spartan handler download --name my-function --project-id my-project   # GCP Cloud Function
        spartan handler download --name my-function --include-config          # Save config too
        """
        try:
            # Get provider from config
            config = ConfigService.get_instance()
            provider = config.get_provider()

            # Instantiate appropriate service based on provider
            if provider == "gcp":
                handler_service = GCPHandlerService(
                    project_id=project_id,
                    location=location,
                )
            else:  # default to AWS
                handler_service = AWSHandlerService(
                    region=location,
                    profile=profile,
                )

            success = handler_service.download_function(
                function_name=name,
                version=version,
                output_path=output,
                extract=extract,
                check_integrity=check_integrity,
                include_config=include_config,
            )

            if not success:
                raise typer.Exit(1)

        except Exception as e:
            print(f"❌ Error downloading function: {e}")
            raise typer.Exit(1)

    @handler_app.command("invoke")
    def handler_invoke(
        name: str = typer.Option(
            ..., "--name", "-n", help="Name of the Lambda function to invoke"
        ),
        payload: Optional[str] = typer.Option(
            None, "--payload", "-p", help="JSON payload to send to the function"
        ),
        invocation_type: str = typer.Option(
            "RequestResponse",
            "--type",
            "-t",
            help="Invocation type: RequestResponse (sync) or Event (async)",
        ),
        log_type: str = typer.Option(
            "Tail", "--log-type", "-l", help="Log type: None or Tail"
        ),
        qualifier: str = typer.Option(
            "$LATEST", "--qualifier", "-q", help="Version or alias to invoke"
        ),
        region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """Run a Lambda function manually and capture the response."""
        try:
            handler_service = HandlerService(region=region, profile=profile)

            success = handler_service.invoke_function(
                function_name=name,
                payload=payload,
                invocation_type=invocation_type,
                log_type=log_type,
                qualifier=qualifier,
            )

            if not success:
                raise typer.Exit(1)

        except Exception as e:
            print(f"❌ Error invoking Lambda function: {e}")
            raise typer.Exit(1)

    @handler_app.command("diff")
    def handler_diff(
        name: str = typer.Option(
            ..., "--name", "-n", help="Name of the Lambda function to compare"
        ),
        local_path: str = typer.Option(
            ..., "--local", "-l", help="Path to local ZIP file or directory"
        ),
        qualifier: str = typer.Option(
            "$LATEST", "--qualifier", "-q", help="Version or alias to compare against"
        ),
        ignore_metadata: bool = typer.Option(
            False, "--ignore-metadata", "-i", help="Skip metadata comparison"
        ),
        show_context: bool = typer.Option(
            True, "--context/--no-context", "-c", help="Show context lines in diff"
        ),
        region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """Compare deployed Lambda function with local version."""
        try:
            handler_service = HandlerService(region=region, profile=profile)

            success = handler_service.diff_function(
                function_name=name,
                local_path=local_path,
                qualifier=qualifier,
                ignore_metadata=ignore_metadata,
                show_context=show_context,
            )

            if not success:
                raise typer.Exit(1)

        except Exception as e:
            print(f"❌ Error comparing Lambda function: {e}")
            raise typer.Exit(1)

    @handler_app.command("upload")
    def handler_upload(
        name: str = typer.Option(
            ..., "--name", "-n", help="Name of the Lambda function"
        ),
        local_path: str = typer.Option(
            ..., "--local", "-l", help="Path to local file, directory, or ZIP file"
        ),
        runtime: Optional[str] = typer.Option(
            None,
            "--runtime",
            "-r",
            help="Lambda runtime (e.g., python3.11, nodejs18.x)",
        ),
        handler: Optional[str] = typer.Option(
            None,
            "--handler",
            help="Function handler (e.g., index.handler, main.lambda_handler)",
        ),
        role: Optional[str] = typer.Option(
            None, "--role", help="IAM role ARN for the function"
        ),
        description: Optional[str] = typer.Option(
            None, "--description", "-d", help="Function description"
        ),
        timeout: Optional[int] = typer.Option(
            None, "--timeout", "-t", help="Function timeout in seconds (1-900)"
        ),
        memory_size: Optional[int] = typer.Option(
            None, "--memory", "-m", help="Memory allocation in MB (128-10240)"
        ),
        env_vars: Optional[str] = typer.Option(
            None, "--env", "-e", help="Environment variables as JSON string"
        ),
        update_if_exists: bool = typer.Option(
            True, "--update/--no-update", help="Update function if it already exists"
        ),
        publish: bool = typer.Option(
            False, "--publish", "-p", help="Publish a new version after upload"
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Show what would be uploaded without actually doing it",
        ),
        region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """Upload/update a Lambda function from a local handler file."""
        try:
            # Parse environment variables if provided
            environment_vars = None
            if env_vars:
                try:
                    environment_vars = json.loads(env_vars)
                    if not isinstance(environment_vars, dict):
                        print("❌ Environment variables must be a JSON object")
                        raise typer.Exit(1)
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON for environment variables: {e}")
                    raise typer.Exit(1)

            handler_service = HandlerService(region=region, profile=profile)

            success = handler_service.upload_function(
                function_name=name,
                local_path=local_path,
                runtime=runtime,
                handler=handler,
                role=role,
                description=description,
                timeout=timeout,
                memory_size=memory_size,
                environment_vars=environment_vars,
                update_if_exists=update_if_exists,
                publish=publish,
                dry_run=dry_run,
            )

            if not success:
                raise typer.Exit(1)

        except Exception as e:
            print(f"❌ Error uploading Lambda function: {e}")
            raise typer.Exit(1)

    @handler_env_app.command(
        "get", help="Get environment variables from a serverless function"
    )
    def handler_env_get(
        name: str = typer.Option(
            ..., "--name", "-n", help="Name of the serverless function"
        ),
        key: Optional[str] = typer.Option(
            None, "--key", "-k", help="Get a specific environment variable by key"
        ),
        format_type: str = typer.Option(
            "text",
            "--format",
            help="Output format: json, yaml, text, markdown, env",
        ),
        mask_secrets: bool = typer.Option(
            True,
            "--mask-secrets/--no-mask-secrets",
            help="Mask values that look like secrets (default: true)",
        ),
        output: Optional[str] = typer.Option(
            None,
            "--output",
            "-o",
            help="Write output to file (e.g., .env.local)",
        ),
        region: Optional[str] = typer.Option(
            None, "--region", "-r", help="Cloud provider region/location"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """Get environment variables from a serverless function.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Gets environment variables from Lambda function
        - GCP: Gets environment variables from Cloud Function

        Examples:
        Get all environment variables:
            spartan handler env get --name my-fn

        Get in .env format:
            spartan handler env get --name my-fn --format env

        Get a single variable:
            spartan handler env get --name my-fn --key LOG_LEVEL

        Save to a file:
            spartan handler env get --name my-fn --format env --output .env.local

        Show full values including secrets:
            spartan handler env get --name my-fn --no-mask-secrets
        """
        try:
            # Get provider from config
            config = ConfigService.get_instance()
            provider = config.get_provider()

            # Instantiate appropriate service based on provider
            if provider == "gcp":
                handler_service = GCPHandlerService(
                    project_id=project_id,
                    location=location or region,
                )
            else:  # default to AWS
                handler_service = AWSHandlerService(
                    region=region,
                    profile=profile,
                )

            # Get environment variables
            success = handler_service.get_environment_variables(
                function_name=name,
                format_type=format_type,
                mask_secrets=mask_secrets,
                output_file=output,
                single_key=key,
            )

            if not success:
                raise typer.Exit(1)

        except Exception as e:
            print(f"❌ Error getting environment variables: {e}")
            raise typer.Exit(1)

    @handler_env_app.command(
        "set", help="Set or update environment variables for a serverless function"
    )
    def handler_env_set(
        name: str = typer.Option(
            ..., "--name", "-n", help="Name of the serverless function"
        ),
        key: List[str] = typer.Option(
            [],
            "--key",
            "-k",
            help="Environment variable in KEY=value format (can be used multiple times)",
        ),
        env_file: Optional[str] = typer.Option(
            None,
            "--env-file",
            "--file",
            help="Path to .env or JSON file containing environment variables",
        ),
        overwrite: bool = typer.Option(
            False,
            "--overwrite",
            help="Replace all existing environment variables instead of merging",
        ),
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Preview changes without applying them"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", "-r", help="Cloud provider region/location"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """Set or update environment variables for a serverless function.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Sets environment variables for Lambda function
        - GCP: Sets environment variables for Cloud Function

        Examples:
        Set a single variable:
            spartan handler env set --name my-fn --key LOG_LEVEL=debug

        Load from .env file:
            spartan handler env set --name my-fn --env-file .env.prod

        Overwrite all variables:
            spartan handler env set --name my-fn --env-file config.json --overwrite

        Merge inline and file:
            spartan handler env set --name my-fn --env-file .env --key DEBUG=true

        Preview changes:
            spartan handler env set --name my-fn --key LOG_LEVEL=info --dry-run
        """
        try:
            # Validate that at least one source of variables is provided
            if not key and not env_file:
                print("[red]❌ Error: Must provide either --key or --env-file[/red]")
                raise typer.Exit(1)

            # Get provider from config
            config = ConfigService.get_instance()
            provider = config.get_provider()

            # Instantiate appropriate service based on provider
            if provider == "gcp":
                print(
                    f"[red]Error: Environment variable management is not yet supported for GCP Cloud Functions.[/red]"
                )
                print(
                    f"[yellow]This feature is coming soon. For now, use the GCP Console or gcloud CLI.[/yellow]"
                )
                raise typer.Exit(1)
            else:  # default to AWS
                handler_service = AWSHandlerService(
                    region=region,
                    profile=profile,
                )

                # Set environment variables
                success = handler_service.set_environment_variables(
                    function_name=name,
                    key_value_pairs=key,
                    env_file_path=env_file,
                    overwrite=overwrite,
                    dry_run=dry_run,
                )

                if not success:
                    raise typer.Exit(1)

        except Exception as e:
            print(f"❌ Error setting environment variables: {e}")
            raise typer.Exit(1)

    @migrate_app.command(
        "upgrade", help="Upgrade the database schema to the latest version."
    )
    def migrate_upgrade():
        try:
            migrate_service = MigrateService(alembic_cfg)
            migrate_service.migrate_upgrade()
        except Exception as e:
            print(f"Error upgrading database: {e}")

    @migrate_app.command(
        "create",
        help="Create a new database migration with an optional message.",
    )
    def migrate_create(
        message: str = typer.Option("", "--comment", "-c", help="Message option."),
    ):
        try:
            migrate_service = MigrateService(alembic_cfg)
            migrate_service.migrate_create(message=message)
        except Exception as e:
            print(f"Error creating database migration: {e}")

    @migrate_app.command(
        "downgrade", help="Downgrade the database schema to a previous version."
    )
    def migrate_downgrade():
        try:
            migrate_service = MigrateService(alembic_cfg)
            migrate_service.migrate_downgrade()
        except Exception as e:
            print(f"Error downgrading database: {e}")

    @migrate_app.command("refresh", help="Refresh the database migrations.")
    def migrate_refresh():
        try:
            migrate_service = MigrateService(alembic_cfg)
            migrate_service.migrate_refresh()
        except Exception as e:
            print(f"Error refreshing database migrations: {e}")

    @migrate_app.command(
        "init",
        help="Initialize database migration with a specified database type.",
    )
    def migrate_init(
        database: str = typer.Option(
            None,
            "--database",
            "-d",
            help="The database type (sqlite, mysql, or psql)..",
        )
    ):
        try:
            migrate_service = MigrateService(alembic_cfg)
            if database not in ["sqlite", "mysql", "psql"]:
                typer.echo(
                    "Invalid or no database type specified. Please choose from 'sqlite', 'mysql', or 'psql'."
                )
                raise typer.Exit()
            migrate_service.migrate_initialize(database)
            typer.echo(f"Migration initialized for database type: {database}")
        except Exception as e:
            print(f"Error initializing database migration: {e}")

    @db_app.command("seed", help="Seed the database with initial data.")
    def db_seed():
        try:
            print("Seeding the database")
            if sys.platform == "darwin":
                subprocess.run(["python3", "-m", "database.seeders.database_seeder"])
            else:
                subprocess.run(["python", "-m", "database.seeders.database_seeder"])
            print("Done")
        except Exception as e:
            print(f"Error seeding the database: {e}")

    @app.command(
        "motivate",
        help="Displays a random inspirational quote and its author for the Spartan like you.",
    )
    def inspire_display():
        try:
            inspiration_service = MotivateService()
            quote = inspiration_service.get_random_quote()
            typer.echo(quote)
        except Exception as e:
            print(f"Error displaying inspirational quote: {e}")

    @note_app.command("init", help="Initialize notebooks folder and setup.py file.")
    def notebook_init():
        try:
            service = NotebookService()
            service.init_notebooks()
        except Exception as e:
            print(f"Error initializing notebooks: {e}")

    @note_app.command("create", help="Create a new notebook file from template.")
    def notebook_create(
        notebook_name: str = typer.Argument(..., help="Name of the notebook to create")
    ):
        try:
            service = NotebookService()
            service.create_notebook(notebook_name)
        except Exception as e:
            print(f"Error creating notebook: {e}")

    @note_app.command(
        "list", help="List notebook files from local directory or S3 bucket."
    )
    def notebook_list(
        path: str = typer.Argument(
            ".",
            help="Path to list notebooks from (local directory or S3 bucket with trailing '/')",
        )
    ):
        try:
            service = NotebookService()
            service.list_notebooks(path)
        except Exception as e:
            print(f"Error listing notebooks: {e}")

    @note_app.command("upload", help="Upload notebook files to S3.")
    def notebook_upload(
        local_path: str = typer.Argument(
            ..., help="Local file/directory path to upload"
        ),
        s3_path: str = typer.Argument(
            ..., help="S3 destination path (s3://bucket/prefix/)"
        ),
    ):
        try:
            service = NotebookService()
            service.upload_notebooks(local_path, s3_path)
        except Exception as e:
            print(f"Error uploading notebooks: {e}")

    @note_app.command("download", help="Download notebook files from S3.")
    def notebook_download(
        s3_path: str = typer.Argument(
            ..., help="S3 source path (s3://bucket/prefix/ or s3://bucket/file.ipynb)"
        ),
        recursive: bool = typer.Option(
            False,
            "--recursive",
            "-r",
            help="Download all files recursively from S3 prefix",
        ),
    ):
        try:
            service = NotebookService()
            service.download_notebooks(s3_path, recursive)
        except Exception as e:
            print(f"Error downloading notebooks: {e}")

    @layer_app.command(
        "list", help="List all Lambda layers in the current AWS account and region."
    )
    def layer_list(
        output: str = typer.Option(
            "table",
            "--output",
            "-o",
            help="Output format: table, json, yaml, text, markdown",
        ),
    ):
        """List all Lambda layers in the current AWS account and region."""
        try:
            service = LayerService()
            service.list_layers(output_format=output)
        except Exception as e:
            print(f"Error listing layers: {e}")

    @layer_app.command(
        "info", help="Get detailed information about a specific Lambda layer."
    )
    def layer_info(
        name: str = typer.Option(..., "--name", "-n", help="Name of the Lambda layer"),
        version: Optional[int] = typer.Option(
            None,
            "--version",
            "-v",
            help="Version number of the layer (defaults to latest)",
        ),
        output: str = typer.Option(
            "table",
            "--output",
            "-o",
            help="Output format: table, json, yaml, text, markdown",
        ),
    ):
        """Get detailed information about a specific Lambda layer."""
        try:
            service = LayerService()
            service.get_layer_info(name, version, output_format=output)
        except Exception as e:
            print(f"Error getting layer info: {e}")

    @layer_app.command("attach", help="Attach a Lambda layer to a function.")
    def layer_attach(
        function: str = typer.Option(
            ..., "--function", "-f", help="Name of the Lambda function"
        ),
        layer: str = typer.Option(
            ..., "--layer", "-l", help="Name or ARN of the Lambda layer"
        ),
        version: str = typer.Option(
            "latest",
            "--version",
            "-v",
            help="Version of the layer (defaults to 'latest')",
        ),
        output: str = typer.Option(
            "table",
            "--output",
            "-o",
            help="Output format: table, json, yaml, text, markdown",
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Show what would be done without making any changes",
        ),
    ):
        """Attach a Lambda layer to a function."""
        try:
            service = LayerService()
            service.attach_layer_to_function(
                function, layer, version, output_format=output, dry_run=dry_run
            )
        except Exception as e:
            print(f"Error attaching layer: {e}")

    @layer_app.command("detach", help="Detach a Lambda layer from a function.")
    def layer_detach(
        function: str = typer.Option(
            ..., "--function", "-f", help="Name of the Lambda function"
        ),
        layer: str = typer.Option(
            ..., "--layer", "-l", help="Name or ARN of the Lambda layer"
        ),
        output: str = typer.Option(
            "table",
            "--output",
            "-o",
            help="Output format: table, json, yaml, text, markdown",
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Show what would be done without making any changes",
        ),
    ):
        """Detach a Lambda layer from a function."""
        try:
            service = LayerService()
            service.detach_layer_from_function(
                function, layer, output_format=output, dry_run=dry_run
            )
        except Exception as e:
            print(f"Error detaching layer: {e}")

    @layer_app.command(
        "scan",
        help="Scan and display which Lambda functions are using a specific layer.",
    )
    def layer_scan_usage(
        layer: str = typer.Option(
            ..., "--layer", "-l", help="Name or ARN of the Lambda layer"
        ),
        output: str = typer.Option(
            "table",
            "--output",
            "-o",
            help="Output format: table, json, yaml, text, markdown",
        ),
    ):
        """Scan and display which Lambda functions are using a specific layer."""
        try:
            service = LayerService()
            service.scan_layer_usage(layer, output_format=output)
        except Exception as e:
            print(f"Error scanning layer usage: {e}")

    @layer_app.command("download", help="Download a Lambda layer.")
    def layer_download(
        name: str = typer.Option(..., "--name", "-n", help="Name of the Lambda layer"),
        version: int = typer.Option(
            ..., "--version", "-v", help="Version number of the layer"
        ),
        output_path: Optional[str] = typer.Option(
            None,
            "--output",
            "-o",
            help="Output path for downloaded .zip or extracted folder",
        ),
        extract: bool = typer.Option(
            False,
            "--extract",
            help="Unzip the downloaded layer to the specified directory",
        ),
    ):
        """Download a Lambda layer."""
        try:
            service = LayerService()
            service.download_layer(name, version, output_path, extract)
        except Exception as e:
            print(f"Error downloading layer: {e}")

    # ========================================================================================
    # LOGS COMMANDS - Unified CloudWatch log management across AWS services
    # ========================================================================================

    @logs_app.command(
        "lambda",
        help="Fetch or tail logs from a Lambda function.",
    )
    def logs_lambda(
        name: str = typer.Option(..., "--name", "-n", help="Lambda function name"),
        start_time: Optional[str] = typer.Option(
            None,
            "--start-time",
            "-s",
            help="Start time (ISO format or relative like '5m', '1h')",
        ),
        end_time: Optional[str] = typer.Option(
            None,
            "--end-time",
            "-e",
            help="End time (ISO format or relative like '5m', '1h')",
        ),
        filter_pattern: Optional[str] = typer.Option(
            None,
            "--filter-pattern",
            "-f",
            help="CloudWatch filter pattern (e.g., 'ERROR', 'level = \"critical\"')",
        ),
        tail: bool = typer.Option(False, "--tail", "-t", help="Stream logs live"),
        limit: int = typer.Option(
            100, "--limit", "-l", help="Maximum number of log events"
        ),
        format_type: str = typer.Option(
            "text", "--format", help="Output format: text, json, yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Write logs to file"
        ),
        highlight: Optional[str] = typer.Option(
            None, "--highlight", help="Pattern to highlight in logs"
        ),
        region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """Fetch or tail logs from a Lambda function.

        Examples:
        spartan logs lambda --name auth-fn --tail
        spartan logs lambda --name process-user --start-time 1h --limit 200
        spartan logs lambda --name my-fn --filter-pattern ERROR --highlight ERROR
        """
        try:
            logs_service = LogsService(region=region, profile=profile)
            logs_service.lambda_logs(
                function_name=name,
                start_time=start_time,
                end_time=end_time,
                filter_pattern=filter_pattern,
                tail=tail,
                limit=limit,
                format_type=format_type,
                output=output,
                highlight=highlight,
            )
        except Exception as e:
            print(f"[red]Error fetching Lambda logs: {e}[/red]")

    @logs_app.command(
        "glue",
        help="Retrieve logs from a specific Glue job run.",
    )
    def logs_glue(
        job: str = typer.Option(..., "--job", "-j", help="Glue job name"),
        run_id: str = typer.Option(..., "--run-id", "-r", help="Job run ID"),
        start_time: Optional[str] = typer.Option(
            None,
            "--start-time",
            "-s",
            help="Start time (ISO format or relative like '5m', '1h')",
        ),
        end_time: Optional[str] = typer.Option(
            None,
            "--end-time",
            "-e",
            help="End time (ISO format or relative like '5m', '1h')",
        ),
        filter_pattern: Optional[str] = typer.Option(
            None, "--filter-pattern", "-f", help="CloudWatch filter pattern"
        ),
        tail: bool = typer.Option(False, "--tail", "-t", help="Stream logs live"),
        limit: int = typer.Option(
            100, "--limit", "-l", help="Maximum number of log events"
        ),
        format_type: str = typer.Option(
            "text", "--format", help="Output format: text, json, yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Write logs to file"
        ),
        highlight: Optional[str] = typer.Option(
            None, "--highlight", help="Pattern to highlight in logs"
        ),
        region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """Retrieve logs from a specific Glue job run.

        Examples:
        spartan logs glue --job user-etl --run-id jr_1234567890
        spartan logs glue --job daily-etl --run-id jr_abc123 --tail
        spartan logs glue --job data-transform --run-id jr_def456 --filter-pattern ERROR
        """
        try:
            logs_service = LogsService(region=region, profile=profile)
            logs_service.glue_logs(
                job_name=job,
                run_id=run_id,
                start_time=start_time,
                end_time=end_time,
                filter_pattern=filter_pattern,
                tail=tail,
                limit=limit,
                format_type=format_type,
                output=output,
                highlight=highlight,
            )
        except Exception as e:
            print(f"[red]Error fetching Glue logs: {e}[/red]")

    @logs_app.command(
        "ecs",
        help="Fetch logs from an ECS task, optionally by container name.",
    )
    def logs_ecs(
        task_id: str = typer.Option(..., "--task-id", "-t", help="ECS task ID"),
        cluster: Optional[str] = typer.Option(
            None, "--cluster", "-c", help="ECS cluster name"
        ),
        container: Optional[str] = typer.Option(
            None, "--container", help="Specific container name"
        ),
        start_time: Optional[str] = typer.Option(
            None,
            "--start-time",
            "-s",
            help="Start time (ISO format or relative like '5m', '1h')",
        ),
        end_time: Optional[str] = typer.Option(
            None,
            "--end-time",
            "-e",
            help="End time (ISO format or relative like '5m', '1h')",
        ),
        filter_pattern: Optional[str] = typer.Option(
            None, "--filter-pattern", "-f", help="CloudWatch filter pattern"
        ),
        tail: bool = typer.Option(False, "--tail", help="Stream logs live"),
        limit: int = typer.Option(
            100, "--limit", "-l", help="Maximum number of log events"
        ),
        format_type: str = typer.Option(
            "text", "--format", help="Output format: text, json, yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Write logs to file"
        ),
        highlight: Optional[str] = typer.Option(
            None, "--highlight", help="Pattern to highlight in logs"
        ),
        region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """Fetch logs from an ECS task, optionally by container name.

        Examples:
        spartan logs ecs --task-id fgh456 --container web
        spartan logs ecs --task-id abc123 --cluster prod --tail
        spartan logs ecs --task-id xyz789 --filter-pattern ERROR --highlight ERROR
        """
        try:
            logs_service = LogsService(region=region, profile=profile)
            logs_service.ecs_logs(
                task_id=task_id,
                cluster=cluster,
                container=container,
                start_time=start_time,
                end_time=end_time,
                filter_pattern=filter_pattern,
                tail=tail,
                limit=limit,
                format_type=format_type,
                output=output,
                highlight=highlight,
            )
        except Exception as e:
            print(f"[red]Error fetching ECS logs: {e}[/red]")

    @logs_app.command(
        "step",
        help="View logs and output for a Step Function execution.",
    )
    def logs_step(
        execution_id: str = typer.Option(
            ..., "--execution-id", "-x", help="Step Function execution ARN or name"
        ),
        start_time: Optional[str] = typer.Option(
            None,
            "--start-time",
            "-s",
            help="Start time (ISO format or relative like '5m', '1h')",
        ),
        end_time: Optional[str] = typer.Option(
            None,
            "--end-time",
            "-e",
            help="End time (ISO format or relative like '5m', '1h')",
        ),
        filter_pattern: Optional[str] = typer.Option(
            None, "--filter-pattern", "-f", help="CloudWatch filter pattern"
        ),
        tail: bool = typer.Option(False, "--tail", "-t", help="Stream logs live"),
        limit: int = typer.Option(
            100, "--limit", "-l", help="Maximum number of log events"
        ),
        format_type: str = typer.Option(
            "text", "--format", help="Output format: text, json, yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Write logs to file"
        ),
        highlight: Optional[str] = typer.Option(
            None, "--highlight", help="Pattern to highlight in logs"
        ),
        region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """View logs and output for a Step Function execution.

        Examples:
        spartan logs step --execution-id exec-1234
        spartan logs step --execution-id arn:aws:states:region:account:execution:myStateMachine:exec-abc
        spartan logs step --execution-id exec-xyz --filter-pattern ERROR
        """
        try:
            logs_service = LogsService(region=region, profile=profile)
            logs_service.step_logs(
                execution_id=execution_id,
                start_time=start_time,
                end_time=end_time,
                filter_pattern=filter_pattern,
                tail=tail,
                limit=limit,
                format_type=format_type,
                output=output,
                highlight=highlight,
            )
        except Exception as e:
            print(f"[red]Error fetching Step Function logs: {e}[/red]")

    @logs_app.command(
        "log-group",
        help="Raw access to any CloudWatch log group.",
    )
    def logs_log_group(
        name: str = typer.Option(..., "--name", "-n", help="CloudWatch log group name"),
        start_time: Optional[str] = typer.Option(
            None,
            "--start-time",
            "-s",
            help="Start time (ISO format or relative like '5m', '1h')",
        ),
        end_time: Optional[str] = typer.Option(
            None,
            "--end-time",
            "-e",
            help="End time (ISO format or relative like '5m', '1h')",
        ),
        filter_pattern: Optional[str] = typer.Option(
            None, "--filter-pattern", "-f", help="CloudWatch filter pattern"
        ),
        tail: bool = typer.Option(False, "--tail", "-t", help="Stream logs live"),
        limit: int = typer.Option(
            100, "--limit", "-l", help="Maximum number of log events"
        ),
        format_type: str = typer.Option(
            "text", "--format", help="Output format: text, json, yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Write logs to file"
        ),
        highlight: Optional[str] = typer.Option(
            None, "--highlight", help="Pattern to highlight in logs"
        ),
        region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """Raw access to any CloudWatch log group.

        Examples:
        spartan logs log-group --name /aws/lambda/my-fn
        spartan logs log-group --name /aws/apigateway/my-api --filter-pattern ERROR
        spartan logs log-group --name /custom/app-logs --tail
        """
        try:
            logs_service = LogsService(region=region, profile=profile)
            logs_service.log_group_logs(
                log_group_name=name,
                start_time=start_time,
                end_time=end_time,
                filter_pattern=filter_pattern,
                tail=tail,
                limit=limit,
                format_type=format_type,
                output=output,
                highlight=highlight,
            )
        except Exception as e:
            print(f"[red]Error fetching log group logs: {e}[/red]")

    @logs_app.command(
        "search",
        help="Grep-like filtering across one or more log groups using a pattern.",
    )
    def logs_search(
        pattern: str = typer.Option(..., "--pattern", "-p", help="Search pattern"),
        log_groups: List[str] = typer.Option(
            ...,
            "--log-groups",
            "-g",
            help="Log group names to search (can be specified multiple times)",
        ),
        start_time: Optional[str] = typer.Option(
            None,
            "--start-time",
            "-s",
            help="Start time (ISO format or relative like '5m', '1h')",
        ),
        end_time: Optional[str] = typer.Option(
            None,
            "--end-time",
            "-e",
            help="End time (ISO format or relative like '5m', '1h')",
        ),
        limit: int = typer.Option(
            100, "--limit", "-l", help="Maximum number of log events"
        ),
        format_type: str = typer.Option(
            "text", "--format", help="Output format: text, json, yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Write logs to file"
        ),
        highlight: Optional[str] = typer.Option(
            None,
            "--highlight",
            help="Pattern to highlight in logs (defaults to search pattern)",
        ),
        region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
        profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile"),
    ):
        """Grep-like filtering across one or more log groups using a pattern.

        Examples:
        spartan logs search --pattern ERROR --log-groups /aws/lambda/fn1 --log-groups /aws/lambda/fn2
        spartan logs search --pattern "user login" --log-groups /custom/app-logs --start-time 2h
        spartan logs search --pattern CRITICAL --log-groups /aws/ecs/cluster1 --limit 50
        """
        try:
            logs_service = LogsService(region=region, profile=profile)
            logs_service.search_logs(
                log_groups=log_groups,
                pattern=pattern,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                format_type=format_type,
                output=output,
                highlight=highlight,
            )
        except Exception as e:
            print(f"[red]Error searching logs: {e}[/red]")

    # Create task subcommand
    tasks_app = typer.Typer(no_args_is_help=True)
    container_app.add_typer(tasks_app, name="task", help="Manage ECS tasks.")

    @tasks_app.command("list", help="List running or recent ECS tasks.")
    def tasks_list(
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        service: Optional[str] = typer.Option(
            None, "--service", "-s", help="ECS service name (for task filtering)"
        ),
        limit: Optional[int] = typer.Option(
            None, "--limit", help="Max number of results"
        ),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format: table, json, text"
        ),
        save_to: Optional[str] = typer.Option(
            None, "--save-to", help="Save results to file"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """List running or recent ECS tasks by service or cluster.

        Examples:
        spartan container task list --cluster dev
        spartan container task list --cluster dev --service auth-api
        spartan container task list --cluster dev --limit 10 --output json
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.list_tasks(
                cluster=cluster,
                service=service,
                limit=limit,
                output_format=output,
                save_to=save_to,
            )
        except Exception as e:
            print(f"Error listing tasks: {e}")

    @tasks_app.command(
        "describe", help="Show full metadata and environment of a specific task."
    )
    def tasks_describe(
        task_id: str = typer.Option(..., "--task-id", "-t", help="Specific task ID"),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format: table, json"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Show full metadata and environment of a specific task.

        Examples:
        spartan container task describe --task-id abc123 --cluster dev
        spartan container task describe --task-id abc123 --cluster dev --output json
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.describe_task(
                cluster=cluster,
                task_id=task_id,
                output_format=output,
            )
        except Exception as e:
            print(f"Error describing task: {e}")

    @tasks_app.command("stop", help="Stop a running task.")
    def tasks_stop(
        task_id: str = typer.Option(..., "--task-id", "-t", help="Specific task ID"),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        reason: Optional[str] = typer.Option(
            None, "--reason", help="Reason for stopping the task"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Stop a running task (e.g., for cleanup or force-exit).

        Examples:
        spartan container task stop --task-id abc123 --cluster dev
        spartan container task stop --task-id abc123 --cluster dev --reason "Manual cleanup"
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.stop_task(
                cluster=cluster,
                task_id=task_id,
                reason=reason,
            )
        except Exception as e:
            print(f"Error stopping task: {e}")

    @tasks_app.command("run", help="Run a one-off task.")
    def tasks_run(
        task_def: str = typer.Option(
            ..., "--task-def", help="Task definition name or ARN"
        ),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        count: int = typer.Option(1, "--count", help="Number of tasks to run"),
        launch_type: str = typer.Option(
            "EC2", "--launch-type", help="Launch type: EC2 or FARGATE"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Run a one-off task (e.g., batch job or manual exec).

        Examples:
        spartan container task run --task-def my-task:2 --cluster batch-cluster
        spartan container task run --task-def my-task:2 --cluster dev --count 3
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.run_task(
                cluster=cluster,
                task_definition=task_def,
                count=count,
                launch_type=launch_type,
            )
        except Exception as e:
            print(f"Error running task: {e}")

    @tasks_app.command("logs", help="Fetch CloudWatch logs for a specific task.")
    def tasks_logs(
        task_id: str = typer.Option(..., "--task-id", "-t", help="Specific task ID"),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        container: Optional[str] = typer.Option(
            None, "--container", help="Specific container name"
        ),
        follow: bool = typer.Option(False, "--follow", help="Tail logs in real-time"),
        lines: int = typer.Option(100, "--lines", help="Number of lines to fetch"),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Fetch CloudWatch logs for a specific task or task group.

        Examples:
        spartan container task logs --task-id abc123 --cluster dev
        spartan container task logs --task-id abc123 --cluster dev --follow
        spartan container task logs --task-id abc123 --cluster dev --container web
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.get_task_logs(
                cluster=cluster,
                task_id=task_id,
                container=container,
                follow=follow,
                lines=lines,
            )
        except Exception as e:
            print(f"Error fetching logs: {e}")

    @tasks_app.command(
        "exec", help="Start an interactive shell session into a running task."
    )
    def tasks_exec(
        task_id: str = typer.Option(..., "--task-id", "-t", help="Specific task ID"),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        container: str = typer.Option(..., "--container", help="Container name"),
        command: str = typer.Option(
            "/bin/bash", "--command", help="Command to execute"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Start an interactive shell session into a running task (requires enablement).

        Examples:
        spartan container task exec --task-id abc123 --cluster dev --container web
        spartan container task exec --task-id abc123 --cluster dev --container web --command "/bin/sh"
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.exec_task(
                cluster=cluster,
                task_id=task_id,
                container=container,
                command=command,
            )
        except Exception as e:
            print(f"Error executing command: {e}")

    @tasks_app.command(
        "status", help="Show current health or container state for tasks."
    )
    def tasks_status(
        task_id: str = typer.Option(..., "--task-id", "-t", help="Specific task ID"),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Show current health or container state for tasks.

        Examples:
        spartan container task status --task-id abc123 --cluster dev
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.get_task_status(
                cluster=cluster,
                task_id=task_id,
            )
        except Exception as e:
            print(f"Error getting task status: {e}")

    # Create cluster subcommand
    cluster_app = typer.Typer(no_args_is_help=True)
    container_app.add_typer(cluster_app, name="cluster", help="Manage ECS clusters.")

    @cluster_app.command("list", help="List ECS clusters.")
    def cluster_list(
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format: table, json, yaml"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """List all ECS clusters.

        Examples:
        spartan container cluster list
        spartan container cluster list --output json
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.list_clusters(output_format=output)
        except Exception as e:
            print(f"Error listing clusters: {e}")

    @cluster_app.command("describe", help="Show details of a specific cluster.")
    def cluster_describe(
        name: str = typer.Option(..., "--name", "-n", help="Cluster name"),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format: table, json"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Show detailed information about a specific cluster.

        Examples:
        spartan container cluster describe --name my-cluster
        spartan container cluster describe --name my-cluster --output json
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.describe_cluster(cluster_name=name, output_format=output)
        except Exception as e:
            print(f"Error describing cluster: {e}")

    @cluster_app.command("services", help="List services deployed in a cluster.")
    def cluster_services(
        name: str = typer.Option(..., "--name", "-n", help="Cluster name"),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format: table, json"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """List all services deployed in a specific cluster.

        Examples:
        spartan container cluster services --name my-cluster
        spartan container cluster services --name my-cluster --output json
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.list_cluster_services(cluster_name=name, output_format=output)
        except Exception as e:
            print(f"Error listing cluster services: {e}")

    @cluster_app.command(
        "capacity", help="Show container instance and resource capacity."
    )
    def cluster_capacity(
        name: str = typer.Option(..., "--name", "-n", help="Cluster name"),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format: table, json"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Show container instance and resource capacity for a cluster.

        Examples:
        spartan container cluster capacity --name my-cluster
        spartan container cluster capacity --name my-cluster --output json
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.get_cluster_capacity(cluster_name=name, output_format=output)
        except Exception as e:
            print(f"Error getting cluster capacity: {e}")

    # Create service subcommand
    service_app = typer.Typer(no_args_is_help=True)
    container_app.add_typer(service_app, name="service", help="Manage ECS services.")

    @service_app.command("list", help="List ECS services in a cluster.")
    def service_list(
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format: table, json, yaml"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """List all ECS services in a specific cluster.

        Examples:
        spartan container service list --cluster dev
        spartan container service list --cluster dev --output json
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.list_services(cluster=cluster, output_format=output)
        except Exception as e:
            print(f"Error listing services: {e}")

    @service_app.command(
        "describe", help="Show detailed information about a specific service."
    )
    def service_describe(
        name: str = typer.Option(..., "--name", "-n", help="Service name"),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format: table, json"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Show detailed information about a specific ECS service.

        Examples:
        spartan container service describe --name auth-api --cluster dev
        spartan container service describe --name auth-api --cluster dev --output json
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.describe_service(
                cluster=cluster, service_name=name, output_format=output
            )
        except Exception as e:
            print(f"Error describing service: {e}")

    @service_app.command("update", help="Update an ECS service configuration.")
    def service_update(
        name: str = typer.Option(..., "--name", "-n", help="Service name"),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        desired_count: Optional[int] = typer.Option(
            None, "--desired-count", help="Desired number of tasks"
        ),
        task_definition: Optional[str] = typer.Option(
            None, "--task-definition", help="Task definition ARN or family:revision"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Update an ECS service configuration (scale, task definition, etc.).

        Examples:
        spartan container service update --name auth-api --cluster dev --desired-count 3
        spartan container service update --name auth-api --cluster dev --task-definition my-task:2
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.update_service(
                cluster=cluster,
                service_name=name,
                desired_count=desired_count,
                task_definition=task_definition,
            )
        except Exception as e:
            print(f"Error updating service: {e}")

    @service_app.command(
        "restart", help="Restart an ECS service by forcing new deployment."
    )
    def service_restart(
        name: str = typer.Option(..., "--name", "-n", help="Service name"),
        cluster: str = typer.Option(..., "--cluster", "-c", help="ECS cluster name"),
        region: Optional[str] = typer.Option(
            None, "--region", help="AWS region to use"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile to use"
        ),
    ):
        """Restart an ECS service by forcing a new deployment.

        Examples:
        spartan container service restart --name auth-api --cluster dev
        """
        try:
            ecs_service = ECSService(region=region, profile=profile)
            ecs_service.restart_service(cluster=cluster, service_name=name)
        except Exception as e:
            print(f"Error restarting service: {e}")

    def validate_s3_uri(uri: str) -> bool:
        return uri.startswith("s3://") and len(uri.split("/", 3)) >= 4

    def submit_glue_job(operation: str, source_uri: str, dest_uri: str):
        glue = boto3.client("glue")
        try:
            response = glue.start_job_run(
                JobName="spartan-data-job",
                Arguments={
                    "--operation": operation,
                    "--source_uri": source_uri,
                    "--dest_uri": dest_uri,
                },
            )
            typer.echo(
                f"Triggered Glue job for '{operation}' from {source_uri} to {dest_uri}. JobRunId: {response['JobRunId']}"
            )
        except botocore.exceptions.ClientError as e:
            typer.echo(f"Error submitting Glue job: {e}")

    @debug_app.command("init", help="Create a VS Code launch.json")
    def debug_init():
        option = select_option("Select debug configuration:", DEBUG_OPTIONS)
        if not option:
            typer.echo("Operation cancelled.")
            raise typer.Exit(1)

        service = DebugService()
        service.create_launch_json(option)

    # ========================================================================================
    # CONFIG COMMANDS - Configuration file management
    # ========================================================================================

    @config_app.command("validate", help="Validate the .spartan configuration file")
    def config_validate():
        """Validate the .spartan configuration file.

        This command checks for the existence of a .spartan configuration file,
        parses it, and validates all configuration values. It displays the current
        configuration if valid, or shows specific error messages for each validation
        failure.

        Examples:
        spartan config validate
        """
        try:
            config = ConfigService.get_instance()
            config_path = config.get_config_path()
            provider = config.get_provider()

            # Display success message with current configuration
            print("[green]✓[/green] Configuration is valid!")
            print()

            if config_path:
                print(f"[cyan]Config file:[/cyan] {config_path}")
            else:
                print("[cyan]Config file:[/cyan] Not found (using defaults)")

            print(f"[cyan]Provider:[/cyan] {provider}")

        except ConfigError as e:
            # Display all error messages
            print("[red]✗ Configuration validation failed:[/red]")
            print()
            print(f"[red]{e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            print(f"[red]✗ Unexpected error: {e}[/red]")
            raise typer.Exit(1)

    @config_app.command("show", help="Display current configuration")
    def config_show():
        """Display the current Spartan CLI configuration.

        This command shows the current configuration including the config file path
        (if found) and the provider value.

        Examples:
        spartan config show
        """
        try:
            config = ConfigService.get_instance()
            config_path = config.get_config_path()
            provider = config.get_provider()

            print()
            print("[bold cyan]Spartan CLI Configuration[/bold cyan]")
            print()

            if config_path:
                print(f"[cyan]Config file:[/cyan] {config_path}")
            else:
                print("[cyan]Config file:[/cyan] Not found (using defaults)")

            print(f"[cyan]Provider:[/cyan] {provider}")
            print()

        except ConfigError as e:
            print(f"[red]✗ Configuration error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            print(f"[red]✗ Unexpected error: {e}[/red]")
            raise typer.Exit(1)

    # ========================================================================================
    # WORKFLOW HELPER FUNCTIONS - Configuration priority chain for GCP workflows
    # ========================================================================================

    def _get_project_id(
        cli_project: Optional[str],
    ) -> str:
        """Get project ID with priority: CLI > env > config > default.

        Args:
            cli_project: Project ID from CLI flag

        Returns:
            Project ID to use

        Raises:
            ValueError: If no project ID found in any source
        """
        import os

        # 1. CLI flag
        if cli_project:
            return cli_project

        # 2. Environment variable
        env_project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if env_project:
            return env_project

        # 3. Config file
        try:
            config = ConfigService.get_instance()
            # Try to get gcp.project_id from config
            # Note: ConfigService currently only handles provider, so this will need enhancement
            # For now, we'll skip this and move to GCP default
        except Exception:
            pass

        # 4. GCP default (from Application Default Credentials)
        try:
            import google.auth

            _, project = google.auth.default()
            if project:
                return project
        except Exception:
            pass

        raise ValueError(
            "Project ID not found. Provide via --project-id flag, "
            "GOOGLE_CLOUD_PROJECT environment variable, or configure GCP credentials."
        )

    def _get_region(
        cli_region: Optional[str],
    ) -> str:
        """Get region with priority: CLI > env > config > default.

        Args:
            cli_region: Region from CLI flag

        Returns:
            Region to use
        """
        import os

        # 1. CLI flag
        if cli_region:
            return cli_region

        # 2. Environment variable
        env_region = os.getenv("GOOGLE_CLOUD_REGION")
        if env_region:
            return env_region

        # 3. Config file
        try:
            config = ConfigService.get_instance()
            # Try to get gcp.region from config
            # Note: ConfigService currently only handles provider, so this will need enhancement
            # For now, we'll skip this and move to default
        except Exception:
            pass

        # 4. Default
        return "us-central1"

    # ========================================================================================
    # WORKFLOW COMMANDS - Manage cloud provider workflows (AWS Step Functions, GCP Workflows)
    # ========================================================================================

    # Create workflow command group
    workflow_app = typer.Typer(no_args_is_help=True)

    # Get provider from config to customize help text
    try:
        config = ConfigService.get_instance()
        provider = config.get_provider()
    except Exception:
        provider = "aws"  # Default to AWS if config fails

    # Provider-specific help text
    if provider == "aws":
        workflow_help = "Manage AWS Step Functions state machines."
    else:  # gcp
        workflow_help = "Manage GCP Workflows."

    app.add_typer(
        workflow_app,
        name="workflow",
        help=workflow_help,
    )

    # ========================================================================================
    # WORKFLOW HELPER FUNCTIONS - File I/O and formatting for import/export
    # ========================================================================================

    def _format_export_output(result: dict, format: str) -> str:
        """Format export output with metadata.

        Args:
            result: Export result from service containing workflow definition and metadata
            format: Output format ('yaml' or 'json')

        Returns:
            Formatted string with metadata and workflow definition

        Raises:
            ValueError: If format is not 'yaml' or 'json'
        """
        metadata = result["metadata"]
        source_contents = result["source_contents"]

        if format == "yaml":
            # Add YAML comments for metadata
            lines = [
                f"# {metadata['workflow_name']}",
                f"# exported: {metadata['timestamp']}",
                f"# revision: {metadata['revision_id']}",
                f"# project: {metadata['project_id']}",
                f"# location: {metadata['location']}",
                "",
                source_contents,
            ]
            return "\n".join(lines)

        elif format == "json":
            # Add metadata as top-level field
            import json

            workflow_data = json.loads(source_contents)
            output = {
                "_metadata": metadata,
                "workflow": workflow_data,
            }
            return json.dumps(output, indent=2)

        else:
            raise ValueError(f"Unsupported format: {format}. Must be 'yaml' or 'json'.")

    def _write_to_file(file_path: str, content: str) -> None:
        """Write content to file, creating directories if needed.

        Uses atomic write (temp file + rename) to prevent partial writes.

        Args:
            file_path: Path to output file
            content: Content to write

        Raises:
            PermissionError: If unable to write to file or create directories
        """
        from pathlib import Path

        path = Path(file_path)

        # Create parent directories if they don't exist
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Cannot create directory {path.parent}: {e}")

        # Atomic write: write to temp file, then rename
        temp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            temp_path.write_text(content)
            temp_path.rename(path)
        except PermissionError as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise PermissionError(f"Cannot write to file {file_path}: {e}")

    def _read_workflow_file(file_path: str) -> str:
        """Read workflow definition from file.

        Strips export metadata if present to allow re-importing exported files.

        Args:
            file_path: Path to workflow file

        Returns:
            Workflow source contents (YAML or JSON) without metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If unable to read file
        """
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = path.read_text()
        except PermissionError as e:
            raise PermissionError(f"Cannot read file {file_path}: {e}")

        # Strip metadata if present (for re-importing exported files)
        content = _strip_export_metadata(content)

        return content

    def _strip_export_metadata(content: str) -> str:
        """Remove export metadata from workflow definition.

        Handles both JSON format (with _metadata field) and YAML format
        (with comment lines at the top).

        Args:
            content: Workflow file content

        Returns:
            Workflow definition without metadata
        """
        import json

        # Try JSON format first
        try:
            data = json.loads(content)
            if "_metadata" in data and "workflow" in data:
                # Exported JSON format - extract workflow and convert back to JSON
                return json.dumps(data["workflow"], indent=2)
            # Not exported format, return as-is
            return content
        except json.JSONDecodeError:
            pass

        # YAML format - strip comment lines at the top
        lines = content.split("\n")
        non_comment_start = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith("#"):
                non_comment_start = i
                break

        return "\n".join(lines[non_comment_start:])

    @workflow_app.command("list", help="List all available workflows")
    def workflow_list(
        provider: Optional[str] = typer.Option(
            None,
            "--provider",
            "-p",
            help="Override configured cloud provider (aws, gcp)",
        ),
        status: Optional[str] = typer.Option(
            None, "--status", help="Filter by workflow status"
        ),
        prefix: Optional[str] = typer.Option(
            None, "--prefix", help="Filter workflows by name prefix"
        ),
        match: Optional[str] = typer.Option(
            None, "--match", help="Filter workflows by regex pattern"
        ),
        contains: Optional[str] = typer.Option(
            None, "--contains", help="Filter workflows whose names contain a substring"
        ),
        sort: Optional[str] = typer.Option(
            "name", "--sort", help="Sort by: name, created"
        ),
        order: Optional[str] = typer.Option(
            "asc", "--order", help="Sort order: asc or desc"
        ),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format (table, json, yaml)"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", "-r", help="Cloud provider region/location"
        ),
        limit: Optional[int] = typer.Option(
            None, "--limit", help="Limit the number of results shown"
        ),
        show_filters: bool = typer.Option(
            False, "--show-filters", help="Show applied filters in output"
        ),
        save_to: Optional[str] = typer.Option(
            None, "--save-to", help="Save results to file (.json, .yaml, .csv, etc.)"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """List all available workflows.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Lists Step Functions state machines
        - GCP: Lists GCP Workflows

        Use --provider flag to override the configured provider.

        Examples:
        spartan workflow list
        spartan workflow list --prefix "prod-" --sort created --order desc
        spartan workflow list --provider gcp --project-id my-project
        spartan workflow list --contains "api" --output json
        """
        try:
            from spartan.services.workflow import get_workflow_service

            service = get_workflow_service(
                provider=provider,
                region=region or location,
                profile=profile,
                project_id=project_id,
                location=location,
            )
            service.list_workflows(
                output_format=output,
                prefix_filter=prefix,
                regex_match=match,
                contains_filter=contains,
                sort_by=sort,
                sort_order=order,
                limit=limit,
                show_filters=show_filters,
                save_to=save_to,
            )
        except ValueError as e:
            print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            print(f"[red]Error listing workflows: {e}[/red]")
            raise typer.Exit(1)

    @workflow_app.command("view", help="View workflow definition and metadata")
    def workflow_view(
        name: str = typer.Argument(..., help="Workflow name"),
        provider: Optional[str] = typer.Option(
            None,
            "--provider",
            "-p",
            help="Override configured cloud provider (aws, gcp)",
        ),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format (table, json, yaml)"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", "-r", help="Cloud provider region/location"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """View workflow definition and metadata.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Displays Step Functions state machine definition
        - GCP: Displays GCP Workflow definition

        Use --provider flag to override the configured provider.

        Examples:
        spartan workflow view my-workflow
        spartan workflow view my-state-machine --output json
        spartan workflow view my-workflow --provider gcp --project-id my-project
        """
        try:
            from spartan.services.workflow import get_workflow_service

            service = get_workflow_service(
                provider=provider,
                region=region or location,
                profile=profile,
                project_id=project_id,
                location=location,
            )
            service.describe_workflow(
                name=name,
                output_format=output,
            )
        except ValueError as e:
            print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            print(f"[red]Error viewing workflow: {e}[/red]")
            raise typer.Exit(1)

    @workflow_app.command("run", help="Execute a workflow")
    def workflow_run(
        name: str = typer.Argument(..., help="Workflow name"),
        provider: Optional[str] = typer.Option(
            None,
            "--provider",
            "-p",
            help="Override configured cloud provider (aws, gcp)",
        ),
        input_data: Optional[str] = typer.Option(
            None, "--input", "-i", help="Execution input as JSON string"
        ),
        input_file: Optional[str] = typer.Option(
            None,
            "--input-file",
            "-f",
            help="Path to JSON file containing execution input",
        ),
        execution_name: Optional[str] = typer.Option(
            None, "--name", "-n", help="Custom execution name"
        ),
        yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
        region: Optional[str] = typer.Option(
            None, "--region", "-r", help="Cloud provider region/location"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """Execute a workflow.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Executes Step Functions state machine
        - GCP: Executes GCP Workflow

        Use --provider flag to override the configured provider.

        Examples:
        spartan workflow run my-workflow
        spartan workflow run my-workflow --input '{"key": "value"}'
        spartan workflow run my-workflow --input-file input.json --yes
        spartan workflow run my-workflow --provider gcp --project-id my-project
        """
        try:
            from spartan.services.workflow import get_workflow_service

            service = get_workflow_service(
                provider=provider,
                region=region or location,
                profile=profile,
                project_id=project_id,
                location=location,
            )
            service.run_workflow(
                workflow_name=name,
                input_data=input_data,
                input_file=input_file,
                execution_name=execution_name,
                skip_confirmation=yes,
            )
        except ValueError as e:
            print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            print(f"[red]Error running workflow: {e}[/red]")
            raise typer.Exit(1)

    @workflow_app.command("executions", help="List execution history for a workflow")
    def workflow_executions(
        name: str = typer.Argument(..., help="Workflow name"),
        provider: Optional[str] = typer.Option(
            None,
            "--provider",
            "-p",
            help="Override configured cloud provider (aws, gcp)",
        ),
        limit: int = typer.Option(
            10,
            "--limit",
            "-l",
            help="Maximum number of executions to display (default: 10, max: 100)",
        ),
        status: Optional[str] = typer.Option(
            None, "--status", help="Filter by execution status"
        ),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format (table, json, yaml)"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", "-r", help="Cloud provider region/location"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """List execution history for a workflow.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Lists Step Functions state machine executions
        - GCP: Lists GCP Workflow executions

        Use --provider flag to override the configured provider.

        Examples:
        spartan workflow executions my-workflow
        spartan workflow executions my-workflow --limit 20
        spartan workflow executions my-workflow --status SUCCEEDED --output json
        spartan workflow executions my-workflow --provider gcp --project-id my-project
        """
        try:
            from spartan.services.workflow import get_workflow_service

            # Validate limit
            if limit < 1 or limit > 100:
                print("[red]Error: Limit must be between 1 and 100[/red]")
                raise typer.Exit(1)

            service = get_workflow_service(
                provider=provider,
                region=region or location,
                profile=profile,
                project_id=project_id,
                location=location,
            )
            service.list_executions(
                workflow_name=name,
                max_results=limit,
                status_filter=status or "ALL",  # Default to "ALL" if not specified
                output_format=output,
            )
        except ValueError as e:
            print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            print(f"[red]Error listing executions: {e}[/red]")
            raise typer.Exit(1)

    @workflow_app.command(
        "execution", help="View detailed logs for a specific execution"
    )
    def workflow_execution_logs(
        execution_id: str = typer.Argument(..., help="Execution ID or ARN"),
        provider: Optional[str] = typer.Option(
            None,
            "--provider",
            "-p",
            help="Override configured cloud provider (aws, gcp)",
        ),
        workflow: Optional[str] = typer.Option(
            None,
            "--workflow",
            "-w",
            help="Workflow name (required for GCP when using execution ID only)",
        ),
        output: str = typer.Option(
            "table", "--output", "-o", help="Output format (table, json, yaml)"
        ),
        follow: bool = typer.Option(
            False,
            "--follow",
            "-f",
            help="Stream logs in real-time for running executions",
        ),
        region: Optional[str] = typer.Option(
            None, "--region", "-r", help="Cloud provider region/location"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        project_id: Optional[str] = typer.Option(
            None, "--project-id", help="GCP project ID (GCP only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """View detailed logs for a specific execution.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Displays Step Functions execution history
        - GCP: Displays GCP Workflow execution logs

        Use --provider flag to override the configured provider.

        For GCP: You can provide either:
        - Full resource name: projects/{project}/locations/{location}/workflows/{workflow}/executions/{id}
        - Just execution ID with --workflow flag: spartan workflow execution {id} --workflow {name}

        Examples:
        spartan workflow execution <execution-id>
        spartan workflow execution <execution-id> --workflow my-workflow
        spartan workflow execution <execution-id> --follow
        spartan workflow execution <execution-id> --output json
        spartan workflow execution <execution-id> --provider gcp --project-id my-project
        """
        try:
            from spartan.services.workflow import get_workflow_service

            service = get_workflow_service(
                provider=provider,
                region=region or location,
                profile=profile,
                project_id=project_id,
                location=location,
            )
            service.get_execution_logs(
                execution_id=execution_id,
                workflow_name=workflow,
                output_format=output,
                follow=follow,
            )
        except ValueError as e:
            print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            print(f"[red]Error viewing execution logs: {e}[/red]")
            raise typer.Exit(1)

    @workflow_app.command(
        "export", help="Export a workflow definition to a file or stdout"
    )
    def workflow_export(
        workflow_name: str = typer.Argument(..., help="Name of the workflow to export"),
        out: Optional[str] = typer.Option(
            None, "--out", "-o", help="Output file path (defaults to stdout)"
        ),
        revision: Optional[str] = typer.Option(
            None, "--revision", "-r", help="Specific revision to export (GCP only)"
        ),
        format: str = typer.Option(
            "yaml", "--format", "-f", help="Output format (yaml or json)"
        ),
        region: Optional[str] = typer.Option(
            None, "--region", help="Cloud provider region/location"
        ),
        project: Optional[str] = typer.Option(
            None, "--project", "-p", help="GCP project ID (GCP only)"
        ),
        provider: Optional[str] = typer.Option(
            None, "--provider", help="Override configured cloud provider (aws, gcp)"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """Export a workflow definition to a file or stdout.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Exports Step Functions state machine definition
        - GCP: Exports GCP Workflow definition

        Use --provider flag to override the configured provider.

        Examples:
        # Export to file
        spartan workflow export my-workflow --out workflow.yaml

        # Export specific revision (GCP)
        spartan workflow export my-workflow --revision 000001-99d --out workflow.yaml

        # Export to stdout (for piping)
        spartan workflow export my-workflow > workflow.yaml

        # Export as JSON
        spartan workflow export my-workflow --format json --out workflow.json

        # Export with specific project (GCP)
        spartan workflow export my-workflow --project my-project --out workflow.yaml
        """
        import sys

        try:
            # Validate format
            format_lower = format.lower()
            if format_lower not in ["yaml", "json"]:
                print(
                    f"[red]Error: Invalid format '{format}'. Valid formats: yaml, json[/red]",
                    file=sys.stderr,
                )
                raise typer.Exit(2)

            # Get service instance
            from spartan.services.workflow import get_workflow_service

            service = get_workflow_service(
                provider=provider,
                region=region or location,
                profile=profile,
                project_id=project,
                location=location,
            )

            # Export workflow
            result = service.export_workflow(
                workflow_name=workflow_name,
                revision_id=revision,
            )

            # Format output
            output_content = _format_export_output(
                result=result,
                format=format_lower,
            )

            # Write to file or stdout
            if out:
                try:
                    _write_to_file(out, output_content)
                    print(
                        f"[green]✓[/green] Exported workflow '{workflow_name}' to {out}"
                    )
                except PermissionError as e:
                    print(f"[red]Error: {e}[/red]", file=sys.stderr)
                    raise typer.Exit(2)
            else:
                # Write to stdout only (no extra messages)
                print(output_content)

        except google_exceptions.NotFound:
            print(
                f"[red]Error: Workflow '{workflow_name}' not found[/red]",
                file=sys.stderr if not out else sys.stdout,
            )
            raise typer.Exit(1)
        except google_exceptions.PermissionDenied as e:
            print(
                f"[red]Error: Permission denied. Ensure you have workflows.workflows.get permission[/red]",
                file=sys.stderr if not out else sys.stdout,
            )
            print(
                f"[yellow]Details: {e}[/yellow]",
                file=sys.stderr if not out else sys.stdout,
            )
            raise typer.Exit(2)
        except auth_exceptions.DefaultCredentialsError:
            print(
                f"[red]Error: GCP credentials not configured[/red]",
                file=sys.stderr if not out else sys.stdout,
            )
            print(
                f"[yellow]Suggestion: Run 'gcloud auth application-default login' or set GOOGLE_APPLICATION_CREDENTIALS[/yellow]",
                file=sys.stderr if not out else sys.stdout,
            )
            raise typer.Exit(2)
        except ValueError as e:
            print(f"[red]Error: {e}[/red]", file=sys.stderr if not out else sys.stdout)
            raise typer.Exit(2)
        except Exception as e:
            print(f"[red]Error: {e}[/red]", file=sys.stderr if not out else sys.stdout)
            raise typer.Exit(2)

    @workflow_app.command("import", help="Import a workflow definition from a file")
    def workflow_import(
        file: str = typer.Argument(..., help="Path to workflow definition file"),
        name: str = typer.Option(..., "--name", "-n", help="Workflow name"),
        region: Optional[str] = typer.Option(
            None, "--region", help="Cloud provider region/location"
        ),
        project: Optional[str] = typer.Option(
            None, "--project", "-p", help="GCP project ID (GCP only)"
        ),
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Validate without making changes"
        ),
        force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
        provider: Optional[str] = typer.Option(
            None, "--provider", help="Override configured cloud provider (aws, gcp)"
        ),
        profile: Optional[str] = typer.Option(
            None, "--profile", help="AWS CLI profile (AWS only)"
        ),
        location: Optional[str] = typer.Option(
            None, "--location", help="GCP location (GCP only)"
        ),
    ):
        """Import a workflow definition from a file.

        The command behavior adapts based on the provider configured in .spartan file:
        - AWS: Imports Step Functions state machine definition
        - GCP: Imports GCP Workflow definition

        Use --provider flag to override the configured provider.

        Examples:
        # Import (create or update)
        spartan workflow import workflow.yaml --name my-workflow

        # Dry run (validate only)
        spartan workflow import workflow.yaml --name my-workflow --dry-run

        # Force import (skip confirmation)
        spartan workflow import workflow.yaml --name my-workflow --force

        # Import with specific project (GCP)
        spartan workflow import workflow.yaml --name my-workflow --project my-project
        """
        import sys

        try:
            # Read file
            try:
                source_contents = _read_workflow_file(file)
            except FileNotFoundError:
                print(f"[red]Error: File '{file}' not found[/red]", file=sys.stderr)
                sys.exit(1)
            except PermissionError as e:
                print(f"[red]Error: {e}[/red]", file=sys.stderr)
                sys.exit(2)

            # Get service instance
            from spartan.services.workflow import get_workflow_service

            service = get_workflow_service(
                provider=provider,
                region=region or location,
                profile=profile,
                project_id=project,
                location=location,
            )

            # Validate workflow definition
            is_valid, error_msg = service.validate_workflow_definition(source_contents)
            if not is_valid:
                print(f"[red]Error: Invalid workflow definition[/red]", file=sys.stderr)
                print(f"[red]{error_msg}[/red]", file=sys.stderr)
                raise typer.Exit(2)

            # Check if workflow exists
            exists = service.workflow_exists(name)
            action = "update" if exists else "create"

            # Dry run mode
            if dry_run:
                print(f"[yellow]Dry run mode - no changes will be made[/yellow]")
                print(f"[blue]Would {action} workflow '{name}'[/blue]")

                if exists:
                    diff = service.get_workflow_diff(name, source_contents)
                    if diff:
                        print("\n[blue]Changes:[/blue]")
                        print(diff)
                    else:
                        print("[green]No changes detected[/green]")

                print(f"\n[green]✓[/green] Validation successful")
                return

            # Confirmation prompt for updates
            if exists and not force:
                diff = service.get_workflow_diff(name, source_contents)
                if diff:
                    print(
                        f"[yellow]Workflow '{name}' already exists. Changes:[/yellow]"
                    )
                    print(diff)
                else:
                    print(f"[green]Workflow '{name}' is already up to date[/green]")
                    return

                confirm = typer.confirm("Do you want to update the workflow?")
                if not confirm:
                    print("[yellow]Import aborted[/yellow]")
                    sys.exit(3)

            # Import workflow
            result = service.import_workflow(
                workflow_name=name,
                source_contents=source_contents,
            )

            # Display result
            action_past = "created" if result["action"] == "created" else "updated"
            print(f"[green]✓[/green] Workflow '{name}' {action_past} successfully")
            print(f"Revision: {result['revision_id']}")

        except google_exceptions.InvalidArgument as e:
            print(f"[red]Error: Invalid workflow definition[/red]", file=sys.stderr)
            print(f"[yellow]Details: {e}[/yellow]", file=sys.stderr)
            raise typer.Exit(2)
        except google_exceptions.PermissionDenied as e:
            print(
                f"[red]Error: Permission denied. Ensure you have workflows.workflows.create/update permission[/red]",
                file=sys.stderr,
            )
            print(f"[yellow]Details: {e}[/yellow]", file=sys.stderr)
            raise typer.Exit(2)
        except auth_exceptions.DefaultCredentialsError:
            print(f"[red]Error: GCP credentials not configured[/red]", file=sys.stderr)
            print(
                f"[yellow]Suggestion: Run 'gcloud auth application-default login' or set GOOGLE_APPLICATION_CREDENTIALS[/yellow]",
                file=sys.stderr,
            )
            raise typer.Exit(2)
        except ValueError as e:
            print(f"[red]Error: {e}[/red]", file=sys.stderr)
            raise typer.Exit(2)
        except Exception as e:
            print(f"[red]Error: {e}[/red]", file=sys.stderr)
            raise typer.Exit(2)

    @parquet_app.command(
        "convert", help="Convert between Parquet, CSV, and JSON formats"
    )
    def parquet_convert(
        path: str = typer.Option(
            ..., "--path", help="Input file or folder path (S3 or local)."
        ),
        format: str = typer.Option(
            ..., "--format", help="Target format: csv, json, or parquet."
        ),
        output: str = typer.Option(
            None,
            "--output",
            help="Output path (defaults to current directory or S3 prefix).",
        ),
        recursive: bool = typer.Option(
            False,
            "--recursive",
            help="Convert all files under the directory recursively.",
        ),
        flatten: bool = typer.Option(
            False, "--flatten", help="Flatten nested columns (optional)."
        ),
        columns: str = typer.Option(
            None, "--columns", help="Convert only selected columns (comma-separated)."
        ),
        overwrite: bool = typer.Option(
            False, "--overwrite", help="Overwrite existing output files."
        ),
        output_format: str = typer.Option(
            "table",
            "--display-format",
            help="Display format: table, json, yaml, text, markdown.",
        ),
    ):
        """Convert between Parquet, CSV, and JSON formats with support for S3 and local paths."""
        from spartan.services.parquet import ParquetService

        try:
            service = ParquetService()
            service.convert_files(
                path=path,
                target_format=format,
                output=output,
                recursive=recursive,
                flatten=flatten,
                columns=columns,
                overwrite=overwrite,
                output_format=output_format,
            )
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
            raise typer.Exit(1)

    @parquet_app.command("describe", help="Show schema and metadata of a Parquet file")
    def parquet_describe(
        path: str = typer.Option(
            ..., "--path", help="Parquet file path (S3 or local)."
        ),
        sample: bool = typer.Option(
            False, "--sample", help="Show a few rows of sample data."
        ),
        columns: str = typer.Option(
            None, "--columns", help="Show only specific columns (comma-separated)."
        ),
        summary: bool = typer.Option(
            False,
            "--summary",
            help="Show summary stats (min, max, nulls) for each column.",
        ),
        output_format: str = typer.Option(
            "table",
            "--format",
            help="Output format: table, json, yaml, text, markdown.",
        ),
    ):
        """Show schema and metadata of a Parquet file with support for S3 and local paths."""
        from spartan.services.parquet import ParquetService

        try:
            service = ParquetService()
            service.describe_file(
                path=path,
                sample=sample,
                columns=columns,
                summary=summary,
                output_format=output_format,
            )
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
            raise typer.Exit(1)

    @parquet_app.command("diff", help="Compare two Parquet files and show differences")
    def parquet_diff(
        expected: str = typer.Option(
            ..., "--expected", help="Expected parquet file path (S3 or local)."
        ),
        actual: str = typer.Option(
            ..., "--actual", help="Actual parquet file path (S3 or local)."
        ),
        columns: str = typer.Option(
            None, "--columns", help="Compare only specific columns (comma-separated)."
        ),
        output: str = typer.Option(
            None, "--output", help="Output differences to file (CSV or JSON)."
        ),
        tolerance: float = typer.Option(
            None, "--tolerance", help="Numerical tolerance for float comparisons."
        ),
        ignore_order: bool = typer.Option(
            False, "--ignore-order", help="Ignore row order when comparing."
        ),
        sample_diff: int = typer.Option(
            10, "--sample-diff", help="Number of different rows to show (default: 10)."
        ),
        key_columns: str = typer.Option(
            None,
            "--key-columns",
            help="Key columns for row matching (comma-separated).",
        ),
        output_format: str = typer.Option(
            "table",
            "--format",
            help="Output format: table, json, yaml, text, markdown.",
        ),
    ):
        """Compare two Parquet files and show detailed differences."""
        from spartan.services.parquet import ParquetService

        try:
            service = ParquetService()
            service.diff_files(
                expected_path=expected,
                actual_path=actual,
                columns=columns,
                output=output,
                tolerance=tolerance,
                ignore_order=ignore_order,
                sample_diff=sample_diff,
                key_columns=key_columns,
                output_format=output_format,
            )
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
            raise typer.Exit(1)

    @parquet_app.command("select", help="Select and filter data from a Parquet file")
    def parquet_select(
        path: str = typer.Option(
            ..., "--path", help="Parquet file path (S3 or local)."
        ),
        columns: str = typer.Option(
            None, "--columns", help="Select specific columns (comma-separated)."
        ),
        filter: str = typer.Option(
            None, "--filter", help="Filter expression (e.g., 'col1 > 100')."
        ),
        limit: int = typer.Option(
            None, "--limit", help="Limit the number of rows returned."
        ),
        output: str = typer.Option(
            None, "--output", help="Output file path (optional)."
        ),
        format: str = typer.Option(
            "table",
            "--format",
            help="Output format: table, json, yaml, text, markdown.",
        ),
    ):
        """Select and filter data from a Parquet file with support for S3 and local paths."""
        from spartan.services.parquet import ParquetService

        try:
            service = ParquetService()
            service.select_data(
                path=path,
                columns=columns,
                filter_expr=filter,
                limit=limit,
                output=output,
                output_format=format,
            )
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
            raise typer.Exit(1)

    @app.command(
        "init",
        help="Initialize a new Spartan project with a starter kit. eq. bogart or lazaro.",
    )
    def app_create(
        project_name: str,
        provider: str = typer.Option(
            "gcp",
            "--provider",
            help="Cloud provider (aws or gcp). Defaults to gcp.",
        ),
    ):
        # Validate provider
        if provider.lower() not in ["aws", "gcp"]:
            typer.echo(f"❌ Invalid provider '{provider}'. Must be 'aws' or 'gcp'.")
            raise typer.Exit(1)

        creator = ApplicationService(project_name, provider=provider)
        creator.create_app()
        typer.echo(f"✅ Project '{project_name}' created for {provider.upper()}")
        typer.echo("✅ Spartan, your project is ready to go!")

    @app.command(
        "serve",
        help="Serve the application.",
    )
    def serve(
        port: int = typer.Option(
            8000, "--port", "-p", help="Port to run the server on."
        ),
        reload: bool = typer.Option(
            True, "--reload/--no-reload", help="Enable auto-reload."
        ),
    ):
        """Run the FastAPI app using Uvicorn."""
        import subprocess
        import sys

        public_main_path = os.path.join(os.getcwd(), "public", "main.py")
        if not os.path.exists(public_main_path):
            print(
                "[red]No 'public/main.py' found. Please create a 'public' folder with a FastAPI 'main.py' file and an 'app' instance.[/]"
            )
            sys.exit(1)
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "public.main:app",
            f"--port={port}",
        ]
        if reload:
            cmd.append("--reload")
        try:
            result = subprocess.run(cmd)
            if result.returncode != 0:
                print(
                    f"[red]Failed to start server (exit code {result.returncode}):[/]"
                )
                sys.exit(result.returncode)
        except Exception as e:
            print(f"[red]Unexpected error: {e}[/]")


def run_poetry_command(command):
    """Run a poetry command with error handling."""
    try:
        result = subprocess.run(
            ["poetry", command], capture_output=True, text=True, check=True
        )

        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Command output:", e.output)


def is_valid_folder_name(name):
    """Check if a given string is a valid folder name."""
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-")

    return all(char in valid_chars for char in name)


# ========================================================================================
# Initialize configuration service and register all commands
# ========================================================================================


def initialize_app():
    """Initialize the Spartan CLI application.

    This function initializes the ConfigService singleton and handles any
    configuration errors gracefully by displaying error messages and exiting
    with a non-zero status code.
    """
    try:
        # Initialize configuration service
        config = ConfigService.get_instance()

        # Store config instance in app context for access by commands
        # Note: Typer doesn't have built-in state management like Click,
        # but the singleton pattern ensures consistent access throughout the app

        # Register all CLI commands
        register_commands()

    except ConfigError as e:
        # Display configuration error and exit
        print(f"[red]Configuration Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        # Display unexpected error and exit
        print(f"[red]Unexpected Error: {e}[/red]")
        sys.exit(1)


# Initialize the application
initialize_app()

if __name__ == "__main__":
    app()
