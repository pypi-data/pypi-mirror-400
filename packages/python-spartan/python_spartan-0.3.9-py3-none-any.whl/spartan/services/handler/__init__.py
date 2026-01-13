"""Handler service module.

This module provides services for managing serverless functions across
different cloud providers (AWS Lambda, GCP Cloud Functions).
"""

from typing import Optional

from spartan.services.config import ConfigService
from spartan.services.handler.aws_handler import AWSHandlerService
from spartan.services.handler.base import BaseHandlerService
from spartan.services.handler.gcp_handler import GCPHandlerService


def get_handler_service(
    name: str,
    provider: Optional[str] = None,
) -> BaseHandlerService:
    """Factory function to get the appropriate handler service.

    Args:
        name: Name of the handler
        provider: Cloud provider ('aws' or 'gcp'). If None, uses ConfigService.

    Returns:
        BaseHandlerService: Instance of AWS or GCP handler service

    Raises:
        ValueError: If provider is not supported
    """
    # Get provider from configuration if not specified
    if provider is None:
        config = ConfigService.get_instance()
        provider = config.get_provider()

    provider = provider.lower()

    if provider == "aws":
        return AWSHandlerService(name=name)
    elif provider == "gcp":
        return GCPHandlerService(name=name)
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Supported providers: aws, gcp"
        )


# For backward compatibility, alias AWSHandlerService as HandlerService
HandlerService = AWSHandlerService

__all__ = [
    "BaseHandlerService",
    "AWSHandlerService",
    "GCPHandlerService",
    "HandlerService",
    "get_handler_service",
]
