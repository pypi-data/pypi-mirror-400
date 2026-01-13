"""ExisOne client for license activation and validation."""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

import requests

from .hardware import generate_hardware_id
from .models import (
    ActivationResult,
    DeactivationResult,
    OfflineValidationResult,
    SmartValidationResult,
    ValidationResult,
)
from .offline import is_offline_key, validate_offline


__version__ = "0.7.0"


@dataclass
class ExisOneClientOptions:
    """Configuration options for ExisOneClient."""

    base_url: str = ""
    """Base URL for the ExisOne API (must use HTTPS)."""

    access_token: str = ""
    """API access token for authentication."""

    offline_public_key: Optional[str] = None
    """RSA public key in PEM format for offline license validation."""

    allowed_base_url_hosts: Optional[List[str]] = None
    """If set, restricts base_url to these hosts only."""

    timeout: int = 30
    """Request timeout in seconds."""


class ExisOneClient:
    """
    Client for ExisOne Software Activation System.

    Provides methods for license activation, validation, deactivation,
    and offline validation.

    Example:
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
        ```
    """

    def __init__(
        self,
        options: Optional[ExisOneClientOptions] = None,
        session: Optional[requests.Session] = None
    ):
        """
        Initialize the ExisOne client.

        Args:
            options: Client configuration options
            session: Optional requests.Session for custom HTTP configuration
        """
        self._options = options or ExisOneClientOptions()

        # Check environment variable for base URL if not set
        if not self._options.base_url:
            env_url = os.environ.get("EXISONE_BASEURL", "")
            if env_url:
                self._options.base_url = env_url

        self._validate_base_url(self._options.base_url)
        self._session = session or requests.Session()

    def with_base_url(self, base_url: str) -> "ExisOneClient":
        """
        Create a new client with a different base URL.

        Args:
            base_url: New base URL to use

        Returns:
            Self for method chaining
        """
        self._validate_base_url(base_url)
        self._options.base_url = base_url
        return self

    @staticmethod
    def get_version() -> str:
        """Get the client SDK version."""
        return __version__

    @staticmethod
    def generate_hardware_id() -> str:
        """
        Generate a hardware fingerprint for this machine.

        Returns:
            64-character uppercase hex string (SHA-256 hash)
        """
        return generate_hardware_id()

    def activate(
        self,
        activation_key: str,
        email: str,
        hardware_id: str,
        product_name: str,
        version: Optional[str] = None
    ) -> ActivationResult:
        """
        Activate a license on this machine.

        Args:
            activation_key: The activation key to activate
            email: User's email address
            hardware_id: Hardware fingerprint from generate_hardware_id()
            product_name: Name of the product
            version: Optional client version string

        Returns:
            ActivationResult with success status and any error details
        """
        payload = {
            "activationKey": activation_key,
            "email": email,
            "hardwareId": hardware_id,
            "productName": product_name,
        }
        if version:
            payload["version"] = version

        try:
            response = self._post("/api/license/activate", payload)

            if not response.ok:
                try:
                    data = response.json()
                    return ActivationResult(
                        success=False,
                        error_code=data.get("error"),
                        error_message=data.get("message", response.text),
                        server_version=data.get("serverVersion"),
                        minimum_required_version=data.get("minimumRequiredVersion")
                    )
                except Exception:
                    return ActivationResult(
                        success=False,
                        error_message=f"{response.status_code} {response.reason}: {response.text}"
                    )

            try:
                data = response.json()
                return ActivationResult(
                    success=True,
                    server_version=data.get("serverVersion"),
                    minimum_required_version=data.get("minimumRequiredVersion"),
                    license_data=response.text
                )
            except Exception:
                return ActivationResult(success=True, license_data=response.text)

        except requests.RequestException as e:
            return ActivationResult(
                success=False,
                error_message=f"Network error: {str(e)}"
            )

    def validate(
        self,
        activation_key: str,
        hardware_id: str,
        product_name: Optional[str] = None,
        version: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a license online.

        Args:
            activation_key: The activation key to validate
            hardware_id: Hardware fingerprint
            product_name: Optional product name
            version: Optional client version string

        Returns:
            ValidationResult with validation status and license details
        """
        payload = {
            "activationKey": activation_key,
            "hardwareId": hardware_id,
        }
        if product_name:
            payload["productName"] = product_name
        if version:
            payload["version"] = version

        response = self._post("/api/license/validate", payload)
        response.raise_for_status()

        data = response.json()

        # Parse expiration date
        expiration_date = None
        exp_str = data.get("expirationDate")
        if exp_str:
            try:
                expiration_date = datetime.fromisoformat(exp_str.replace("Z", "+00:00").replace("+00:00", ""))
            except Exception:
                pass

        return ValidationResult(
            is_valid=data.get("isValid", False),
            status=data.get("status", "invalid" if not data.get("isValid") else "licensed"),
            expiration_date=expiration_date,
            features=data.get("features", []),
            server_version=data.get("serverVersion"),
            minimum_required_version=data.get("minimumRequiredVersion")
        )

    def deactivate(
        self,
        activation_key: str,
        hardware_id: str,
        product_name: str
    ) -> bool:
        """
        Deactivate a license.

        Args:
            activation_key: The activation key to deactivate
            hardware_id: Hardware fingerprint
            product_name: Name of the product

        Returns:
            True if deactivation succeeded

        Raises:
            requests.HTTPError: If the server returns an error
        """
        payload = {
            "licenseKey": activation_key,
            "hardwareId": hardware_id,
            "productName": product_name,
        }

        response = self._post("/api/license/deactivate", payload)
        response.raise_for_status()
        return True

    def generate_activation_key(
        self,
        product_name: str,
        email: str,
        plan_id: Optional[int] = None,
        validity_days: Optional[int] = None
    ) -> str:
        """
        Generate a new activation key (requires admin token).

        Args:
            product_name: Name of the product
            email: User's email address
            plan_id: Optional plan ID
            validity_days: Optional validity period in days

        Returns:
            The generated activation key
        """
        payload = {
            "productName": product_name,
            "email": email,
        }
        if plan_id is not None:
            payload["planId"] = plan_id
        if validity_days is not None:
            payload["validityDays"] = validity_days

        response = self._post("/api/activationkey/generate", payload)
        response.raise_for_status()
        return response.text

    def get_licensed_features_csv(self, activation_key: str) -> str:
        """
        Get licensed features as a comma-separated string.

        Args:
            activation_key: The activation key

        Returns:
            Comma-separated list of feature names
        """
        payload = {"activationKey": activation_key}
        response = self._post("/api/license/features/csv", payload)
        response.raise_for_status()

        data = response.json()
        return data.get("features", "")

    def send_support_ticket(
        self,
        product_name: str,
        email: str,
        subject: str,
        message: str
    ) -> None:
        """
        Send a support ticket.

        Args:
            product_name: Name of the product
            email: User's email address
            subject: Ticket subject
            message: Ticket message body
        """
        payload = {
            "productName": product_name,
            "email": email,
            "subject": subject,
            "message": message,
        }

        response = self._post("/api/support/ticket", payload)
        response.raise_for_status()

    def validate_offline(
        self,
        offline_code: str,
        hardware_id: str
    ) -> OfflineValidationResult:
        """
        Validate an offline activation code locally without server connection.

        Requires offline_public_key to be set in options.

        Args:
            offline_code: The offline activation code (Base32 with dashes)
            hardware_id: The hardware ID to validate against

        Returns:
            OfflineValidationResult with validation details
        """
        public_key = self._options.offline_public_key or ""
        return validate_offline(offline_code, hardware_id, public_key)

    def validate_smart(
        self,
        activation_key_or_offline_code: str,
        hardware_id: str,
        product_name: Optional[str] = None
    ) -> SmartValidationResult:
        """
        Smart validation that auto-detects offline vs online keys.

        For offline keys, validates locally. For online keys, validates with server.
        Falls back to offline validation if server is unreachable.

        Args:
            activation_key_or_offline_code: Either an online key or offline code
            hardware_id: Hardware fingerprint
            product_name: Optional product name (for online validation)

        Returns:
            SmartValidationResult with validation details
        """
        # Detect if this is an offline key based on length
        if is_offline_key(activation_key_or_offline_code):
            # Offline key - validate locally
            offline_result = self.validate_offline(activation_key_or_offline_code, hardware_id)

            # Opportunistically try to sync with server (fire and forget)
            if offline_result.is_valid:
                try:
                    self.validate(activation_key_or_offline_code, hardware_id)
                except Exception:
                    pass  # Ignore server errors for offline licenses

            status = "licensed"
            if not offline_result.is_valid:
                status = "expired" if offline_result.is_expired else "invalid"

            return SmartValidationResult(
                is_valid=offline_result.is_valid,
                status=status,
                expiration_date=offline_result.expiration_date,
                features=offline_result.features,
                was_offline=True,
                error_message=offline_result.error_message,
                product_name=offline_result.product_name
            )

        # Online key - try server validation first
        try:
            result = self.validate(
                activation_key_or_offline_code,
                hardware_id,
                product_name
            )
            return SmartValidationResult(
                is_valid=result.is_valid,
                status=result.status,
                expiration_date=result.expiration_date,
                features=result.features,
                was_offline=False,
                product_name=product_name,
                server_version=result.server_version,
                minimum_required_version=result.minimum_required_version
            )
        except requests.RequestException:
            # Server unreachable - try offline validation as fallback
            if self._options.offline_public_key:
                offline_result = self.validate_offline(
                    activation_key_or_offline_code,
                    hardware_id
                )
                return SmartValidationResult(
                    is_valid=offline_result.is_valid,
                    status="licensed" if offline_result.is_valid else "invalid",
                    expiration_date=offline_result.expiration_date,
                    features=offline_result.features,
                    was_offline=True,
                    error_message=None if offline_result.is_valid else "Server unreachable and offline validation failed",
                    product_name=offline_result.product_name
                )

            return SmartValidationResult(
                is_valid=False,
                status="offline",
                was_offline=True,
                error_message="Server unreachable and no offline validation available"
            )

    def deactivate_smart(
        self,
        activation_key_or_offline_code: str,
        hardware_id: str,
        product_name: str
    ) -> DeactivationResult:
        """
        Deactivate a license with opportunistic online sync.

        Attempts to notify the server, but succeeds even if offline.

        Args:
            activation_key_or_offline_code: The key to deactivate
            hardware_id: Hardware fingerprint
            product_name: Name of the product

        Returns:
            DeactivationResult with status
        """
        try:
            self.deactivate(activation_key_or_offline_code, hardware_id, product_name)
            return DeactivationResult(
                success=True,
                server_notified=True
            )
        except requests.RequestException:
            # Server unreachable - deactivation succeeds locally
            return DeactivationResult(
                success=True,
                server_notified=False,
                error_message="License deactivated locally. Server will be notified when connection is restored."
            )
        except Exception as e:
            return DeactivationResult(
                success=False,
                server_notified=False,
                error_message=str(e)
            )

    def _post(self, path: str, payload: dict) -> requests.Response:
        """Make a POST request to the API."""
        url = urljoin(self._options.base_url, path)
        headers = {"Content-Type": "application/json"}

        if self._options.access_token:
            headers["Authorization"] = f"ExisOneApi {self._options.access_token}"

        return self._session.post(
            url,
            json=payload,
            headers=headers,
            timeout=self._options.timeout
        )

    def _validate_base_url(self, base_url: str) -> None:
        """Validate the base URL."""
        if not base_url:
            raise ValueError("base_url is required")

        if not base_url.startswith("https://"):
            raise ValueError("base_url must use HTTPS")

        if self._options.allowed_base_url_hosts:
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            if parsed.hostname not in self._options.allowed_base_url_hosts:
                raise ValueError("base_url host not allowed")
