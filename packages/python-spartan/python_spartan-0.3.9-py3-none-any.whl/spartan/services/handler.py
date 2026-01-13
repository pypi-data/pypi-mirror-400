"""Handler service for AWS Lambda function management.

DEPRECATED: This module is deprecated. Please use:
- spartan.services.handler.aws_handler.AWSHandlerService for AWS Lambda
- spartan.services.handler.gcp_handler.GCPHandlerService for GCP Cloud Functions

This module is maintained for backward compatibility and will be removed in a future version.
"""

import warnings

# Import AWSHandlerService and alias it as HandlerService for backward compatibility
from spartan.services.handler.aws_handler import AWSHandlerService as HandlerService

# Issue deprecation warning when this module is imported
warnings.warn(
    "spartan.services.handler.HandlerService is deprecated. "
    "Please use spartan.services.handler.aws_handler.AWSHandlerService instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["HandlerService"]
