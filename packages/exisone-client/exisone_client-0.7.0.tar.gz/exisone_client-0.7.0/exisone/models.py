"""Data models for ExisOne client responses."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class ActivationResult:
    """Result of license activation."""
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    server_version: Optional[str] = None
    minimum_required_version: Optional[str] = None
    license_data: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of online license validation."""
    is_valid: bool
    status: str = ""
    expiration_date: Optional[datetime] = None
    features: List[str] = field(default_factory=list)
    server_version: Optional[str] = None
    minimum_required_version: Optional[str] = None


@dataclass
class OfflineValidationResult:
    """Result of offline license validation."""
    is_valid: bool
    error_message: Optional[str] = None
    product_name: Optional[str] = None
    product_id: int = 0
    expiration_date: Optional[datetime] = None
    email: Optional[str] = None
    features: List[str] = field(default_factory=list)
    version: Optional[str] = None
    is_expired: bool = False
    hardware_mismatch: bool = False


@dataclass
class SmartValidationResult:
    """Result of smart validation (online or offline)."""
    is_valid: bool
    status: str = ""
    expiration_date: Optional[datetime] = None
    features: List[str] = field(default_factory=list)
    was_offline: bool = False
    error_message: Optional[str] = None
    product_name: Optional[str] = None
    server_version: Optional[str] = None
    minimum_required_version: Optional[str] = None


@dataclass
class DeactivationResult:
    """Result of smart deactivation."""
    success: bool
    server_notified: bool = False
    error_message: Optional[str] = None


@dataclass
class OfflineKeyPayload:
    """Payload embedded in offline activation codes."""
    product_id: int
    product_name: str
    hardware_id: str
    expiration_date: datetime
    email: str
    features: List[str]
    tenant_id: int
    version: str = ""
