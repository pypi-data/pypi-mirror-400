"""Abstract base class for workflow services."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseWorkflowService(ABC):
    """Abstract base class for workflow services.

    This class defines the common interface that all workflow service
    implementations must follow, regardless of cloud provider.
    """

    @abstractmethod
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
        """List all workflows.

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
        pass

    @abstractmethod
    def describe_workflow(
        self,
        name: str,
        output_format: str = "table",
    ) -> None:
        """Describe a specific workflow.

        Args:
            name: Workflow name
            output_format: Output format (table, json, yaml, text, markdown)
        """
        pass

    @abstractmethod
    def run_workflow(
        self,
        workflow_name: str,
        input_data: Optional[str] = None,
        input_file: Optional[str] = None,
        execution_name: Optional[str] = None,
        skip_confirmation: bool = False,
    ) -> None:
        """Execute a workflow.

        Args:
            workflow_name: Name of the workflow to execute
            input_data: Execution input as JSON string
            input_file: Path to JSON file containing execution input
            execution_name: Custom execution name
            skip_confirmation: Skip confirmation prompt
        """
        pass

    @abstractmethod
    def list_executions(
        self,
        workflow_name: str,
        status_filter: str = "ALL",
        max_results: int = 50,
        output_format: str = "table",
    ) -> None:
        """List executions for a workflow.

        Args:
            workflow_name: Name of the workflow
            status_filter: Filter by status (ALL, RUNNING, SUCCEEDED, FAILED, etc.)
            max_results: Maximum number of executions to return
            output_format: Output format (table, json, yaml, text, markdown)
        """
        pass

    @abstractmethod
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
        """Get detailed logs for an execution.

        Args:
            execution_id: Execution ID or ARN/resource name
            workflow_name: Workflow name (optional, used to construct full resource path for GCP)
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
        pass
