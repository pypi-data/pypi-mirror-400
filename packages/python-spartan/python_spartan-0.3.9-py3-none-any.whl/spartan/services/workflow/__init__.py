"""Workflow service module for managing cloud provider workflows.

This module provides a unified interface for managing workflows across
different cloud providers (AWS Step Functions, GCP Workflows).
"""

import os
from typing import Optional

from spartan.services.config import ConfigService
from spartan.services.workflow.base import BaseWorkflowService


def get_workflow_service(
    provider: Optional[str] = None,
    region: Optional[str] = None,
    profile: Optional[str] = None,
    project_id: Optional[str] = None,
    location: Optional[str] = None,
) -> BaseWorkflowService:
    """Factory function to get the appropriate workflow service.

    Args:
        provider: Cloud provider ('aws' or 'gcp'). If None, uses ConfigService.
        region: AWS region or GCP location. If None, uses environment variables:
               - AWS: AWS_DEFAULT_REGION or AWS_REGION
               - GCP: GOOGLE_CLOUD_REGION
        profile: AWS CLI profile (AWS only)
        project_id: GCP project ID (GCP only). If None, uses GOOGLE_CLOUD_PROJECT env var.
        location: GCP location (GCP only). If None, uses GOOGLE_CLOUD_REGION env var.

    Returns:
        BaseWorkflowService: Instance of AWS or GCP workflow service

    Raises:
        ValueError: If provider is not supported

    Examples:
        >>> # Use configured provider with environment variables
        >>> service = get_workflow_service()
        >>>
        >>> # Override provider
        >>> service = get_workflow_service(provider='aws', region='us-east-1')
        >>>
        >>> # GCP with project ID
        >>> service = get_workflow_service(
        ...     provider='gcp',
        ...     project_id='my-project',
        ...     location='us-central1'
        ... )
    """
    # Get provider from configuration if not specified
    if provider is None:
        config = ConfigService.get_instance()
        provider = config.get_provider()

    provider = provider.lower()

    if provider == "aws":
        from spartan.services.workflow.aws_workflow import AWSWorkflowService

        # Use environment variables as fallback for region
        aws_region = (
            region
            or os.environ.get("AWS_DEFAULT_REGION")
            or os.environ.get("AWS_REGION")
        )
        return AWSWorkflowService(region=aws_region, profile=profile)
    elif provider == "gcp":
        from spartan.services.workflow.gcp_workflow import GCPWorkflowService

        # Use environment variables as fallback for project_id and location
        gcp_project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        gcp_location = location or region or os.environ.get("GOOGLE_CLOUD_REGION")
        return GCPWorkflowService(
            project_id=gcp_project_id,
            location=gcp_location,
        )
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Supported providers: aws, gcp"
        )


__all__ = ["BaseWorkflowService", "get_workflow_service"]
