"""
ExisOne Python SDK for Software Activation System.

Example usage:
    ```python
    from exisone import ExisOneClient, ExisOneClientOptions

    options = ExisOneClientOptions(
        base_url="https://www.exisone.com",
        access_token="your-api-token"
    )
    client = ExisOneClient(options)

    # Generate hardware ID
    hardware_id = client.generate_hardware_id()

    # Activate a license
    result = client.activate(
        activation_key="XXXX-XXXX-XXXX-XXXX",
        email="user@example.com",
        hardware_id=hardware_id,
        product_name="MyProduct"
    )

    if result.success:
        print("License activated!")
    else:
        print(f"Activation failed: {result.error_message}")
    ```
"""

from .client import ExisOneClient, ExisOneClientOptions, __version__
from .hardware import generate_hardware_id
from .models import (
    ActivationResult,
    DeactivationResult,
    OfflineKeyPayload,
    OfflineValidationResult,
    SmartValidationResult,
    ValidationResult,
)

__all__ = [
    # Main client
    "ExisOneClient",
    "ExisOneClientOptions",
    # Utility functions
    "generate_hardware_id",
    # Result types
    "ActivationResult",
    "ValidationResult",
    "OfflineValidationResult",
    "SmartValidationResult",
    "DeactivationResult",
    "OfflineKeyPayload",
    # Version
    "__version__",
]
